"""
Example: Voltage Divider Data Collection
Using phpython abstraction layer for cross-platform compatibility

This reproduces the functionality of starter_micro.py using only phpython features.
"""

from phpython import A, Timer, DataLogger
import time

# --- CONFIGURATION ---
V_DAC_MAX = 3.3
vfactor_dac = V_DAC_MAX / 255

# Initialize hardware using phpython
dac = A(17, 'out')  # DAC on pin 17
adc1 = A(15)        # ADC on pin 15
adc2 = A(10)        # ADC on pin 10

def read_avg_voltage(adc_pin, samples=16):
    """
    Read averaged voltage from ADC pin.

    Args:
        adc_pin: phpython A object (analog input)
        samples: Number of samples to average (default 16)

    Returns:
        Average voltage in volts
    """
    total = 0
    for _ in range(samples):
        total += adc_pin.read_voltage()
    return total / samples

# --- EXECUTION ---
with DataLogger('starter.csv', ['j', 'v_target', 'v1_measured', 'v2_measured', 'time']) as log:
    dac.write(0)
    print("Discharging...")
    time.sleep(2)

    timer = Timer()

    for i in range(0, 100, 5):
        time.sleep(0.4)
        t_sec = timer.elapsed()

        # Write DAC value (0-255)
        dac.write(i * vfactor_dac)  # Convert to voltage

        # Calculate target voltage
        v_target = i * vfactor_dac

        # Read voltages (with averaging)
        v1 = read_avg_voltage(adc1)
        v2 = read_avg_voltage(adc2)

        # Log data
        log.log(i, v_target, v1, v2, t_sec)
        print(f"{i},{v_target:.3f},{v1:.3f},{v2:.3f},{t_sec:.3f}")

    # Reset DAC
    dac.write(0)

print("Done.")
