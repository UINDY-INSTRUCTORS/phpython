"""
Platform detection and import management.

Detects whether we're running on CircuitPython, MicroPython, or in mock mode,
and provides a unified namespace for platform-specific functionality.
"""

import sys

# Detect platform
PLATFORM = None
_board = None
_time = None

# Try to detect what we're running on
try:
    import board
    PLATFORM = 'circuitpython'
    _board = board
except (ImportError, AttributeError):
    try:
        from machine import Pin
        PLATFORM = 'micropython'
    except ImportError:
        PLATFORM = 'mock'

# Get time module (same across platforms)
import time as _time_module
_time = _time_module


def pin_number_to_pin(pin_num):
    """
    Convert a pin number to the platform-specific pin object.

    CircuitPython: returns board.IO{pin_num}
    MicroPython: returns {pin_num}
    Mock: returns {pin_num}
    """
    if PLATFORM == 'circuitpython':
        return getattr(_board, f'IO{pin_num}')
    else:
        return pin_num


def get_adc_max():
    """Get the maximum ADC value for the current platform."""
    if PLATFORM == 'circuitpython':
        return 2**16 - 1  # CircuitPython uses 16-bit on ESP32
    elif PLATFORM == 'micropython':
        return 2**12 - 1  # MicroPython ADC is 12-bit by default (0-4095)
    else:  # mock
        return 2**16 - 1


def get_ref_voltage():
    """Get the reference voltage for ADC conversions."""
    if PLATFORM == 'circuitpython':
        try:
            import analogio
            # Create a dummy ADC to get reference voltage
            dummy = analogio.AnalogIn(_board.IO36)
            ref = dummy.reference_voltage
            dummy.deinit()
            return ref
        except:
            return 3.3  # Fallback for ESP32
    else:
        return 3.3  # MicroPython, typically 3.3V


def get_board_info():
    """
    Get information about the current board and platform.

    Returns:
        dict: Board information including platform, processor, memory, etc.
    """
    info = {
        'platform': PLATFORM,
        'python_version': None,
        'board': None,
        'processor': None,
        'frequency': None,
        'ram_total': None,
        'ram_free': None,
    }

    if PLATFORM == 'circuitpython':
        try:
            import board
            import microcontroller
            import gc

            info['python_version'] = sys.version
            info['board'] = board.board_id if hasattr(board, 'board_id') else 'unknown'
            info['processor'] = microcontroller.cpu.frequency
            info['frequency'] = microcontroller.cpu.frequency

            # Memory info
            gc.collect()
            import supervisor
            if hasattr(supervisor, 'runtime'):
                info['ram_total'] = supervisor.runtime.max_stack_depth if hasattr(supervisor.runtime, 'max_stack_depth') else None
            info['ram_free'] = gc.mem_free()
        except Exception as e:
            info['error'] = str(e)

    elif PLATFORM == 'micropython':
        try:
            import gc
            import machine

            info['python_version'] = sys.version
            info['processor'] = 'ESP32'
            info['frequency'] = machine.freq()

            # Memory info
            gc.collect()
            info['ram_free'] = gc.mem_free()
            info['ram_total'] = gc.mem_alloc() + gc.mem_free()
        except Exception as e:
            info['error'] = str(e)

    else:  # mock
        info['python_version'] = sys.version
        info['platform'] = 'mock (CPython)'

    return info


def print_board_info():
    """Print board information in a readable format."""
    info = get_board_info()

    print("=" * 60)
    print("Board Information")
    print("=" * 60)
    print("Platform:        {}".format(info['platform']))

    if info.get('python_version'):
        print("Python Version:  {}".format(info['python_version']))

    if info.get('board'):
        print("Board ID:        {}".format(info['board']))

    if info.get('processor'):
        print("Processor:       {}".format(info['processor']))

    if info.get('frequency'):
        freq_mhz = info['frequency'] / 1_000_000
        print("CPU Frequency:   {:.1f} MHz".format(freq_mhz))

    if info.get('ram_total'):
        ram_kb = info['ram_total'] / 1024
        print("Total RAM:       {:.1f} KB".format(ram_kb))

    if info.get('ram_free'):
        ram_free_kb = info['ram_free'] / 1024
        print("Free RAM:        {:.1f} KB".format(ram_free_kb))

    if info.get('error'):
        print("Error:           {}".format(info['error']))

    print("=" * 60)
