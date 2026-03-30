from phpython import D, disable_irq, enable_irq
import time

count = 0
IRQ_PIN = 2  # choose
LED_PIN = 15 # no choice here!

def handle_interrupt(pin):
    global count
    count += 1
    led.toggle()

led = D(LED_PIN, 'out')
sig = D(IRQ_PIN, 'in')
sig.attach_irq(handle_interrupt, trigger='rising')

while True:
    time.sleep(1)
    state = disable_irq()
    cval = count
    count = 0
    enable_irq(state)
    print(cval)

