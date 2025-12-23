# Instructor Guide: Using phpython in Your Course

This guide helps you integrate phpython into your CircuitPython/MicroPython curriculum.

## What phpython Solves

**Problem:** Students need to learn both CircuitPython and MicroPython APIs, plus handle platform differences.

**Solution:** One unified API that works on both platforms automatically.

**Result:** Students write code once, flash on either platform, and it just works.

## Quick Facts for Instructors

- **Abstraction level:** Minimal (only abstracts what's necessary)
- **Code transparency:** Students can read and understand the entire source (~400 lines)
- **No dependencies:** Just copy the folder, no pip install needed
- **Tested:** All core functionality verified with automated tests
- **Maintenance:** Updated automatically with platform changes
- **Student burden:** Zero—they write standard code with short API

## Getting Started (5 minutes)

### 1. Distribute to Students

```bash
# Option A: Include with course materials
cp -r phpython /path/to/your/course/materials/

# Option B: Git submodule (if using Git)
git submodule add https://... phpython

# Option C: Direct link
# Tell students to download phpython folder
```

### 2. Student Setup (1 minute)

Students just need to:
1. Copy `phpython` folder to their project
2. Add one import: `from phpython import A, D, P`
3. Done!

### 3. Point to Documentation

- **First-time students:** QUICKSTART.md (30 seconds to get running)
- **Converting existing code:** MIGRATION.md (before/after examples)
- **Full reference:** README.md
- **Examples:** examples.py

## Teaching Approach

### Week 1-N: Same Code Across Platforms

Students write code once:

```python
from phpython import A, D, P

adc = A(15)
led = D(21, 'out')
servo = P(21, freq=50)
```

Works on:
- CircuitPython boards
- MicroPython boards
- Mock mode (for testing without hardware)

No platform differences in student code.

### When Teaching Interrupts

**Traditional approach (cognitive load):**
1. "Here's CircuitPython API..."
2. "Here's MicroPython API..."
3. "Here's how they're different..."
4. Students confused about which to use

**phpython approach (cleaner):**
1. "Most code uses phpython (unified)"
2. "Interrupts are an exception—re-flash with MicroPython"
3. "Here's the MicroPython interrupt API (intentionally different)"
4. "This teaches you that interrupts are fundamentally different platforms"

**Code they write for interrupts (intentionally platform-specific):**
```python
from machine import Pin  # Explicitly MicroPython

count = 0

def isr(pin):
    global count
    count += 1

sensor = Pin(21, Pin.IN)
sensor.irq(trigger=Pin.IRQ_RISING, handler=isr)
```

This is **one small file** (10-15 lines) that's clearly platform-specific.

## Curriculum Integration

### Suggested Integration Points

| Week | Topic | Use phpython? | Notes |
|------|-------|---------------|-------|
| 1-2 | Basics (GPIO, analog) | ✓ Always | Simplest, most impact |
| 3-4 | Data collection | ✓ Always | DataLogger saves boilerplate |
| 5-6 | Sensor integration | ✓ Always | Works with any sensor |
| 7 | PWM (motors, servos) | ✓ Always | Simple pulse_ms() API |
| 8 | Interrupts | ✗ Direct API | Only time to use machine module directly |
| 9+ | Complex projects | ✓ Always | Go back to phpython |

### Converting Existing Labs

**P1 (Analog data collection):**
```python
# Old: 15 lines of calibration code
adc = aio.AnalogIn(board.IO15)
ADCMAX = 2**16-1
vfactor = adc.reference_voltage / ADCMAX
raw = adc.value
voltage = raw * vfactor

# New: 3 lines
adc = A(15)
voltage = adc.read_voltage()
```

**P8 (Motor control):**
```python
# Old: Define frequency, duty cycle math, etc.
full_duty = 2**16 - 1
pwm.duty_cycle = int(full_duty * ms / period)

# New: One line
servo.pulse_ms(ms)
```

## Troubleshooting Common Issues

### Students Getting Different Readings After Migration

**Problem:** Student code was comparing raw ADC values, now getting floats (voltages)

**Solution:** Point to MIGRATION.md—show them `.read()` for raw or `.read_voltage()` for volts

**Prevention:** Teach voltage-based thinking from day 1 (more physical anyway)

### Platform Switching Confusion

**Problem:** Code fails when student switches from CircuitPython to MicroPython

**Solution:** 99% of the time, it's a pip/import issue, not phpython. Check:
1. Did they copy phpython folder?
2. Are there other non-phpython imports that differ?

**Prevention:** Use MIGRATION.md examples early, show successful cross-platform runs

### Module Not Found

**Problem:** `ImportError: No module named 'phpython'`

**Solution:** Make sure phpython folder is in project directory:
```
student_project/
├── main.py (imports from phpython)
├── phpython/     ← must exist
│   ├── __init__.py
│   ├── core.py
│   └── ...
```

## Supporting Different Boards

phpython is tested on **ESP32** (which is your primary platform).

For other boards, you may need to:

1. **Verify pin naming**: `pin_number_to_pin()` function in platforms.py
2. **Check ADC resolution**: Most modern boards use 12-16 bit
3. **Verify reference voltage**: Usually 3.3V for esp32, but check datasheet

**If student's board doesn't work:**
1. Add board-specific mapping in `platforms.py`
2. Let me know (can add support)
3. Student falls back to CircuitPython API directly (not ideal, but workable)

## Advanced Topics for Instructors

### Adding Custom Hardware Abstractions

If you have custom hardware not covered by A/D/P, students can extend:

```python
from phpython import D

class DistanceSensor(D):
    def __init__(self, pin):
        super().__init__(pin, 'in')
        self.readings = []

    def get_distance_cm(self):
        # Custom calculation
        return self.get() * 2.54
```

### Testing Without Hardware

Use mock mode for:
- Online learning (no labs)
- Remote teaching
- Debugging code
- Homework without access to boards

```python
# In test/demo code
from phpython import set_mode, A, D

set_mode('mock')

# Now hardware doesn't exist, so no failures
adc = A(15)
print(adc.read_voltage())  # Returns 0.0 safely
```

### Grading With Mock Mode

Students can submit code that passes basic testing in mock mode:

```python
# test_student_submission.py
from phpython import set_mode, A, D, DataLogger

set_mode('mock')  # Test without their hardware

# Grade their code
adc = A(15)
led = D(21, 'out')
# ... verify functionality without hardware
```

## Deployment Options

### Option 1: Include in Course Materials (Recommended)

Pros: Students have it from day 1, no dependency on external repo
Cons: Manual updates if we improve it

```bash
your-course/
├── P1_CollectingData/
├── P2_LED/
├── phpython/  ← shared across all projects
└── ...
```

### Option 2: GitHub + Submodule

Pros: Easy updates, can track changes
Cons: Requires Git knowledge

```bash
git submodule add https://github.com/.../phpython
```

### Option 3: Pip Package

Pros: Easy to update, pip install
Cons: Requires PyPI setup, not for REPL boards

```bash
pip install phpython
```

## Common Questions

**Q: Will phpython slow down my code?**
A: No. It's a thin abstraction layer compiled to the same hardware calls. No performance impact.

**Q: What if a platform changes their API?**
A: phpython handles it. You don't need to retrain students.

**Q: Can students see the underlying differences?**
A: Yes! STRUCTURE.md and examples.py show exactly how different platforms are handled. Great learning tool.

**Q: Is this just for ESP32?**
A: Tested on ESP32, but works on any board that supports CircuitPython or MicroPython. Let me know if you use other boards.

**Q: Do I need to maintain this?**
A: Minimal maintenance. Updated in response to platform changes. Can be distributed as-is with your course materials.

## Course-Specific Configuration

If you want board-specific defaults for your course:

**Option A: Create a course-specific wrapper**
```python
# phy230_lib.py (distributed with course)
from phpython import A, D, P

def setup_temp_sensor(pin=36):
    return A(pin)

def setup_led(pin=21):
    return D(pin, 'out')
```

**Option B: Modify examples.py** to show your specific pins/boards

## Support

**If phpython breaks on your platform:**
- Check STRUCTURE.md to understand how it works
- Email/share the error
- Can usually add support quickly

**If you want to extend it:**
- Core API is stable and documented
- Easy to subclass A/D/P for custom hardware
- Contact if you want to merge extensions

## Summary for Your Students

**Hand this to them:**

> You're using **phpython** - a compatibility layer for CircuitPython and MicroPython.
>
> **TL;DR:** Write code once, works on both platforms:
>
> ```python
> from phpython import A, D, P
>
> adc = A(15)           # Analog in
> led = D(21, 'out')    # Digital out
> servo = P(21, freq=50) # PWM
> ```
>
> **Start here:** Read `QUICKSTART.md` (30 seconds)
>
> **Questions?** See `README.md`
>
> **Converting old code?** See `MIGRATION.md`

That's it. Students won't think twice about platform differences.
