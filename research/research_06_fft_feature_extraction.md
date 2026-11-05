---
date: 2025-09-02
type: research
status: success
topic: FFT for Feature Extraction — IMU Sensor Data, Embedded Implementation & Tremor Analysis
sources: [web_search, web_extract]
---

# Research Handoff: FFT for Feature Extraction

## Research Question
What are the current best practices for using Fast Fourier Transform (FFT) to extract features from IMU sensor data, including embedded implementation on ESP32, spectral analysis techniques, and specific applications to tremor monitoring?

## Key Findings

### 1. FFT Fundamentals for Sensor Data

**Core Concept**
- FFT converts time-domain signals to frequency-domain representation
- Reveals dominant frequencies, harmonic content, and spectral energy distribution
- For tremor analysis: isolates tremor frequency (3-12 Hz) from voluntary motion (<2 Hz)

**Key Parameters**
| Parameter | Formula | Tremor Example (100 Hz, 1s window) |
|-----------|---------|-----------------------------------|
| Frequency resolution | Δf = fs / N | 100/100 = 1 Hz |
| Nyquist frequency | fs / 2 | 50 Hz |
| Bin spacing | fs / N | 1 Hz |
| Time window | T = N / fs | 1 second |

**Critical Insight**: True frequency resolution depends on **signal duration**, not zero-padding. Zero-padding only interpolates the spectrum (smoother display) but doesn't reveal hidden frequencies.

### 2. FFT Implementation — Python (Host Scripts)

**NumPy/SciPy Standard Approach**
```python
import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq

def extract_fft_features(imu_data, fs=100):
    """
    Extract FFT features from IMU data window.
    
    Args:
        imu_data: (N, 6) array — [ax, ay, az, gx, gy, gz] in g or dps
        fs: sampling frequency in Hz
    
    Returns:
        features: dict of spectral features per axis
    """
    N = len(imu_data)
    
    # Compute FFT for each axis
    features = {}
    axis_names = ['ax', 'ay', 'az', 'gx', 'gy', 'gz']
    
    for i, name in enumerate(axis_names):
        x = imu_data[:, i]
        
        # Remove DC component (mean)
        x = x - np.mean(x)
        
        # Apply window (Hann is good default)
        window = np.hanning(N)
        x_windowed = x * window
        
        # Compute FFT
        X = fft(x_windowed)
        freqs = fftfreq(N, 1/fs)
        
        # Take positive frequencies only
        pos_mask = freqs >= 0
        freqs = freqs[pos_mask]
        magnitudes = 2.0 / N * np.abs(X[pos_mask])
        
        # === Feature Extraction ===
        
        # 1. Dominant frequency (peak in tremor band 3-12 Hz)
        tremor_mask = (freqs >= 3) & (freqs <= 12)
        tremor_freqs = freqs[tremor_mask]
        tremor_mags = magnitudes[tremor_mask]
        
        if len(tremor_mags) > 0:
            dominant_idx = np.argmax(tremor_mags)
            features[f'{name}_dominant_freq'] = tremor_freqs[dominant_idx]
            features[f'{name}_dominant_magnitude'] = tremor_mags[dominant_idx]
        else:
            features[f'{name}_dominant_freq'] = 0
            features[f'{name}_dominant_magnitude'] = 0
        
        # 2. Spectral power in tremor band (3-12 Hz)
        features[f'{name}_tremor_power'] = np.sum(tremor_mags ** 2)
        
        # 3. Total spectral power (2-50 Hz)
        valid_mask = (freqs >= 2) & (freqs <= 50)
        features[f'{name}_total_power'] = np.sum(magnitudes[valid_mask] ** 2)
        
        # 4. Spectral entropy (flatness of spectrum)
        power_spectrum = magnitudes[valid_mask] ** 2
        power_norm = power_spectrum / np.sum(power_spectrum)
        power_norm = power_norm[power_norm > 0]  # Avoid log(0)
        features[f'{name}_spectral_entropy'] = -np.sum(power_norm * np.log2(power_norm))
        
        # 5. Spectral centroid (center of mass of spectrum)
        features[f'{name}_spectral_centroid'] = np.sum(freqs[valid_mask] * power_spectrum) / np.sum(power_spectrum)
        
        # 6. Band power ratios (tremor vs voluntary)
        voluntary_mask = (freqs >= 0.5) & (freqs < 3)
        voluntary_power = np.sum(magnitudes[voluntary_mask] ** 2)
        if voluntary_power > 0:
            features[f'{name}_tremor_voluntary_ratio'] = features[f'{name}_tremor_power'] / voluntary_power
        else:
            features[f'{name}_tremor_voluntary_ratio'] = 0
        
        # 7. Peak frequency using Welch PSD (more robust)
        freqs_psd, psd = signal.welch(x, fs=fs, nperseg=min(N, 256), 
                                        noverlap=min(N, 256)//2, window='hann')
        tremor_psd_mask = (freqs_psd >= 3) & (freqs_psd <= 12)
        if np.any(tremor_psd_mask):
            features[f'{name}_welch_peak_freq'] = freqs_psd[tremor_psd_mask][np.argmax(psd[tremor_psd_mask])]
            features[f'{name}_welch_peak_power'] = np.max(psd[tremor_psd_mask])
        else:
            features[f'{name}_welch_peak_freq'] = 0
            features[f'{name}_welch_peak_power'] = 0
    
    return features
```

**Welch Periodogram (More Robust PSD Estimation)**
```python
def compute_welch_features(imu_data, fs=100):
    """
    Welch PSD — better for noisy sensor data.
    Averages overlapping windows to reduce variance.
    """
    features = {}
    axis_names = ['ax', 'ay', 'az', 'gx', 'gy', 'gz']
    
    for i, name in enumerate(axis_names):
        x = imu_data[:, i] - np.mean(imu_data[:, i])
        
        # Welch PSD: window=256, overlap=128 (50%)
        freqs, psd = signal.welch(x, fs=fs, nperseg=256, noverlap=128, 
                                    window='hann', scaling='density')
        
        # Tremor band power (3-12 Hz)
        tremor_mask = (freqs >= 3) & (freqs <= 12)
        features[f'{name}_tremor_band_power'] = np.trapz(psd[tremor_mask], freqs[tremor_mask])
        
        # Low band power (0.5-3 Hz) — voluntary motion
        low_mask = (freqs >= 0.5) & (freqs < 3)
        features[f'{name}_low_band_power'] = np.trapz(psd[low_mask], freqs[low_mask])
        
        # Ratio: tremor / voluntary
        if features[f'{name}_low_band_power'] > 0:
            features[f'{name}_power_ratio'] = features[f'{name}_tremor_band_power'] / features[f'{name}_low_band_power']
        else:
            features[f'{name}_power_ratio'] = 0
        
        # Peak frequency
        if np.any(tremor_mask):
            features[f'{name}_peak_freq'] = freqs[tremor_mask][np.argmax(psd[tremor_mask])]
        else:
            features[f'{name}_peak_freq'] = 0
    
    return features
```

### 3. FFT Implementation — ESP32 (Embedded)

**ESP32 DSP Library (esp-dsp)**
```cpp
#include <esp_dsp.h>

// FFT configuration
#define FFT_SIZE 256
#define SAMPLE_RATE 100.0f

// Real FFT input/output (interleaved: real, imag, real, imag...)
float fft_input[FFT_SIZE * 2];
float fft_output[FFT_SIZE * 2];

void setup_fft() {
    // Initialize FFT tables (one-time)
    dsps_fft2r_init_fc32(FFT_SIZE);
}

void compute_fft(float* data, int n) {
    // Prepare input: real data in even indices, zeros in odd (imaginary)
    for (int i = 0; i < n; i++) {
        fft_input[2 * i] = data[i];      // Real part
        fft_input[2 * i + 1] = 0.0f;      // Imaginary part
    }
    
    // Zero-pad if needed
    for (int i = n; i < FFT_SIZE; i++) {
        fft_input[2 * i] = 0.0f;
        fft_input[2 * i + 1] = 0.0f;
    }
    
    // Apply window (Hann)
    for (int i = 0; i < n; i++) {
        float window = 0.5f * (1.0f - cosf(2.0f * M_PI * i / (n - 1)));
        fft_input[2 * i] *= window;
    }
    
    // Execute real FFT
    dsps_fft2r_fc32(fft_input, FFT_SIZE);
    
    // Bit-reverse reorder
    dsps_bit_rev_fc32(fft_input, FFT_SIZE);
    
    // Convert to magnitude spectrum
    for (int i = 0; i < FFT_SIZE / 2; i++) {
        float real = fft_input[2 * i];
        float imag = fft_input[2 * i + 1];
        fft_output[i] = sqrtf(real * real + imag * imag) / FFT_SIZE;
    }
}

// Extract features from FFT magnitude spectrum
typedef struct {
    float dominant_freq;
    float dominant_magnitude;
    float tremor_power;      // 3-12 Hz
    float total_power;       // 2-50 Hz
    float spectral_entropy;
    float peak_frequency;
} FFTFeatures;

FFTFeatures extract_fft_features(float* magnitude_spectrum, int n_bins, float sample_rate) {
    FFTFeatures features = {0};
    float bin_resolution = sample_rate / (2.0f * n_bins);
    
    // Tremor band: 3-12 Hz
    int tremor_start = (int)(3.0f / bin_resolution);
    int tremor_end = (int)(12.0f / bin_resolution);
    
    // Find dominant frequency in tremor band
    float max_mag = 0;
    int max_idx = 0;
    for (int i = tremor_start; i <= tremor_end && i < n_bins; i++) {
        if (magnitude_spectrum[i] > max_mag) {
            max_mag = magnitude_spectrum[i];
            max_idx = i;
        }
    }
    features.dominant_freq = max_idx * bin_resolution;
    features.dominant_magnitude = max_mag;
    
    // Compute tremor power
    for (int i = tremor_start; i <= tremor_end && i < n_bins; i++) {
        features.tremor_power += magnitude_spectrum[i] * magnitude_spectrum[i];
    }
    
    // Compute total power (2-50 Hz)
    int total_start = (int)(2.0f / bin_resolution);
    int total_end = (int)(50.0f / bin_resolution);
    for (int i = total_start; i <= total_end && i < n_bins; i++) {
        features.total_power += magnitude_spectrum[i] * magnitude_spectrum[i];
    }
    
    // Spectral entropy
    float sum_power = 0;
    for (int i = total_start; i <= total_end && i < n_bins; i++) {
        sum_power += magnitude_spectrum[i] * magnitude_spectrum[i];
    }
    if (sum_power > 0) {
        float entropy = 0;
        for (int i = total_start; i <= total_end && i < n_bins; i++) {
            float p = (magnitude_spectrum[i] * magnitude_spectrum[i]) / sum_power;
            if (p > 0) {
                entropy -= p * log2f(p);
            }
        }
        features.spectral_entropy = entropy;
    }
    
    return features;
}
```

**KISS FFT (Lightweight Alternative)**
```cpp
// KISS FFT — simpler, smaller footprint
// https://github.com/mborgerding/kissfft

#include "kiss_fftr.h"

#define FFT_SIZE 256
kiss_fft_cpx fft_out[FFT_SIZE / 2 + 1];
kiss_fftr_cfg fft_cfg;

void setup_kiss_fft() {
    fft_cfg = kiss_fftr_alloc(FFT_SIZE, 0, NULL, NULL);
}

void compute_kiss_fft(float* input, int n) {
    // Apply Hann window
    for (int i = 0; i < n; i++) {
        float window = 0.5f * (1.0f - cosf(2.0f * M_PI * i / (n - 1)));
        input[i] *= window;
    }
    
    // Execute real FFT
    kiss_fftr(fft_cfg, input, fft_out);
    
    // Compute magnitudes
    for (int i = 0; i <= FFT_SIZE / 2; i++) {
        float mag = sqrtf(fft_out[i].r * fft_out[i].r + fft_out[i].i * fft_out[i].i);
        // Store or process magnitude
    }
}
```

### 4. Windowing & Spectral Leakage

**Window Functions Comparison**

| Window | Main Lobe Width | Side Lobe Level | Best For |
|--------|----------------|-----------------|----------|
| **Rectangular** | 2 bins | -13 dB | Transient signals, short windows |
| **Hann** | 4 bins | -32 dB | **General purpose (recommended)** |
| **Hamming** | 4 bins | -43 dB | Narrowband signals |
| **Blackman** | 6 bins | -58 dB | High dynamic range |
| **Kaiser (β=8)** | ~4 bins | -50 dB | Adjustable trade-off |
| **Flat Top** | 8 bins | -44 dB | Accurate amplitude measurement |

**Recommendation**: Use **Hann window** for tremor analysis — good balance of main lobe width and side lobe suppression.

**Spectral Leakage Mitigation**
- Caused by non-integer number of periods in window (non-coherent sampling)
- **Solution**: Apply window function before FFT
- **Zero-padding**: Interpolates spectrum (smoother) but does NOT improve true resolution
- **True resolution improvement**: Increase window length (more samples)

### 5. Feature Extraction from FFT Spectrum

**Tremor-Specific Features**

| Feature | Formula | Clinical Relevance |
|---------|---------|-------------------|
| **Dominant frequency** | argmax(PSD) in 3-12 Hz | Tremor type (PD: 4-6 Hz, ET: 4-12 Hz) |
| **Peak amplitude** | max(PSD) in tremor band | Tremor severity |
| **Tremor power** | ∫ PSD df (3-12 Hz) | Total tremor energy |
| **Total power** | ∫ PSD df (2-50 Hz) | Overall movement |
| **Power ratio** | Tremor power / Voluntary power | Tremor vs voluntary motion |
| **Spectral entropy** | -Σ p(f) log₂ p(f) | Tremor regularity (low = regular) |
| **Spectral centroid** | Σ f·PSD(f) / Σ PSD(f) | Center of tremor energy |
| **3 dB bandwidth** | Width at half-power point | Tremor frequency spread |
| **Harmonic ratio** | PSD(2f₀) / PSD(f₀) | Tremor harmonic content |
| **Welch peak frequency** | Peak of Welch PSD | Robust dominant frequency |

**Clinical Validation (PMC10776092)**
- Ratio of PSD in 4-12 Hz vs 0.5-4 Hz: **R² = 0.818** with FTM clinical score
- Combined accelerometer + gyroscope features: **91.42% accuracy** for ET vs controls (SVM)
- Gyroscope features added significant value over accelerometer alone

### 6. Short-Time Fourier Transform (STFT)

**For Non-Stationary Tremor Signals**
```python
def compute_stft_features(imu_data, fs=100, window_size=100, hop_size=50):
    """
    STFT — captures time-varying frequency content.
    Useful for tremor that changes during tasks.
    """
    f, t, Zxx = signal.stft(imu_data, fs=fs, nperseg=window_size, 
                             noverlap=window_size-hop_size, window='hann')
    
    # Zxx is complex STFT matrix
    magnitude = np.abs(Zxx)
    
    # Features per time frame
    features = {
        'time': t,
        'frequencies': f,
        'spectrogram': magnitude,
        'tremor_power_over_time': np.sum(magnitude[(f >= 3) & (f <= 12), :], axis=0),
        'dominant_freq_over_time': f[np.argmax(magnitude, axis=0)]
    }
    
    return features
```

**STFT Parameters for Tremor**
- Window size: 100 samples (1 second at 100 Hz) → 1 Hz frequency resolution
- Hop size: 50 samples (50% overlap) → smooth time evolution
- Window: Hann (good leakage suppression)

### 7. Continuous Wavelet Transform (CWT) — Alternative to FFT

**For Transient Tremor Events**
- Better time-frequency localization than STFT
- Good for detecting tremor episodes during drawing tasks
- Used in PD kinetic tremor detection (PMC10540033)
- **Trade-off**: Higher computational cost than FFT

### 8. Practical Implementation Guidelines

**Sampling Rate Selection**
| Application | Sample Rate | FFT Size | Frequency Resolution |
|-------------|-------------|----------|---------------------|
| Rest tremor | 100 Hz | 256 | 0.39 Hz |
| Postural tremor | 100 Hz | 256 | 0.39 Hz |
| Kinetic tremor | 100 Hz | 256 | 0.39 Hz |
| High-resolution | 200 Hz | 512 | 0.39 Hz |
| Real-time embedded | 100 Hz | 128 | 0.78 Hz |

**Preprocessing Pipeline**
1. **Remove DC offset**: Subtract mean from each axis
2. **Bandpass filter**: 0.5-50 Hz (remove DC drift and high-freq noise)
3. **Apply window**: Hann window
4. **Zero-pad** (optional): To next power of 2 for FFT efficiency
5. **Compute FFT**: Real FFT for efficiency
6. **Extract features**: Magnitude spectrum → features

**Post-Processing**
- **Smoothing**: Moving average on spectrum for noise reduction
- **Peak interpolation**: Parabolic interpolation for sub-bin frequency estimation
- **Averaging**: Welch method (overlapping windows) for robust PSD

### 9. ESP32-Specific Optimizations

**Hardware Acceleration**
- ESP32 has hardware-accelerated FFT in DSP library (`esp-dsp`)
- ESP32-S3 has additional SIMD instructions for DSP
- Use `dsps_fft2r_fc32()` for real FFT (2x faster than complex FFT)

**Memory Constraints**
- 256-point FFT: ~2 KB RAM (input + output buffers)
- 512-point FFT: ~4 KB RAM
- Use `float` (32-bit) — ESP32 has FPU for single-precision float

**Real-Time Performance**
- 256-point real FFT: ~0.5 ms on ESP32 at 240 MHz
- 512-point real FFT: ~1.0 ms on ESP32 at 240 MHz
- Leaves plenty of time for sensor reading and BLE

**Power Optimization**
- Compute FFT in batches (FIFO mode)
- Use lower sample rate when possible (100 Hz vs 200 Hz)
- Disable WiFi during FFT computation (reduces noise)

### 10. Complete Feature Extraction Pipeline

```python
class TremorFeatureExtractor:
    """
    Complete FFT-based feature extraction for tremor analysis.
    Processes IMU windows and outputs feature vector for ML model.
    """
    
    def __init__(self, fs=100, window_size=100, overlap=50):
        self.fs = fs
        self.window_size = window_size
        self.overlap = overlap
        self.bin_resolution = fs / window_size
        
        # Tremor frequency bands
        self.tremor_band = (3.0, 12.0)    # Hz
        self.voluntary_band = (0.5, 3.0)  # Hz
        self.total_band = (2.0, 50.0)     # Hz
    
    def extract(self, imu_data):
        """
        Extract all features from IMU window.
        
        Args:
            imu_data: (N, 6) array — [ax, ay, az, gx, gy, gz]
        
        Returns:
            features: dict of all features
        """
        features = {}
        
        # Scalar magnitude (placement-invariant)
        accel_mag = np.sqrt(np.sum(imu_data[:, :3]**2, axis=1))
        gyro_mag = np.sqrt(np.sum(imu_data[:, 3:]**2, axis=1))
        
        # Process each axis + magnitudes
        signals = {
            'accel_mag': accel_mag,
            'gyro_mag': gyro_mag,
            'ax': imu_data[:, 0], 'ay': imu_data[:, 1], 'az': imu_data[:, 2],
            'gx': imu_data[:, 3], 'gy': imu_data[:, 4], 'gz': imu_data[:, 5]
        }
        
        for name, signal in signals.items():
            sig_features = self._extract_single_axis(signal, name)
            features.update(sig_features)
        
        # Cross-axis features
        features['accel_gyro_correlation'] = np.corrcoef(accel_mag, gyro_mag)[0, 1]
        
        return features
    
    def _extract_single_axis(self, x, name):
        """Extract features from single axis."""
        features = {}
        
        # Preprocess
        x = x - np.mean(x)
        window = np.hanning(len(x))
        x_windowed = x * window
        
        # FFT
        X = np.fft.rfft(x_windowed)
        freqs = np.fft.rfftfreq(len(x), 1/self.fs)
        magnitudes = 2.0 / len(x) * np.abs(X)
        power = magnitudes ** 2
        
        # Band masks
        tremor_mask = (freqs >= self.tremor_band[0]) & (freqs <= self.tremor_band[1])
        voluntary_mask = (freqs >= self.voluntary_band[0]) & (freqs < self.voluntary_band[1])
        total_mask = (freqs >= self.total_band[0]) & (freqs <= self.total_band[1])
        
        # Dominant frequency
        if np.any(tremor_mask):
            tremor_power = power[tremor_mask]
            tremor_freqs = freqs[tremor_mask]
            peak_idx = np.argmax(tremor_power)
            features[f'{name}_dominant_freq'] = tremor_freqs[peak_idx]
            features[f'{name}_dominant_power'] = tremor_power[peak_idx]
        else:
            features[f'{name}_dominant_freq'] = 0
            features[f'{name}_dominant_power'] = 0
        
        # Band powers
        features[f'{name}_tremor_power'] = np.sum(power[tremor_mask])
        features[f'{name}_voluntary_power'] = np.sum(power[voluntary_mask])
        features[f'{name}_total_power'] = np.sum(power[total_mask])
        
        # Power ratio
        if features[f'{name}_voluntary_power'] > 0:
            features[f'{name}_power_ratio'] = features[f'{name}_tremor_power'] / features[f'{name}_voluntary_power']
        else:
            features[f'{name}_power_ratio'] = 0
        
        # Spectral entropy
        total_p = power[total_mask]
        if np.sum(total_p) > 0:
            p_norm = total_p / np.sum(total_p)
            p_norm = p_norm[p_norm > 0]
            features[f'{name}_spectral_entropy'] = -np.sum(p_norm * np.log2(p_norm))
        else:
            features[f'{name}_spectral_entropy'] = 0
        
        # Spectral centroid
        if np.sum(total_p) > 0:
            features[f'{name}_spectral_centroid'] = np.sum(freqs[total_mask] * total_p) / np.sum(total_p)
        else:
            features[f'{name}_spectral_centroid'] = 0
        
        # Zero-crossing rate (time domain)
        features[f'{name}_zcr'] = np.sum(np.diff(np.sign(x)) != 0) / len(x)
        
        # RMS
        features[f'{name}_rms'] = np.sqrt(np.mean(x**2))
        
        return features
```

## Recommendations

1. **Use Welch PSD for robust features** — averaging overlapping windows reduces noise variance. Window size 256 samples, 50% overlap is good default.

2. **Extract both time and frequency domain features** — combine FFT features (dominant frequency, band power) with time-domain features (RMS, ZCR, crest factor) for best ML performance.

3. **Use scalar magnitude for placement invariance** — √(ax² + ay² + az²) is less sensitive to sensor orientation than individual axes.

4. **Apply Hann window before FFT** — reduces spectral leakage. Rectangular window only if signal has integer number of periods.

5. **Zero-pad to power of 2** — improves FFT computational efficiency (radix-2 algorithm). Does NOT improve frequency resolution.

6. **For ESP32 embedded**: Use `esp-dsp` library with 256-point real FFT. Compute on batches from FIFO. Target <2 ms per FFT.

7. **Feature selection**: Dominant frequency, tremor band power (3-12 Hz), power ratio (tremor/voluntary), and spectral entropy are most clinically relevant.

8. **Validate against clinical scales**: FTM (Fahn-Tolosa-Marin) or TETRAS scores. Aim for R² > 0.7 for regression, accuracy > 85% for classification.

## Potential Pitfalls

- **Spectral leakage**: Not using window function causes energy to leak into adjacent bins, distorting peak frequency estimation.
- **Aliasing**: Sampling too slowly (fs < 2 × f_max) causes high frequencies to fold back. Use anti-aliasing filter before ADC.
- **DC offset**: Not removing mean causes large 0 Hz bin that masks low-frequency tremor.
- **Insufficient window length**: Short windows → poor frequency resolution. Need ≥1 second for 1 Hz resolution.
- **Ignoring gyroscope**: Gyroscope captures rotational tremor that accelerometer misses. Combine both for best results.
- **Over-reliance on peak frequency**: Tremor frequency varies with task, medication, stress. Use multiple features for robust classification.
- **Zero-padding misconception**: Zero-padding interpolates spectrum but does NOT improve ability to distinguish close frequencies. Only longer windows improve true resolution.

## Sources

1. [Smart Tremor Analysis (GitHub)](https://github.com/dj08l/Smart-Tremor-Analysis)
2. [Professional IMU FFT Analysis (GitHub)](https://github.com/Codeharshw/Professional_IMU_FFT_Analysis)
3. [Wearable Accelerometer and Gyroscope Sensors for ET Severity (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10776092)
4. [IMU Sensing Data-based Kinetic Tremor Detection in PD (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10540033)
5. [Kinetic Tremor Measurement via IMU Sensing Data Analysis (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10509752)
6. [Practical FFT on ESP32-S3 (Reddit)](https://www.reddit.com/r/esp32/comments/1r5xhkz/practical_fft_on_the_esp32s3_dsp_acceleration_and/)
7. [Fast Fourier Transform on ESP32 (Elektor)](https://www.elektormagazine.com/articles/fast-fourier-transform-fft-on-the-esp32)
8. [KISS FFT Arduino Library (Adafruit)](https://blog.adafruit.com/2026/04/28/the-kiss-fft-arduino-esp32-library/)
9. [FFT on ESP32 (Robin Scheibler)](http://www.robinscheibler.org/2017/12/12/esp32-fft.html)
10. [Iterative Amplitude Equalization for Frequency Estimation (PMC)](https://ncbi.nlm.nih.gov/pmc/articles/PMC12694258)
11. [FFT Bin Resolution Calculator (rftools.io)](https://rftools.io/calculators/signal/fft-bin-resolution)
12. [Spectral Leakage, Zero-Padding and Frequency Resolution (DSP Illustrations)](https://dspillustrations.com/pages/posts/misc/spectral-leakage-zero-padding-and-frequency-resolution.html)
13. [Short-Time Fourier Transform (MetricGate)](https://metricgate.com/docs/short-time-fourier-stft)
14. [How Frequency Resolution Really Works (mmjal.com)](https://mmjal.com/BLOG?bmode=view&idx=170653804)
15. [ESP_DSP_FFT Library (GitHub)](https://github.com/johnny49r/ESP_DSP_FFT)

## For Next Agent

This research directly supports the `host_scripts/fft.py` and `feature_extract.py` in this project. Key takeaways:

- **Python implementation**: Use `scipy.signal.welch` for robust PSD estimation, `numpy.fft.rfft` for efficiency
- **ESP32 implementation**: Use `esp-dsp` library (`dsps_fft2r_fc32`) for hardware-accelerated real FFT
- **Window**: Hann window is best default for tremor analysis
- **Features**: Dominant frequency, tremor band power (3-12 Hz), power ratio, spectral entropy, spectral centroid
- **Window size**: 100-256 samples at 100 Hz (1-2.56 seconds) for good frequency resolution
- **Preprocessing**: Remove DC offset, apply bandpass filter (0.5-50 Hz), then window + FFT
- **Validation**: Target R² > 0.7 with FTM/TETRAS clinical scores
- **Combined sensing**: Use both accelerometer AND gyroscope — gyro adds significant value
- **Scalar magnitude**: √(ax² + ay² + az²) for placement-invariant features
