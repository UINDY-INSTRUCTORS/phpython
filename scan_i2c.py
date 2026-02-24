from phpython import D, I2C
import time

def main():
    dout = D(40, 'out')
    dout.set(1)  # power for board
    time.sleep(0.1)

    i2c = I2C(scl=2, sda=1)
    print("Scanning I2C bus...")
    devices = i2c.scan()
    if devices:
        for addr in devices:
            print("  0x{:02X}".format(addr))
    else:
        print("  No devices found")

if __name__ == "__main__":
    main()
