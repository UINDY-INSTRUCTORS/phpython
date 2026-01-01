"""
P1: Measuring the Time Constant of an RC Circuit
Decay Code - RC Time Constant Measurement

This program measures the voltage decay across a discharging capacitor
to determine the RC time constant, using the phpython abstraction layer
for cross-platform compatibility.

Circuit:
- Digital output (pin 17) charges the capacitor when HIGH
- ADC inputs (pins 13, 15, 10) measure voltages during decay
"""

from phpython import A, D, DataLogger, countdown, Timer
import time

def main():
    """Measure RC circuit decay and infer time constant."""

    # Create analog I/O objects for measurement
    adc1 = A(13)        # Analog input: voltage measurement 1
    adc2 = A(15)        # Analog input: voltage measurement 2
    adc3 = A(10)        # Analog input: voltage measurement 3 (capacitor voltage)

    # Create digital output for capacitor charging
    dout = D(17, 'out')  # Digital output: charge capacitor when HIGH

    print("Starting RC time constant measurement...")
    print("-" * 60)

    # Set digital output HIGH to charge capacitor
    dout.set(1)

    # Let capacitor fully charge before starting
    countdown(3, "Charging capacitor")

    # Collect data during discharge
    data = []
    timer = Timer()

    print("Discharging and collecting data...")

    # Switch to discharge mode
    dout.set(0)

    print(f"{'Step':>4} | {'V1 (V)':>8} | {'V2 (V)':>8} | {'V3 (V)':>8} | {'Time (ms)':>10}")
    
    # Rapidly sample voltages during decay
    for i in range(0, 256, 2):
        time.sleep(0.001)  # 1ms between samples

        # Collect raw values first
        v1_raw = adc1.read()
        v2_raw = adc2.read()
        v3_raw = adc3.read()
        elapsed_ns = timer.elapsed() * 1e9

        # Store data
        data.append((i, v1_raw, v2_raw, v3_raw, elapsed_ns))

        # Convert to voltage for display
        v1 = adc1.read_voltage()
        v2 = adc2.read_voltage()
        v3 = adc3.read_voltage()
        elapsed_ms = timer.elapsed() * 1000

    # Log data to CSV
    with DataLogger('decay.csv', ['j', 'v1', 'v2', 'v3', 'time']) as log:
        for j, v1_raw, v2_raw, v3_raw, t_ns in data:
            v1 = v1_raw * adc1.vfactor
            v2 = v2_raw * adc2.vfactor
            v3 = v3_raw * adc3.vfactor
            t_s = t_ns / 1e9
            print(f"{j:4d} | {v1:8.3f} | {v2:8.3f} | {v3:8.3f} | {t_s*1000:10.1f}")
            log.log(j, v1, v2, v3, t_s)

    print("-" * 60)
    print("Data collection complete!")
    print("Data saved to: decay.csv")

if __name__ == "__main__":
    main()
