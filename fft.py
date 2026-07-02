from machine import I2C, Pin
import time
import math
import sys

# ---- 1. HARDWARE & SENSOR CLASS ----

class GY521:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self.i2c.writeto_mem(self.addr, 0x6B, b'\x80') # Reset
        time.sleep(0.1)
        self.i2c.writeto_mem(self.addr, 0x6B, b'\x00') # Wake
        self.i2c.writeto_mem(self.addr, 0x1C, b'\x00') # +/- 2g
        self.i2c.writeto_mem(self.addr, 0x1A, b'\x02') # DLPF 94Hz
        self.i2c.writeto_mem(self.addr, 0x19, b'\x00') # Divisor 0

    def get_values(self):
        try:
            raw = self.i2c.readfrom_mem(self.addr, 0x3B, 2)
            val = (raw[0] << 8) | raw[1]
            x = val if val < 32768 else val - 65536
            return x / 16384.0
        except Exception:
            return 0.0


# ---- 2. FFT PROCESSING CLASS ----

class FFTProcessor:
    def __init__(self, num_samples=128): # Upgraded to 128
        self.num_samples = num_samples
        self.window = [0.5 * (1 - math.cos(2 * math.pi * i / (num_samples - 1))) for i in range(num_samples)]

    def _in_place_fft(self, real, imag):
        n = len(real)
        if n <= 1:
            return

        j = 0
        for i in range(n):
            if i < j:
                real[i], real[j] = real[j], real[i]
                imag[i], imag[j] = imag[j], imag[i]
            m = n >> 1
            while m >= 1 and j >= m:
                j -= m
                m >>= 1
            j += m

        size = 2
        while size <= n:
            half_size = size // 2
            for i in range(0, n, size):
                for k in range(half_size):
                    angle = -2 * math.pi * k / size
                    c = math.cos(angle)
                    s = math.sin(angle)
                    
                    idx_even = i + k
                    idx_odd = i + k + half_size
                    
                    r_odd = real[idx_odd]
                    i_odd = imag[idx_odd]
                    
                    t_real = r_odd * c - i_odd * s
                    t_imag = r_odd * s + i_odd * c
                    
                    real[idx_odd] = real[idx_even] - t_real
                    imag[idx_odd] = imag[idx_even] - t_imag
                    real[idx_even] += t_real
                    imag[idx_even] += t_imag
            size *= 2

    def process_data(self, signal_data, actual_fs):
        mean_val = sum(signal_data) / len(signal_data)
        real = [(signal_data[i] - mean_val) * self.window[i] for i in range(self.num_samples)]
        imag = [0.0] * self.num_samples
        
        self._in_place_fft(real, imag)
        
        max_mag = 0.0
        dominant_freq = 0.0
        NOISE_THRESHOLD = 0.35 
        
        start_bin = 1
        
        for i in range(start_bin, self.num_samples // 2):
            magnitude = math.sqrt(real[i]**2 + imag[i]**2)
            frequency = (i * actual_fs) / self.num_samples
            
            # Notch out remaining 60Hz power lines just in case
            if 57.0 <= frequency <= 63.0:
                continue
                
            if magnitude > max_mag:
                max_mag = magnitude
                dominant_freq = frequency
                
        if max_mag < NOISE_THRESHOLD:
            return 0.0, 0.0
            
        return dominant_freq, max_mag


# ---- 3. MAIN EXECUTION ----

led = Pin(2, Pin.OUT)
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)

try:
    sensor = GY521(i2c)
    print("GY-521 High-Resolution Mode Initialized!")
except Exception as e:
    print("Connection Failed:", e)
    sys.exit()

SAMPLES = 128  # Double the window sample depth
processor = FFTProcessor(num_samples=SAMPLES)
SAMPLE_INTERVAL_US = 20000  # Stays at 200 Hz sampling rate

try:
    while True:
        x_buffer = [0.0] * SAMPLES
        get_values = sensor.get_values
        
        t_start = time.ticks_us()
        for i in range(SAMPLES):
            t_sample_start = time.ticks_us()
            x_buffer[i] = get_values()
            
            while time.ticks_diff(time.ticks_us(), t_sample_start) < SAMPLE_INTERVAL_US:
                pass
        t_end = time.ticks_us()
        
        total_duration_seconds = time.ticks_diff(t_end, t_start) / 1000000.0
        
        if total_duration_seconds > 0:
            actual_fs = SAMPLES / total_duration_seconds
            freq, mag = processor.process_data(x_buffer, actual_fs)
            
            led.value(1 if mag > 1.2 else 0)
            
            if mag > 0:
                print("Vibration Freq: {:.2f} Hz | Strength: {:.2f} (Loop speed: {:.1f} Hz)".format(freq, mag, actual_fs))
            else:
                print("Vibration Freq: 0.00 Hz | Stable")
                
        time.sleep(0.05)

except KeyboardInterrupt:
    led.value(0)
    print("\nLoop stopped.")