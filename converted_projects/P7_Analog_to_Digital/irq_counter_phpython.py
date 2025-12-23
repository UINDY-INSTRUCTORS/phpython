"""
P7_Analog_to_Digital - IRQ Counter (phpython Version with Polling)

This is a CONVERTED version that uses phpython and polling instead of interrupts.

IMPORTANT NOTES:
- This version works on BOTH CircuitPython AND MicroPython
- It uses polling (checking the pin repeatedly) instead of hardware interrupts
- Polling is slightly less efficient but works everywhere

When to use each version:
- irq_counter_micropython.py: If you NEED hardware interrupts (MicroPython only)
- irq_counter_phpython.py: If you want cross-platform code (use this unless you need interrupts)

This program:
1. Checks a PIR motion sensor on pin 21 repeatedly
2. Counts rising edges when motion is detected
3. Toggles an LED on each detection
4. Logs the count every second
"""

from phpython import D, DataLogger
import time

# Create digital I/O objects
led = D(15, 'out')      # Onboard LED on pin 15
pir = D(21, 'in')       # PIR motion sensor on pin 21

# Counter and state tracking
count = 0
last_state = False

# Log interrupt counts
with DataLogger('count_data.csv', ['count']) as log:
    try:
        for i in range(1000):
            # Check if pin changed from low to high (rising edge)
            current_state = pir.get()

            if current_state and not last_state:
                # Rising edge detected
                count += 1
                led.toggle()  # Toggle LED on detection

            last_state = current_state

            # Every 1 second, log and reset counter
            if i % 10 == 0:  # Assuming ~100ms loop, so 10 iterations ≈ 1 second
                print(count)
                log.log(count)
                count = 0

            time.sleep(0.1)  # Small delay between checks

    except KeyboardInterrupt:
        print("\nKeyboard interrupt")

print("Done.")
