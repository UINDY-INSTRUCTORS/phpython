"""
PWM output on pin 15 at 50 Hz, sweeping duty cycle from 5% to 10% in 0.1% steps.
"""

from phpython import P
import time

pwm = P(15, freq=50, duty_percent=5)

print("PWM started on pin 15")
print("Frequency: 50 Hz")
print("Sweeping duty cycle 5% -> 10% in 0.1% steps, 1s per step")

duty = 5.0

try:
    while True:
        pwm.duty(duty)
        print(f"Duty cycle: {duty:.1f}%")
        time.sleep(1)

        duty += 0.1
        if duty > 10.0:
            duty = 5.0

except KeyboardInterrupt:
    print("\nStopping PWM")
    pwm.deinit()
