"""
Examples showing how to use phpython across different project types.

These examples are based on the actual student projects from PH230.
"""

# ============================================================================
# Example 1: ADC/DAC (from P1_CollectingData)
# ============================================================================

def example_adc_dac():
    """Read from ADC and write to DAC."""
    from phpython import A, DataLogger, countdown
    import time

    # Create analog I/O objects
    adc1 = A(15)        # Analog input on pin 15
    adc2 = A(10)        # Analog input on pin 10
    dac = A(17, 'out')  # Analog output on pin 17

    # Let capacitor discharge
    countdown(3, "Discharging capacitor")

    # Log data while charging
    with DataLogger('charge_curve.csv', ['time_s', 'vdac', 'v1', 'v2']) as log:
        t0 = time.monotonic_ns()

        # Step DAC voltage from 0V to 3.3V
        for step in range(0, 256, 5):
            elapsed = (time.monotonic_ns() - t0) / 1e9

            # Set DAC voltage (smart API: 0-3.3 is voltage, >4 is raw)
            vdac = (step / 255) * 3.3
            dac.write(vdac)

            v1 = adc1.read_voltage()
            v2 = adc2.read_voltage()

            log.log(elapsed, vdac, v1, v2)

            if v1 > 3.0:  # Stop when charged
                break

            time.sleep(0.1)


# ============================================================================
# Example 2: Digital I/O with LED (from P2_LED)
# ============================================================================

def example_digital_io():
    """Blink an LED using digital output."""
    from phpython import D
    import time

    led = D(21, 'out')

    for i in range(10):
        led.set(1)  # High
        time.sleep(0.5)
        led.set(0)  # Low
        time.sleep(0.5)

    led.deinit()


# ============================================================================
# Example 3: PWM for servo control (from P8_Motors)
# ============================================================================

def example_pwm_servo():
    """Control a servo with PWM."""
    from phpython import P
    import time

    servo = P(21, freq=50)  # 50 Hz for standard servo

    # Sweep servo from min to max
    for angle_ms in range(10, 20):  # 1.0 to 2.0 ms pulse width
        servo.pulse_ms(angle_ms / 10.0, period_ms=20)
        time.sleep(0.1)

    servo.deinit()


# ============================================================================
# Example 4: Input reading with callback (simple version, not interrupt)
# ============================================================================

def example_input_polling():
    """Read a button input using polling."""
    from phpython import D
    import time

    button = D(22, 'in')
    led = D(21, 'out')

    while True:
        if button.get():  # Button pressed
            led.set(1)
        else:
            led.set(0)

        time.sleep(0.01)


# ============================================================================
# Example 5: Multiple sensors with timed logging (from P7_Analog_to_Digital)
# ============================================================================

def example_sensor_logging():
    """Log data from temperature sensor."""
    from phpython import A, DataLogger, Timer
    import time

    # LM335 temperature sensor connected to ADC
    temp_sensor = A(36)  # Analog input pin

    # Calibration: LM335 outputs 10mV per Kelvin
    # At 25°C, output is ~2.98V
    def celsius_from_voltage(v):
        return (v / 0.01) - 273.15

    with DataLogger('temperature.csv', ['time_s', 'voltage', 'celsius']) as log:
        timer = Timer()

        for _ in range(60):  # Log for 60 seconds
            v = temp_sensor.read_voltage()
            c = celsius_from_voltage(v)
            elapsed = timer.elapsed()

            log.log(elapsed, v, c)
            print(f"{elapsed:.2f}s: {c:.2f}°C")

            time.sleep(1)


# ============================================================================
# Example 6: Interrupt handler with phpython (MicroPython only)
# ============================================================================

def example_interrupt_handler():
    """
    Example of interrupt handling on MicroPython using phpython API.

    NOTE: This example only works on MicroPython, not CircuitPython.
    CircuitPython will raise NotImplementedError.
    """
    from phpython import D
    import time

    count = 0

    def handle_interrupt(pin):
        global count
        count += 1
        led.toggle()

    # Create digital I/O objects
    led = D(15, 'out')      # Onboard LED
    pir = D(21, 'in')       # Motion sensor

    # Attach interrupt handler
    pir.attach_irq(handle_interrupt, trigger='rising')

    # Main loop - interrupt will fire independently
    while True:
        print(f"Interrupts detected: {count}")
        time.sleep(1)


# ============================================================================
# Example 6b: Interrupt with multiple triggers (MicroPython only)
# ============================================================================

def example_interrupt_both_edges():
    """
    Example of interrupt handling on both rising and falling edges.
    """
    from phpython import D
    import time

    edge_count = 0

    def handle_edge(pin):
        global edge_count
        edge_count += 1

    button = D(22, 'in')

    # Detect both press and release
    button.attach_irq(handle_edge, trigger='both')

    while True:
        print(f"Button edges detected: {edge_count}")
        time.sleep(1)


# ============================================================================
# Example 7: I2C Bus - Scanning for devices
# ============================================================================

def example_i2c_scan():
    """
    Scan I2C bus for connected devices.

    Works on CircuitPython or MicroPython.
    """
    from phpython import I2C

    # Create I2C bus on standard pins
    i2c = I2C(scl=6, sda=8)

    # Scan for devices
    devices = i2c.scan()

    if devices:
        print(f"Found {len(devices)} I2C device(s):")
        for addr in devices:
            print(f"  Address: 0x{addr:02x} ({addr})")
    else:
        print("No I2C devices found")

    i2c.deinit()


# ============================================================================
# Example 8: I2C with Temperature Sensor (MCP9808)
# ============================================================================

def example_i2c_temperature():
    """
    Example of reading temperature from MCP9808 sensor via I2C.

    Requires: adafruit_mcp9808 library installed

    This example shows how to use phpython's I2C abstraction with
    standard Adafruit sensor libraries.
    """
    from phpython import I2C, DataLogger, Timer
    import time

    try:
        import adafruit_mcp9808
    except ImportError:
        print("Requires: pip install adafruit-circuitpython-mcp9808")
        return

    # Create I2C bus
    i2c = I2C(scl=6, sda=8, frequency=400000)

    # Create sensor object
    mcp = adafruit_mcp9808.MCP9808(i2c)

    # Log temperature readings
    with DataLogger('temperature.csv', ['time', 'celsius', 'fahrenheit']) as log:
        timer = Timer()

        for _ in range(60):  # Log for 60 seconds
            temp_c = mcp.temperature
            temp_f = temp_c * 9 / 5 + 32

            elapsed = timer.elapsed()
            log.log(elapsed, temp_c, temp_f)

            print(f"{elapsed:.2f}s: {temp_c:.2f}°C / {temp_f:.2f}°F")

            if elapsed >= 10:  # Just 10 seconds for demo
                break

            time.sleep(1)

    i2c.deinit()


# ============================================================================
# Example 9: I2C with Accelerometer (MMA8451)
# ============================================================================

def example_i2c_accelerometer():
    """
    Example of reading acceleration from MMA8451 sensor via I2C.

    Requires: adafruit_mma8451 library installed

    This example shows how to use phpython's I2C abstraction with
    a 3-axis accelerometer.
    """
    from phpython import I2C, DataLogger, Timer
    import time

    try:
        import adafruit_mma8451
    except ImportError:
        print("Requires: pip install adafruit-circuitpython-mma8451")
        return

    # Create I2C bus
    i2c = I2C(scl=6, sda=8)

    # Create sensor object
    sensor = adafruit_mma8451.MMA8451(i2c)

    # Log acceleration data
    with DataLogger('accelerometer.csv', ['time', 'x', 'y', 'z']) as log:
        timer = Timer()

        for _ in range(20):
            x, y, z = sensor.acceleration
            elapsed = timer.elapsed()

            log.log(elapsed, x, y, z)
            print(f"{elapsed:.2f}s: X={x:.3f} Y={y:.3f} Z={z:.3f}")

            time.sleep(0.2)

    i2c.deinit()


if __name__ == '__main__':
    # Uncomment an example to test it
    # example_adc_dac()
    # example_digital_io()
    # example_pwm_servo()
    # example_input_polling()
    # example_sensor_logging()
    pass
