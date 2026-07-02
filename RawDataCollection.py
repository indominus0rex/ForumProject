from machine import I2C, Pin
import time

# 1. Setup Pins
led = Pin(2, Pin.OUT)
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

class GY521:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        
        # ลบ xVal, yVal, zVal แบบเก่าออกเพราะเราเซฟลงไฟล์โดยตรงแทนแล้ว เพื่อประหยัด RAM
        self.i2c.writeto_mem(self.addr, 0x6B, b'\x00')

    def get_values(self):
        raw = self.i2c.readfrom_mem(self.addr, 0x3B, 6)
        
        def combine(high, low):
            val = (high << 8) | low
            return val if val < 32768 else val - 65536

        x = combine(raw[0], raw[1]) / 16384.0
        y = combine(raw[2], raw[3]) / 16384.0
        z = combine(raw[4], raw[5]) / 16384.0
        
        return {
            "x": x,
            "y": y,
            "z": z
        }
    
# Initialize sensor
try:
    sensor = GY521(i2c)
    print("GY-521 (MPU6050) Connected!")
except Exception as e:
    print("Connection Failed. Check SDA/SCL wiring.")
    print("Error details:", e)
    import sys
    sys.exit()

# ---- 2. เริ่มกระบวนการบันทึกข้อมูลลงไฟล์แบบ Overwrite ("w") ----
print("Starting data log... (100 samples)")
with open("data.txt", "w") as f:
    
    # วิ่งวนลูป 100 รอบ (ประมาณ 10 วินาที) สามารถเปลี่ยนตัวเลขเพิ่ม/ลดได้ตามต้องการ
    for i in range(100):
        data = sensor.get_values()
        
        # ส่งค่าไปยัง Thonny Plotter (แสดงผลสดเป็นกราฟเส้น)
        print((data['x'], data['y'], data['z']))
        
        # เขียนข้อมูลลงไฟล์ data.txt ใน ESP32
        f.write("{},{},{}\n".format(data['x'], data['y'], data['z']))	
        
        # ระบบไฟแจ้งเตือนความสั่น (Motion Alarm)
        if abs(data['x']) > 0.5 or abs(data['y']) > 0.5:
            led.value(1) 
        else:
            led.value(0) 
            
        time.sleep(0.1) # เก็บบันทึกข้อมูลทุกๆ 0.1 วินาที

# ปิดไฟและบันทึกเสร็จสิ้น
led.value(0)
print("Data log finished! Now open the Files tab and download 'data.txt'.")