from machine import UART
import time

# Initialize UART on specific pins (GPIO 1 and 2 in this example)
# The ESP32-S2 has multiple UART controllers (0, 1, 2)
uart = UART(1, baudrate=9600, tx=4, rx=6)

# Example: writing and reading data

while True:
    for j in range(1,128):
        uart.write(chr(j))
        print(f"{j:03d},{j:07b}")
        time.sleep(1)
