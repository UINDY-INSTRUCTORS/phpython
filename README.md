# phpython

A minimal abstraction layer for CircuitPython and MicroPython that lets you write code once and run it on both platforms without learning two APIs.

## Why?

- **One API**: Write code that works on both CircuitPython and MicroPython
- **Less typing**: Short names and sensible defaults (`A`, `D`, `P` instead of `AnalogIn`, `DigitalOut`, `PWMOut`)
- **Same patterns**: Consistent interface across platforms
- **Testable**: Mock backend lets you test without hardware

## Installation

Copy the `phpython` directory to your microcontroller alongside your code, or put it in your Python path.

## Quick Start

```python
from phpython import A, D, P, DataLogger, Timer

# Analog input/output
adc = A(15)              # Analog input on pin 15
voltage = adc.read_voltage()  # Read as voltage (in volts)
raw = adc.read()         # Read raw ADC value

dac = A(17, 'out')       # Analog output on pin 17
dac.write(1.5)           # Write 1.5V

# Digital input/output
led = D(21, 'out')       # Digital output on pin 21
led.set(1)               # Set high
led.value = 0            # Alternative syntax
is_high = led.get()      # Read

button = D(22, 'in')     # Digital input on pin 22
pressed = button.get()   # Read input

# PWM
servo = P(21, freq=50)   # 50 Hz PWM on pin 21
servo.duty(50)           # 50% duty cycle
servo.pulse_ms(1.5)      # 1.5 ms pulse (for servos)

# Data logging
with DataLogger('data.csv', ['time', 'voltage', 'current']) as log:
    for t in range(100):
        log.log(t, 3.0, 0.5)

# Timing
timer = Timer()
time.sleep(1)
print(timer.elapsed())   # 1.0 seconds
```

## API Reference

### Analog I/O: `A(pin, mode='in')`

Read analog voltages or output analog voltages.

```python
# Input
adc = A(15)
voltage = adc.read_voltage()  # Voltage in volts
raw = adc.read()              # Raw ADC value (0 to 65535)

# Output
dac = A(17, 'out')
dac.write(2.5)                # Write voltage
dac.write(32768)              # Or raw value
```

**Properties:**
- `read()` - Get raw ADC value
- `read_voltage()` - Get voltage in volts
- `write(value)` - Set output (voltage < 10 is treated as volts, else raw)
- `adc_max` - Maximum ADC value
- `ref_voltage` - Reference voltage for conversions
- `vfactor` - Conversion factor (volts per count)

### Digital I/O: `D(pin, mode='in')`

Read or write digital pins (high/low).

```python
# Output
led = D(21, 'out')
led.set(1)           # High
led.set(0)           # Low
led.toggle()         # Toggle
led.value = 1        # Alternative syntax

# Input
button = D(22, 'in')
is_pressed = button.get()
is_pressed = button.value  # Alternative syntax
```

**Properties:**
- `set(value)` - Set pin high (1) or low (0)
- `get()` - Read pin state (True/False)
- `toggle()` - Toggle output
- `value` - Property for get/set (use as `pin.value = 1` or `x = pin.value`)

### PWM: `P(pin, freq=1000, duty_percent=0)`

Pulse width modulation for motors, LEDs, and servos.

```python
pwm = P(21, freq=50)        # 50 Hz on pin 21
pwm.duty(75)                # 75% duty cycle
pwm.pulse_ms(1.5)           # 1.5 ms pulse width (for servos)
```

**Properties:**
- `duty(percent)` - Set duty cycle (0-100%), or read current value
- `pulse_ms(ms, period_ms=20)` - Set pulse width in milliseconds
- `frequency` - Operating frequency in Hz

## Utilities

### DataLogger

Log data to CSV files without string formatting overhead.

```python
with DataLogger('data.csv', ['time', 'voltage', 'temp']) as log:
    for t in range(100):
        log.log(t, 3.3, 25.0)
```

### Timer

High-precision timing with nanosecond resolution.

```python
timer = Timer()
time.sleep(1)
print(timer.elapsed())      # 1.0 (seconds)
print(timer.elapsed_ms())   # 1000.0 (milliseconds)
timer.reset()               # Start over
```

### countdown()

Helpful for startup delays while your hardware stabilizes.

```python
countdown(3, "Discharging capacitor...")
# Prints:
# Discharging capacitor...
# 3
# 2
# 1
# 0 --- go!
```

## Platform-Specific Code

### Interrupts (MicroPython only)

CircuitPython doesn't support hardware interrupts. When you need interrupts:

1. Re-flash your board with MicroPython
2. Use the machine API directly (this is intentionally platform-specific):

```python
from machine import Pin
import time

count = 0

def handle_interrupt(pin):
    global count
    count += 1

sensor = Pin(21, Pin.IN)
sensor.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt)

while True:
    print(f"Interrupts: {count}")
    time.sleep(1)
```

This is the **one place** where you'll write platform-specific code. Everything else uses phpython.

## Testing Without Hardware

phpython includes a mock backend for testing code without a microcontroller:

```python
from phpython import set_mode, A, D, P

set_mode('mock')  # Use mock hardware

led = D(21, 'out')
led.set(1)
print(led.get())  # True

adc = A(15)
print(adc.read())  # 0 (always returns 0 in mock mode)
```

## Troubleshooting

**"ImportError: No module named 'phpython'"**
- Make sure the `phpython` directory is in your code path or copied to your board

**"AttributeError: module 'board' has no attribute 'IO15'"**
- CircuitPython pin names vary by board. Adjust pin numbers to match your board's pinout

**"Hardware not responding"**
- Check your wiring
- Verify pin numbers against your board's pinout
- Add delays between operations if hardware is slow to respond

## Examples

See `examples.py` for complete examples covering:
- ADC/DAC data collection
- Digital I/O (LEDs, buttons)
- PWM servo control
- Sensor logging
- Interrupt handling (MicroPython)

## Supported Platforms

- **CircuitPython**: Full support for all features except interrupts
- **MicroPython**: Full support for all features
- **Mock**: Testing without hardware (always works)

## Version

0.1.0
