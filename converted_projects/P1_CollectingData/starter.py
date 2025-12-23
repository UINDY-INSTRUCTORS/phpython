"""
P1_CollectingData - Starter (Converted to phpython)

Original: starter.py
Converted to use phpython for cross-platform compatibility (CircuitPython/MicroPython)

This program charges a capacitor by increasing DAC voltage in steps,
reading the resulting voltages from analog inputs while measuring time.
"""

from phpython import A, DataLogger, countdown
import time

# Create analog I/O objects
adc1 = A(15)        # Analog input on pin 15
adc2 = A(10)        # Analog input on pin 10
dac = A(17, 'out')  # Analog output (DAC) on pin 17

# Let capacitor fully discharge before starting
countdown(3, "Sleeping.... let C fully discharge")

# Log data to CSV
with DataLogger('starter.csv', ['j', 'vdac', 'v1', 'v2', 'time']) as log:
    # Set initial DAC output to zero
    dac.write(0)

    t0 = time.monotonic_ns()

    # Step through DAC values from 0 to 255 (in steps of 5 to save time)
    for i in range(0, 255, 5):
        time.sleep(0.4)  # Let the capacitor charge

        elapsed = (time.monotonic_ns() - t0) / 1e9

        # Calculate DAC output voltage (0 to 3.3V)
        vout = (i / 255) * 3.3

        # Write to DAC (in volts)
        dac.write(vout)

        # Read analog inputs
        v1 = adc1.read_voltage()
        v2 = adc2.read_voltage()

        # Log data
        log.log(i, vout, v1, v2, elapsed)
        print(f"{i},{vout:.3f},{v1:.3f},{v2:.3f},{elapsed:.3f}")

# Reset DAC
dac.write(0)

print("Done!")
