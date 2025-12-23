"""
Simple tests for phpython module.

These tests use mock mode, so they don't require any hardware.
Run with: python test_phpython.py
"""

import sys
import os

# Add parent directory to path so we can import phpython
# We need the parent of phpython directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phpython import set_mode, A, D, P, DataLogger, Timer
import time


def test_platform_detection():
    """Test that platform detection works."""
    print("Testing platform detection...", end=" ")
    from phpython.platforms import PLATFORM
    print(f"Platform: {PLATFORM}")
    assert PLATFORM in ['circuitpython', 'micropython', 'mock']


def test_analog_input_mock():
    """Test analog input in mock mode."""
    print("Testing analog input (mock)...", end=" ")
    set_mode('mock')

    adc = A(15)
    assert adc.pin_num == 15
    assert adc.read() == 0
    assert adc.read_voltage() == 0.0
    print("OK")


def test_analog_output_mock():
    """Test analog output in mock mode."""
    print("Testing analog output (mock)...", end=" ")
    set_mode('mock')

    dac = A(17, 'out')
    dac.write(2.5)
    assert dac._value > 0
    print("OK")


def test_digital_output_mock():
    """Test digital output in mock mode."""
    print("Testing digital output (mock)...", end=" ")
    set_mode('mock')

    led = D(21, 'out')
    assert led.pin_num == 21
    assert led.mode == 'out'

    led.set(1)
    assert led.get() == True
    assert led.value == True

    led.set(0)
    assert led.get() == False
    assert led.value == False

    led.toggle()
    assert led.get() == True

    print("OK")


def test_digital_input_mock():
    """Test digital input in mock mode."""
    print("Testing digital input (mock)...", end=" ")
    set_mode('mock')

    button = D(22, 'in')
    assert button.pin_num == 22
    assert button.mode == 'in'

    # In mock mode, starts at 0
    assert button.get() == False
    print("OK")


def test_pwm_mock():
    """Test PWM in mock mode."""
    print("Testing PWM (mock)...", end=" ")
    set_mode('mock')

    pwm = P(21, freq=50)
    assert pwm.pin_num == 21
    assert pwm.frequency == 50
    assert pwm.duty() == 0

    pwm.duty(75)
    assert pwm.duty() == 75

    pwm.pulse_ms(1.5)
    # 1.5ms in 20ms period = 7.5%
    assert abs(pwm.duty() - 7.5) < 0.1

    print("OK")


def test_timer():
    """Test Timer utility."""
    print("Testing Timer...", end=" ")

    timer = Timer()
    time.sleep(0.1)
    elapsed = timer.elapsed()

    # Should be approximately 0.1 seconds
    assert 0.05 < elapsed < 0.2, f"Expected ~0.1s, got {elapsed}s"

    timer.reset()
    time.sleep(0.05)
    elapsed2 = timer.elapsed()
    assert 0.01 < elapsed2 < 0.1

    print("OK")


def test_data_logger():
    """Test DataLogger utility."""
    print("Testing DataLogger...", end=" ")

    import tempfile
    import os

    # Create temp file
    fd, temp_file = tempfile.mkstemp(suffix='.csv')
    os.close(fd)
    os.remove(temp_file)

    # Write data
    with DataLogger(temp_file, ['time', 'value', 'status']) as log:
        log.log(0.0, 1.5, 'ok')
        log.log(0.1, 2.5, 'ok')
        log.log(0.2, 3.5, 'error')

    # Read and verify
    with open(temp_file, 'r') as f:
        lines = f.readlines()

    assert len(lines) == 4  # Header + 3 data rows
    assert 'time,value,status' in lines[0]
    assert '0.0,1.5,ok' in lines[1]
    assert '0.1,2.5,ok' in lines[2]
    assert '0.2,3.5,error' in lines[3]

    # Cleanup
    os.remove(temp_file)
    print("OK")


def test_context_managers():
    """Test that pins work as context managers."""
    print("Testing context managers...", end=" ")
    set_mode('mock')

    with D(21, 'out') as led:
        led.set(1)
        assert led.get() == True

    # Pin should be deinit'd after context

    with A(15) as adc:
        assert adc.read() == 0

    print("OK")


def run_all_tests():
    """Run all tests."""
    print("\nRunning phpython tests...\n")

    try:
        test_platform_detection()
        test_analog_input_mock()
        test_analog_output_mock()
        test_digital_output_mock()
        test_digital_input_mock()
        test_pwm_mock()
        test_timer()
        test_data_logger()
        test_context_managers()

        print("\n✓ All tests passed!")
        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
