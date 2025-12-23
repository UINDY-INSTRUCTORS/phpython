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
# Example 6: Interrupt handler (MicroPython only, P7_Analog_to_Digital)
# ============================================================================

def example_interrupt_handler():
    """
    Example of interrupt handling on MicroPython.

    NOTE: This example only works on MicroPython, not CircuitPython.
    When you need interrupts, you'll re-flash with MicroPython and use
    the machine API directly (this is platform-specific).
    """
    from machine import Pin
    import time

    count = 0

    def handle_interrupt(pin):
        global count
        count += 1
        led.value(not led.value())

    led = Pin(15, Pin.OUT)  # Onboard LED
    pir = Pin(21, Pin.IN)   # Motion sensor

    pir.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt)

    while True:
        print(f"Interrupts: {count}")
        time.sleep(1)


if __name__ == '__main__':
    # Uncomment an example to test it
    # example_adc_dac()
    # example_digital_io()
    # example_pwm_servo()
    # example_input_polling()
    # example_sensor_logging()
    pass
