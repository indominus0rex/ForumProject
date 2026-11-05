---
date: 2025-09-02
type: research
status: success
topic: Deep Neural Networks — Architecture, Training, Regularization & Embedded Deployment
sources: [web_search, web_extract]
---

# Research Handoff: Deep Neural Networks

## Research Question
What are the current best practices for designing, training, and deploying deep neural networks, with emphasis on sensor data (IMU, physiological signals) and embedded/TinyML deployment relevant to wearable tremor monitoring?

## Key Findings

### 1. Architecture Design Best Practices

**Systematic Architecture Selection**
- For vision tasks: start with pre-trained models (largest manageable or smallest achieving target performance)
- For sensor/time-series tasks: start with 1D-CNNs or LSTM-based architectures
- Neural Architecture Search (NAS) using reinforcement learning (MetaQNN) or evolution can automate design but requires significant compute
- Modular NAS (e.g., NASNet) reduces search cost from thousands to ~4 GPU-days

**Architecture Components for Sensor Data**
- **1D Convolutional layers**: Extract local temporal patterns from IMU windows
- **Batch Normalization**: Stabilizes training, allows higher learning rates, acts as mild regularizer
- **Residual connections**: Enable deeper networks without vanishing gradients
- **Global Average Pooling**: Reduces parameters before fully-connected layers
- **Recurrent layers (LSTM/GRU)**: Capture long-term temporal dependencies in tremor sequences

**General Design Principles**
- Start simple, increase complexity only when underfitting is observed
- Use skip connections for networks >10 layers
- Match receptive field to relevant signal features (e.g., 1-2 seconds for tremor)
- Favor depth over width for same parameter count

### 2. Training Optimization

**Learning Rate Selection**
- **LR ranges**: 1e-4 to 1e-2 for Adam, 0.01 to 0.1 for SGD with momentum
- **Warmup**: Essential for deep networks — start with small LR, linearly increase over first 5-10% of training
- **Schedules**: Cosine annealing with warm restarts (SGDR) consistently outperforms step decay
- **Seesaw schedule**: When LR would halve, instead multiply by 1/√2 and double batch size — reduces wall-clock time by ~36% while matching cosine decay performance
- **AdaLRS**: Online LR search via loss descent velocity optimization — adjusts suboptimal LRs to optimum in single run

**Batch Size Considerations**
- Larger batches = more stable gradients but require LR scaling (linear scaling rule)
- Critical batch size (CBS) metric: scales with noise in loss landscape
- "Batch ramp" during training: double batch size when halving LR preserves loss dynamics

**Optimizer Choice**
- **Adam/AdamW**: Default for most tasks, robust to LR choice, weight decay decoupled
- **SGD + Momentum**: Better generalization with proper LR scheduling, requires more tuning
- **Scion**: Emerging optimizer with norm-transfer properties across model/dataset scaling

### 3. Regularization Techniques

**Dropout — Still Relevant**
- Analytic theory confirms: dropout reduces detrimental correlations between hidden nodes
- Optimal dropout probability increases with label noise level
- Optimal activation rate r* decreases with more hidden nodes K (mitigates co-adaptation)
- **Best practice**: Apply AFTER BatchNorm (not before) to avoid disturbing batch statistics
- For CNNs: use Dropout2d after convolutional layers, standard Dropout after FC layers

**Batch Normalization**
- Normalizes activations across mini-batch → stabilizes training, allows higher LR
- Acts as implicit regularizer
- **Key insight**: BatchNorm + Dropout can cause instability if Dropout disturbs BN statistics
- Recommendation: Apply BatchNorm first, then Dropout, or use Dropout only in layers without BatchNorm

**Combined Regularization Strategy (2025 findings)**
- BatchNorm alone: fast convergence but may overfit
- Dropout alone: slower overfitting but not best accuracy
- **BatchNorm + Dropout**: Best generalization when properly configured
- However: significantly increases training time

**Momentum-Adaptive Gradient Dropout (MAGDrop)**
- Novel 2025 method: dynamically adjusts dropout rates based on gradient norms + accumulated momentum
- Reduces generalization gap by 0.46% on CIFAR-10 vs standard dropout
- 29.2% tighter PAC-Bayes generalization bounds
- Particularly effective for high-stakes applications (medical diagnostics)

**Progressive Data Dropout (PDD)**
- Drop difficult/random training samples progressively across epochs
- Reduces effective epochs to 12.4% of baseline while improving accuracy up to 4.82%
- Schedule-matched random variant (SMRD) consistently outperforms structured approaches
- No architectural changes needed — drop-in improvement

**Weight Decay / L2 Regularization**
- Standard approach: λ = 1e-4 to 1e-3
- AdamW decouples weight decay from gradient update — preferred over L2 in Adam

### 4. Activation Functions & Normalization

**Activation Functions**
- **ReLU**: Default for hidden layers — simple, effective
- **LeakyReLU / PReLU**: Mitigates dying ReLU problem
- **GELU**: Used in transformers, smooth alternative
- **Swish/Sigmoid**: Self-gated, can outperform ReLU in deep networks

**Normalization Layers**
- **BatchNorm**: Standard for CNNs, uses batch statistics
- **LayerNorm**: Preferred for RNNs/Transformers, normalizes across features
- **GroupNorm**: Alternative when batch sizes are very small
- **RMSNorm**: Used in modern LLMs, no trainable parameters

### 5. Embedded/TinyML Deployment

**The Challenge**
- Standard ResNet-50: 97MB storage, 3.8 GFLOPS
- Typical MCU (Cortex-M4): 256KB Flash, 64KB SRAM, 80-168 MHz
- Need 100-1000× compression to fit

**Quantization (Most Critical Technique)**
- **FP32 → INT8**: 4× size reduction, <1% accuracy loss for most tasks
- **Post-Training Quantization (PTQ)**: No retraining needed, 2-3% accuracy loss possible
- **Quantization-Aware Training (QAT)**: Simulates quantization during training, <0.5% accuracy loss
- **INT8 full integer**: Both weights and activations as integers — fastest inference
- **Sub-INT8 (4-bit, 2-bit)**: Possible but requires QAT, limited tooling support
- **Typical result**: 286-536KB flash footprint within 1MB budget, 3.47-14.98ms inference latency

**Pruning (Structured vs Unstructured)**
- **Structured pruning**: Remove entire filters/channels — directly reduces computation, no sparse hardware needed
  - L1-norm importance scoring: remove filters with smallest norms
  - On MobileNetV2: 40% filters removable with only 1.8% accuracy loss
  - Fine-tuning recovers loss to within 0.6%
- **Unstructured pruning**: Remove individual weights — creates sparse matrices
  - Problematic for MCUs: no sparse computation hardware, index overhead
  - Avoid for MCU deployment

**Knowledge Distillation**
- Student model learns from teacher's soft labels (dark knowledge)
- Combine with quantization + pruning for maximum compression
- Pipeline: distill → prune → quantize

**Model Architecture Choices for MCUs**
- **MobileNetV2**: Depthwise separable convolutions, inverted residuals
- **TinyNav**: 23k-parameter 1D-CNN achieves 30ms inference on ESP32
- **Custom small CNNs**: 3-5 conv layers + 1-2 FC layers often sufficient for sensor data

**Memory Optimization**
- Arena size: must fit all intermediate tensors — often the limiting factor
- Buffer choreography: reuse memory between layers
- Operator fusion: combine conv+BN+ReLU into single operation
- Use ESP-NN or TFLite Micro optimized kernels

**Deployment Pipeline**
1. Train model in PyTorch/TensorFlow
2. Apply QAT (quantization-aware training)
3. Convert to TFLite with INT8 quantization
4. Generate C++ source from TFLite model
5. Integrate with TFLite Micro runtime
6. Profile memory and latency on target hardware

### 6. Evaluation Metrics for DNNs

**Classification Tasks**
- Accuracy, Precision, Recall, F1-score
- Confusion matrix for multi-class
- ROC-AUC for binary classification

**Regression Tasks**
- RMSE, MAE, R², MAPE (as detailed in linear regression research)

**Model Efficiency Metrics**
- Parameters count
- FLOPs (floating-point operations)
- Inference latency (ms)
- Memory footprint (KB)
- Energy per inference (mJ)

## Code Examples

### DNN Architecture for IMU Sensor Data (PyTorch)

```python
import torch
import torch.nn as nn

class TremorDNN(nn.Module):
    def __init__(self, input_channels=6, num_classes=3):
        super().__init__()
        # Input: (batch, channels, sequence_length)
        # e.g., 6 channels (acc_x,y,z + gyro_x,y,z), 100 samples at 100Hz
        
        self.features = nn.Sequential(
            # Block 1
            nn.Conv1d(input_channels, 32, kernel_size=7, padding=3),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Dropout2d(0.1),
            
            # Block 2
            nn.Conv1d(32, 64, kernel_size=5, padding=2),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Dropout2d(0.15),
            
            # Block 3
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),  # Global average pooling
        )
        
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

# Count parameters
model = TremorDNN()
total_params = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {total_params:,}")
# Target: <50k parameters for MCU deployment
```

### Training Loop with Best Practices

```python
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
from torch.utils.data import DataLoader

# Optimizer: AdamW with decoupled weight decay
optimizer = optim.AdamW(
    model.parameters(),
    lr=1e-3,
    weight_decay=1e-4
)

# Scheduler: Cosine annealing with warm restarts
scheduler = CosineAnnealingWarmRestarts(
    optimizer,
    T_0=10,      # First restart at epoch 10
    T_mult=2     # Double restart interval after each restart
)

# Loss function
criterion = nn.CrossEntropyLoss()

# Training loop
for epoch in range(num_epochs):
    model.train()
    for batch_x, batch_y in train_loader:
        optimizer.zero_grad()
        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)
        loss.backward()
        
        # Gradient clipping for stability
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        
        optimizer.step()
    
    scheduler.step()
    
    # Validation
    model.eval()
    with torch.no_grad():
        val_outputs = model(val_x)
        val_loss = criterion(val_outputs, val_y)
        # Track accuracy, save best model
```

### Quantization-Aware Training for TinyML

```python
import torch.quantization as quant

# Prepare model for QAT
model.train()
model.qconfig = quant.get_default_qat_qconfig('fbgemm')
quant.prepare_qat(model, inplace=True)

# Fine-tune with quantization simulation
for epoch in range(qat_epochs):
    # ... training loop as above ...
    pass

# Convert to quantized model
model.eval()
quantized_model = quant.convert(model)

# Export to TFLite (via ONNX or direct conversion)
# Then deploy with TFLite Micro
```

### Export to C for Embedded Deployment

```python
def export_model_tflite(model, save_path):
    """Export trained model to TFLite format for MCU deployment."""
    import tensorflow as tf
    
    # Convert PyTorch → ONNX → TensorFlow → TFLite
    # (simplified — actual conversion may need intermediate steps)
    
    converter = tf.lite.TFLiteConverter.from_saved_model(model_path)
    
    # Optimization settings
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = representative_data_gen  # calibration data
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8
    
    tflite_model = converter.convert()
    
    with open(save_path, 'wb') as f:
        f.write(tflite_model)
    
    print(f"Model size: {len(tflite_model) / 1024:.1f} KB")
    return tflite_model

def tflite_to_c_array(tflite_model, output_path):
    """Convert TFLite model to C array for embedding in firmware."""
    with open(output_path, 'w') as f:
        f.write(f"#ifndef MODEL_H\n#define MODEL_H\n\n")
        f.write(f"const unsigned char model_data[] = {{\n")
        for i, byte in enumerate(tflite_model):
            if i % 12 == 0:
                f.write("    ")
            f.write(f"0x{byte:02x}, ")
            if i % 12 == 11:
                f.write("\n")
        f.write(f"\n}};\n\n")
        f.write(f"const unsigned int model_len = {len(tflite_model)};\n\n")
        f.write(f"#endif // MODEL_H\n")
```

## Recommendations

1. **Start with a simple 1D-CNN** for IMU tremor classification — 3-5 conv layers + 2 FC layers is often sufficient. Only increase complexity if underfitting.

2. **Use BatchNorm + Dropout together** but apply BatchNorm first. This gives best generalization — critical for small medical datasets.

3. **Apply QAT (Quantization-Aware Training)** from the start if MCU deployment is planned. PTQ accuracy loss (2-3%) may be unacceptable for clinical applications.

4. **Target <50k parameters** for comfortable deployment on Cortex-M4 with 256KB SRAM. Use depthwise separable convolutions (MobileNet-style) to reduce computation.

5. **Use AdamW with cosine annealing** as default training setup. It's robust and requires minimal hyperparameter tuning.

6. **Implement Progressive Data Dropout** — it's a free lunch: reduces training time AND improves accuracy with zero architectural changes.

7. **Profile memory early** — tensor arena size is usually the bottleneck, not flash. Use TFLite Micro's memory planner.

8. **Validate on real hardware** — simulation accuracy doesn't capture quantization effects, memory constraints, or real-time deadlines.

## Potential Pitfalls

- **Overfitting on small datasets**: Medical IMU datasets are often small (<100 patients). Use aggressive regularization (Dropout 0.3-0.5), data augmentation, and early stopping.

- **Ignoring temporal structure**: Random train/test split on time-series data leaks future information. Use `TimeSeriesSplit` or patient-wise splits.

- **Quantization without QAT**: PTQ can cause 2-3% accuracy drop — unacceptable for clinical use. Always use QAT for INT8 deployment.

- **Unstructured pruning for MCUs**: Creates sparse matrices that MCUs can't exploit. Use structured pruning (remove entire filters).

- **BatchNorm + Dropout ordering**: Dropout before BatchNorm disturbs batch statistics → training instability. Always BatchNorm → Dropout.

- **Too large tensor arena**: AllocateTensors() fails at boot. Profile memory usage and use memory planning tools.

- **Ignoring inference latency variance**: RTOS deadlines require deterministic latency. Test worst-case execution time, not just average.

## Sources

1. [Deep learning architectures — IBM Developer](https://developer.ibm.com/articles/cc-machine-learning-deep-learning-architectures/)
2. [Optimal DNN architecture design (Springer)](https://link.springer.com/article/10.1007/s00521-025-11212-7)
3. [Architectural optimisation in DNNs (Nature)](https://www.nature.com/articles/s44387-025-00034-6)
4. [Efficient Global NAS (arXiv)](https://arxiv.org/html/2502.03553v1)
5. [Seesaw: Batch-size scheduling for LR (arXiv)](https://arxiv.org/pdf/2510.14717)
6. [AdaLRS: Loss-guided adaptive LR search (NeurIPS 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/file/8516e0109e6c4a3cdd17645dd61af7c7-Paper-Conference.pdf)
7. [Optimal Scaling Needs Optimal Norm (arXiv)](https://arxiv.org/html/2510.03871v2)
8. [UBA: Unified Budget-Aware LR schedule (NeurIPS 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/file/dce0ad3bd4981fea9a5a5a274a2256d9-Paper-Conference.pdf)
9. [Analytic theory of dropout regularization (alphaXiv)](https://www.alphaxiv.org/abs/2505.07792)
10. [MAGDrop: Momentum-Adaptive Gradient Dropout (arXiv)](https://arxiv.org/html/2510.18410)
11. [Progressive Data Dropout (NeurIPS 2025)](https://papers.nips.cc/paper_files/paper/2025/file/ed2dad593d87ca474a636cba610a29d3-Paper-Conference.pdf)
12. [BatchNorm and Dropout as regularizers](https://learnopencv.com/batch-normalization-and-dropout-as-regularizers/)
13. [General LR improvement strategy (Springer)](https://link.springer.com/article/10.1007/s40747-026-02226-2)
14. [Deploying TinyML for energy-efficient object detection (Nature)](https://doi.org/10.1038/s41598-025-27818-9)
15. [From TinyML to TinyDL: A Survey (ACM)](https://dl.acm.org/doi/10.1145/3776588)
16. [TinyML Complete Guide](https://meta-intelligence.tech/en/insight-tinyml)
17. [TinyML in Practice: Engineering Methods](https://meta-intelligence.tech/en/paper-tinyml.html)
18. [TinyNav: End-to-End TinyML on ESP32 (arXiv)](https://arxiv.org/pdf/2603.11071v1.pdf)
19. [TinyML Deployment: Quantization & Pruning Tips](https://beefed.ai/en/tinyml-deployment-quantization-pruning-memory-optimization)
20. [Neural Network Quantization for MCUs (arXiv)](https://arxiv.org/abs/2508.15008)
21. [TinyML Enhances CubeSat Mission Capabilities (arXiv)](https://arxiv.org/html/2603.20174v1)

## For Next Agent

This research directly supports the `host_scripts/` ML pipeline and `firmware/embedded_main.py` inference code. Key takeaways for implementation:

- **Architecture**: Use 1D-CNN (3-5 layers) for IMU tremor classification. Start simple, add complexity only if underfitting.
- **Training**: AdamW + CosineAnnealingWarmRestarts + BatchNorm + Dropout (after BN). Use QAT if MCU deployment planned.
- **Regularization**: Dropout 0.1-0.3 for conv layers, 0.3-0.5 for FC layers. Apply AFTER BatchNorm.
- **Deployment**: Target <50k parameters. Use structured pruning + INT8 QAT. Export via TFLite Micro.
- **Memory**: Profile tensor arena size early. Use ESP-NN or TFLite Micro optimized kernels.
- **Validation**: Use TimeSeriesSplit for temporal data. Report both accuracy and inference latency.
- **Data augmentation**: Critical for small medical datasets — time shifting, scaling, noise injection.

The project's existing `model.py` and `train_classifier.py` can be extended with these patterns. The `embedded_main.py` can integrate TFLite Micro for on-device inference.
