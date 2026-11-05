---
date: 2025-09-02
type: research
status: success
topic: IMU + ESP32 — Hardware, Firmware, Signal Processing & Wearable Deployment
sources: [web_search, web_extract]
---

# Research Handoff: IMU + ESP32 for Wearable Tremor Monitoring

## Research Question
What are the current best practices for integrating IMU sensors with ESP32 microcontrollers for wearable tremor monitoring, including hardware selection, firmware configuration, signal processing, power optimization, and sensor fusion?

## Key Findings

### 1. IMU Sensor Selection

**Modern IMU Comparison for Tremor Monitoring**

| IMU | Interface | Accel Range | Gyro Range | Key Features | Status |
|-----|-----------|-------------|------------|--------------|--------|
| **ISM330DHCX** | I2C/SPI | ±2/±4/±8/±16g | ±125/±250/±500/±1000/±2000dps | Low noise, FIFO, embedded ML core | ✅ Recommended |
| **BMI270** | I2C/SPI | ±2/±4/±8/±16g | ±125/±250/±500/±1000/±2000dps | Ultra-low power, CRT auto-calibration | ✅ Recommended |
| **BMI160** | I2C/SPI | ±2/±4/±8/±16g | ±125/±250/±500/±1000/±2000dps | Low power, compact, motion detection | ✅ Good |
| **ICM-42688-P** | I2C/SPI | ±2/±4/±8/±16g | ±125/±250/±500/±1000/±2000dps | Low noise, FIFO, ODR up to 32kHz | ✅ Good |
| **LSM6DSO** | I2C/SPI | ±2/±4/±8/±16g | ±125/±250/±500/±1000/±2000dps | Low power, finite state machine | ✅ Good |
| **LSM6DSV** | I2C/SPI | ±2/±4/±8/±16g | ±125/±250/±500/±1000/±2000dps | 6-axis with QWIIC, low noise | ✅ Good |
| **MPU-6050** | I2C | ±2/±4/±8/±16g | ±250/±500/±1000/±2000dps | Obsolete but widely available | ⚠️ Legacy |
| **MPU-9250** | I2C/SPI | ±2/±4/±8/±16g | ±250/±500/±1000/±2000dps | 9-axis (accel+gyro+mag) | ⚠️ Legacy |
| **BNO085** | I2C | ±2/±4/±8/±16g | ±125/±250/±500/±1000/±2000dps | Integrated AR/VR stabilization, DMP | ✅ Best fusion |

**Recommendation for Tremor Project**
- **Primary**: ISM330DHCX (already used in project) — low noise, FIFO, embedded ML core
- **Alternative**: BMI270 — ultra-low power, good for battery-powered wearables
- **For 9-axis**: BNO085 — integrated sensor fusion, ARVR stabilization
- **Avoid**: MPU-6050/9250 — discontinued, counterfeit issues common

### 2. ESP32 + IMU Hardware Integration

**I2C Wiring (Default)**
```
IMU Pin  →  ESP32 Pin
VCC      →  3.3V
GND      →  GND
SCL      →  GPIO22 (default I2C clock)
SDA      →  GPIO21 (default I2C data)
SA0      →  GND (address 0x68) or 3.3V (address 0x69)
```

**SPI Wiring (Higher Speed)**
```
IMU Pin  →  ESP32 Pin
VCC      →  3.3V
GND      →  GND
SCL/SCK  →  GPIO18 (VSPI SCK)
SDA/MOSI →  GPIO23 (VSPI MOSI)
SDO/MISO →  GPIO19 (VSPI MISO)
CS       →  GPIO5 (VSPI CS)
```

**Key Hardware Notes**
- ESP32 operates at 3.3V logic — do NOT use 5V on GPIO pins
- I2C requires pull-up resistors (typically 4.7kΩ-10kΩ to 3.3V) — many breakout boards include them
- SPI is faster (up to 5 MHz vs 400 kHz I2C) — preferred for high sample rates
- ESP32 has two I2C ports (Wire and Wire1) — can use different pins
- For tremor monitoring: I2C at 400 kHz is sufficient for 100-200 Hz sample rates

### 3. Firmware Configuration

**Sample Rate & Range Settings for Tremor**
```cpp
// Tremor frequency range: 3-12 Hz (PD: 4-6 Hz, ET: 4-12 Hz)
// Nyquist: sample at >24 Hz, recommended 100-200 Hz
// ISM330DHCX configuration:
IMU.setAccelODR(ODR_104_HZ);    // 104 Hz output data rate
IMU.setAccelFS(2);                // ±2g for maximum resolution of low-amplitude tremors
IMU.setGyroODR(ODR_104_HZ);      // 104 Hz gyro ODR
IMU.setGyroFS(500);              // ±500 dps for tremor
IMU.setBlockDataUpdate(true);    // Enable BDU to prevent data corruption
```

**FIFO Usage (Critical for Power Efficiency)**
```cpp
// Enable FIFO to batch readings — reduces MCU wake time
IMU.enableFifo(true);
IMU.setFifoThreshold(100);  // Interrupt when 100 samples in FIFO

// In main loop:
if (fifoInterrupt) {
    IMU.readFifo(buffer, 100);  // Read 100 samples at once
    processBatch(buffer, 100);
}
```

**Interrupt-Driven Data Ready**
```cpp
// Configure INT1 pin for data-ready interrupt
IMU.enableInterrupt(INT1_PIN, INT_DATA_READY);

// Attach ESP32 interrupt
attachInterrupt(GPIO_NUM_4, imuDataReadyISR, RISING);

void IRAM_ATTR imuDataReadyISR() {
    dataReady = true;
}
```

### 4. Signal Processing Pipeline

**Raw Data Conversion**
```cpp
// ISM330DHCX raw to physical units
// Accel ±2g: sensitivity = 0.061 mg/LSB
// Gyro ±500dps: sensitivity = 17.50 mdps/LSB

float accelToG(int16_t raw) {
    return raw * 0.061f / 1000.0f;  // Convert to g
}

float gyroToDps(int16_t raw) {
    return raw * 17.50f / 1000.0f;  // Convert to degrees/sec
}

float accelToMs2(int16_t raw) {
    return raw * 0.061f * 9.81f / 1000.0f;  // Convert to m/s²
}
```

**Feature Extraction (Per Window)**
```cpp
// Window: 1000ms at 100 Hz = 100 samples
// Features per axis: RMS, peak frequency, spectral entropy, zero-crossing rate

typedef struct {
    float rms_x, rms_y, rms_z;
    float peak_freq_x, peak_freq_y, peak_freq_z;
    float spectral_entropy;
    float zero_crossing_rate;
    float crest_factor;
    float jerk_metric;
} ImuFeatures;

float computeRMS(float* data, int n) {
    float sum = 0;
    for (int i = 0; i < n; i++) sum += data[i] * data[i];
    return sqrtf(sum / n);
}

float computePeakFrequency(float* data, int n, float sampleRate) {
    // FFT using esp-dsps library or similar
    // Return frequency with maximum magnitude
}

float computeSpectralEntropy(float* fftMagnitude, int n) {
    float total = 0;
    for (int i = 0; i < n/2; i++) total += fftMagnitude[i];
    float entropy = 0;
    for (int i = 0; i < n/2; i++) {
        float p = fftMagnitude[i] / total;
        if (p > 0) entropy -= p * log2f(p);
    }
    return entropy;
}
```

**Calibration Procedure**
```cpp
// 6-side accelerometer calibration (from SlimeVR firmware)
// 1. Place device on flat surface, wait 5 seconds
// 2. Rotate through 6 orientations (cube sides)
// 3. Hold each orientation still for 3 seconds
// 4. Use gravity as reference to compute offsets and scale factors

void calibrateAccel() {
    float min[3] = {999, 999, 999};
    float max[3] = {-999, -999, -999};
    
    for (int side = 0; side < 6; side++) {
        // Prompt user to place device in orientation
        waitForStillness();
        
        // Collect samples
        for (int i = 0; i < 100; i++) {
            float ax, ay, az;
            readAccel(&ax, &ay, &az);
            min[0] = fminf(min[0], ax); max[0] = fmaxf(max[0], ax);
            min[1] = fminf(min[1], ay); max[1] = fmaxf(max[1], ay);
            min[2] = fminf(min[2], az); max[2] = fmaxf(max[2], az);
            delay(10);
        }
    }
    
    // Compute offsets and scale factors
    for (int i = 0; i < 3; i++) {
        accel_offset[i] = (min[i] + max[i]) / 2.0f;
        accel_scale[i] = 2.0f / (max[i] - min[i]);
    }
}
```

### 5. Sensor Fusion for Tremor

**Complementary Filter (Simple, Effective)**
```cpp
// Combines gyro (fast dynamics) with accel (slow drift correction)
// alpha = 0.98: trust gyro 98%, accel 2%

class ComplementaryFilter {
    float alpha = 0.98f;
    float pitch = 0, roll = 0;
    
public:
    void update(float ax, float ay, float az, float gx, float gy, float dt) {
        // Accelerometer angles (low-frequency stable)
        float accel_pitch = atan2f(ay, sqrtf(ax*ax + az*az)) * 180.0f / M_PI;
        float accel_roll = atan2f(-ax, az) * 180.0f / M_PI;
        
        // Complementary filter
        pitch = alpha * (pitch + gx * dt) + (1.0f - alpha) * accel_pitch;
        roll = alpha * (roll + gy * dt) + (1.0f - alpha) * accel_roll;
    }
    
    float getPitch() { return pitch; }
    float getRoll() { return roll; }
};
```

**Kalman Filter (Optimal Estimation)**
```cpp
// 1D Kalman filter for single angle estimation
// State: [angle, gyro_bias]

class KalmanFilter1D {
    float Q_angle = 0.001f;   // Process noise (angle)
    float Q_bias = 0.003f;    // Process noise (bias)
    float R_measure = 0.03f;  // Measurement noise (accel)
    
    float angle = 0, bias = 0;
    float P[2][2] = {{0,0},{0,0}};
    
public:
    float update(float newAngle, float newRate, float dt) {
        // Predict
        float rate = newRate - bias;
        angle += dt * rate;
        
        // Predict covariance
        P[0][0] += dt * (dt * P[1][1] - P[0][1] - P[1][0] + Q_angle);
        P[0][1] -= dt * P[1][1];
        P[1][0] -= dt * P[1][1];
        P[1][1] += Q_bias * dt;
        
        // Update
        float y = newAngle - angle;  // Innovation
        float S = P[0][0] + R_measure;  // Innovation covariance
        float K[2];  // Kalman gain
        K[0] = P[0][0] / S;
        K[1] = P[1][0] / S;
        
        // Correct
        angle += K[0] * y;
        bias += K[1] * y;
        
        // Update covariance
        float P00_temp = P[0][0];
        float P01_temp = P[0][1];
        P[0][0] -= K[0] * P00_temp;
        P[0][1] -= K[0] * P01_temp;
        P[1][0] -= K[1] * P00_temp;
        P[1][1] -= K[1] * P01_temp;
        
        return angle;
    }
};
```

**Mahony AHRS (Quaternion-Based, No Gimbal Lock)**
```cpp
// Mahony AHRS — quaternion-based, no gimbal lock
// Better for 3D orientation tracking

class MahonyAHRS {
    float q0 = 1, q1 = 0, q2 = 0, q3 = 0;
    float Kp = 2.0f, Ki = 0.005f;
    float eInt[3] = {0, 0, 0};
    
public:
    void update(float gx, float gy, float gz, float ax, float ay, float az, float dt) {
        float recipNorm;
        float halfvx, halfvy, halfvz;
        float halfex, halfey, halfez;
        float qa, qb, qc;
        
        // Compute feedback only if accelerometer measurement valid
        if (!((ax == 0.0f) && (ay == 0.0f) && (az == 0.0f))) {
            // Normalize accelerometer measurement
            recipNorm = 1.0f / sqrtf(ax*ax + ay*ay + az*az);
            ax *= recipNorm;
            ay *= recipNorm;
            az *= recipNorm;
            
            // Estimated direction of gravity
            halfvx = q1 * q3 - q0 * q2;
            halfvy = q0 * q1 + q2 * q3;
            halfvz = q0 * q0 - 0.5f + q3 * q3;
            
            // Error is cross product between estimated and measured direction of gravity
            halfex = (ay * halfvz - az * halfvy);
            halfey = (az * halfvx - ax * halfvz);
            halfez = (ax * halfvy - ay * halfvx);
            
            // Compute and apply integral feedback if enabled
            if (Ki > 0.0f) {
                eInt[0] += Ki * halfex * dt;
                eInt[1] += Ki * halfey * dt;
                eInt[2] += Ki * halfez * dt;
                gx += eInt[0];
                gy += eInt[1];
                gz += eInt[2];
            }
            
            // Apply proportional feedback
            gx += Kp * halfex;
            gy += Kp * halfey;
            gz += Kp * halfez;
        }
        
        // Integrate rate of change of quaternion
        gx *= 0.5f * dt;
        gy *= 0.5f * dt;
        gz *= 0.5f * dt;
        qa = q0;
        qb = q1;
        qc = q2;
        q0 += (-qb * gx - qc * gy - q3 * gz);
        q1 += (qa * gx + qc * gz - q3 * gy);
        q2 += (qa * gy - qb * gz + q3 * gx);
        q3 += (qa * gz + qb * gy - qc * gx);
        
        // Normalize quaternion
        recipNorm = 1.0f / sqrtf(q0*q0 + q1*q1 + q2*q2 + q3*q3);
        q0 *= recipNorm;
        q1 *= recipNorm;
        q2 *= recipNorm;
        q3 *= recipNorm;
    }
};
```

### 6. Power Optimization for Wearables

**ESP32 Power Modes**
| Mode | Current | Use Case |
|------|---------|----------|
| Active (240 MHz) | ~20 mA | ML inference, BLE transmission |
| Active (80 MHz) | ~10 mA | Sensor polling, light processing |
| Modem Sleep | ~3 mA | CPU active, WiFi/BLE off |
| Light Sleep | ~0.8 mA | CPU paused, RTC active |
| Deep Sleep | ~10 µA | Wake on timer/IMU interrupt |

**Power Optimization Strategies**

1. **Reduce CPU frequency**: 80 MHz instead of 240 MHz saves ~50% power
2. **Use FIFO + batch processing**: Read 100 samples at once, process, then sleep
3. **Deep sleep between measurements**: Wake every 100ms, read FIFO, process, sleep
4. **Disable unused peripherals**: ADC, DAC, WiFi when not needed
5. **IMU low-power mode**: Use IMU's built-in low-power mode for accelerometer-only wake
6. **BLE instead of WiFi**: BLE consumes ~10 mA vs WiFi ~200 mA

**Power Budget Example (100 Hz sampling)**
```
Active (80 MHz, 10ms):     10 mA × 0.01s = 0.1 mAs
Deep Sleep (90ms):          0.01 mA × 0.09s = 0.0009 mAs
Average:                    ~10 mA

With 100 mAh battery: ~10 hours continuous
With FIFO batching (100 samples): ~45 hours (from MistyWest case study)
```

**Deep Sleep with IMU Wake**
```cpp
// Configure IMU to generate interrupt on motion
IMU.enableMotionInterrupt(threshold_mg = 50, duration_ms = 100);

// ESP32 deep sleep with external wake
esp_sleep_enable_ext0_wakeup(GPIO_NUM_4, 1);  // Wake on INT1 high

void loop() {
    // Read FIFO, process, transmit
    readAndProcessData();
    
    // Enter deep sleep
    esp_deep_sleep_start();
}
```

### 7. Communication Protocols

**BLE GATT for Tremor Data**
```cpp
// BLE service for IMU data streaming
// Service UUID: 0000180d-0000-1000-8000-00805f9b34fb
// Characteristic UUID: 00002a37-0000-1000-8000-00805f9b34fb

// Data packet format (20 bytes — fits in single BLE packet)
struct __attribute__((packed)) ImuPacket {
    uint32_t timestamp_ms;
    int16_t accel_x, accel_y, accel_z;  // 6 bytes
    int16_t gyro_x, gyro_y, gyro_z;      // 6 bytes
    uint8_t flags;                        // 1 byte (data ready, etc.)
    uint8_t battery_pct;                  // 1 byte
};
// Total: 16 bytes — fits in BLE MTU
```

**WiFi/UDP for High-Bandwidth Streaming**
```cpp
// UDP streaming for raw data to host computer
// Use only when high sample rate needed (>200 Hz)

void sendImuDataUDP(float* accel, float* gyro) {
    WiFiUDP udp;
    udp.beginPacket(hostIP, 8080);
    udp.write((uint8_t*)accel, 3 * sizeof(float));
    udp.write((uint8_t*)gyro, 3 * sizeof(float));
    udp.endPacket();
}
```

### 8. Recommended Libraries

| Library | Purpose | Notes |
|---------|---------|-------|
| **SparkFun ISM330DHCX** | ISM330DHCX driver | Arduino + ESP32 compatible |
| **Bosch BMI270-Sensor-API** | BMI270 driver | Official, low-level |
| **MPU6050 by Electronic Cats** | MPU6050 driver | Easy Arduino integration |
| **esp-dsps** | FFT/DSP | ESP32 optimized DSP library |
| **ESP32 BLE Arduino** | BLE stack | NimBLE based |
| **FreeRTOS** | Task scheduling | Built into ESP32 Arduino |
| **SlimeVR Firmware** | Reference implementation | Multi-IMU, sensor fusion, calibration |
| **esp-gyrologger** | GyroFlow data logger | BMI270/BMI160/MPU6050 support |

### 9. Reference Firmware Architecture

**Multi-Core Task Design (ESP32)**
```
Core 1 (Protocol CPU):
  - Task 1: IMU reading (Priority 5, 100 Hz)
    → Read FIFO, extract features, post to queue
  - Task 2: Sensor fusion (Priority 4)
    → Complementary/Kalman filter, post orientation

Core 0 (Application CPU):
  - Task 3: BLE transmission (Priority 3)
    → Send data packets to host
  - Task 4: Power management (Priority 2)
    → Enter deep sleep between measurements
  - Task 5: Configuration (Priority 1)
    → Handle host commands, update settings
```

**Complete Firmware Skeleton**
```cpp
#include <Wire.h>
#include <SparkFun_ISM330DHCX.h>
#include <BLEDevice.h>

// IMU
SparkFun_ISM330DHCX imu;
sfe_ism_data_t accelData, gyroData;

// BLE
BLEServer* pServer;
BLECharacteristic* pImuChar;
bool deviceConnected = false;

// FreeRTOS handles
TaskHandle_t imuTaskHandle = NULL;
QueueHandle_t imuQueue;

// Data packet
struct ImuPacket {
    uint32_t timestamp;
    float accel[3];
    float gyro[3];
    uint8_t battery;
};

void setup() {
    Serial.begin(115200);
    
    // Initialize IMU
    Wire.begin(21, 22);
    while (!imu.begin()) {
        Serial.println("IMU not found!");
        delay(1000);
    }
    imu.setAccelODR(SFE_ODR_104_HZ);
    imu.setAccelFS(2);
    imu.setGyroODR(SFE_ODR_104_HZ);
    imu.setGyroFS(500);
    imu.enableBlockDataUpdate(true);
    
    // Initialize BLE
    BLEDevice::init("TremorMonitor");
    pServer = BLEDevice::createServer();
    BLEService* pService = pServer->createService("180d");
    pImuChar = pService->createCharacteristic(
        "2a37",
        BLECharacteristic::PROPERTY_READ |
        BLECharacteristic::PROPERTY_NOTIFY
    );
    pService->start();
    BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->start();
    
    // Create queue
    imuQueue = xQueueCreate(10, sizeof(ImuPacket));
    
    // Create tasks
    xTaskCreatePinnedToCore(imuTask, "IMU", 4096, NULL, 5, &imuTaskHandle, 1);
    xTaskCreatePinnedToCore(bleTask, "BLE", 4096, NULL, 3, NULL, 0);
}

void imuTask(void* parameter) {
    ImuPacket packet;
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(10);  // 100 Hz
    
    while (true) {
        vTaskDelayUntil(&xLastWakeTime, xFrequency);
        
        if (imu.checkStatus()) {
            imu.getAllRawAccel(&accelData);
            imu.getAllRawGyro(&gyroData);
            
            packet.timestamp = millis();
            packet.accel[0] = accelData.xData * 0.061f / 1000.0f;
            packet.accel[1] = accelData.yData * 0.061f / 1000.0f;
            packet.accel[2] = accelData.zData * 0.061f / 1000.0f;
            packet.gyro[0] = gyroData.xData * 17.50f / 1000.0f;
            packet.gyro[1] = gyroData.yData * 17.50f / 1000.0f;
            packet.gyro[2] = gyroData.zData * 17.50f / 1000.0f;
            packet.battery = readBattery();
            
            xQueueSend(imuQueue, &packet, 0);
        }
    }
}

void bleTask(void* parameter) {
    ImuPacket packet;
    
    while (true) {
        if (xQueueReceive(imuQueue, &packet, portMAX_DELAY)) {
            if (deviceConnected) {
                pImuChar->setValue((uint8_t*)&packet, sizeof(packet));
                pImuChar->notify();
            }
        }
    }
}

void loop() {
    // Empty — all work in tasks
    vTaskDelay(pdMS_TO_TICKS(1000));
}
```

## Recommendations

1. **Use ISM330DHCX or BMI270** — both have low noise, FIFO, and embedded processing. Avoid obsolete MPU series.

2. **Sample at 100-200 Hz** — captures tremor frequencies (3-12 Hz) with overhead for filtering. Use FIFO to batch readings.

3. **Implement 6-side calibration** — critical for accurate accelerometer readings. Store offsets in ESP32's NVS flash.

4. **Use complementary filter for tremor** — simple, effective, low CPU. Use Mahony/quaternion if full 3D orientation needed.

5. **Optimize power with FIFO + deep sleep** — read 100 samples, process, sleep. Target <2 mA average for multi-day battery life.

6. **Use BLE for wearable** — WiFi is too power-hungry. BLE 5.0 with 20-byte packets at 50 Hz is sufficient.

7. **Leverage ESP32 dual-core** — Core 1 for IMU/sensor fusion, Core 0 for BLE/power management.

8. **Use SlimeVR firmware as reference** — production-quality multi-IMU firmware with calibration, sensor fusion, and BLE streaming.

## Potential Pitfalls

- **Counterfeit IMUs**: MPU-6050/9250 are discontinued — high counterfeit rate. Buy from reputable suppliers (Adafruit, SparkFun, DigiKey).

- **I2C bus conflicts**: ESP32 has two I2C ports. Use `Wire1` with different pins if needed. Always scan bus first.

- **No pull-up resistors**: I2C requires 4.7kΩ-10kΩ pull-ups. Many breakouts include them; verify with multimeter.

- **FIFO overflow**: If read rate < ODR, FIFO overflows. Use interrupt pin or ensure read within 1/ODR seconds.

- **Gyro drift**: Uncorrected gyro integration drifts ~1°/min. Always use sensor fusion (complementary/Kalman).

- **Power supply noise**: Switching regulators add noise to IMU readings. Use LDO for analog supply if possible.

- **Mechanical coupling**: Vibration from battery/motor couples into IMU. Use mechanical isolation (foam, rubber mounts).

- **Temperature drift**: IMU sensitivity changes with temperature. BMI270 has built-in CRT compensation — enable it.

## Sources

1. [ESP32 MPU-6050 Guide (Random Nerd Tutorials)](https://randomnerdtutorials.com/esp32-mpu-6050-accelerometer-gyroscope-arduino/)
2. [ESP32 with BMI160 (How2Electronics)](https://how2electronics.com/esp32-with-bmi160-accelerometer-gyroscope-sensor/)
3. [SlimeVR Tracker ESP Firmware (GitHub)](https://github.com/SlimeVR/SlimeVR-Tracker-ESP)
4. [esp-gyrologger (GitHub)](https://github.com/VladimirP1/esp-gyrologger)
5. [ESP32 Sensor Fusion (Zbotic)](https://zbotic.in/esp32-sensor-fusion-combine-imu-baro-and-gps-data/)
6. [Robot IMU Sensor Fusion: Kalman Filter (Zbotic)](https://zbotic.in/robot-imu-sensor-fusion-kalman-filter-for-stable-orientation)
7. [IMU Sensor Fusion on ESP32 (GitHub)](https://github.com/Tofigh-Tevfik/imu_sensor_fusion)
8. [esp32-MPU-driver (GitHub)](https://github.com/natanaeljr/esp32-MPU-driver)
9. [Low Power Optimizations for Bluetooth Wearable (MistyWest)](https://www.mistywest.com/posts/low-power-optimizations-for-a-bluetooth-connected-wearable/)
10. [ESP32 Tips to save Power](https://esp32.com/viewtopic.php?t=4132)
11. [IoT on ESP32: Battery Life Optimization (ResearchGate)](https://www.researchgate.net/publication/369763204_IoT_on_an_ESP32_Optimization_Methods_Regarding_Battery_Life_and_Write_Speed_to_an_SD-Card)
12. [Adafruit ISM330DHCX](https://www.adafruit.com/product/4502)
13. [BNO085 for ESP32 (Mischianti)](https://mischianti.org/bno055-for-esp32-esp8266-and-arduino-gyroscope-high-rate-and-any-motion-interrupt-6/)
14. [ESP32 with Accelerometer Complete Tutorial](https://blog.usro.net/2025/04/esp32-with-accelerometer-complete-tutorial-for-beginners/)

## For Next Agent

This research directly supports the `firmware/` directory in this project. Key takeaways for implementation:

- **IMU**: ISM330DHCX is already selected — use SparkFun library, configure for 104 Hz, ±2g accel, ±500 dps gyro
- **Firmware**: Use FreeRTOS tasks — Core 1 for IMU reading (100 Hz), Core 0 for BLE transmission
- **Calibration**: Implement 6-side accelerometer calibration on first boot, store in NVS
- **Sensor fusion**: Start with complementary filter (alpha=0.8), upgrade to Mahony if needed
- **Power**: Use FIFO batching + deep sleep to achieve <2 mA average current
- **Communication**: BLE with 16-byte packets at 50 Hz (features) or 100 Hz (raw data)
- **Reference**: SlimeVR firmware is the best open-source reference for multi-IMU + BLE + calibration
- **Feature extraction**: Implement RMS, peak frequency, spectral entropy per axis in firmware or host
- **Data pipeline**: Raw IMU → FIFO → batch read → feature extraction → BLE → host → ML model
