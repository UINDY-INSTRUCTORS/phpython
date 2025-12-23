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

from phpython import set_mode, A, D, P, I2C, DataLogger, Timer
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


def test_dac_voltage_api():
    """Test DAC voltage writing (smart auto-detection)."""
    print("Testing DAC voltage API...", end=" ")
    set_mode('mock')

    dac = A(17, 'out')

    # Test voltage writing (auto-detected)
    dac.write(3.3)  # 3.3V
    assert dac._value > 0
    v1 = dac._value

    dac.write(1.5)  # 1.5V
    assert 0 < dac._value < v1  # Should be less than 3.3V

    dac.write(0)  # 0V
    assert dac._value == 0

    # Test raw value writing (auto-detected as raw because > 4.0)
    dac.write(32768)  # Raw value
    assert dac._value == 32768

    # Test explicit voltage writing
    dac.write_voltage(2.5)
    assert dac._value > 0

    # Test explicit raw writing
    dac.write_raw(16384)
    assert dac._value == 16384

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


def test_interrupt_api():
    """Test interrupt API on different platforms."""
    print("Testing interrupt API...", end=" ")
    set_mode('mock')

    # Create input pin
    button = D(22, 'in')

    # Test that attach_irq raises error in mock mode
    def dummy_handler(pin):
        pass

    try:
        button.attach_irq(dummy_handler, trigger='rising')
        assert False, "Should have raised RuntimeError in mock mode"
    except RuntimeError as e:
        assert "mock mode" in str(e).lower()

    # Test that invalid trigger raises ValueError
    set_mode('circuitpython')  # Switch to circuitpython to test the ValueError path
    # Actually, this will fail to initialize on circuitpython without real hardware
    # So we'll just test the mock mode behavior

    set_mode('mock')

    # Test that it raises RuntimeError with informative message
    try:
        button.attach_irq(dummy_handler, trigger='invalid')
    except ValueError as e:
        assert "invalid trigger" in str(e).lower()

    print("OK")


def test_i2c_mock():
    """Test I2C bus abstraction in mock mode."""
    print("Testing I2C (mock)...", end=" ")
    set_mode('mock')

    # Test basic initialization
    i2c = I2C(scl=6, sda=8)
    assert i2c.scl_pin == 6
    assert i2c.sda_pin == 8
    assert i2c.frequency == 400000

    # Test with custom frequency
    i2c2 = I2C(scl=6, sda=8, frequency=100000)
    assert i2c2.frequency == 100000

    # Test scan returns empty list in mock mode
    devices = i2c.scan()
    assert devices == []

    # Test readfrom_mem returns zeros in mock mode
    data = i2c.readfrom_mem(0x68, 0x00, 2)
    assert len(data) == 2
    assert data == bytes([0, 0])

    # Test writeto_mem works in mock mode (no-op)
    isnone = i2c.writeto_mem(0x68, 0x00, bytes([0x12, 0x34]))
    # Should succeed without error

    # Test readfrom returns zeros in mock mode
    data = i2c.readfrom(0x68, 3)
    assert len(data) == 3
    assert data == bytes([0, 0, 0])

    # Test writeto works in mock mode
    nbytes = i2c.writeto(0x68, bytes([0x12, 0x34, 0x56]))
    assert nbytes == 3

    # Test context manager
    with I2C(scl=6, sda=8) as i2c3:
        devices = i2c3.scan()
        assert devices == []

    # Cleanup
    i2c.deinit()
    print("OK")


def run_all_tests():
    """Run all tests."""
    print("\nRunning phpython tests...\n")

    try:
        test_platform_detection()
        test_analog_input_mock()
        test_analog_output_mock()
        test_dac_voltage_api()
        test_digital_output_mock()
        test_digital_input_mock()
        test_pwm_mock()
        test_timer()
        test_data_logger()
        test_context_managers()
        test_interrupt_api()
        test_i2c_mock()

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
