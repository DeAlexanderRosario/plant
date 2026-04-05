import cv2
import torch
import numpy as np
from ultralytics import YOLO

# Comprehensive Class Mappings (Professional Labels)
class EdenScopeInference:
    """
    Optimized Inference Engine for EdenScope.
    Designed for production deployment on CPU.
    """
# Comprehensive Class Mappings (Professional Labels)
TREATMENT_ADVICE = {
    "Scab": "Apply fungicides like Myclobutanil or Captan. Prune infected branches and remove fallen leaves to prevent overwintering.",
    "Rust": "Use sulfur-based fungicides or Copper sprays. Improve air circulation and avoid overhead watering.",
    "Blight": "Remove and destroy infected tissue immediately. Apply Copper-based fungicides every 7-10 days during wet weather.",
    "Spot": "Apply Neem Oil or Potassium Bicarbonate. Ensure plants have adequate spacing for air flow.",
    "Mildew": "Mix 1 tbsp baking soda with 1 gallon water and a dash of dish soap; spray weekly. Increase sunlight exposure.",
    "Virus": "No cure for viral infections. Remove and destroy the entire plant to prevent spread. Control insect vectors like aphids.",
    "Mites": "Spray with strong water streams to dislodge. Use Insecticidal soap or Neem oil. Encourage natural predators like ladybugs.",
    "Rot": "Improve drainage and reduce watering. Remove affected fruit or leaves promptly.",
    "Healthy": "Plant appears in peak condition. Maintain current irrigation and fertilization schedule. Monitor for early signs of stress."
}

class EdenScopeInference:
    """
    Optimized Inference Engine for EdenScope.
    Designed for production deployment on CPU.
    """
    # Comprehensive Class Mappings (Professional Labels)
    CLASS_MAPPINGS = {
        "Apple leaf": "Healthy Apple",
        "Apple Scab Leaf": "Apple Scab",
        "Apple rust leaf": "Apple Rust",
        "Bell_pepper leaf": "Healthy Bell Pepper",
        "Bell_pepper leaf spot": "Pepper Leaf Spot",
        "Blueberry leaf": "Healthy Blueberry",
        "Cherry leaf": "Healthy Cherry",
        "Corn leaf blight": "Corn Leaf Blight",
        "Corn Gray leaf spot": "Corn Gray Spot",
        "Corn rust leaf": "Corn Rust",
        "Peach leaf": "Healthy Peach",
        "Potato leaf": "Healthy Potato",
        "Potato leaf early blight": "Potato Early Blight",
        "Potato leaf late blight": "Potato Late Blight",
        "Raspberry leaf": "Healthy Raspberry",
        "Soyabean leaf": "Healthy Soybean",
        "Squash Powdery mildew leaf": "Squash Powdery Mildew",
        "Strawberry leaf": "Healthy Strawberry",
        "Tomato leaf": "Healthy Tomato",
        "Tomato Early blight leaf": "Tomato Early Blight",
        "Tomato Septoria leaf spot": "Tomato Septoria Spot",
        "Tomato leaf bacterial spot": "Tomato Bacterial Spot",
        "Tomato leaf late blight": "Tomato Late Blight",
        "Tomato leaf mosaic virus": "Tomato Mosaic Virus",
        "Tomato leaf yellow virus": "Tomato Yellow Virus",
        "Tomato mold leaf": "Tomato Mold",
        "Tomato two spotted spider mites leaf": "Tomato Spider Mites",
        "grape leaf": "Healthy Grape",
        "grape leaf black rot": "Grape Black Rot",
        "healthy": "Healthy",
        "background": "Clear Ground"
    }

    def __init__(self, model_path, device='cpu'):
        print(f"Initializing EdenScope Inference on {device}...")
        self.device = torch.device(device)
        self.model = YOLO(model_path)
        # Force model to device
        self.model.to(self.device)
        
    def predict(self, frame, imgsz=320, conf=0.25):
        """Perform inference on a single frame."""
        results = self.model.predict(
            source=frame, 
            device=self.device, 
            imgsz=imgsz, 
            conf=conf, 
            verbose=False
        )
        return results

    def draw_results(self, frame, results):
        """Draw bounding boxes and labels on the frame."""
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Bbox coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                
                # Get label
                raw_label = result.names[cls_id]
                label = self.CLASS_MAPPINGS.get(raw_label, raw_label)
                
                # Styling
                is_healthy = "Healthy" in label or "healthy" in raw_label or "Clear" in label
                color = (0, 255, 0) if is_healthy else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                text = f"{label} ({conf:.1%})"
                cv2.putText(frame, text, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return frame

if __name__ == "__main__":
    # Test loading
    try:
        engine = EdenScopeInference("weights/best-yolov8n.pt")
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
