"""
Example: Voltage Divider Data Collection
Using phpython abstraction layer for cross-platform compatibility

This reproduces the functionality of starter_micro.py using only phpython features.
"""

from phpython import A
import time

# --- CONFIGURATION ---
V_DAC_MAX = 3.3
deltaVdac = V_DAC_MAX / 255

# Initialize hardware using phpython
dac = A(17, 'out')  # DAC on pin 17
adc1 = A(15)        # ADC on pin 15
adc2 = A(10)        # ADC on pin 10
dac.write(0)
print("Discharging...")
time.sleep(3)
print(f"i,v_target,v1_measured,v2_measured")
for i in range(0, 100, 5):
    time.sleep(0.4)

    # Calculate target voltage
    v_target = i * deltaVdac

    # Write DAC value
    dac.write(v_target)  

    # Read voltages (with averaging)
    v1 = adc1.read_voltage()
    v2 = adc2.read_voltage()

    # Log data
    print(f"{i},{v_target:.3f},{v1:.3f},{v2:.3f}")

# Reset DAC
dac.write(0)

print("Done.")
