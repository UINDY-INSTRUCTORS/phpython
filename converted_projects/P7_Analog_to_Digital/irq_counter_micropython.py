"""
P7_Analog_to_Digital - IRQ Counter (MicroPython Version)

This is the ORIGINAL code using MicroPython's interrupt (IRQ) API.

IMPORTANT: This code only works on MicroPython, not CircuitPython.

Hardware Interrupts:
- CircuitPython does NOT support hardware interrupts
- MicroPython DOES support hardware interrupts via the machine module
- This is one of the fundamental platform differences

When you need interrupts:
1. Flash your ESP32 with MicroPython (not CircuitPython)
2. Use this code as-is
3. Your other code can use phpython (which works on both platforms)

This program:
1. Sets up a PIR motion sensor on pin 21
2. Counts interrupts when motion is detected
3. Toggles an LED on each interrupt
4. Logs the count every second
"""

from machine import Pin
import time

count = 0

def handle_interrupt(pin):
    """Interrupt handler - called when PIR sensor detects motion."""
    global count
    count += 1
    led.value(not led.value())

# Setup pins
led = Pin(15, Pin.OUT)  # Onboard LED on pin 15
pir = Pin(21, Pin.IN)   # PIR motion sensor on pin 21

# Attach interrupt handler
pir.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt)

# Log interrupt counts
with open('count_data.csv', 'w') as f:
    f.write('count\n')
    try:
        for i in range(1000):
            time.sleep(1)  # Wait for one second
            cval = count
            count = 0
            print(cval)
            f.write(f'{cval}\n')
    except KeyboardInterrupt:
        pass

print("Done.")
