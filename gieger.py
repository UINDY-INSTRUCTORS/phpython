from phpython import D, disable_irq, enable_irq
import time

count = 0

def handle_interrupt(pin):
    global count
    count += 1
    led.toggle()

led = D(15, 'out')
gmt = D(2, 'in')
gmt.attach_irq(handle_interrupt, trigger='falling')

for i in range(1000):
    time.sleep(1)
    state = disable_irq()
    cval = count
    count = 0
    enable_irq(state)
    print(cval)

print("Done.")