"""
phpython: A unified abstraction layer for CircuitPython and MicroPython

Provides simple interfaces for analog I/O, digital I/O, and PWM that work
across platforms without forcing students to learn both APIs.

Quick start:
    from phpython import A, D, P

    adc = A(15)           # AnalogIn on pin 15
    dac = A(17, 'out')    # AnalogOut on pin 17
    led = D(21, 'out')    # DigitalOut on pin 21
    pwm = P(21, freq=50)  # PWM on pin 21 at 50 Hz
"""

from .core import A, D, P, I2C, set_mode
from .utils import DataLogger, Timer, countdown, disable_irq, enable_irq
from .platforms import PLATFORM, get_board_info, print_board_info

__version__ = "0.1.0"
__all__ = ['A', 'D', 'P', 'I2C', 'set_mode', 'DataLogger', 'Timer', 'countdown', 'disable_irq', 'enable_irq', 'PLATFORM', 'get_board_info', 'print_board_info']
