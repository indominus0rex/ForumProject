from machine import I2C, Pin
import time
import math
import sys

# ---- 1. HARDWARE & SENSOR CLASS ----

class GY521:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self.i2c.writeto_mem(self.addr, 0x6B, b'\x00')

    def get_values(self):
        try:
            raw = self.i2c.readfrom_mem(self.addr, 0x3B, 6)
            
            def combine(high, low):
                val = (high << 8) | low
                return val if val < 32768 else val - 65536

            x = combine(raw[0], raw[1]) / 16384.0
            y = combine(raw[2], raw[3]) / 16384.0
            z = combine(raw[4], raw[5]) / 16384.0
            return {"x": x, "y": y, "z": z}
        except Exception:
            return {"x": 0.0, "y": 0.0, "z": 0.0}


# ---- 2. FFT PROCESSING CLASS ----

class FFTProcessor:
    def __init__(self, num_samples=64):
        self.num_samples = num_samples

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
        """ Processes FFT dynamically using the true measured sampling frequency """
        real = list(signal_data)
        imag = [0.0] * self.num_samples
        
        self._in_place_fft(real, imag)
        
        max_mag = 0.0
        dominant_freq = 0.0
        
        # Noise floor filter: ignore weak ambient electrical noise
        NOISE_THRESHOLD = 0.5 
        
        for i in range(self.num_samples // 2):
            if i == 0: 
                continue  # Skip DC Offset (Gravity)
                
            magnitude = math.sqrt(real[i]**2 + imag[i]**2)
            frequency = (i * actual_fs) / self.num_samples
            
            if magnitude > max_mag:
                max_mag = magnitude
                dominant_freq = frequency
                
        # If the vibrations are tinier than the noise threshold, report 0 Hz
        if max_mag < NOISE_THRESHOLD:
            return 0.0, 0.0
            
        return dominant_freq, max_mag


# ---- 3. MAIN EXECUTION ----

led = Pin(2, Pin.OUT)
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

try:
    sensor = GY521(i2c)
    print("GY-521 Connected!")
except Exception as e:
    print("Connection Failed:", e)
    sys.exit()

# Stable Configuration Settings
DELAY = 0.01   # 10ms delay (~70-80 Hz actual sampling rate including execution overhead)
SAMPLES = 64   
STRIDE = 16    # Processes slightly less frequently to keep calculations accurate

processor = FFTProcessor(num_samples=SAMPLES)
x_buffer = []  
sample_counter = 0

# Timestamps to dynamically measure actual sampling frequency
timestamps = [] 

print("Starting streaming real-time monitoring... Press Ctrl+C to stop.")

try:
    while True:
        t_start = time.ticks_ms()
        data = sensor.get_values()
        
        if abs(data['x']) > 0.5 or abs(data['y']) > 0.5:
            led.value(1)
        else:
            led.value(0)
            
        x_buffer.append(data['x'])
        timestamps.append(t_start)
        sample_counter += 1
        
        if len(x_buffer) > SAMPLES:
            x_buffer.pop(0)
            timestamps.pop(0)
            
        if len(x_buffer) == SAMPLES and sample_counter >= STRIDE:
            # Dynamically calculate true sample frequency (Fs = total samples / total time)
            total_duration_ms = time.ticks_diff(timestamps[-1], timestamps[0])
            if total_duration_ms > 0:
                actual_fs = (SAMPLES - 1) / (total_duration_ms / 1000.0)
                
                freq, mag = processor.process_data(x_buffer, actual_fs)
                if mag > 0:
                    print("Freq: {:.2f} Hz | Mag: {:.2f} (True Fs: {:.1f} Hz)".format(freq, mag, actual_fs))
                else:
                    print("Freq: 0.00 Hz | No significant vibration")
                    
            sample_counter = 0  
            
        time.sleep(DELAY)

except KeyboardInterrupt:
    led.value(0)
    print("\nLoop stopped by user.")