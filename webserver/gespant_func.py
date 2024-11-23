import threading
import time
import os

class GPIOControl(threading.Thread):
    def __init__(self):
        super().__init__()

        # GPIO setup for both input and output pins
        self.runswitch_pin = 520  # GPIO pin for input (RunSwitch)
        self.ledsys_pin = 537  # GPIO pin for LED (LedSys)

        self.state_plc = False
        self.callback_start_plc = False
        self.callback_stop_plc = False

        self.flag_blink = False
        self.blink_period = 1

        try:
            # Setup GPIO input runswitch_pin (pin 520)
            self._export_gpio(self.runswitch_pin)
            self._set_gpio_direction(self.runswitch_pin, 'in')
            # Setup GPIO output ledsys (pin 537)
            self._export_gpio(self.ledsys_pin)
            self._set_gpio_direction(self.ledsys_pin, 'out')
            self._setLED()
        except Exception as e:
            print(f"Error in GPIO setup: {e}")

    def setup(self, start_run, callback_start_plc, callback_stop_plc):
        self.state_plc = start_run
        self.callback_start_plc = callback_start_plc
        self.callback_stop_plc = callback_stop_plc
        
    def _export_gpio(self, pin):
        """Export the GPIO pin to make it available for use."""
        try:
            gpio_path = f'/sys/class/gpio/gpio{pin}'
            if not os.path.exists(gpio_path):
                with open('/sys/class/gpio/export', 'w') as f:
                    f.write(str(pin))
                print(f"GPIO pin {pin} exported successfully.")
            else:
                print(f"GPIO pin {pin} is already exported.")
        except Exception as e:
            print(f"Error exporting GPIO pin {pin}: {e}")

    def _set_gpio_direction(self, pin, direction):
        """Set the direction of the GPIO pin (input/output)."""
        try:
            with open(f'/sys/class/gpio/gpio{pin}/direction', 'w') as f:
                f.write(direction)
        except Exception as e:
            print(f"Error setting direction for GPIO pin {pin}: {e}")

    def _read_gpio(self, pin):
        """Read the value from the GPIO pin (HIGH/LOW)."""
        try:
            with open(f'/sys/class/gpio/gpio{pin}/value', 'r') as f:
                value = f.read().strip()
            return int(value)
        except Exception as e:
            return None

    def read_gpio(self):
        """Read the GPIO pin and call the appropriate callback."""
        input_value = self._read_gpio(self.runswitch_pin)
        if input_value is not None:
            if self.state_plc is not input_value:
                if input_value == 1:  # GPIO HIGH
                    print(f"GPIO {self.runswitch_pin} is HIGH")
                    self.callback_start_plc()
                else:  # GPIO LOW
                    print(f"GPIO {self.runswitch_pin} is LOW")
                    self.callback_stop_plc()
                self.state_plc = input_value

    def _setLED(self):
        """Set the LED to ON."""
        try:
            with open(f'/sys/class/gpio/gpio{self.ledsys_pin}/value', 'w') as writer:
                writer.writelines('0')
        except Exception as e:
            print(f"Error setting LED: {e}")

    def _clearLED(self):
        """Set the LED to OFF."""
        try:
            with open(f'/sys/class/gpio/gpio{self.ledsys_pin}/value', 'w') as writer:
                writer.writelines('1')
        except Exception as e:
            print(f"Error clearing LED: {e}")

    def _set_blink_period(self, value):
        """Set the blink period."""
        self.blink_period = value

    def _enable_blink(self):
        """Enable blinking of the LED."""
        self.flag_blink = True

    def _disable_blink(self):
        """Disable blinking and keep the LED on."""
        self.flag_blink = False

    def start_ledsys(self):
        """Start the blinking process."""
        self._clearLED()
        self._disable_blink()
        self._set_blink_period(1)
        self._enable_blink()

    def stop_ledsys(self):
        """Stop the blinking process."""
        self._disable_blink()

    def run(self, interval=1):
        """Continuously check the GPIO pin value and handle LED blinking concurrently."""
        try:
            while True:
                # Read the GPIO pin and handle the callbacks
                self.read_gpio()

                # Manage LED blinking
                if self.flag_blink:
                    self._setLED()
                    time.sleep(self.blink_period)
                    self._clearLED()
                    time.sleep(self.blink_period)
                else:
                    self._setLED()  # Keep the LED on if blinking is disabled
                    time.sleep(interval)

        except KeyboardInterrupt:
            print("Program interrupted.")
        finally:
            # Clean up and unexport GPIO pins
            self._unexport_gpio(self.runswitch_pin)
            self._unexport_gpio(self.ledsys_pin)

    def _unexport_gpio(self, pin):
        """Unexport the GPIO pin when done."""
        try:
            with open('/sys/class/gpio/unexport', 'w') as f:
                f.write(str(pin))
        except Exception as e:
            print(f"Error unexporting GPIO pin {pin}: {e}")

Gespantgpio = GPIOControl()
    
# Main function
def run_thred_GespantGPIO(start_run, callback_start_plc, callback_stop_plc):
    Gespantgpio.setup(start_run, callback_start_plc, callback_stop_plc)
    Gespantgpio.start()  # Start the thread, this will call `run()` automatically

def start_GespantLedsys():
    Gespantgpio.start_ledsys()

def stop_GespantLedsys():
    Gespantgpio.stop_ledsys()