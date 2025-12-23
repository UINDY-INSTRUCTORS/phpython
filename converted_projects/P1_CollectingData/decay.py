"""
P1_CollectingData - Decay (Converted to phpython)

Original: decay.py
Converted to use phpython for cross-platform compatibility (CircuitPython/MicroPython)

This program measures capacitor discharge by:
1. Charging a capacitor (set digital output high)
2. Discharging through a resistor (set digital output low)
3. Recording analog voltages during discharge
"""

from phpython import A, D, DataLogger, Timer
import time

# Create analog input objects
adc1 = A(13)  # Analog input on pin 13
adc2 = A(15)  # Analog input on pin 15
adc3 = A(10)  # Analog input on pin 10

# Create digital output for charging/discharging control
dout = D(17, 'out')  # Digital output on pin 17

# Let capacitor fully charge before discharging
print("Sleeping.... let C fully charge")
for i in range(3, 0, -1):
    print(i)
    time.sleep(1)
print("0 --- go!")

# Set digital output high to charge
dout.set(1)
time.sleep(1)

# Prepare to collect discharge data
t0 = time.monotonic_ns()
dout.set(0)  # Start discharge

data = []

# Collect data quickly during discharge
for i in range(0, 0xff, 0x2):
    time.sleep(0.001)
    elapsed = (time.monotonic_ns() - t0) / 1e9
    data.append((
        i,
        adc1.read_voltage(),
        adc2.read_voltage(),
        adc3.read_voltage(),
        elapsed
    ))

# Log all collected data to CSV
with DataLogger('decay.csv', ['j', 'v1', 'v2', 'v3', 'time']) as log:
    for j, v1, v2, v3, t in data:
        log.log(j, v1, v2, v3, t)
        print(f"{j},{v1:.3f},{v2:.3f},{v3:.3f},{t:.3f}")

print("Done!")
