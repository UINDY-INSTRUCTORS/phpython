"""
Core hardware abstraction classes: A (Analog), D (Digital), P (PWM)

These provide a minimal, unified API across CircuitPython and MicroPython.
"""

from .platforms import PLATFORM, pin_number_to_pin, get_adc_max, get_ref_voltage

# Platform-specific imports
if PLATFORM == 'circuitpython':
    import board
    import analogio
    import digitalio
    import pwmio
elif PLATFORM == 'micropython':
    from machine import ADC, Pin, PWM
elif PLATFORM == 'mock':
    pass  # Mock implementations below


class A:
    """
    Analog input/output abstraction.

    Usage:
        adc = A(15)           # Analog input on pin 15
        dac = A(17, 'out')    # Analog output on pin 17

    DAC Writing (smart detection):
        dac.write(3.3)        # 3.3 volts (auto-detected as voltage)
        dac.write(1.5)        # 1.5 volts
        dac.write(0)          # 0 volts
        dac.write(65535)      # Raw value (auto-detected as raw)
        dac.write_voltage(2.5)  # Explicit voltage
        dac.write_raw(32768)  # Explicit raw value
    """

    def __init__(self, pin, mode='in'):
        """
        Initialize analog pin.

        Args:
            pin: Pin number (e.g., 15)
            mode: 'in' for input (default) or 'out' for output
        """
        self.pin_num = pin
        self.mode = mode
        self.adc_max = get_adc_max()
        self.ref_voltage = get_ref_voltage()
        self.vfactor = self.ref_voltage / self.adc_max

        if PLATFORM == 'circuitpython':
            pin_obj = pin_number_to_pin(pin)
            if mode == 'in':
                self._obj = analogio.AnalogIn(pin_obj)
            else:  # 'out'
                self._obj = analogio.AnalogOut(pin_obj)

        elif PLATFORM == 'micropython':
            if mode == 'in':
                self._obj = ADC(Pin(pin))
            else:
                raise NotImplementedError("MicroPython DAC not yet supported in phpython")

        elif PLATFORM == 'mock':
            self._value = 0

    def read(self):
        """Read raw ADC value (0 to adc_max)."""
        if PLATFORM == 'circuitpython':
            return self._obj.value
        elif PLATFORM == 'micropython':
            return self._obj.read()
        elif PLATFORM == 'mock':
            return self._value

    def read_voltage(self):
        """Read voltage (in volts)."""
        raw = self.read()
        return raw * self.vfactor

    def write(self, value):
        """
        Write value to DAC.

        Intelligently detects whether input is voltage or raw value:
        - Values 0 to ~3.3V are treated as voltage
        - Larger values are treated as raw ADC counts
        - For explicit control, use write_voltage() or write_raw()

        Args:
            value: Voltage (0-3.3V) or raw value (0-65535)
                   Auto-detects based on magnitude
        """
        if self.mode != 'out':
            raise ValueError("Can't write to input pin")

        # Smart detection: if value <= ref_voltage (typically 3.3V),
        # treat as voltage; otherwise treat as raw
        # Using 4.0 as threshold for safety margin
        if value <= 4.0:
            # Treat as voltage
            value = int(value / self.vfactor)
        # else: treat as raw, use value as-is

        if PLATFORM == 'circuitpython':
            self._obj.value = int(value)
        elif PLATFORM == 'mock':
            self._value = int(value)

    def write_voltage(self, voltage):
        """
        Write voltage to DAC (explicit).

        Args:
            voltage: Voltage in volts (0 to ref_voltage)
        """
        if self.mode != 'out':
            raise ValueError("Can't write to input pin")

        value = int(voltage / self.vfactor)

        if PLATFORM == 'circuitpython':
            self._obj.value = int(value)
        elif PLATFORM == 'mock':
            self._value = int(value)

    def write_raw(self, value):
        """
        Write raw ADC count to DAC (explicit).

        Args:
            value: Raw count (0 to adc_max, typically 0-65535)
        """
        if self.mode != 'out':
            raise ValueError("Can't write to input pin")

        if PLATFORM == 'circuitpython':
            self._obj.value = int(value)
        elif PLATFORM == 'mock':
            self._value = int(value)

    def deinit(self):
        """Clean up the pin (CircuitPython only)."""
        if PLATFORM == 'circuitpython' and hasattr(self._obj, 'deinit'):
            self._obj.deinit()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.deinit()


class D:
    """
    Digital input/output abstraction.

    Usage:
        led = D(21, 'out')  # Digital output on pin 21
        btn = D(22, 'in')   # Digital input on pin 22
    """

    def __init__(self, pin, mode='in'):
        """
        Initialize digital pin.

        Args:
            pin: Pin number (e.g., 21)
            mode: 'in' for input or 'out' for output
        """
        self.pin_num = pin
        self.mode = mode

        if PLATFORM == 'circuitpython':
            pin_obj = pin_number_to_pin(pin)
            self._obj = digitalio.DigitalInOut(pin_obj)
            if mode == 'out':
                self._obj.direction = digitalio.Direction.OUTPUT
            else:
                self._obj.direction = digitalio.Direction.INPUT

        elif PLATFORM == 'micropython':
            direction = Pin.OUT if mode == 'out' else Pin.IN
            self._obj = Pin(pin, direction)

        elif PLATFORM == 'mock':
            self._value = 0

    def set(self, value):
        """Set output to high (1) or low (0)."""
        if self.mode != 'out':
            raise ValueError("Can't write to input pin")

        if PLATFORM == 'circuitpython':
            self._obj.value = bool(value)
        elif PLATFORM == 'micropython':
            self._obj.value(1 if value else 0)
        elif PLATFORM == 'mock':
            self._value = bool(value)

    def get(self):
        """Read input value (True or False)."""
        if PLATFORM == 'circuitpython':
            return self._obj.value
        elif PLATFORM == 'micropython':
            return bool(self._obj.value())
        elif PLATFORM == 'mock':
            return bool(self._value)

    def toggle(self):
        """Toggle output."""
        self.set(not self.get())

    # Convenience: allow direct assignment
    @property
    def value(self):
        return self.get()

    @value.setter
    def value(self, v):
        self.set(v)

    def deinit(self):
        """Clean up the pin (CircuitPython only)."""
        if PLATFORM == 'circuitpython' and hasattr(self._obj, 'deinit'):
            self._obj.deinit()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.deinit()


class P:
    """
    PWM (Pulse Width Modulation) abstraction.

    Usage:
        servo = P(21, freq=50)      # 50 Hz PWM on pin 21
        servo.duty(1.5)             # 1.5 ms pulse
    """

    def __init__(self, pin, freq=1000, duty_percent=0):
        """
        Initialize PWM pin.

        Args:
            pin: Pin number (e.g., 21)
            freq: Frequency in Hz (default 1000)
            duty_percent: Initial duty cycle as percentage (0-100)
        """
        self.pin_num = pin
        self.frequency = freq
        self._duty_percent = duty_percent

        if PLATFORM == 'circuitpython':
            pin_obj = pin_number_to_pin(pin)
            full_duty = 2**16 - 1
            duty_cycle = int(full_duty * duty_percent / 100)
            self._obj = pwmio.PWMOut(pin_obj, frequency=freq, duty_cycle=duty_cycle)
            self._full_duty = full_duty

        elif PLATFORM == 'micropython':
            from machine import Pin
            self._obj = PWM(Pin(pin))
            self._obj.freq(freq)
            self._obj.duty(int(1023 * duty_percent / 100))

        elif PLATFORM == 'mock':
            self._duty_percent = duty_percent

    def duty(self, value=None):
        """
        Set or get duty cycle.

        Args:
            value: Percentage (0-100) or None to get current value

        Returns:
            Current duty cycle if value is None
        """
        if value is None:
            return self._duty_percent

        self._duty_percent = value

        if PLATFORM == 'circuitpython':
            self._obj.duty_cycle = int(self._full_duty * value / 100)
        elif PLATFORM == 'micropython':
            self._obj.duty(int(1023 * value / 100))
        elif PLATFORM == 'mock':
            pass

    def pulse_ms(self, ms, period_ms=20):
        """
        Set pulse width in milliseconds (useful for servos).

        Args:
            ms: Pulse width in milliseconds
            period_ms: Period in milliseconds (default 20 for 50Hz)
        """
        duty = (ms / period_ms) * 100
        self.duty(duty)

    def deinit(self):
        """Clean up the PWM (CircuitPython only)."""
        if PLATFORM == 'circuitpython' and hasattr(self._obj, 'deinit'):
            self._obj.deinit()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.deinit()


def set_mode(platform):
    """
    Override platform detection (mainly for testing).

    Args:
        platform: 'circuitpython', 'micropython', or 'mock'
    """
    global PLATFORM
    PLATFORM = platform
