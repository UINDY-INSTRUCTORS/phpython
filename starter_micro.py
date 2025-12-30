import machine
import time

# --- CONFIGURATION ---
# DAC still needs a factor because it doesn't have a 'write_uv' equivalent.
V_DAC_MAX = 3.3  
vfactor_dac = V_DAC_MAX / 255

# Initialize hardware
vdac = machine.DAC(machine.Pin(17))
adc1 = machine.ADC(machine.Pin(15))
adc2 = machine.ADC(machine.Pin(10))

# Set 11dB attenuation
adc1.atten(machine.ADC.ATTN_11DB)
adc2.atten(machine.ADC.ATTN_11DB)

def read_avg_voltage(adc_pin):
    total_uv = 0
    for _ in range(16):
        total_uv += adc_pin.read_uv()
    return (total_uv / 16) / 1_000_000

# --- EXECUTION ---
f = open('starter.csv', 'w')
try:
    f.write("j,v_target,v1_measured,v2_measured,time\n")
    vdac.write(0)
    print("Discharging...")
    time.sleep(2)
    
    t0 = time.ticks_ms()
    for i in range(0, 100, 5):
        time.sleep(0.4)
        t_sec = time.ticks_diff(time.ticks_ms(), t0) / 1000.0
        
        vdac.write(i)
        
        v_target = i * vfactor_dac
        v1 = read_avg_voltage(adc1)
        v2 = read_avg_voltage(adc2)
        
        # Now the measured values are naturally calibrated!
        sval = f"{i},{v_target:.3f},{v1:.3f},{v2:.3f},{t_sec:.3f}"
        f.write(sval + "\n")
        print(sval)
finally:
    vdac.write(0)
    f.close()
    print("Done.")