# System Architecture Improvements

## Overview
This document outlines architectural improvements for the Parkinson's Tremor Monitoring System based on current codebase analysis and performance optimization research.

## Current Architecture Assessment

### Strengths
1. Clear separation between firmware (ESP32 MicroPython) and host-side analysis
2. Modular design with separate components for sensor, FFT, feature extraction, classification
3. Well-organized directory structure after reorganization
4. Data pipeline established for training and inference

### Areas for Improvement

## 1. Hardware Performance Optimizations

### I2C Communication
- **Current**: Single I2C bus at 400kHz for all sensors
- **Improvement**: Use ESP32's dual I2C controllers
  - I2C0 (GPIO22/21): MPU6050 sensors
  - I2C1 (GPIO23/19): Peripherals (LRA drivers, etc.)
- **Expected gain**: 2x reduction in sensor read latency

### Memory Management
- **Current**: Dynamic allocation in sampling loops
- **Improvement**: Pre-allocate buffers at startup
```python
# Pre-allocate at module level
SENSOR_BUFFER = bytearray(384)  # 128 samples × 3 axes
FFT_BUFFER = [0.0] * 128
OUTPUT_BUFFER = [0.0] * 384
```
- **Expected gain**: 30% reduction in memory fragmentation, more predictable performance

### FFT Optimization
- **Current**: Pure Python Cooley-Tukey with on-the-fly twiddle factor computation
- **Improvement**: Pre-compute twiddle factors, use fixed-point arithmetic
```python
# Pre-compute at initialization
WINDOW = [0.5 * (1 - math.cos(2 * math.pi * i / 127)) for i in range(128)]
TWIDDLE = [...]  # Pre-computed sine/cosine values
```
- **Expected gain**: 3-5x faster FFT processing

## 2. Power Consumption Reduction

### ESP32 Deep Sleep Integration
- Implement deep sleep between sampling windows
- Use RTC memory to preserve state across sleep cycles
- Wake via timer interrupt

### Adaptive Sampling
- Reduce sampling rate during low-activity periods
- Dynamic adjustment based on tremor detection confidence

## 3. Firmware Architecture Refinements

### Current Issue: Busy-wait loops
```python
while time.ticks_diff(time.ticks_us(), t_sample_start) < SAMPLE_INTERVAL_US:
    pass  # Wastes CPU cycles
```

### Proposed Solution: Timer-based sampling
```python
from machine import Timer

class SensorSampler:
    def __init__(self, sample_interval_us):
        self.timer = Timer(0)
        self.buffer = []
        self.timer.init(period=sample_interval_us // 1000, 
                       mode=Timer.PERIODIC, 
                       callback=self._sample_callback)
```

## 4. Multi-Sensor Support

### I2C Multiplexer Integration
- Currently designed for single sensor
- Need TCA9548A support for 4 IMUs
- Each IMU on separate channel, share I2C bus
- Address management: All IMUs at 0x68, multiplexer selects channel

### Sensor Fusion Architecture
- Need architecture for combining data from 4 IMUs
- Weighted average based on tremor sensitivity
- Joint-specific tremor localization

## 5. Host-Side Analysis Improvements

### Current Issues
- Manual CSV copying from Thonny shell
- No automated data validation
- Limited cross-validation in training pipeline

### Improvements
1. Automated CSV capture via serial protocol
2. Real-time data validation during capture
3. Stratified k-fold cross-validation for training
4. Feature importance analysis

## 6. Data Pipeline Enhancements

### Data Versioning
- Implement data versioning for training datasets
- Track data lineage from raw capture to model weights
- Automatic data quality checks

### Model Management
- Version control for trained models
- A/B testing framework for model comparison
- Automatic rollback on performance degradation

## Implementation Priority

1. **High**: I2C multiplexer support, memory pre-allocation
2. **Medium**: FFT optimization, timer-based sampling
3. **Low**: Deep sleep integration, automatic CSV capture

## Testing Strategy

1. Unit tests for each firmware module
2. Integration tests for multi-sensor setup
3. Performance benchmarks (latency, power, accuracy)
4. Real-world validation with Parkinson's patients

## Next Steps

1. Update firmware files with pre-allocation patterns
2. Add I2C multiplexer support to sensor driver
3. Implement timer-based sampling
4. Create automated testing framework
5. Document all architectural changes