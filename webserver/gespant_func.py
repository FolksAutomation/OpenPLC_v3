import threading
import time

class LedSys(threading.Thread):
    def __init__(self):
        super().__init__()  # Initialize the Thread class properly
        self.led_pin = 537  # GPIO pin number
        self.flag_blink = False
        self.blink_period = 1
        self._thread_started = False
        try:
            # Export the GPIO pin if necessary
            with open('/sys/class/gpio/export', 'a') as file:
                file.write(str(self.led_pin))
                print("Text appended to gpio ledsys successfully.")
            self.setLED()
        except Exception as e:
            print(f"Error in gpio setup: {e}")

    def setLED(self):
        """Set the LED to ON"""
        try:
            with open(f'/sys/class/gpio/gpio{self.led_pin}/value', 'w') as writer:
                writer.writelines('0')
        except Exception as e:
            print(f"Error setting LED: {e}")

    def clearLED(self):
        """Set the LED to OFF"""
        try:
            with open(f'/sys/class/gpio/gpio{self.led_pin}/value', 'w') as writer:
                writer.writelines('1')
        except Exception as e:
            print(f"Error clearing LED: {e}")

    def set_blink_period(self, value):
        """Set the blink period"""
        self.blink_period = value

    def run(self):
        """Override the run method of threading.Thread"""
        while True:
            if self.flag_blink:
                self.setLED()
                time.sleep(self.blink_period)
                self.clearLED()
                time.sleep(self.blink_period)
            else:
                self.setLED()  # Keep the LED on if blinking is disabled
                time.sleep(1)

    def enable_blink(self):
        """Enable blinking of the LED"""
        self.flag_blink = True

    def disable_blink(self):
        """Disable blinking and keep the LED on"""
        self.flag_blink = False

    def callbackfunction_start(self):
        """Start the blinking process"""
        print("ledsys start")
        self.clearLED()
        self.disable_blink()
        self.set_blink_period(1)
        self.enable_blink()
        if not self._thread_started:
          self._thread_started = True
          self.start()  # Start the thread

    def callbackfunction_stop(self):
        """Stop the blinking process"""
        print("ledsys stop")
        self.disable_blink()
        # The run method will stop blinking but will keep the LED on
