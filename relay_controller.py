import time
import threading

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("[Hardware] Warning: RPi.GPIO module not found. Mocking relay output.")

class RelayController:
    """
    A lightweight, asynchronous controller for a GPIO relay designed for Raspberry Pi.
    Uses RPi.GPIO for robust physical pin control.
    """
    def __init__(self, pin=17, pump_duration=2.0, cooldown=5.0):
        self.pin = pin
        self.pump_duration = pump_duration
        self.cooldown = cooldown
        
        self.is_pumping = False
        self.last_pump_time = 0.0

        if GPIO_AVAILABLE:
            try:
                # Use BCM pin numbering
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                GPIO.setup(self.pin, GPIO.OUT)
                GPIO.output(self.pin, GPIO.LOW) # Ensure it's off initially
                print(f"[Hardware] Initialized Relay on BCM GPIO {self.pin}.")
            except Exception as e:
                print(f"[Hardware] Error setting up GPIO: {e}")

    def _pump_thread(self):
        self.is_pumping = True
        self.last_pump_time = time.time()
        
        print(f"[Relay] -> PUMP ON (Duration: {self.pump_duration}s)...")
        if GPIO_AVAILABLE:
            GPIO.output(self.pin, GPIO.HIGH)
            
        time.sleep(self.pump_duration)
        
        print("[Relay] -> PUMP OFF. Entering Cooldown...")
        if GPIO_AVAILABLE:
            GPIO.output(self.pin, GPIO.LOW)
            
        self.is_pumping = False

    def trigger_pump(self):
        """
        Attempts to trigger the pump. Returns True if triggered, False if on cooldown or already pumping.
        """
        if self.is_pumping:
            return False
            
        time_since_last = time.time() - self.last_pump_time
        if time_since_last < (self.pump_duration + self.cooldown):
            # Still in cooldown
            return False

        # Start the pump sequence in a non-blocking thread so the camera feed doesn't freeze
        t = threading.Thread(target=self._pump_thread)
        t.daemon = True
        t.start()
        return True

    def get_status(self):
        if self.is_pumping:
            return "PUMPING"
        elif time.time() - self.last_pump_time < (self.pump_duration + self.cooldown):
            return "COOLDOWN"
        return "READY"

    def cleanup(self):
        """Clean up GPIO resources on exit."""
        if GPIO_AVAILABLE:
            GPIO.cleanup()
            print("[Hardware] GPIO Cleanup Complete.")

if __name__ == "__main__":
    # Test
    rc = RelayController()
    print("Triggering pump...")
    rc.trigger_pump()
    time.sleep(1)
    print("Status:", rc.get_status())
    time.sleep(7)
    print("Status after wait:", rc.get_status())
    rc.trigger_pump()
    time.sleep(3)
    rc.cleanup()
