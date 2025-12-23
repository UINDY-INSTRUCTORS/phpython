# phpython Module Structure

## Overview

phpython is a minimal abstraction layer for CircuitPython and MicroPython. It provides a unified API (`A`, `D`, `P`) that works on both platforms, eliminating the need to teach students two different APIs.

## Directory Structure

```
phpython/
├── __init__.py          # Module entry point, exports A, D, P, etc.
├── core.py              # Main classes: A, D, P (Analog, Digital, PWM)
├── platforms.py         # Platform detection and utilities
├── utils.py             # DataLogger, Timer, countdown helper
├── examples.py          # Working examples for each project type
├── test_phpython.py     # Unit tests (run with `python test_phpython.py`)
├── README.md            # Full API documentation
├── QUICKSTART.md        # Quick start guide for students
├── MIGRATION.md         # Guide for converting CircuitPython → phpython
└── STRUCTURE.md         # This file
```

## File Descriptions

### `__init__.py` (11 lines)
**What it does:** Exports the public API
**Exports:** `A`, `D`, `P`, `set_mode`, `DataLogger`, `Timer`
**For students:** Just use `from phpython import A, D, P`

### `core.py` (330 lines)
**What it does:** Main hardware abstraction classes
**Key classes:**
- `A()` - Analog input/output
- `D()` - Digital input/output
- `P()` - PWM (servo, LED brightness, etc.)

**Design philosophy:**
- Short names for minimal typing
- Handles platform differences transparently
- Works on CircuitPython, MicroPython, and mock mode

### `platforms.py` (50 lines)
**What it does:** Platform detection and import handling
**Key functions:**
- Detects which platform you're on (CircuitPython/MicroPython/mock)
- Normalizes pin numbering across platforms
- Gets voltage calibration info

**For students:** They never interact with this directly

### `utils.py` (95 lines)
**What it does:** Utility functions for common patterns
**Key classes:**
- `Timer` - High-precision timing (nanosecond resolution)
- `DataLogger` - CSV logging without manual file handling
- `countdown()` - Helpful startup countdown

**Why it's useful:** Removes boilerplate from student code

### `examples.py` (170 lines)
**What it does:** Working examples for each project type
**Includes:**
- ADC/DAC data collection (P1)
- Digital I/O and LEDs (P2)
- PWM servo control (P8)
- Sensor logging with Timer (P7)
- Interrupt handlers (MicroPython only)

**For students:** Copy these patterns for their own projects

### `test_phpython.py` (220 lines)
**What it does:** Unit tests verifying all functionality
**Coverage:**
- Platform detection
- Analog input/output
- Digital input/output
- PWM functionality
- Timer and DataLogger utilities
- Context managers (cleanup)

**Run it:** `python test_phpython.py`
**Result:** All tests pass ✓

## API Summary

### Three Main Classes

```
A(pin, mode='in')     → Analog Input/Output
  .read()             → Get raw ADC value
  .read_voltage()     → Get voltage in volts
  .write(value)       → Set DAC output
  .adc_max, .ref_voltage, .vfactor

D(pin, mode='in')     → Digital Input/Output
  .set(1), .set(0)    → Set output high/low
  .get()              → Read input
  .toggle()           → Toggle output
  .value (property)   → Alternative syntax

P(pin, freq, duty)    → PWM Output
  .duty(percent)      → Set/get duty cycle
  .pulse_ms(ms)       → Set pulse width (for servos)
  .frequency          → PWM frequency
```

### Utility Classes

```
Timer()               → High-precision timer
  .elapsed()          → Seconds elapsed
  .elapsed_ms()       → Milliseconds elapsed
  .reset()            → Restart timer

DataLogger(file, headers) → CSV logging
  .log(*values)       → Write row to CSV
  .close()            → Close file
  (supports 'with' statement)

countdown(seconds, label) → Print countdown
```

## How It Works

### Platform Detection

When phpython loads:

1. **Tries to import CircuitPython**: If successful → use CircuitPython APIs
2. **Tries to import MicroPython**: If successful → use machine API
3. **Neither found?** → Use mock (for testing)

Then student code works unchanged on any platform.

### Example: Reading an Analog Pin

**Student writes:**
```python
from phpython import A
adc = A(15)
voltage = adc.read_voltage()
```

**Behind the scenes (CircuitPython):**
```python
import analogio, board
pin = board.IO15
obj = analogio.AnalogIn(pin)
return obj.value * (ref_voltage / 65535)
```

**Behind the scenes (MicroPython):**
```python
from machine import ADC, Pin
obj = ADC(Pin(15))
return obj.read() * (3.3 / 1023)
```

**Student sees:** Same output, same code! ✓

## Total Size and Complexity

| File | Lines | Complexity |
|------|-------|------------|
| `__init__.py` | 11 | Trivial |
| `core.py` | 330 | Moderate |
| `platforms.py` | 50 | Simple |
| `utils.py` | 95 | Simple |
| `examples.py` | 170 | Examples |
| **TOTAL** | **656** | **~400 lines of real code** |

**Key point:** This is a SIMPLE module that students can read and understand entirely. It's not hiding complexity; it's eliminating it.

## Usage in Your Course

### For Existing Code

1. Copy `phpython` folder to your project
2. Replace imports (see MIGRATION.md)
3. Done! Code works on both platforms

### For New Code

Students start with:
```python
from phpython import A, D, P, DataLogger, Timer
```

And never need to learn CircuitPython vs MicroPython differences.

### For Interrupts (P6)

**One-time exception:** When teaching interrupts, students flash with MicroPython and use the machine API directly:

```python
from machine import Pin

def isr(pin):
    # interrupt handler
    pass

sensor = Pin(21, Pin.IN)
sensor.irq(trigger=Pin.IRQ_RISING, handler=isr)
```

This is **intentionally platform-specific**—helps them understand that interrupts are fundamentally different between platforms. Everything else stays unified.

## Testing

All functionality tested in mock mode:

```bash
$ python test_phpython.py
Running phpython tests...

Testing platform detection... Platform: mock
Testing analog input (mock)... OK
Testing analog output (mock)... OK
Testing digital output (mock)... OK
Testing digital input (mock)... OK
Testing PWM (mock)... OK
Testing Timer... OK
Testing DataLogger... OK
Testing context managers... OK

✓ All tests passed!
```

## Documentation

- **QUICKSTART.md** - 30-second intro for students
- **README.md** - Full API reference and troubleshooting
- **MIGRATION.md** - Before/after examples converting CircuitPython code
- **examples.py** - Complete working examples
- This file - Architecture and design decisions

## Design Philosophy

1. **Minimal**: Only abstract what's necessary, no feature bloat
2. **Clear**: Students can read and understand the entire source (400 lines)
3. **Safe**: No hidden platform differences; interrupts are intentionally exposed as different
4. **Tested**: All functionality verified with unit tests
5. **Practical**: Based on actual student projects from your course

This isn't a heavy framework. It's a lightweight convenience layer that eliminates cognitive load while keeping everything transparent.
