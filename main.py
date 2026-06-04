from machine import I2C, Pin
import time
import matplotlib

matplotlib.use('TkAgg')

import matplotlib.pyplot as plt

# 1. Setup Pins
# The blue LED on your WROOM board
led = Pin(2, Pin.OUT)
# I2C communication
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

class GY521:
    xVal : list
    yVal : list
    zVal : list
    
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        # Wake up the GY-521
        self.i2c.writeto_mem(self.addr, 0x6B, b'\x00')

    def get_values(self):
        # Read 6 bytes (Accel X, Y, Z)
        raw = self.i2c.readfrom_mem(self.addr, 0x3B, 6)
        
        def combine(high, low):
            val = (high << 8) | low
            return val if val < 32768 else val - 65536

        # Convert to 'g' units (assuming +/- 2g range)
        
        x = combine(raw[0], raw[1]) / 16384.0
        y = combine(raw[2], raw[3]) / 16384.0
        z = combine(raw[4], raw[5]) / 16384.0
        
        self.xVal.append(x)
        self.yVal.append(y)
        self.zVal.append(z)
        
        return {
            "x": x,
            "y": y,
            "z": z
        }
    
    def plotGraph(self):
        plt.plot(self.xVal, self.yVal)
        plt.plot(self.yVal, self.zVal)
        plt.plot(self.zVal, self.xVal)
        plt.title("Separate Window Plot")
    
# Initialize sensor
try:
    sensor = GY521(i2c)
    print("GY-521 (MPU6050) Connected!")
except:
    print("Connection Failed. Check SDA/SCL wiring.")
    import sys
    sys.exit()

# 3. Main Loop
while True:
    data = sensor.get_values()
    
    # Print the values to Thonny Shell
    print("X: {:.2f}g  Y: {:.2f}g  Z: {:.2f}g".format(data['x'], data['y'], data['z']))
    
    # MOTION ALARM:
    # If the sensor is tilted or moved (absolute value > 1.2g), turn on LED
    # (Note: Z-axis is normally 1.00g due to gravity)
    if abs(data['x']) > 0.5 or abs(data['y']) > 0.5:
        led.value(1) # LED ON
    else:
        led.value(0) # LED OFF
        
    time.sleep(0.1) # Check 10 times per second