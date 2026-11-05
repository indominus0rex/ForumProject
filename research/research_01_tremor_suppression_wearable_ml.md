---
date: 2025-09-02
type: research
status: success
topic: Tremor Suppression Wearables with Machine Learning
sources: [web_search, web_extract]
---

# Research Handoff: Tremor Suppression Wearables with Machine Learning

## Research Question
What are the current state-of-the-art approaches for tremor suppression using wearable devices integrated with machine learning, particularly for Parkinson's disease and essential tremor?

## Key Findings

### 1. ML for Tremor Detection & Classification

**Deep Learning Classification (BiLSTM, CNN)**
- **BiLSTM on sEMG signals**: 88±5% tremor type classification, 84±8% task classification in 15 PD patients using purely sEMG data. Processing time <300ms (250ms windows + <50ms preprocessing) — viable for real-time suppression systems. [PMC9570986]
- **CNN + quantum-inspired filters**: Graphene-printed capacitive sensors with Quantvolution/QuantClass filters for ET detection. Shows improved stability in loss variability vs classical baselines. [Nature Scientific Reports 2025]
- **ETSD-Net (MobileNetV2-based)**: 88.44% accuracy for remote ET severity assessment from handwritten Archimedean spiral images. Outperforms ConvNeXt-Tiny, DenseNet, ResNet50. Enables low-cost remote diagnosis. [Nature Scientific Reports 2025]

**Tremor Differentiation (ET vs PD)**
- Scoping review of 46 studies (6,051 patients): ML models differentiate ET from PD with 60-100% accuracy (mean 89%). Most common inputs: accelerometers (26 studies), EMG (9), Archimedes spirals (6). Algorithms: SVM (18), k-NN (9), CNN (8). [Tremor Journal 2025]
- Key gap: heterogeneity in data types and reporting limits cross-study comparability.

**Severity Tracking**
- ML + wearable sensors enable continuous monitoring and total tremor burden estimation. [Newswise 2025]

### 2. ML-Controlled Active Suppression

**AI-Closed-Loop Transcutaneous Peripheral Nerve Stimulation (TPNS)**
- **Felix NeuroAI Wristband (Fasikl)**: FDA-cleared (July 2025), first AI-powered ET treatment. Cloud-based AI continuously adjusts stimulation (pulse counts, sequence, intensity) based on IMU data. Stimulates radial, median, and ulnar nerves.
  - Pilot study (17 ET patients): TETRAS PS improved 14.1→11.4 (p=0.0002), ADL 29.9→20.7 (p<0.001). 82% reported improvement.
  - TRANQUIL pivotal trial (125 patients): sham-controlled, met primary endpoint. Significant tremor reduction and daily function improvement.
  - LSTM-based AI: 89.5% prediction accuracy, reducing unnecessary stimulation.
  - Preclinical: 43.4% tremor amplitude reduction (rodents), 46.8% RMS drop (human bench). [PMC11927668, BusinessWire 2025]

**Deep Reinforcement Learning for Soft Exoskeletons**
- **DRL encoder-actor controller**: Models multiple arm joints and tremor propagation in physical simulation. Adaptable RL environment for dynamic movements across shoulder/elbow axes. Overcomes limitations of traditional control algorithms. [Frontiers in Robotics and AI 2025]

**Adaptive Phase-Tracking Stimulation**
- Wrist-worn system (48.7g) with adaptable phase-tracking algorithm for PD rest tremor. Accounts for tremor dynamic changes (frequency shifts, axis variation). Triggers CE-marked stimulator via TTL. [IEEE TNSRE 2026]

### 3. Hardware Modulation Approaches

**Functional Electrical Stimulation (FES)**
- Anti-phase stimulation: detect tremor at flexor → stimulate extensor (and vice versa). Uses electromechanical delay (EMD, 20-100ms) for timing.
- **MMSRC (Multiple Model Switched Repetitive Control)**: Adapts to time-varying physiological changes and electrode placement shifts. Addresses muscle fatigue limitations. [Southampton published PDF]
- Limitations: rapid muscle fatigue, skin irritation, co-contraction hindering voluntary movement.

**Peripheral Nerve Stimulation (PNS)**
- Closed-loop PNS with accelerometer: 42.17±3.09% tremor power reduction after 18 trials. Phase-locked closed-loop more efficient at modulating dominant frequency. [PMC7313727]
- TAPS (Transcutaneous Afferent Patterned Stimulation): FDA-cleared Cala system. Alternating median/radial nerve stimulation tuned to patient's tremor frequency. 38-83% tremor reduction in RCTs. Mechanism: modulates VIM thalamus alpha/beta band LFPs. [Brain Stimulation 2025]

**Mechanical/Exoskeleton**
- Soft exoskeletons preferred over rigid (compliance, comfort). WTSG (Wearable Tremor Suppression Glove) uses nonstretchable cables as artificial tendons.
- Equivalent-input-disturbance control: increases impedance in tremor frequency band while maintaining voluntary motion band impedance. [IEEE TNSRE 2026]

### 4. Sensing Modalities for Wearables

| Modality | Use Case | Pros | Cons |
|----------|----------|------|------|
| IMU (ACC+GYRO) | Tremor detection, phase tracking | Low cost, wearable, real-time | Orientation drift, motion artifacts |
| sEMG | Voluntary motion vs tremor distinction | Direct muscle activity, forearm-worn | Electrode placement, skin prep |
| Capacitive (graphene) | Low-cost ET detection | Flexible, printed, multi-finger | Durability, environmental resilience |
| mmWave radar (60GHz) | Contactless assessment | Non-contact, works at distance | Limited to lab/clinical settings |
| Handwriting images | Remote severity assessment | Low-cost, natural, scalable | Requires camera/pen, not real-time |

### 5. Key Datasets & Open Source

- **PT-Net (Western University)**: Open-source generative model for PD tremor data. Predictive model achieves 99.2% motion estimation accuracy, 90% at 100-step prediction horizon. Tremor classification 91.2%, task classification 91.1%. [ir.lib.uwo.ca/etd/9164/]
- **WearMe Lab datasets**: PD tremor data for WTSD development.

## Code Examples

```python
# BiLSTM for tremor/task classification from sEMG (conceptual)
# Input: 250ms windows of sEMG data
# Architecture: Bidirectional LSTM with regularized evolutionary NAS
# Output: Task label (5 classes) or tremor type (3 classes)
# Accuracy: 84% task, 88% tremor classification
# Processing: <300ms per window (real-time capable)

# DRL encoder-actor for soft exoskeleton control (conceptual)
# State: Multi-joint arm kinematics (shoulder, elbow)
# Action: Exoskeleton torque/assistance
# Reward: Tremor power reduction + voluntary motion preservation
# Trained in physical simulation with tremor propagation model
```

## Recommendations

1. **For real-time wearable suppression**: Combine IMU-based tremor detection with BiLSTM or LSTM classification. The <300ms processing window is feasible for embedded deployment on STM32WB or similar BLE-MCU.

2. **For closed-loop stimulation**: Consider the Felix/Fasikl approach — cloud-based AI with on-device IMU sensing. The LSTM prediction model (89.5% accuracy) reduces unnecessary stimulation and addresses neural adaptation.

3. **For voluntary motion discrimination**: sEMG-based BiLSTM is the strongest approach (84-88% accuracy). This is critical — suppressing voluntary motion is a major failure mode of mechanical approaches.

4. **For soft exoskeleton control**: DRL encoder-actor in simulation is promising but needs physical validation. Start with single-joint (wrist) before multi-joint.

5. **For data scarcity**: Use PT-Net's open-source generative model to augment training data. The 99.2% prediction accuracy suggests synthetic data captures real tremor dynamics well.

6. **Hardware trade-off**: FES/PNS approaches are lighter and less socially stigmatizing than exoskeletons but face muscle fatigue and skin irritation. Soft exoskeletons are more comfortable than rigid but still bulky.

## Potential Pitfalls

- **Small sample sizes**: Most studies use <20 patients. Validation on larger, demographically diverse cohorts is essential.
- **Simulated vs real tremor**: Many studies use healthy volunteers with induced tremor — may not generalize to PD/ET patients.
- **Muscle fatigue**: FES approaches show declining effectiveness over time due to fatigue and co-contraction.
- **Neural adaptation**: Prolonged patterned stimulation (TAPS) may lead to habituation; AI-driven variation (Felix) addresses this.
- **Phase delay**: EMD (20-100ms) and filtering delays can cause mistimed stimulation that amplifies rather than suppresses tremor.
- **Voluntary motion interference**: Mechanical suppression without ML-based discrimination can impede intended movement.

## Sources

1. [Learning to suppress tremors: DRL-enabled soft exoskeleton](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2025.1537470/abstract)
2. [AI-Controlled TPNS for ET — Felix/PMC11927668](https://pmc.ncbi.nlm.nih.gov/articles/PMC11927668/)
3. [BiLSTM for task/tremor classification in PD](https://pmc.ncbi.nlm.nih.gov/articles/PMC9570986/)
4. [PT-Net: ML for smarter wearable tremor suppression](https://ir.lib.uwo.ca/etd/9164/)
5. [Non-invasive wearable systems review (U of T)](https://urncst.com/index.php/urncst/article/view/983)
6. [Felix NeuroAI FDA clearance (BusinessWire)](https://www.businesswire.com/news/home/20250701753633/en/)
7. [TAPS mechanism — VIM thalamus modulation](https://doi.org/10.1016/j.brs.2025.06.004)
8. [ML for differentiating essential tremor — scoping review](https://tremorjournal.org/articles/10.5334/tohm.1182)
9. [Quantum-classical DL with graphene sensors](https://www.nature.com/articles/s41598-025-06359-1)
10. [ETSD-Net: Remote ET assessment via handwriting](https://www.nature.com/articles/s41598-025-94729-0)
11. [Wearable PNS system for ET attenuation](https://pmc.ncbi.nlm.nih.gov/articles/PMC7313727/)
12. [MMSRC for tremor suppression](https://eprints.soton.ac.uk/505044/1/MMSRC_published.pdf)
13. [Adaptable phase-tracking for PD rest tremor](https://ieeexplore.ieee.org/document/11216392)
14. [Lightweight wrist exoskeleton with EID control](https://doi.org/10.1109/tnsre.2026.3679550)

## For Next Agent

This research directly informs the wearable tremor monitoring/suppression system in this project. Key takeaways for implementation:

- **Sensing**: IMU (ISM330DHCX or similar) + optional sEMG for voluntary motion discrimination
- **ML pipeline**: BiLSTM or lightweight CNN for real-time tremor classification; LSTM for tremor prediction
- **Suppression modality**: If pursuing active suppression, consider TAPS-like PNS or soft exoskeleton with DRL control
- **Embedded target**: STM32WB series (BLE + sufficient compute for TinyML models)
- **Open datasets**: PT-Net generative model can supplement training data
- **Clinical validation**: Plan for standardized metrics (TETRAS, ADL scales) and sham-controlled protocols

The field is moving rapidly toward AI-driven closed-loop neuromodulation (Felix being the first FDA-cleared example). The project's ESP32/IMU firmware could evolve toward this paradigm by adding stimulation output and ML inference.
