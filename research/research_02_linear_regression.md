---
date: 2025-09-02
type: research
status: success
topic: Linear Regression — Implementation, Regularization, Evaluation & Embedded Deployment
sources: [web_search, web_extract]
---

# Research Handoff: Linear Regression

## Research Question
What are the current best practices for implementing linear regression models — including regularization, evaluation metrics, time-series considerations, and embedded deployment — with emphasis on sensor data (IMU, physiological signals) relevant to wearable tremor monitoring?

## Key Findings

### 1. Linear Regression Fundamentals (scikit-learn)

**Core API**
```python
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score

# Always use a Pipeline with scaling for sensor data
pipeline = Pipeline([
    ('scaler', StandardScaler()),  # Critical: linear models are sensitive to feature scales
    ('lr', LinearRegression())
])

# Hyperparameters for LinearRegression:
# fit_intercept=True (usually keep True)
# positive=False (set True if physics demands positive coefficients)
# copy_X=True, n_jobs=None, tol=1e-06
```

**Key Heuristics for Sensor Data Preparation**
- **Linear assumption**: Verify with scatter plots; polynomial features if curved
- **Noise removal**: Low-pass filter IMU data before regression
- **Remove collinearity**: Check correlation matrix; VIF > 10 indicates problematic multicollinearity
- **Gaussian distributions**: Residuals should be approximately normal (Q-Q plot)

### 2. Regularization — Critical for Sensor Data

**The Multicollinearity Problem in IMU Data**
IMU features (RMS, spectral power, peak frequency) are often highly correlated. This causes OLS coefficient estimates to be unstable and sensitive to noise. Regularization is essential.

**Three Canonical Methods**

| Method | Penalty | Best For | Multicollinearity Handling |
|--------|---------|----------|---------------------------|
| **Ridge (L2)** | `α * Σβ²` | Prediction accuracy, all features relevant | Excellent — shrinks correlated features together |
| **Lasso (L1)** | `α * Σ\|β\|` | Feature selection, sparse solutions | Poor — picks one from correlated group at random |
| **ElasticNet (L1+L2)** | `α * (ρ\|β\| + (1-ρ)β²)` | Correlated features + sparsity | Best — grouping effect maintains high recall |

**Empirical Finding (2025 survey, 134,400 simulations)**
- When sample-to-feature ratio n/p ≥ 78: Ridge, Lasso, ElasticNet are nearly interchangeable for prediction accuracy
- **Lasso recall collapses under multicollinearity**: At high condition numbers (κ ≈ 10⁵–10⁶) and low SNR, Lasso recall drops to 0.18 while ElasticNet maintains 0.93
- **Recommendation**: Use ElasticNet when features are correlated (common in spectral IMU features). Use Lasso only when features are known to be independent.

**Implementation**
```python
from sklearn.linear_model import RidgeCV, LassoCV, ElasticNetCV

# Ridge with built-in cross-validation for alpha
ridge = RidgeCV(alphas=[0.01, 0.1, 1.0, 10.0, 100.0], cv=5)
ridge.fit(X_train, y_train)
print(f"Best alpha: {ridge.alpha_}")

# ElasticNet with CV for both alpha and l1_ratio
enet = ElasticNetCV(
    l1_ratio=[0.1, 0.3, 0.5, 0.7, 0.9],  # 0=Ridge, 1=Lasso
    alphas=[0.01, 0.1, 1.0, 10.0],
    cv=5
)
enet.fit(X_train, y_train)
print(f"Best l1_ratio: {enet.l1_ratio_}, Best alpha: {enet.alpha_}")
```

**Decision Guide**
- Condition number κ > 10⁴: Use ElasticNet or Ridge (avoid Lasso)
- Need feature selection: Use ElasticNet with l1_ratio ≈ 0.5
- All features known relevant: Use Ridge
- Independent sparse features: Use Lasso

### 3. Evaluation Metrics

**Standard Metrics**

| Metric | Formula | Use When | Sensitivity |
|--------|---------|----------|-------------|
| **RMSE** | `√(Σ(y-ŷ)²/n)` | General regression, penalize large errors | High to outliers |
| **MAE** | `Σ\|y-ŷ\|/n` | Robust evaluation, interpretable units | Linear (robust) |
| **R²** | `1 - SS_res/SS_tot` | Variance explained, model comparison | Scale-independent |
| **Adjusted R²** | `1 - (1-R²)(n-1)/(n-p-1)` | Multiple features, penalize complexity | Feature-count aware |
| **MAPE** | `Σ\|y-ŷ\|/y * 100/n` | Percentage interpretation | Undefined at y=0 |

**Cross-Validation Strategy**
- **Standard k-fold (k=5 or 10)**: For i.i.d. data, balanced classes
- **TimeSeriesSplit**: For temporal/IMU data — never shuffle, respect chronology
- **Expanding window**: When more history always helps
- **Rolling window**: When data-generating process changes over time

```python
from sklearn.model_selection import TimeSeriesSplit, cross_val_score

# For IMU time-series data
tscv = TimeSeriesSplit(n_splits=5)
scores = cross_val_score(pipeline, X, y, cv=tscv, scoring='neg_rmse')
print(f"CV-RMSE: {-scores.mean():.4f} ± {scores.std():.4f}")
```

**Key Insight**: Always report fold-wise metric standard deviation. High variance indicates overfitting or data heterogeneity.

### 4. Time-Series Specific Considerations

**Why Standard CV Fails for Sensor Data**
Random k-fold shuffles temporal order, allowing the model to "peek" at future data. This produces unrealistically optimistic metrics. For IMU tremor data, always use `TimeSeriesSplit` or walk-forward validation.

**Feature Extraction Pipeline for IMU**
```python
# Typical IMU feature extraction window
# Window size: 1000ms (captures 4+ cycles of 4Hz tremor)
# Features per axis: RMS, peak frequency, spectral entropy, zero-crossing rate
# Total features: 3 axes × 4 features = 12 features per window

# Pipeline structure
from sklearn.preprocessing import PolynomialFeatures

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('poly', PolynomialFeatures(degree=2, interaction_only=True)),  # If non-linear
    ('en', ElasticNetCV(l1_ratio=[0.3, 0.5, 0.7], cv=TimeSeriesSplit(5)))
])
```

### 5. Embedded/TinyML Deployment

**Linear Regression on Microcontrollers**
Linear regression is one of the simplest models to deploy on MCUs — it's just a dot product plus bias. Several approaches:

**A. Manual Implementation (C)**
```c
// Weights trained in Python, deployed as static array
float weights[N_FEATURES] = {0.42, -1.37, 0.89, ...};
float bias = 2.15;

float predict(float *features) {
    float y = bias;
    for (int i = 0; i < N_FEATURES; i++) {
        y += weights[i] * features[i];
    }
    return y;
}
// Cost: N_FEATURES multiply-accumulate operations
// Memory: N_FEATURES + 1 floats (4 bytes each)
```

**B. embml Library (Online Learning)**
- `embml_linear`: Online linear regression via SGD — learns on-device
- `embml_lms`: LMS adaptive filter
- `embml_rls`: Recursive Least Squares with forgetting factor
- Each module is a .c/.h pair, no external deps

```c
#include "embml.h"
#define N_FEAT 8  // 8 IMU features
float weights[N_FEAT];
LinearModel model;

void setup(void) {
    linear_init(&model, N_FEAT, 0.01f, weights);  // lr=0.01
}

void loop(void) {
    float x[N_FEAT] = {rms_x, rms_y, rms_z, peak_freq, ...};
    float y_true = read_reference();
    linear_update(&model, x, y_true);  // Online learning
    float corrected = linear_predict(&model, x);
}
```

**C. Edge Impulse sklearn-linear-models**
- Custom ML blocks for scikit-learn linear models
- Supports LinearRegression, Ridge, RidgeCV, Lasso, ElasticNet
- Exports as C++ for embedded deployment
- EON tuner can optimize hyperparameters

**D. TensorFlow Lite Micro**
- Quantize linear model to int8 for 4× memory reduction
- Use TFLite Micro API for Cortex-M deployment

**Memory Budget Example**
- 20 features × 4 bytes = 80 bytes for weights
- 4 bytes for bias
- Total model: 84 bytes (fits in any MCU RAM)
- Inference: 20 MACC operations (~microseconds on Cortex-M4)

### 6. Feature Extraction from IMU for Regression

**Common Features for Tremor Regression**
| Feature | Description | Relevance |
|---------|-------------|-----------|
| RMS | `√(Σx²/n)` | Tremor amplitude |
| Peak frequency | Dominant FFT frequency | Tremor type (PD: 4-6Hz, ET: 4-12Hz) |
| Spectral entropy | Flatness of spectrum | Tremor regularity |
| Zero-crossing rate | Signal oscillation frequency | Tremor frequency proxy |
| Crest factor | Peak/RMS | Tremor burstiness |
| Jerk metric | Mean absolute jerk | Tremor severity |

**Windowing Strategy**
- Window size: 1000ms (captures 4+ cycles of 4Hz tremor)
- Overlap: 50% (sliding window for continuous monitoring)
- Nyquist: Sample at >12Hz for 6Hz tremors; 119Hz provides filtering overhead

## Code Examples

### Complete Pipeline for IMU Tremor Regression

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNetCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Load IMU features and tremor severity labels
# X: (n_samples, n_features) — extracted IMU features
# y: (n_samples,) — clinical tremor score (e.g., TETRAS)

# Build pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('en', ElasticNetCV(
        l1_ratio=[0.3, 0.5, 0.7],
        alphas=[0.001, 0.01, 0.1, 1.0, 10.0],
        cv=TimeSeriesSplit(n_splits=5),
        max_iter=10000
    ))
)

# Evaluate with time-series CV
cv_scores = cross_val_score(
    pipeline, X, y,
    cv=TimeSeriesSplit(n_splits=5),
    scoring='neg_root_mean_squared_error'
)
print(f"CV-RMSE: {-cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

# Fit on full training set
pipeline.fit(X_train, y_train)

# Extract best model
best_model = pipeline.named_steps['en']
print(f"Best l1_ratio: {best_model.l1_ratio_}")
print(f"Best alpha: {best_model.alpha_}")
print(f"Non-zero coefficients: {np.sum(best_model.coef_ != 0)}/{len(best_model.coef_)}")

# Evaluate on test set
y_pred = pipeline.predict(X_test)
print(f"Test RMSE: {mean_squared_error(y_test, y_pred, squared=False):.3f}")
print(f"Test MAE: {mean_absolute_error(y_test, y_pred):.3f}")
print(f"Test R²: {r2_score(y_test, y_pred):.3f}")

# Export weights for embedded deployment
weights = best_model.coef_
bias = best_model.intercept_
print(f"// Weights: {weights.tolist()}")
print(f"// Bias: {bias}")
```

### Export to C for Embedded Deployment

```python
def export_to_c(weights, bias, feature_names, output_path):
    """Export trained linear model as C header file."""
    n = len(weights)
    with open(output_path, 'w') as f:
        f.write(f"#ifndef TREMOR_MODEL_H\n")
        f.write(f"#define TREMOR_MODEL_H\n\n")
        f.write(f"#define N_FEATURES {n}\n\n")
        f.write(f"static const float weights[N_FEATURES] = {{\n    ")
        f.write(", ".join(f"{w:.6f}f" for w in weights))
        f.write(f"\n}};\n\n")
        f.write(f"static const float bias = {bias:.6f}f;\n\n")
        f.write(f"static inline float predict(const float *x) {{\n")
        f.write(f"    float y = bias;\n")
        f.write(f"    for (int i = 0; i < N_FEATURES; i++) {{\n")
        f.write(f"        y += weights[i] * x[i];\n")
        f.write(f"    }}\n")
        f.write(f"    return y;\n")
        f.write(f"}}\n\n")
        f.write(f"#endif // TREMOR_MODEL_H\n")
    print(f"Exported to {output_path}")
```

## Recommendations

1. **Always use StandardScaler before linear regression** — IMU features have different units (g, Hz, g/s) and scales. Linear models are sensitive to feature magnitude.

2. **Use ElasticNet over Lasso for IMU data** — spectral features (RMS, peak frequency, band power) are inherently correlated. ElasticNet's grouping effect handles this; Lasso's random feature selection produces unstable models.

3. **Use TimeSeriesSplit for evaluation** — tremor data is temporal. Random k-fold leaks future information and produces optimistic metrics.

4. **Report multiple metrics** — RMSE (penalizes large errors), MAE (robust, interpretable), R² (variance explained). No single metric captures full model quality.

5. **Check condition number** — `np.linalg.cond(X)` > 10⁴ indicates severe multicollinearity. Use Ridge or ElasticNet, avoid Lasso.

6. **For embedded deployment**: Linear regression is ideal — just a dot product. Export weights as C array, implement predict() as loop. Fits in <100 bytes, runs in microseconds.

7. **Consider online learning** — `embml_linear` with SGD adapts to patient-specific tremor patterns on-device without cloud dependency.

8. **Feature selection via Lasso coefficients** — if Lasso sets a feature to zero consistently across CV folds, consider removing it to simplify the embedded model.

## Potential Pitfalls

- **Multicollinearity without regularization**: OLS coefficients become unstable, signs may flip, predictions have high variance.
- **Data leakage via scaling**: Fit scaler on training data only, transform test data. Never fit on full dataset before split.
- **Ignoring temporal structure**: Random train/test split on time-series data produces unrealistically good metrics.
- **Over-reliance on R²**: R² can be high even with biased predictions. Always check residual plots and MAE/RMSE.
- **Lasso with correlated features**: Lasso arbitrarily selects one feature from a correlated group, producing non-reproducible models.
- **Not checking residual normality**: Linear regression assumes normally distributed residuals. Skewed residuals suggest log-transform or non-linear model.
- **Too many features for sample size**: When p > n, OLS is undefined. Use regularization (Ridge/ElasticNet) or reduce features.

## Sources

1. [scikit-learn Linear Models documentation](https://scikit-learn.org/stable/modules/linear_model.html)
2. [scikit-learn LinearRegression API](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)
3. [scikit-learn ElasticNet API](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ElasticNet.html)
4. [L1-based models for Sparse Signals example](https://scikit-learn.org/stable/auto_examples/linear_model/plot_lasso_and_elasticnet.html)
5. [Regularization survey (Ridge/Lasso/ElasticNet comparison)](https://www.arxiv.org/pdf/2604.03541)
6. [Edge Impulse sklearn-linear-models](https://www.edgeimpulse.com/blog/sklearn-linear-models-doing-more-with-less-data)
7. [embml — embedded ML library with online linear regression](https://dev.to/hejhdiss/running-machine-learning-on-microcontrollers-a-sample-usage-of-embml-56n4)
8. [Regression Metrics Explained (MAE, RMSE, R²)](https://joyoshish.github.io/blog/2025/ds010-heartofml-regression4/)
9. [Time Series Cross-Validation](https://kindatechnical.com/r-language/time-series-cross-validation-and-accuracy-metrics.html)
10. [Arduino Parkinson's Tremor Tracking Wearable Config](https://electricalflux.com/mcu-general/arduino-parkinsons-tremor-tracking-wearable-config)
11. [Embedded ML for Microcontroller-Class Edge Devices](https://alphaxiv.org/abs/2606.18122)
12. [On-Device Vision Training on Microcontroller](https://arxiv.org/pdf/2604.23012)

## For Next Agent

This research directly supports the `host_scripts/logreg.py` and `host_scripts/model.py` in this project. Key takeaways for implementation:

- **Current project has `logreg.py`** — likely logistic regression for classification. Consider adding a regression variant for tremor severity prediction (continuous output).
- **Feature extraction** (`feature_extract.py`) should output features compatible with linear regression: RMS, peak frequency, spectral entropy per axis.
- **For embedded deployment**: Linear regression is the simplest model to port to ESP32. Export weights from scikit-learn → C header → inference on MCU.
- **Regularization is non-negotiable** for IMU data — use ElasticNetCV with TimeSeriesSplit.
- **Evaluation**: Use `TimeSeriesSplit` not `train_test_split` for tremor data. Report RMSE + MAE + R².
- **TinyML path**: Start with linear regression as baseline, then compare against decision tree/random forest for non-linear improvement.
