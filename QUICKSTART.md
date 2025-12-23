# phpython Quick Start

Get up and running in 5 minutes.

## Installation

1. **Copy phpython to your project** (or to your microcontroller's filesystem):
   ```bash
   cp -r phpython /path/to/your/project/
   ```

2. **That's it!** No dependencies, no pip install needed.

## 30-Second Example

Read an analog sensor and log data:

```python
from phpython import A, DataLogger, Timer

# Create analog input on pin 15
sensor = A(15)

# Log data to CSV
with DataLogger('data.csv', ['time', 'voltage']) as log:
    timer = Timer()
    while timer.elapsed() < 10:  # Run for 10 seconds
        v = sensor.read_voltage()
        log.log(timer.elapsed(), v)
```

That's it! No calibration, no manual file handling, no board definitions.

## Common Tasks

### Read Analog Voltage
```python
from phpython import A

adc = A(15)  # Pin 15
voltage = adc.read_voltage()
print(f"Voltage: {voltage:.2f}V")
```

### Control an LED
```python
from phpython import D
import time

led = D(21)  # Pin 21, defaults to output

led.set(1)      # Turn on
time.sleep(1)
led.set(0)      # Turn off

# Or use .value property
led.value = 1
```

### Read a Button
```python
from phpython import D

button = D(22, 'in')  # Pin 22, input mode

if button.get():
    print("Button pressed!")
```

### Control a Servo
```python
from phpython import P

servo = P(21, freq=50)  # 50 Hz standard servo

servo.pulse_ms(1.0)   # Min position (1.0 ms)
servo.pulse_ms(1.5)   # Center (1.5 ms)
servo.pulse_ms(2.0)   # Max position (2.0 ms)
```

### Log Multiple Sensors
```python
from phpython import A, DataLogger, Timer

adc1 = A(15)
adc2 = A(10)

with DataLogger('sensors.csv', ['time', 'sensor1', 'sensor2']) as log:
    timer = Timer()
    for _ in range(100):
        v1 = adc1.read_voltage()
        v2 = adc2.read_voltage()
        log.log(timer.elapsed(), v1, v2)
```

### Write to DAC (Analog Output)
```python
from phpython import A

dac = A(17, 'out')  # Analog output on pin 17

# Write voltage (smart auto-detection)
dac.write(3.3)      # 3.3 volts
dac.write(1.5)      # 1.5 volts
dac.write(0)        # 0 volts

# Or explicit methods for clarity
dac.write_voltage(2.5)  # Always voltage
dac.write_raw(32768)    # Raw value (0-65535)
```

### Interrupt Handler (MicroPython only)
```python
from phpython import D
import time

def on_button(pin):
    print("Button pressed!")

button = D(22, 'in')
button.attach_irq(on_button, trigger='rising')  # MicroPython only!

# Main loop continues while interrupt fires independently
while True:
    print("Running...")
    time.sleep(1)
```

Note: Interrupts only work on **MicroPython**. CircuitPython will raise `NotImplementedError`.

## Platform Switching

**CircuitPython:** Just run your code normally
```bash
# Flash your ESP32 with CircuitPython
# Copy your code and phpython folder
# Code runs unchanged!
```

**MicroPython:** Just run your code normally
```bash
# Flash your ESP32 with MicroPython
# Copy your code and phpython folder
# Code runs unchanged!
```

**Need interrupts?** Only MicroPython supports them. Use the machine API directly (one time, platform-specific):
```python
from machine import Pin

count = 0

def isr(pin):
    global count
    count += 1

sensor = Pin(21, Pin.IN)
sensor.irq(trigger=Pin.IRQ_RISING, handler=isr)
```

## Testing Without Hardware

Test your code without a microcontroller:

```python
from phpython import set_mode, A, D

set_mode('mock')  # Use fake hardware

led = D(21)
led.set(1)
print(led.get())  # True

adc = A(15)
print(adc.read_voltage())  # 0.0
```

## Pin Numbers

Find your pin numbers in the datasheet or online docs. For ESP32:
- **Analog pins**: 36, 39, 34, 35, 32, 33, 27, 14, 12, 13, 4, 2, 15, 5, 18, 19, 23, 25, 26
- **Digital pins**: Same as above, plus many others

## Troubleshooting

**"Module not found"**
- Make sure `phpython` folder is in your project directory or Python path

**"No attribute IO15"**
- Wrong pin number. Check your board's pinout. Try a pin like 15, 21, 22.

**"Hardware not responding"**
- Double-check your wiring
- Verify pin numbers match your circuit
- Add `time.sleep()` if hardware is slow to respond

**"Got different readings than before"**
- phpython automatically converts to voltage. Use `.read_voltage()` for voltage (default) or `.read()` for raw ADC value.

## Next Steps

- See `examples.py` for complete working examples
- Check `MIGRATION.md` to convert existing CircuitPython code
- Read `README.md` for full API documentation

## Got Questions?

See the full documentation:
- **API Reference**: README.md
- **Code Migration**: MIGRATION.md
- **Examples**: examples.py
- **Run tests**: `python test_phpython.py`

Happy coding! 🎉
