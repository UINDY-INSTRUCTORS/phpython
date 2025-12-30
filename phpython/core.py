"""
Core hardware abstraction classes: A (Analog), D (Digital), P (PWM), I2C

These provide a minimal, unified API across CircuitPython and MicroPython.
"""

from .platforms import PLATFORM, pin_number_to_pin, get_adc_max, get_ref_voltage

# Platform-specific imports
if PLATFORM == 'circuitpython':
    import board
    import analogio
    import digitalio
    import pwmio
    import busio
elif PLATFORM == 'micropython':
    from machine import ADC, Pin, PWM, I2C as MachineI2C
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
                # Set 11dB attenuation for full 0-3.3V range
                self._obj.atten(ADC.ATTN_11DB)
            else:  # 'out'
                from machine import DAC
                self._obj = DAC(Pin(pin))

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
        if PLATFORM == 'micropython':
            # Use read_uv() for calibrated microvolts, convert to volts
            return self._obj.read_uv() / 1_000_000
        else:
            # CircuitPython and mock use scaling factor
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
            value: Voltage (0-3.3V) or raw value (0-255 for MicroPython, 0-65535 for CircuitPython)
                   Auto-detects based on magnitude
        """
        if self.mode != 'out':
            raise ValueError("Can't write to input pin")

        # Smart detection: if value <= ref_voltage (typically 3.3V),
        # treat as voltage; otherwise treat as raw
        # Using 4.0 as threshold for safety margin
        if value <= 4.0:
            # Treat as voltage - convert to platform-specific DAC value
            if PLATFORM == 'micropython':
                # MicroPython DAC is 8-bit (0-255)
                dac_value = int(value / self.ref_voltage * 255)
                self._obj.write(dac_value)
            elif PLATFORM == 'circuitpython':
                # CircuitPython DAC is 16-bit (0-65535)
                self._obj.value = int(value / self.vfactor)
            elif PLATFORM == 'mock':
                self._value = int(value / self.vfactor)
        else:
            # Treat as raw value
            if PLATFORM == 'circuitpython':
                self._obj.value = int(value)
            elif PLATFORM == 'micropython':
                # For raw values, assume 16-bit input, scale to 8-bit
                dac_value = int(value) >> 8
                self._obj.write(dac_value)
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

        if PLATFORM == 'circuitpython':
            value = int(voltage / self.vfactor)
            self._obj.value = value
        elif PLATFORM == 'micropython':
            # MicroPython DAC uses 8-bit resolution (0-255)
            dac_value = int(voltage / self.ref_voltage * 255)
            self._obj.write(dac_value)
        elif PLATFORM == 'mock':
            value = int(voltage / self.vfactor)
            self._value = value

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
        elif PLATFORM == 'micropython':
            # MicroPython DAC uses 8-bit resolution (0-255)
            # Convert from 16-bit normalized value to 8-bit
            dac_value = int(value) >> 8  # Divide by 256
            self._obj.write(dac_value)
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

    Interrupt Handling (MicroPython only):
        def on_press(pin):
            print("Button pressed!")

        button = D(22, 'in')
        button.attach_irq(on_press, trigger='rising')
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

    def attach_irq(self, handler, trigger='rising'):
        """
        Attach interrupt handler to digital input pin.

        Only works on MicroPython. CircuitPython will raise NotImplementedError.

        Args:
            handler: Callback function that takes pin as argument
                    def handler(pin):
                        # Pin triggered
                        pass
            trigger: 'rising', 'falling', or 'both'

        Returns:
            IRQ object (MicroPython) or None (other platforms)

        Raises:
            NotImplementedError: If running on CircuitPython
            ValueError: If invalid trigger value or output pin
            RuntimeError: If running in mock mode

        Example:
            def on_motion(pin):
                print("Motion detected!")

            sensor = D(21, 'in')
            sensor.attach_irq(on_motion, trigger='rising')
        """
        if self.mode != 'in':
            raise ValueError("Can't attach interrupt to output pin")

        # Validate trigger parameter first (platform-independent)
        trigger_map = {
            'rising': 1,  # Pin.IRQ_RISING value
            'falling': 2,  # Pin.IRQ_FALLING value
            'both': 3,  # Pin.IRQ_RISING | Pin.IRQ_FALLING
        }
        if trigger not in trigger_map:
            raise ValueError(
                "Invalid trigger: '{}'. "
                "Use 'rising', 'falling', or 'both'.".format(trigger)
            )

        if PLATFORM == 'circuitpython':
            raise NotImplementedError(
                "Hardware interrupts are not supported on CircuitPython. "
                "To use interrupts, flash your board with MicroPython instead. "
                "See MIGRATION.md for examples."
            )
        elif PLATFORM == 'micropython':
            # Map trigger string to machine.Pin constants
            actual_trigger_map = {
                'rising': Pin.IRQ_RISING,
                'falling': Pin.IRQ_FALLING,
                'both': Pin.IRQ_RISING | Pin.IRQ_FALLING,
            }
            # Attach interrupt to the underlying Pin object
            irq = self._obj.irq(trigger=actual_trigger_map[trigger], handler=handler)
            return irq
        elif PLATFORM == 'mock':
            raise RuntimeError(
                "Interrupts not supported in mock mode. "
                "Use set_mode('micropython') or flash actual hardware."
            )

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


class I2C:
    """
    I2C Bus abstraction for CircuitPython and MicroPython.

    Works with Adafruit sensor libraries on both platforms without modification.

    Usage:
        i2c = I2C(scl=6, sda=8)  # Pins for I2C bus
        mcp = adafruit_mcp9808.MCP9808(i2c)  # Pass to Adafruit drivers

    Parameters:
        scl: SCL (clock) pin number
        sda: SDA (data) pin number
        frequency: I2C frequency in Hz (default 400000 = 400 kHz)
        timeout: Timeout in microseconds (MicroPython only, default None)
    """

    def __init__(self, scl, sda, frequency=400000, timeout=None):
        """
        Initialize I2C bus.

        Args:
            scl: SCL pin number (e.g., 6)
            sda: SDA pin number (e.g., 8)
            frequency: Bus frequency in Hz (default 400000)
            timeout: Timeout in microseconds (MicroPython only)
        """
        self.scl_pin = scl
        self.sda_pin = sda
        self.frequency = frequency
        self.timeout = timeout

        if PLATFORM == 'circuitpython':
            scl_obj = pin_number_to_pin(scl)
            sda_obj = pin_number_to_pin(sda)
            self._bus = busio.I2C(scl=scl_obj, sda=sda_obj, frequency=frequency)

        elif PLATFORM == 'micropython':
            # MicroPython I2C uses pin numbers directly
            self._bus = MachineI2C(
                id=0,
                scl=Pin(scl),
                sda=Pin(sda),
                freq=frequency,
                timeout=timeout if timeout else 2000,
            )

        elif PLATFORM == 'mock':
            self._bus = None

    def scan(self):
        """
        Scan I2C bus for connected devices.

        Returns:
            List of addresses (in decimal) of devices found on the bus
        """
        if PLATFORM == 'circuitpython':
            return self._bus.scan()
        elif PLATFORM == 'micropython':
            return self._bus.scan()
        elif PLATFORM == 'mock':
            return []

    def readfrom_mem(self, addr, memaddr, nbytes, *, addrsize=8):
        """
        Read from I2C device memory (advanced use).

        Args:
            addr: I2C device address
            memaddr: Memory address to read from
            nbytes: Number of bytes to read
            addrsize: Address size in bits (default 8)

        Returns:
            Bytes read from device
        """
        if PLATFORM == 'circuitpython':
            return self._bus.readfrom_mem(addr, memaddr, nbytes, addrsize=addrsize)
        elif PLATFORM == 'micropython':
            return self._bus.readfrom_mem(addr, memaddr, nbytes)
        elif PLATFORM == 'mock':
            return bytes([0] * nbytes)

    def writeto_mem(self, addr, memaddr, buf, *, addrsize=8):
        """
        Write to I2C device memory (advanced use).

        Args:
            addr: I2C device address
            memaddr: Memory address to write to
            buf: Bytes to write
            addrsize: Address size in bits (default 8)
        """
        if PLATFORM == 'circuitpython':
            return self._bus.writeto_mem(addr, memaddr, buf, addrsize=addrsize)
        elif PLATFORM == 'micropython':
            return self._bus.writeto_mem(addr, memaddr, buf)
        elif PLATFORM == 'mock':
            pass

    def readfrom(self, addr, nbytes, *, start=0, end=None):
        """
        Read from I2C device (advanced use).

        Args:
            addr: I2C device address
            nbytes: Number of bytes to read
            start: Start of slice (CircuitPython only)
            end: End of slice (CircuitPython only)

        Returns:
            Bytes read from device
        """
        if PLATFORM == 'circuitpython':
            return self._bus.readfrom(addr, nbytes, start=start, end=end)
        elif PLATFORM == 'micropython':
            return self._bus.readfrom(addr, nbytes)
        elif PLATFORM == 'mock':
            return bytes([0] * nbytes)

    def writeto(self, addr, buf, *, start=0, end=None, stop=True):
        """
        Write to I2C device (advanced use).

        Args:
            addr: I2C device address
            buf: Bytes to write
            start: Start of slice (CircuitPython only)
            end: End of slice (CircuitPython only)
            stop: Send stop condition (CircuitPython only)

        Returns:
            Number of bytes written
        """
        if PLATFORM == 'circuitpython':
            return self._bus.writeto(addr, buf, start=start, end=end, stop=stop)
        elif PLATFORM == 'micropython':
            return self._bus.writeto(addr, buf)
        elif PLATFORM == 'mock':
            return len(buf)

    def deinit(self):
        """Clean up I2C bus."""
        if PLATFORM == 'circuitpython' and hasattr(self._bus, 'deinit'):
            self._bus.deinit()
        elif PLATFORM == 'micropython' and hasattr(self._bus, 'deinit'):
            self._bus.deinit()

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
