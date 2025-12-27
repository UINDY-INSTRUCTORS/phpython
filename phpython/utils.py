"""
Utility functions for common patterns in student projects.

These handle data logging, timing, and other repetitive tasks.
"""

import time


class Timer:
    """Simple timer for measuring elapsed time with high precision."""

    def __init__(self):
        """Start the timer."""
        self.start_time = time.monotonic_ns()

    def elapsed(self):
        """Get elapsed time in seconds."""
        return (time.monotonic_ns() - self.start_time) / 1e9

    def elapsed_ms(self):
        """Get elapsed time in milliseconds."""
        return (time.monotonic_ns() - self.start_time) / 1e6

    def reset(self):
        """Reset the timer."""
        self.start_time = time.monotonic_ns()


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
                f"Expected {len(self.headers)} values, got {len(values)}"
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
