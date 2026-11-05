---
date: 2025-09-02
type: research
status: success
topic: CNN vs DNN — Comparison, Architecture Differences & When to Use Each
sources: [web_search, web_extract]
---

# Research Handoff: CNN vs DNN

## Research Question
What are the key differences between Convolutional Neural Networks (CNNs) and Deep Neural Networks (DNNs), and when should each be used — particularly for sensor data and embedded applications?

## Key Findings

### 1. Relationship: CNN is a Subset of DNN

**All CNNs are DNNs, but not all DNNs are CNNs.**

| Term | Definition |
|------|-----------|
| **DNN** (Deep Neural Network) | Any neural network with multiple hidden layers. Often used interchangeably with MLP (Multi-Layer Perceptron) — fully connected layers. |
| **CNN** (Convolutional Neural Network) | A specialized DNN that uses convolutional layers with local connectivity and parameter sharing. |

### 2. Architecture Comparison

| Feature | DNN (MLP) | CNN |
|---------|-----------|-----|
| **Layer type** | Fully connected (dense) | Convolutional + pooling + FC |
| **Connectivity** | Each neuron connects to ALL neurons in previous layer | Each neuron connects to LOCAL region (receptive field) |
| **Parameter sharing** | No — each weight is unique | Yes — same filter slides across input |
| **Parameters** | Very many (prone to overfitting) | Fewer (weight sharing reduces count) |
| **Spatial awareness** | None — loses spatial structure | Yes — preserves local patterns |
| **Translation invariance** | No | Yes (via pooling) |
| **Best for** | Tabular data, feature vectors | Images, time series, grid-like data |

### 3. Visual Summary

```
DNN (MLP):                    CNN:
Input → FC → FC → FC → Output  Input → CONV → POOL → CONV → POOL → FC → Output

FC Layer:                     CONV Layer:
  ●───●                         ●───●
  │╲ │╲ │                       │   │
  ●───●───●  (all-to-all)       ●───●  (local + shared)
  │  │╲ │                       │   │
  ●───●───●                     ●───●
```

### 4. When to Use Each

**Use DNN (MLP) when:**
- Tabular data (age, income, features without spatial structure)
- Features are independent (no local correlations)
- Small datasets (CNNs need more data)
- Simple classification/regression with pre-extracted features
- Example: credit scoring, patient demographics

**Use CNN when:**
- Image data (2D-CNN)
- Time series / sensor data (1D-CNN)
- Audio/speech signals
- Any data with local spatial/temporal correlations
- Example: tremor classification from IMU windows, image recognition

### 5. Performance Comparison for Sensor/Time Series Data

**Research findings for time series classification:**

| Study | Dataset | CNN Result | DNN/MLP Result |
|-------|---------|------------|----------------|
| **CNN-TS (Springer 2023)** | Benchmark time series | +5.1% vs base CNN | +21.1% vs classical ML |
| **1D-CNN vs MLP (IEEE 2022)** | Sensor data | Higher accuracy | Lower accuracy |
| **DeepF-SVM (2022)** | HAR (human activity) | 96.44% accuracy | 93.57% (SVM alone) |
| **Motor fault diagnosis (2023)** | Multi-sensor | 99.3% (1D-CNN) | — |

**Key insight**: For time series/sensor data, **1D-CNN consistently outperforms DNN/MLP** because:
- Local patterns (tremor oscillations) are captured by convolutional filters
- Parameter sharing reduces overfitting on small datasets
- Hierarchical feature learning (low-level → high-level patterns)

### 1D-CNN Architecture for IMU Time Series
```
Input: (batch, channels=6, sequence_length=100)
  ↓
Conv1D(64, kernel_size=5) + ReLU + MaxPool(2)
  ↓
Conv1D(128, kernel_size=3) + ReLU + MaxPool(2)
  ↓
Conv1D(256, kernel_size=3) + ReLU + GlobalAvgPool
  ↓
FC(128) + ReLU + Dropout(0.3)
  ↓
FC(num_classes) + Softmax
```

### 6. Hybrid Approaches

**CNN as Feature Extractor + DNN for Classification**
- CNN extracts spatial/temporal features
- FC layers perform final classification
- This is the standard CNN architecture

**CNN + SVM (DeepF-SVM)**
- CNN extracts deep features
- SVM replaces final FC layer
- Achieves 96.44% on HAR dataset

**CNN + Random Forest**
- CNN features fed to RF classifier
- Good for small datasets

### 7. Computational Comparison

| Metric | DNN (MLP) | CNN |
|--------|-----------|-----|
| **Parameters** | O(n²) — grows with input size | O(k²×c) — fixed by kernel size |
| **Training time** | Faster per epoch | Slower per epoch (convolution ops) |
| **Inference time** | Fast | Fast (optimized conv kernels) |
| **Memory** | High (many weights) | Lower (weight sharing) |
| **Data efficiency** | Needs more data | Better for small datasets (spatial prior) |

### 8. For Embedded/TinyML Deployment

**1D-CNN advantages for MCU:**
- Fewer parameters than equivalent DNN
- Better accuracy with less data
- Can be quantized to INT8 efficiently
- Works with raw sensor data (no manual feature extraction)

**DNN advantages for MCU:**
- Simpler to implement
- Faster inference for small models
- Lower memory for tiny models (<10k params)

**Recommendation**: For tremor classification on ESP32, **1D-CNN is preferred** — better accuracy with raw IMU data, and modern TinyML frameworks (TFLite Micro) support CNN ops.

### 9. Summary Decision Matrix

| Scenario | Recommended | Why |
|----------|-------------|-----|
| **Image classification** | 2D-CNN | Spatial hierarchies, translation invariance |
| **Time series / IMU** | 1D-CNN | Local temporal patterns, fewer params |
| **Tabular data** | DNN/MLP | No spatial structure, simple FC works |
| **Small dataset (<1000)** | 1D-CNN or classical ML | CNN's spatial prior helps generalization |
| **Large dataset (>100k)** | Either (CNN often better) | Enough data for either architecture |
| **Embedded (MCU)** | 1D-CNN (quantized) | Better accuracy/size trade-off |
| **Real-time critical** | DNN (tiny) or 1D-CNN | Both can be fast with quantization |

## Recommendations

1. **For tremor classification**: Use **1D-CNN** on raw IMU windows. It outperforms DNN on time series and can learn features automatically.

2. **Start simple**: Try a 3-layer 1D-CNN (64-128-256 filters) before going deeper. Add FC layers at the end for classification.

3. **Hybrid option**: If you have pre-extracted features (FFT, RMS, etc.), a small DNN (2-3 FC layers) can work well and is simpler to deploy.

4. **For ESP32**: Use TFLite Micro with a quantized 1D-CNN. Target <50k parameters for comfortable deployment.

5. **Don't use 2D-CNN for 1D sensor data**: Unless you convert time series to images (spectrograms, recurrence plots), 1D-CNN is more appropriate.

## Potential Pitfalls

- **Using DNN for spatial data**: Loses local structure, needs more data, more parameters.
- **Using CNN for tabular data**: No spatial locality to exploit, may underperform DNN.
- **Too deep for small data**: CNNs with many layers overfit on small datasets. Start shallow.
- **Ignoring batch normalization**: Critical for CNN training stability.
- **Forgetting pooling**: Pooling provides translation invariance and reduces computation.

## Sources

1. [CS231n Convolutional Neural Networks (Stanford)](https://cs231n.github.io/convolutional-networks/)
2. [Deep Learning Book — Convolutional Networks](https://www.deeplearningbook.org/contents/convnets.html)
3. [CNN for Time Series Classification (IEEE)](https://ieeexplore.ieee.org/document/7870510)
4. [Deep CNN for Time Series with Intermediate Targets (Springer)](https://link.springer.com/article/10.1007/s42979-023-02159-4)
5. [Comparison of CNN and DNN for Multivariate Time Series (Springer)](https://link.springer.com/chapter/10.1007/978-981-97-6678-9_22)
6. [1D vs 2D CNN for Time Series (ResearchGate)](https://www.researchgate.net/publication/358179729)
7. [Understanding CNNs (LearnOpenCV)](https://learnopencv.com/understanding-convolutional-neural-networks-cnn/)
8. [Why FC layers at end of CNN? (StackOverflow)](https://stackoverflow.com/questions/42317238/)
9. [Difference between CNN and DNN (EITCA)](https://eitca.org/artificial-intelligence/eitc-ai-gcml-google-cloud-machine-learning/first-steps-in-machine-learning/deep-neural-networks-and-estimators/what-is-the-difference-between-cnn-and-dnn/)
10. [Comprehensive Survey of Convolutions in DL (arXiv)](https://doi.org/10.48550/arxiv.2402.15490)

## For Next Agent

This research supports architecture decisions for the tremor classification ML pipeline. Key takeaways:

- **CNN ⊂ DNN**: CNN is a type of DNN with convolutional layers
- **For IMU time series**: 1D-CNN is the clear winner over DNN/MLP
- **Architecture**: Conv1D → Pool → Conv1D → Pool → Conv1D → GlobalAvgPool → FC → Output
- **For ESP32**: Quantized 1D-CNN via TFLite Micro is feasible and recommended
- **Alternative**: If using pre-extracted features (FFT, RMS), a small DNN (2-3 FC layers) is simpler
- **Start with 1D-CNN on raw data**: Let the network learn features automatically
