# System Architecture Improvements

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
- **Status**: Not yet implemented (research referenced)

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
- **Status**: Implemented in firmware files (RawDataCollection.py, collect_pilot.py, embedded_main.py) - see commit a651166

### FFT Optimization
- **Current**: Pure Python Cooley-Tukey with on-the-fly twiddle factor computation
- **Improvement**: Pre-compute twiddle factors, use fixed-point arithmetic
  ```python
  # Pre-compute at initialization
  WINDOW = [0.5 * (1 - math.cos(2 * math.pi * i / 127)) for i in range(128)]
  TWIDDLE = [...]  # Pre-computed sine/cosine values
  ```
- **Expected gain**: 3-5x faster FFT processing
- **Status**: Not yet implemented (research referenced)

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
- **Status**: Addressed via timer-based sampling (see below)
- **Original code**:
  ```python
  while time.ticks_diff(time.ticks_us(), t_sample_start) < SAMPLE_INTERVAL_US:
      pass  # Wastes CPU cycles
  ```

### Proposed Solution: Timer-based sampling
- **Status**: Implemented in firmware files (RawDataCollection.py, collect_pilot.py, embedded_main.py) - see commit a651166
- **Implementation**:
  ```python
  from machine import Timer

  # Timer-based sampling state
  sample_buffer = [0.0] * SAMPLES
  sample_index = 0
  first_sample_time = None
  last_sample_time = None
  buffer_ready = False

  def sample_callback(t):
      global sample_index, first_sample_time, last_sample_time, buffer_ready
      # Get sensor sample
      sample = sensor.get_3axis_vector()
      sample_buffer[sample_index] = sample
      now = time.ticks_us()
      if sample_index == 0:
          first_sample_time = now
      last_sample_time = now
      sample_index += 1
      if sample_index >= SAMPLES:
          buffer_ready = True
          sample_index = 0  # Reset for next buffer

  # Initialize timer for periodic sampling
  timer = Timer(0)
  timer.init(period=SAMPLE_INTERVAL_US // 1000, mode=Timer.PERIODIC, callback=sample_callback)

  # In main loop:
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

      # ... process sample_buffer ...
  ```
- **Expected gain**: Eliminates CPU spinning, reduces power consumption, allows other tasks to run during sampling intervals

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

## 7. Differentiated but Feasible Architecture Direction

The next architecture should not simply copy common research patterns such as
"more IMUs + generic sensor fusion + LRA array." Those are useful building
blocks, but the project needs a design that is visibly different while staying
implementable on ESP32 + MicroPython.

### Proposed Direction: Context-Aware Edge Tremor Coach

Instead of acting only as a tremor detector or suppression glove, structure the
system as a lightweight real-time coach:

```text
IMU window
  -> signal-quality gate
  -> tremor-state classifier
  -> context state machine
  -> confidence-gated haptic policy
  -> short event log for offline personalization
```

This keeps the current 128-sample @ 100 Hz pipeline, but adds decision layers
around it rather than requiring unrealistic hardware or a large neural model.

### What Makes This Different from Typical Prior Work

1. **Signal-quality-first architecture**
   - Many systems classify every window directly.
   - This system should first detect invalid windows: loose strap, gravity-only
     fallback, I2C read failure patterns, saturation, or excessive motion
     artifact.
   - Benefit: safer feedback and cleaner training data.
   - Feasibility: uses simple thresholds already available from accelerometer
     values and timestamp jitter.

2. **Context state machine, not one-shot prediction**
   - Research prototypes often report per-window accuracy.
   - This system should maintain a small state machine:
     `idle -> observing -> tremor_candidate -> confirmed_tremor -> feedback -> cooldown`.
   - Benefit: reduces false LRA activation from a single noisy window.
   - Feasibility: a few integer states and counters in `embedded_main.py`.

3. **Personalized baseline profile**
   - Instead of using the same threshold/model behavior for every user, store a
     small baseline profile: rest RMS, dominant tremor band, preferred LRA duty,
     and recent false-positive count.
   - Benefit: more original than a fixed classifier and more practical than
     on-device retraining.
   - Feasibility: persist a small dictionary or constants block; update offline
     from captured sessions.

4. **Confidence-gated haptic feedback**
   - Do not vibrate only because the class is `kinetic` or `postural`.
   - Gate feedback by class confidence, signal quality, state duration, and
     cooldown time.
   - Benefit: creates a safer assistive device behavior and avoids annoying or
     misleading stimulation.
   - Feasibility: no extra hardware; only policy logic.

5. **Event-based data logging instead of full streaming**
   - Full BLE/SD logging is heavier and currently out of scope.
   - Log only compact events: timestamp, predicted class, confidence, dominant
     frequency, tremor-band power, signal-quality flag, and feedback action.
   - Benefit: supports research analysis and personalization without continuous
     raw-data storage.
   - Feasibility: print compact CSV lines to Thonny now; later route over serial
     or BLE.

6. **Feedback as cueing, not claimed mechanical suppression**
   - Prior suppression-glove research often implies direct tremor reduction.
   - This project should position LRAs as adaptive sensory cueing and motor
     awareness support unless clinical suppression is validated.
   - Benefit: scientifically safer and still novel for a student prototype.
   - Feasibility: uses current PWM LRA output and existing feedback map.

### Minimum Viable Implementation

1. Add `quality.py` firmware module:
   - checks fallback ratio, per-axis variance, saturation, sample timing jitter
   - returns `quality_ok`, `quality_reason`, and compact metrics
2. Add `state_machine.py` firmware module:
   - debounces predictions across 2-3 windows
   - enforces feedback cooldown
   - emits final action: `none`, `observe`, `cue_low`, `cue_high`
3. Update `embedded_main.py`:
   - run quality gate before classifier output is trusted
   - feed `(label, conf, quality_ok)` into the state machine
   - call `apply_feedback()` only from the state machine action
4. Update host scripts:
   - include quality metrics in analysis reports
   - compare raw classifier accuracy vs. state-machine event accuracy

### Why This Is Not Impossible

- No new processor is required.
- No cloud inference is required.
- No large neural network is required.
- No invasive or medical-grade actuator control is required.
- It builds directly on the existing 15-feature classifier and PWM feedback.
- The hardest parts are software policy and validation, not unavailable hardware.

### Success Criteria

- False haptic activations decrease versus direct per-window feedback.
- Invalid/loose-sensor windows are flagged instead of classified as tremor.
- End-to-end decision latency stays within 2-3 windows.
- Event logs show when the system refused to act and why.
- Architecture can be explained as an edge tremor coach, not just another
  IMU-classifier-plus-vibrator design.

## Implementation Priority

1. **High**: signal-quality gate, confidence/state-machine feedback gating,
   memory pre-allocation (**DONE**), timer-based sampling (**DONE**)
2. **Medium**: event logging, FFT optimization, I2C multiplexer support
3. **Low**: deep sleep integration, automatic CSV capture, BLE telemetry

## Testing Strategy

1. Unit tests for each firmware module
2. Integration tests for multi-sensor setup
3. Performance benchmarks (latency, power, accuracy)
4. Real-world validation with Parkinson's patients

## Next Steps

1. Add a signal-quality gate before trusting classifier output
2. Add a small feedback state machine with confidence and cooldown gating
3. Emit compact event logs for offline personalization
4. Implement FFT optimization with pre-computed twiddle factors
5. Add I2C multiplexer support only after the single-IMU architecture is stable
6. Create automated testing framework
7. Document all architectural changes