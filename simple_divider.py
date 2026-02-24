"""
BJT measurement
"""

from phpython import A, D, countdown, Timer
import time
V_DAC_MAX = 3.3             # max DAC output voltage
deltaVdac = V_DAC_MAX / 255 # size of voltage step


def main():
    """Measure BJT characteristics."""

    # Create analog I/O objects for measurement
    adc1 = A(10)        # Analog input: voltage measurement 3 (capacitor voltage)
    adc2 = A(15)
    adc3 = A(13)
    
    dac = A(17,'out')        # dac output

    # Create digital output for capacitor charging
    dout = D(1, 'out')  # Digital output: charge capacitor when HIGH

    dout.set(1)

    # Let capacitor fully charge before starting
    # Collect data during discharge
    data = []

    print(f"i,vdac,v1,v2,v3")


    # Rapidly sample voltages during decay
    for i in range(0, 256, 2):
        time.sleep(0.001)  # 1ms between samples

        # Collect voltages
        v_target = i * deltaVdac

        # Write DAC value
        dac.write(v_target)  

        # Read voltages (with averaging)
        v1 = adc1.read_voltage()
        v2 = adc2.read_voltage()
        v3 = adc3.read_voltage()

        # Log data
        print(f"{i},{v_target:.3f},{v1:.3f},{v2:.3f},{v3:.3f}")

    print("Done.")
    dac.write(0)


if __name__ == "__main__":
    main()
