"""
Utility functions for common patterns in student projects.

These handle data logging, timing, and other repetitive tasks.
"""

import time
from .platforms import PLATFORM


class Timer:
    """Simple timer for measuring elapsed time with high precision."""

    def __init__(self):
        """Start the timer."""
        if PLATFORM == 'circuitpython':
            self.start_time = time.monotonic_ns()
            self._use_ns = True
        elif PLATFORM == 'micropython':
            # Use microsecond resolution for better precision
            self.start_time = time.ticks_us()
            self._use_us = True
        else:  # mock
            self.start_time = time.time()
            self._use_seconds = True

    def elapsed(self):
        """Get elapsed time in seconds."""
        if PLATFORM == 'circuitpython':
            return (time.monotonic_ns() - self.start_time) / 1e9
        elif PLATFORM == 'micropython':
            return time.ticks_diff(time.ticks_us(), self.start_time) / 1_000_000
        else:  # mock
            return time.time() - self.start_time

    def elapsed_ms(self):
        """Get elapsed time in milliseconds."""
        if PLATFORM == 'circuitpython':
            return (time.monotonic_ns() - self.start_time) / 1e6
        elif PLATFORM == 'micropython':
            return time.ticks_diff(time.ticks_us(), self.start_time) / 1000
        else:  # mock
            return (time.time() - self.start_time) * 1000

    def elapsed_us(self):
        """Get elapsed time in microseconds."""
        if PLATFORM == 'circuitpython':
            return (time.monotonic_ns() - self.start_time) / 1000
        elif PLATFORM == 'micropython':
            return time.ticks_diff(time.ticks_us(), self.start_time)
        else:  # mock
            return (time.time() - self.start_time) * 1_000_000

    def reset(self):
        """Reset the timer."""
        if PLATFORM == 'circuitpython':
            self.start_time = time.monotonic_ns()
        elif PLATFORM == 'micropython':
            self.start_time = time.ticks_us()
        else:  # mock
            self.start_time = time.time()


class DataLogger:
    """
    Simple CSV data logger for experiments.

    Usage:
        logger = DataLogger('data.csv', ['time', 'voltage', 'current'])
        while True:
            logger.log(t, v, i)
        logger.close()
    """

    def __init__(self, filename, headers):
        """
        Initialize logger.

        Args:
            filename: Output CSV filename
            headers: List of column headers
        """
        self.filename = filename
        self.headers = headers
        self.file = open(filename, 'w')

        # Write header row
        self.file.write(','.join(str(h) for h in headers) + '\n')
        self.file.flush()

    def log(self, *values):
        """
        Log a row of data.

        Args:
            *values: Values corresponding to headers (in order)
        """
        if len(values) != len(self.headers):
            raise ValueError(
                "Expected {} values, got {}".format(len(self.headers), len(values))
            )

        row = ','.join(str(v) for v in values)
        self.file.write(row + '\n')
        self.file.flush()

    def close(self):
        """Close the file."""
        if self.file:
            self.file.close()
            self.file = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def disable_irq():
    """Disable interrupts and return saved state. No-op on non-MicroPython platforms."""
    if PLATFORM == 'micropython':
        import machine
        return machine.disable_irq()
    return None


def enable_irq(state):
    """Re-enable interrupts using saved state. No-op on non-MicroPython platforms."""
    if PLATFORM == 'micropython':
        import machine
        machine.enable_irq(state)


def countdown(seconds, label=""):
    """
    Print a countdown timer (useful for startup delays).

    Args:
        seconds: Number of seconds to count down
        label: Optional label to print (e.g., "Charging capacitor")
    """
    if label:
        print(label)
    for i in range(seconds, 0, -1):
        print(i)
        time.sleep(1)
    print("0 --- go!")
