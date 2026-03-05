from phpython import D, disable_irq, enable_irq
import time

NUM_SECONDS = 120
count = 0

IRQ_PIN = ?? # choose
LED_PIN = 15 # no choice here!
PWR_PIN = ?? # choose

def handle_interrupt(pin):
    global count
    count += 1
    led.toggle()

led = D(LED_PIN, 'out')

pwr = D(PWR_PIN, 'out')
pwr.set(1) # power for level shifter

gmt = D(IRQ_PIN, 'in')
gmt.attach_irq(handle_interrupt, trigger='rising')

for i in range(NUM_SECONDS):
    time.sleep(1)
    state = disable_irq()
    cval = count
    count = 0
    enable_irq(state)
    print(cval)

print("Done.")

