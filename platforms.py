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
    return 2**16 - 1  # Standard for both platforms on ESP32


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
