from machine import I2C, Pin, Timer
import time
import math
import sys

# ---- 1. HARDWARE & SENSOR CLASS ----

class TCA9548A:
    def __init__(self, i2c, addr=0x70):
        self.i2c = i2c
        self.addr = addr

    def select_channel(self, channel):
        if channel < 0 or channel > 7:
            raise ValueError("Channel must be 0-7")
        self.i2c.writeto(self.addr, bytes([1 << channel]))

class GY521:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self.i2c.writeto_mem(self.addr, 0x6B, b'\x80') # Reset
        time.sleep(0.1)
        self.i2c.writeto_mem(self.addr, 0x6B, b'\x00') # Wake
        self.i2c.writeto_mem(self.addr, 0x1C, b'\x00') # +/- 2g range
        self.i2c.writeto_mem(self.addr, 0x1A, b'\x02') # DLPF 94Hz Filter
        self.i2c.writeto_mem(self.addr, 0x19, b'\x00') # Sample Rate Divisor 0

    def get_3axis_vector(self):
        try:
            raw = self.i2c.readfrom_mem(self.addr, 0x3B, 6)

            def combine(high, low):
                val = (high << 8) | low
                return val if val < 32768 else val - 65536

            x = combine(raw[0], raw[1]) / 16384.0
            y = combine(raw[2], raw[3]) / 16384.0
            z = combine(raw[4], raw[5]) / 16384.0

            magnitude_vector = math.sqrt(x**2 + y**2 + z**2)
            return magnitude_vector
        except Exception:
            return 1.0


# ---- 2. FFT PROCESSING CLASS ----

class FFTProcessor:
    def __init__(self, num_samples=128):
        self.num_samples = num_samples
        self.window = [0.5 * (1 - math.cos(2 * math.pi * i / (num_samples - 1))) for i in range(num_samples)]

    def _in_place_fft(self, real, imag):
        n = len(real)
        if n <= 1: return
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

        for i in range(1, self.num_samples // 2):
            magnitude = math.sqrt(real[i]**2 + imag[i]**2)
            frequency = (i * actual_fs) / self.num_samples

            if magnitude > max_mag:
                max_mag = magnitude
                dominant_freq = frequency

        if max_mag < NOISE_THRESHOLD:
            return 0.0, 0.0

        return dominant_freq, max_mag


# Pre-allocate buffers at module level for performance improvement
SENSOR_BUFFER = [0.0] * 128
FFT_REAL_BUFFER = [0.0] * 128
FFT_IMAG_BUFFER = [0.0] * 128

# ---- 3. MAIN EXECUTION ----

# Data Collection Configuration
LABEL = "healthy"  # Manually change to "tremor" when you want to simulate shaking!

led = Pin(2, Pin.OUT)
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
mux = TCA9548A(i2c)  # TCA9548A multiplexer at address 0x70

try:
    # Initialize 4 IMUs on different multiplexer channels
    sensors = []
    for channel in range(4):
        mux.select_channel(channel)
        sensor = GY521(i2c)
        sensors.append(sensor)
    print("4 IMUs initialized on TCA9548A multiplexer!")
except Exception as e:
    print("Connection Failed:", e)
    sys.exit()

SAMPLES = 128
processor = FFTProcessor(num_samples=SAMPLES)
SAMPLE_INTERVAL_US = 20000  # 20ms = Stable 50 Hz Sample rate

# Timer-based sampling state - store samples from all 4 sensors
# Format: [imu0_x1, imu0_y1, imu0_z1, imu1_x1, imu1_y1, imu1_z1, ...] for each sample
sample_buffer = [0.0] * (128 * 4 * 3)  # 128 samples * 4 sensors * 3 axes
sample_index = 0
first_sample_time = None
last_sample_time = None
buffer_ready = False

def sample_callback(t):
    global sample_index, first_sample_time, last_sample_time, buffer_ready
    # Get samples from all 4 IMUs
    imu_samples = []
    for channel in range(4):
        mux.select_channel(channel)
        sample = sensors[channel].get_3axis_vector()
        imu_samples.append(sample)

    # Store 3-axis data for each IMU (we're storing magnitude only for now)
    # In future, we could store x,y,z separately for each IMU
    base_idx = sample_index * 12  # 4 sensors * 3 axes each
    for i in range(4):
        sample_buffer[base_idx + i*3] = imu_samples[i]  # x
        sample_buffer[base_idx + i*3 + 1] = imu_samples[i]  # y (same for magnitude approach)
        sample_buffer[base_idx + i*3 + 2] = imu_samples[i]  # z (same for magnitude approach)

    now = time.ticks_us()
    if sample_index == 0:
        first_sample_time = now
    last_sample_time = now
    sample_index += 1
    if sample_index >= SAMPLES:
        buffer_ready = True
        sample_index = 0  # Reset for next buffer (will overwrite)

# Initialize timer for periodic sampling
try:
    timer = Timer(0)
    timer.init(period=SAMPLE_INTERVAL_US // 1000, mode=Timer.PERIODIC, callback=sample_callback)
except Exception as e:
    print("Timer init failed:", e)
    sys.exit()

try:
    while True:
        if buffer_ready:
            # Process the filled buffer
            buffer_ready = False
            # Calculate actual sampling frequency from first and last sample timestamps
            if first_sample_time is not None and last_sample_time is not None:
                total_time_us = time.ticks_diff(last_sample_time, first_sample_time)
                if total_time_us > 0:
                    actual_fs = SAMPLES / (total_time_us / 1000000.0)
                else:
                    actual_fs = SAMPLES / (SAMPLE_INTERVAL_US / 1000000.0)  # fallback
            else:
                actual_fs = SAMPLES / (SAMPLE_INTERVAL_US / 1000000.0)  # fallback

            # Use pre-allocated FFT buffers for first IMU (for now)
            # TODO: Process all 4 IMUs separately or fuse data
            for i in range(SAMPLES):
                # Extract data for IMU 0 (first sensor)
                base_idx = i * 12  # 4 sensors * 3 axes
                imu0_mag = sample_buffer[base_idx]  # Using x-axis as magnitude placeholder
                FFT_REAL_BUFFER[i] = (imu0_mag - sum(sample_buffer[::12][:SAMPLES])/SAMPLES) * processor.window[i]
                FFT_IMAG_BUFFER[i] = 0.0

            processor._in_place_fft(FFT_REAL_BUFFER, FFT_IMAG_BUFFER)

            max_mag = 0.0
            dominant_freq = 0.0
            NOISE_THRESHOLD = 0.35

            for i in range(1, SAMPLES // 2):
                magnitude = math.sqrt(FFT_REAL_BUFFER[i]**2 + FFT_IMAG_BUFFER[i]**2)
                frequency = (i * actual_fs) / SAMPLES

                if magnitude > max_mag:
                    max_mag = magnitude
                    dominant_freq = frequency

            if max_mag < NOISE_THRESHOLD:
                freq, mag = 0.0, 0.0
            else:
                freq, mag = dominant_freq, max_mag

            led.value(1 if mag > 1.2 else 0)

            # FORMATTED FOR CSV LOGGING:
            # For now, output data from first IMU only to maintain compatibility
            # Format: LABEL,imu0_sample1,imu0_sample2,...,imu0_sample128
            raw_data_string = ",".join(["{:.4f}".format(sample_buffer[i*12]) for i in range(SAMPLES)])
            print(f"{LABEL},{raw_data_string}")

            # Reset timing for next buffer
            first_sample_time = None
            last_sample_time = None

        time.sleep(0.001)  # Short sleep to prevent busy-wait in main loop

except KeyboardInterrupt:
    timer.deinit()
    led.value(0)
    print("\nLoop stopped.")