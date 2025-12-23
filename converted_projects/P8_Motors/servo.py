"""
P8_Motors - Servo Control (Converted to phpython)

Original: servo.py
Converted to use phpython for cross-platform compatibility (CircuitPython/MicroPython)

This program controls a servo motor by sweeping through different pulse widths:
- Min: 1.0 ms (0 degrees)
- Mid: 1.5 ms (90 degrees)
- Max: 2.0 ms (180 degrees)
"""

from phpython import P
import time

# Create PWM object for servo control on pin 21
# Standard servo uses 50 Hz frequency
servo = P(21, freq=50)

# Servo pulse width parameters (in milliseconds)
tmin_ms = 1.0   # Minimum pulse width (0 degrees)
tmid_ms = 1.5   # Middle pulse width (90 degrees)
tmax_ms = 2.0   # Maximum pulse width (180 degrees)

# Print servo parameters
print("Servo Control Program")
print(f"PWM frequency: 50 Hz")
print(f"PWM period: 20 ms")
print(f"Min pulse width: {tmin_ms} ms")
print(f"Mid pulse width: {tmid_ms} ms")
print(f"Max pulse width: {tmax_ms} ms")
print()

try:
    while True:
        # Move to minimum position (0 degrees)
        print(f"Servo at 0 degrees ({tmin_ms} ms)")
        servo.pulse_ms(tmin_ms)
        time.sleep(2)

        # Move to middle position (90 degrees)
        print(f"Servo at 90 degrees ({tmid_ms} ms)")
        servo.pulse_ms(tmid_ms)
        time.sleep(2)

        # Move to maximum position (180 degrees)
        print(f"Servo at 180 degrees ({tmax_ms} ms)")
        servo.pulse_ms(tmax_ms)
        time.sleep(2)

except KeyboardInterrupt:
    print("\nKeyboard interrupt - stopping servo")
    servo.deinit()

print("Done!")
