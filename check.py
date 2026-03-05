from phpython import D, disable_irq, enable_irq
import time

count = 0

led = D(15, 'out')
sig = D(2, 'in')
val = 0

led.set(val)

while True:
    time.sleep(1)
    val = not val
    print("Setting", val)
    led.set(val)


print("Done.")
