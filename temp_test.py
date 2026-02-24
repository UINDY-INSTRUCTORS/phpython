
from phpython import A, D, I2C
import mcp9808
import time

def main():
    dout = D(40,'out')
    dout.set(1) # power for board
    time.sleep(0.1)  # wait for board to power up

    i2c = I2C(scl=2, sda=1)

    mcp = mcp9808.MCP9808(i2c=i2c)

    while True:
        print(mcp.get_temp())
        time.sleep(1)

    
if __name__ == "__main__":
    main()
