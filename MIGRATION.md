# Migration Guide: Converting CircuitPython Code to phpython

This guide shows how to convert existing CircuitPython code to use phpython, so it works on both CircuitPython and MicroPython.

## Before and After Examples

### Example 1: Simple ADC Reading (P1_CollectingData)

**Before (CircuitPython-only):**
```python
import board
import analogio as aio
import time

ADCMAX = 2**16 - 1
adc1 = aio.AnalogIn(board.IO15)
vfactor = adc1.reference_voltage / ADCMAX

while True:
    raw = adc1.value
    voltage = raw * vfactor
    print(f"Raw: {raw}, Voltage: {voltage:.3f}V")
    time.sleep(0.1)
```

**After (phpython):**
```python
from phpython import A
import time

adc1 = A(15)

while True:
    raw = adc1.read()
    voltage = adc1.read_voltage()
    print(f"Raw: {raw}, Voltage: {voltage:.3f}V")
    time.sleep(0.1)
```

**Changes:**
- Replace `import board` and `import analogio as aio` with `from phpython import A`
- Replace `aio.AnalogIn(board.IO15)` with `A(15)`
- Replace `.value` with `.read()` for raw, or `.read_voltage()` for volts
- No need to calculate `vfactor` manually (phpython handles it)

---

### Example 2: Data Collection with CSV

**Before (CircuitPython-only):**
```python
import board
import analogio as aio
import time

ADCMAX = 2**16 - 1
adc1 = aio.AnalogIn(board.IO15)
adc2 = aio.AnalogIn(board.IO10)
vfactor = adc1.reference_voltage / ADCMAX

f = open('data.csv', 'w')
f.write("time_s,v1,v2\n")

t0 = time.monotonic_ns()
while True:
    elapsed = (time.monotonic_ns() - t0) / 1e9
    v1 = adc1.value * vfactor
    v2 = adc2.value * vfactor

    f.write(f"{elapsed:.3f},{v1:.3f},{v2:.3f}\n")
    f.flush()

    if elapsed > 10:
        break

f.close()
```

**After (phpython):**
```python
from phpython import A, DataLogger, Timer
import time

adc1 = A(15)
adc2 = A(10)

with DataLogger('data.csv', ['time_s', 'v1', 'v2']) as log:
    timer = Timer()
    while True:
        elapsed = timer.elapsed()
        v1 = adc1.read_voltage()
        v2 = adc2.read_voltage()

        log.log(elapsed, v1, v2)

        if elapsed > 10:
            break
```

**Changes:**
- Replace CSV file handling with `DataLogger`
- Replace manual timing with `Timer`
- Replace `adc.value * vfactor` with `adc.read_voltage()`
- Use context manager (`with`) for automatic file cleanup

---

### Example 3: Digital I/O

**Before (CircuitPython-only):**
```python
import board
import digitalio as dio

led = dio.DigitalInOut(board.IO21)
led.direction = dio.Direction.OUTPUT

for i in range(10):
    led.value = 1
    time.sleep(0.5)
    led.value = 0
    time.sleep(0.5)

led.deinit()
```

**After (phpython):**
```python
from phpython import D
import time

led = D(21, 'out')

for i in range(10):
    led.set(1)
    time.sleep(0.5)
    led.set(0)
    time.sleep(0.5)

led.deinit()
```

**Alternative (even simpler):**
```python
from phpython import D
import time

led = D(21, 'out')

for i in range(10):
    led.value = 1  # Can use .value directly
    time.sleep(0.5)
    led.value = 0
    time.sleep(0.5)
```

**Changes:**
- Replace `dio.DigitalInOut(board.IO21)` with `D(21, 'out')`
- Replace `dio.Direction.OUTPUT` with `'out'` parameter
- Can use `.set()`, `.get()`, or `.value` property

---

### Example 4: PWM Servo Control

**Before (CircuitPython-only):**
```python
import board
import pwmio
import time

frequency = 50
full_duty = 2**16 - 1
period_ms = 20

servo = pwmio.PWMOut(board.IO21, frequency=frequency)

def set_pulse_ms(pwm, t_ms):
    pwm.duty_cycle = int(full_duty * t_ms / period_ms)

# Sweep servo
for angle_ms in range(10, 20):
    set_pulse_ms(servo, angle_ms / 10.0)
    time.sleep(0.1)

servo.deinit()
```

**After (phpython):**
```python
from phpython import P
import time

servo = P(21, freq=50)

# Sweep servo
for angle_ms in range(10, 20):
    servo.pulse_ms(angle_ms / 10.0)
    time.sleep(0.1)

servo.deinit()
```

**Changes:**
- Replace `pwmio.PWMOut(board.IO21, frequency=50)` with `P(21, freq=50)`
- Use `.pulse_ms()` directly instead of calculating duty cycle
- No need to define `frequency`, `full_duty`, or `period_ms`

---

### Example 4b: DAC (Analog Output)

**Before (CircuitPython-only):**
```python
import board
import analogio as aio

ADCMAX = 2**16 - 1
dac = aio.AnalogOut(board.IO17)
vfactor = 3.3 / ADCMAX  # Manual calibration

# Write 1.5V to DAC
vout = 1.5
vout_raw = int(vout / vfactor)
dac.value = vout_raw

# Write raw value
dac.value = 32768
```

**After (phpython):**
```python
from phpython import A

dac = A(17, 'out')

# Write voltage (smart auto-detection)
dac.write(1.5)      # 1.5V - intuitive!

# Write raw value (auto-detected)
dac.write(32768)    # Raw ADC count

# Or explicit methods for clarity
dac.write_voltage(1.5)  # Always voltage
dac.write_raw(32768)    # Always raw value
```

**Changes:**
- Replace `aio.AnalogOut(board.IO17)` with `A(17, 'out')`
- Write voltage directly: `dac.write(1.5)` instead of manual math
- No need to calculate `vfactor` or convert to raw values
- Smart detection: 0-4.0 is voltage, larger values are raw
- Optional explicit methods for clarity: `write_voltage()` or `write_raw()`

---

### Example 5: Complete Multi-Sensor Project

**Before (CircuitPython-only):**
```python
import board
import analogio as aio
import digitalio as dio
import time

ADCMAX = 2**16 - 1

# Setup
adc1 = aio.AnalogIn(board.IO15)
adc2 = aio.AnalogIn(board.IO10)
vfactor = adc1.reference_voltage / ADCMAX

led = dio.DigitalInOut(board.IO21)
led.direction = dio.Direction.OUTPUT

button = dio.DigitalInOut(board.IO22)
button.direction = dio.Direction.INPUT

# Data collection
f = open('data.csv', 'w')
f.write("time_s,v1,v2,led_on\n")

t0 = time.monotonic_ns()

try:
    while True:
        elapsed = (time.monotonic_ns() - t0) / 1e9
        v1 = adc1.value * vfactor
        v2 = adc2.value * vfactor

        if button.value:
            led.value = 1
        else:
            led.value = 0

        f.write(f"{elapsed:.3f},{v1:.3f},{v2:.3f},{int(led.value)}\n")
        f.flush()

        if elapsed > 30:
            break

except KeyboardInterrupt:
    print("Interrupted")
finally:
    f.close()
    led.deinit()
    adc1.deinit()
    adc2.deinit()
    button.deinit()
```

**After (phpython):**
```python
from phpython import A, D, DataLogger, Timer
import time

# Setup
adc1 = A(15)
adc2 = A(10)
led = D(21, 'out')
button = D(22, 'in')

# Data collection
with DataLogger('data.csv', ['time_s', 'v1', 'v2', 'led_on']) as log:
    timer = Timer()

    try:
        while True:
            elapsed = timer.elapsed()
            v1 = adc1.read_voltage()
            v2 = adc2.read_voltage()

            led.value = button.value  # Copy button state to LED

            log.log(elapsed, v1, v2, int(led.value))

            if elapsed > 30:
                break

    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        led.deinit()
        adc1.deinit()
        adc2.deinit()
        button.deinit()
```

**Changes:**
- Single import line replaces multiple CircuitPython imports
- No ADC calibration needed (`.read_voltage()` handles it)
- `DataLogger` replaces manual file handling
- `Timer` replaces manual `monotonic_ns()` calculations
- Code is ~40% shorter and clearer

---

## Summary of Changes

| CircuitPython | phpython | Type |
|---------------|----------|------|
| `import board` | (not needed) | Import |
| `import analogio as aio` | `from phpython import A` | Import |
| `import digitalio as dio` | `from phpython import D` | Import |
| `import pwmio` | `from phpython import P` | Import |
| `aio.AnalogIn(board.IO15)` | `A(15)` | Analog Input |
| `aio.AnalogOut(board.IO17)` | `A(17, 'out')` | Analog Output |
| `dio.DigitalInOut(pin)` | `D(pin, mode)` | Digital I/O |
| `pwmio.PWMOut(pin, freq=50)` | `P(pin, freq=50)` | PWM |
| Manual CSV writing | `DataLogger()` | CSV Logging |
| `monotonic_ns()` + math | `Timer()` | Timing |
| `time.sleep()` countdown | `countdown()` | Startup |

## Tips

1. **Start small**: Convert one function at a time, test thoroughly
2. **Keep file structure**: Don't restructure your code, just replace imports
3. **Test on CircuitPython first**: Before testing on MicroPython, verify everything works on your existing platform
4. **Keep backup**: Keep original CircuitPython versions until you're confident
5. **Use mock mode**: Test non-hardware logic without a board using `set_mode('mock')`

## Troubleshooting

**"My analog readings are different"**
- phpython automatically handles voltage conversion. If you were doing raw comparisons, adjust to use `.read_voltage()` instead

**"ADC readings seem off"**
- Check that your pin numbers are correct
- Verify reference voltage is correct for your board (ESP32 is typically 3.3V)

**"Code still looks too complex"**
- Focus on critical sections: initialization and the main loop
- Use `with` statements for context managers (automatic cleanup)
- Remove manual calibration code

## Moving Back to CircuitPython-Only

If you ever need to go back to pure CircuitPython, the conversion is straightforward:

- `A(15)` → `aio.AnalogIn(board.IO15)`
- `D(21, 'out')` → `dio.DigitalInOut(board.IO21); pin.direction = dio.Direction.OUTPUT`
- `DataLogger()` → manual file writing
- `Timer()` → manual `monotonic_ns()` code

But with phpython, you shouldn't need to!
