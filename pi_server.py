import sys
print("[System] SCRIPT BOOTING - PLEASE WAIT...", flush=True)

def check_ram():
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if "MemAvailable" in line:
                    print(f"[System] RAM -> {line.strip()}", flush=True)
                if "SwapTotal" in line:
                    print(f"[System] RAM -> {line.strip()}", flush=True)
    except:
        pass

check_ram()
import os
import cv2
import time
import threading
from flask import Flask, render_template, Response, jsonify, request
from werkzeug.utils import secure_filename
from inference import EdenScopeInference
from relay_controller import RelayController

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # Limit upload size to 100MB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Hardware and AI Initialization
print("[System] Loading AI Engine...")
engine = EdenScopeInference("weights/best-yolov8n.pt")
relay = RelayController(pin=17, pump_duration=2.0, cooldown=5.0)

# Global State
config = {
    "confidence_threshold": 0.35,
    "pump_duration": 2.0,
    "pump_cooldown": 5.0
}

video_source = 0  # 0 for camera, or path to MP4
camera_lock = threading.Lock()
video_capture = None

state_status = {
    "target": "SCANNING...",
    "is_healthy": None,
    "pump_status": "READY",
    "source": "CAMERA"
}

def get_video_capture():
    global video_capture, video_source
    if video_capture is None or not video_capture.isOpened():
        # Use V4L2 for USB webcams on Linux/Pi for better performance
        if isinstance(video_source, int) and os.name != 'nt':
            video_capture = cv2.VideoCapture(video_source, cv2.CAP_V4L2)
        else:
            video_capture = cv2.VideoCapture(video_source)
            
        # Set lower capture resolution to save CPU - Pi 3B can't handle 1080p well
        if video_source == 0:
            video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            video_capture.set(cv2.CAP_PROP_FPS, 15) # 15 FPS is enough for detection
            time.sleep(2.0) 
    return video_capture

def generate_frames():
    global state_status, video_source

    while True:
        loop_start = time.time()

        with camera_lock:
            cap = get_video_capture()
            ret, frame = cap.read()
            
            if not ret:
                # If a video file ended, loop it or switch to camera (looping it here for demo purposes)
                if video_source != 0:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    time.sleep(0.5)
                    continue

        # Run Inference
        results = engine.predict(frame, conf=config["confidence_threshold"])
        
        # Analyze Results
        detections = []
        is_healthy = True
        top_label = "SCANNING..."

        for r in results:
            for box in r.boxes:
                raw_name = engine.model.names[int(box.cls[0])]
                label = engine.CLASS_MAPPINGS.get(raw_name, raw_name)
                detections.append(label)
                if "Healthy" not in label and "Clear" not in label:
                    is_healthy = False
                
        if detections:
            top_label = detections[0]
            # --- HARDWARE TRIGGER LOGIC ---
            if not is_healthy:
                # Target is diseased / anomalous
                relay.trigger_pump()
        else:
            is_healthy = None # None means no target

        # Draw overlays for the feed
        display_frame = engine.draw_results(frame.copy(), results)

        # Update global state for UI polling
        state_status['target'] = top_label
        state_status['is_healthy'] = is_healthy
        state_status['pump_status'] = relay.get_status()
        state_status['source'] = "VIDEO UPLOAD" if video_source != 0 else "CAMERA"

        # Encode to JPEG for MJPEG stream
        ret, buffer = cv2.imencode('.jpg', display_frame)
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        # Rate Limit - If processing a file, sleep to maintain ~20 FPS.
        # This prevents the Pi 3B from hitting 100% CPU and hanging.
        if video_source != 0:
            elapsed = time.time() - loop_start
            target_delay = 0.05 # 20 FPS
            if elapsed < target_delay:
                time.sleep(target_delay - elapsed)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    # Return current state for telemetry dashboard
    # The actual pump status is real-time from the relay
    state_status['pump_status'] = relay.get_status()
    return jsonify(state_status)

@app.route('/upload_video', methods=['POST'])
def upload_video():
    global video_source, video_capture
    if 'video' not in request.files:
        return jsonify({"success": False, "error": "No video file found"}), 400
        
    file = request.files['video']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400
        
    if file:
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"[System] Saving uploaded video to {filepath}...")
            file.save(filepath)
            
            with camera_lock:
                if video_capture:
                    video_capture.release()
                video_source = filepath
                video_capture = None # Force re-init next frame request
                
            return jsonify({"success": True, "message": "Video uploaded and source switched"})
        except Exception as e:
            print(f"[System] Upload failed: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

@app.route('/switch_camera', methods=['POST'])
def switch_camera():
    global video_source, video_capture
    with camera_lock:
        if video_capture:
            video_capture.release()
        video_source = 0
        video_capture = None
    return jsonify({"success": True, "message": "Switched to live camera"})

@app.route('/run_sample', methods=['POST'])
def run_sample():
    global video_source, video_capture
    sample_path = 'samples/test_video.mp4'
    if not os.path.exists(sample_path):
        return jsonify({"success": False, "error": "Sample video not found"}), 404
        
    with camera_lock:
        if video_capture:
            video_capture.release()
        video_source = sample_path
        video_capture = None
    return jsonify({"success": True, "message": "Running sample video"})

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    global config
    if request.method == 'GET':
        return jsonify(config)
    elif request.method == 'POST':
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "Invalid payload"}), 400
            
        # Update config values safely
        if 'confidence_threshold' in data:
            config['confidence_threshold'] = float(data['confidence_threshold'])
            
        if 'pump_duration' in data:
            config['pump_duration'] = float(data['pump_duration'])
            relay.pump_duration = config['pump_duration']
            
        if 'pump_cooldown' in data:
            config['pump_cooldown'] = float(data['pump_cooldown'])
            relay.cooldown = config['pump_cooldown']
            
        return jsonify({"success": True, "message": "Settings updated", "config": config})

if __name__ == '__main__':
    try:
        # Run app on all interfaces (0.0.0.0) so it's accessible over local WiFi
        print("[System] Starting payload local web server...")
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    finally:
        print("[System] Shutting down, cleaning up hardware...")
        relay.cleanup()
