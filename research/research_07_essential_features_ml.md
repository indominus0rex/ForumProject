---
date: 2025-09-02
type: research
status: success
topic: Essential Features for Machine Learning — Feature Engineering, Selection & Extraction for Sensor Data
sources: [web_search, web_extract]
---

# Research Handoff: Essential Features for Machine Learning

## Research Question
What are the essential features and best practices for feature engineering, extraction, and selection when building machine learning models for sensor data (IMU, physiological signals), with emphasis on tremor monitoring applications?

## Key Findings

### 1. Feature Engineering Pipeline for Sensor Data

**Standard Workflow**
```
Raw Sensor Data → Preprocessing → Feature Extraction → Feature Selection → Model Training
       ↓                  ↓                ↓                  ↓
   [IMU 6-axis]    [Filter/Normalize]  [Time/Freq Domain]  [Filter/Wrapper/Embedded]
```

**Three Pillars of Feature Engineering**

| Pillar | Description | Examples |
|--------|-------------|----------|
| **Feature Extraction** | Transform raw data into informative representations | FFT → spectral features, PCA, autoencoders |
| **Feature Selection** | Choose most relevant subset | Correlation filter, RFE, LASSO |
| **Feature Construction** | Create new features from existing ones | Rolling statistics, interactions |

### 2. Feature Selection Methods — Three Categories

**A. Filter Methods** (Fast, model-agnostic)
- **Correlation-based**: Pearson, Spearman, Kendall tau
- **Mutual Information (MI)**: Captures non-linear dependencies
- **mRMR** (minimum Redundancy Maximum Relevance): Balances relevance vs redundancy
- **ANOVA F-test**: For classification tasks
- **Variance Threshold**: Remove near-constant features

```python
from sklearn.feature_selection import (
    SelectKBest, mutual_info_classif, f_classif,
    VarianceThreshold
)

# Variance threshold
selector = VarianceThreshold(threshold=0.01)
X_reduced = selector.fit_transform(X)

# Mutual information
selector = SelectKBest(mutual_info_classif, k=20)
X_selected = selector.fit_transform(X, y)

# mRMR
from mrmr import mrmr_classif
selected_features = mrmr_classif(X=X, y=y, K=20)
```

**B. Wrapper Methods** (Slow, model-specific)
- **Recursive Feature Elimination (RFE)**: Iteratively removes weakest features
- **Sequential Forward/Backward Selection**: Greedy subset search
- **Genetic Algorithms**: Evolutionary search

```python
from sklearn.feature_selection import RFECV
from sklearn.ensemble import RandomForestClassifier

# RFE with cross-validation
estimator = RandomForestClassifier(n_estimators=100)
selector = RFECV(estimator, cv=5, scoring='accuracy', min_features_to_select=10)
selector.fit(X_train, y_train)
selected_features = X.columns[selector.support_]
```

**C. Embedded Methods** (Medium speed, built into model)
- **LASSO (L1)**: Shrinks irrelevant coefficients to zero
- **Ridge (L2)**: Shrinks all coefficients
- **ElasticNet**: L1 + L2 combined
- **Tree-based importance**: Gini impurity, information gain

```python
from sklearn.linear_model import LassoCV
from sklearn.ensemble import RandomForestClassifier

# LASSO
lasso = LassoCV(cv=5)
lasso.fit(X_train, y_train)
important = np.abs(lasso.coef_) > 0

# Random Forest importance
rf = RandomForestClassifier(n_estimators=500)
rf.fit(X_train, y_train)
importances = rf.feature_importances_
```

### 3. Feature Importance from Tree-Based Models

**Random Forest Feature Importance**
- **MDI (Mean Decrease in Impurity)**: Sum of impurity decreases across all trees
- **Permutation Importance**: Drop in accuracy when feature is shuffled
- **SHAP Values**: Game-theoretic feature attribution

```python
import shap
from sklearn.inspection import permutation_importance

# MDI (built-in)
rf_importance = rf.feature_importances_

# Permutation importance (unbiased)
perm_imp = permutation_importance(rf, X_test, y_test, n_repeats=20, random_state=42)

# SHAP values
explainer = shap.TreeExplainer(rf)
shap_values = explainer.shap_values(X_test)
shap.summary_plot(shap_values, X_test)
```

**XGBoost Feature Importance**
- **Gain**: Average gain of splits using feature
- **Weight**: Number of times feature is used in splits
- **Cover**: Coverage of splits using feature

```python
import xgboost as xgb

xgb_model = xgb.XGBClassifier(n_estimators=200, max_depth=5)
xgb_model.fit(X_train, y_train)

# Gain-based importance
importance = xgb_model.get_booster().get_score(importance_type='gain')

# SHAP for XGBoost
explainer = shap.TreeExplainer(xgb_model)
shap_values = explainer.shap_values(X_test)
```

**Key Insight**: MDI/Gain can be biased toward high-cardinality features. Always validate with **permutation importance** or **SHAP**.

### 4. Essential Features for IMU/Tremor Sensor Data

**Time-Domain Features**
| Feature | Formula | Relevance |
|---------|---------|-----------|
| **RMS** | √(Σx²/n) | Tremor amplitude |
| **Peak-to-peak** | max(x) − min(x) | Tremor range |
| **Zero-crossing rate** | Σ(sign(x[i]) ≠ sign(x[i+1])) | Tremor frequency proxy |
| **Crest factor** | peak/RMS | Tremor burstiness |
| **Skewness** | E[(x−μ)³]/σ³ | Asymmetry |
| **Kurtosis** | E[(x−μ)⁴]/σ⁴ | Tail heaviness |
| **Jerk metric** | mean(\|Δa/Δt\|) | Tremor severity |

**Frequency-Domain Features**
| Feature | Formula | Relevance |
|---------|---------|-----------|
| **Dominant frequency** | argmax(PSD) | Tremor type (PD: 4-6 Hz, ET: 4-12 Hz) |
| **Peak amplitude** | max(PSD) | Tremor severity |
| **Band power** | ∫ PSD df (3-12 Hz) | Total tremor energy |
| **Spectral entropy** | −Σ p(f) log₂ p(f) | Tremor regularity |
| **Spectral centroid** | Σ f·PSD(f) / Σ PSD(f) | Center of tremor energy |
| **3 dB bandwidth** | Width at half-power | Tremor frequency spread |
| **Power ratio** | Tremor power / Voluntary power | Tremor vs voluntary motion |

**Cross-Axis Features**
- **Accel-gyro correlation**: Correlation between linear and rotational tremor
- **Cross-spectral density**: Phase relationship between axes
- **Coherence**: Frequency-domain correlation

### 5. Automated Feature Engineering (AutoFE)

**Tools & Libraries**
| Tool | Description | Best For |
|------|-------------|----------|
| **tsfresh** | Automatic time-series feature extraction | Sensor data, 600+ features |
| **Featuretools** | Deep feature synthesis | Relational data |
| **AutoMAN** | Mask-based feature engineering | Time series, heterogeneous data |
| **PyCaret** | Low-code AutoML with AutoFE | Quick prototyping |
| **autofeat** | Automated feature engineering | Tabular data |

**tsfresh Example**
```python
from tsfresh import extract_features, select_features
from tsfresh.utilities.dataframe_functions import impute

# Extract 600+ features automatically
extracted = extract_features(df, column_id='id', column_sort='time')

# Remove NaN/constant features
impute(extracted)

# Select relevant features
selected = select_features(extracted, y)
```

**AutoMAN (State-of-the-art 2024)**
- Learns feature importance masks end-to-end
- Scales linearly with number of features
- Preserves temporal relations in time series
- Outperforms tsfresh, Featuretools on multiple benchmarks

### 6. Dimensionality Reduction

**PCA (Principal Component Analysis)**
- Linear dimensionality reduction
- Preserves maximum variance
- Good for visualization and noise reduction
- **Limitation**: Loses interpretability

**t-SNE / UMAP**
- Non-linear dimensionality reduction
- Good for visualization
- Not suitable for feature extraction (no inverse transform)

**Autoencoders**
- Neural network-based dimensionality reduction
- Can capture non-linear relationships
- Requires more data and tuning

### 7. Feature Selection for Embedded ML

**Resource-Constrained Considerations**
- Fewer features → smaller model → faster inference
- Feature selection directly reduces memory and compute
- **Goal**: Find minimal feature set with acceptable accuracy

**Embedded Feature Selection Methods**
- **LASSO**: Built-in L1 regularization
- **Decision trees**: Natural feature selection via splits
- **ElasticNet**: Balanced L1/L2 for correlated features

**Practical Workflow for Embedded**
1. Extract 50-100 candidate features
2. Remove low-variance features (VarianceThreshold)
3. Remove highly correlated features (r > 0.95)
4. Apply mRMR or mutual information (top 20-30)
5. Train Random Forest, get permutation importance
6. Select top 10-15 features for final model
7. Validate with cross-validation

### 8. SHAP for Explainable Feature Importance

**SHAP (SHapley Additive exPlanations)**
- Game-theoretic feature attribution
- **Global importance**: Mean |SHAP| per feature
- **Local explanations**: Per-prediction feature contributions
- **Model-agnostic**: Works with any model
- **TreeExplainer**: Fast for tree-based models

```python
import shap

# Tree-based models
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Global importance plot
shap.summary_plot(shap_values, X_test, plot_type='bar')

# Feature interaction
shap.dependence_plot('feature_1', shap_values, X_test, interaction_index='feature_2')

# Local explanation (single prediction)
shap.force_plot(explainer.expected_value, shap_values[0], X_test.iloc[0])
```

### 9. Complete Feature Engineering Pipeline

```python
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold, SelectKBest, mutual_info_classif
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import cross_val_score
import shap

class TremorFeaturePipeline:
    """
    Complete feature engineering pipeline for tremor classification.
    """
    
    def __init__(self, variance_threshold=0.01, correlation_threshold=0.95, n_features=20):
        self.variance_threshold = variance_threshold
        self.correlation_threshold = correlation_threshold
        self.n_features = n_features
        self.scaler = StandardScaler()
        self.selected_features = None
        
    def fit_transform(self, X, y):
        """Full pipeline: clean → select → scale."""
        
        # Step 1: Remove low-variance features
        vt = VarianceThreshold(threshold=self.variance_threshold)
        X_var = vt.fit_transform(X)
        remaining_cols = X.columns[vt.get_support()]
        X = pd.DataFrame(X_var, columns=remaining_cols)
        
        # Step 2: Remove highly correlated features
        corr_matrix = X.corr().abs()
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        to_drop = [col for col in upper.columns if any(upper[col] > self.correlation_threshold)]
        X = X.drop(columns=to_drop)
        
        # Step 3: Univariate selection (mutual information)
        selector = SelectKBest(mutual_info_classif, k=min(self.n_features * 2, len(X.columns)))
        X_selected = selector.fit_transform(X, y)
        remaining_cols = X.columns[selector.get_support()]
        X = pd.DataFrame(X_selected, columns=remaining_cols)
        
        # Step 4: Tree-based selection (permutation importance)
        rf = RandomForestClassifier(n_estimators=200, random_state=42)
        rf.fit(X, y)
        perm_imp = permutation_importance(rf, X, y, n_repeats=10, random_state=42)
        
        # Select top features by permutation importance
        top_idx = np.argsort(perm_imp.importances_mean)[-self.n_features:]
        self.selected_features = X.columns[top_idx].tolist()
        X = X[self.selected_features]
        
        # Step 5: Scale
        X_scaled = self.scaler.fit_transform(X)
        
        return pd.DataFrame(X_scaled, columns=self.selected_features)
    
    def transform(self, X):
        """Apply fitted pipeline to new data."""
        X = X[self.selected_features]
        X_scaled = self.scaler.transform(X)
        return pd.DataFrame(X_scaled, columns=self.selected_features)
    
    def get_feature_importance(self, X, y):
        """Get SHAP-based feature importance."""
        rf = RandomForestClassifier(n_estimators=200, random_state=42)
        rf.fit(X, y)
        
        explainer = shap.TreeExplainer(rf)
        shap_values = explainer.shap_values(X)
        
        importance = pd.DataFrame({
            'feature': X.columns,
            'shap_importance': np.abs(shap_values[1]).mean(axis=0) if isinstance(shap_values, list) else np.abs(shap_values).mean(axis=0)
        }).sort_values('shap_importance', ascending=False)
        
        return importance
```

### 10. Recommended Feature Set for Tremor Classification

**Minimal Feature Set (10-15 features)**
1. `accel_rms` — RMS of accelerometer magnitude
2. `gyro_rms` — RMS of gyroscope magnitude
3. `dominant_freq` — Peak frequency in 3-12 Hz band
4. `tremor_power` — Power in 3-12 Hz band
5. `voluntary_power` — Power in 0.5-3 Hz band
6. `power_ratio` — Tremor / voluntary power ratio
7. `spectral_entropy` — Entropy of spectrum
8. `spectral_centroid` — Center of spectral mass
9. `accel_zcr` — Zero-crossing rate (accel)
10. `gyro_zcr` — Zero-crossing rate (gyro)
11. `crest_factor` — Peak / RMS ratio
12. `accel_gyro_corr` — Correlation between accel and gyro
13. `peak_amplitude` — Maximum spectral amplitude
14. `bandwidth_3db` — 3 dB bandwidth of spectral peak
15. `jerk_metric` — Mean absolute jerk

**Extended Feature Set (30-50 features)**
- All above, plus:
- Per-axis features (ax, ay, az, gx, gy, gz)
- Cross-axis correlations
- Wavelet decomposition coefficients
- Higher-order statistics (skewness, kurtosis)
- STFT-based time-varying features

## Recommendations

1. **Start with domain knowledge**: Use known tremor characteristics (3-12 Hz band, PD vs ET frequency differences) to guide feature extraction.

2. **Extract many features, then select**: Use tsfresh or manual extraction to generate 50-100 candidate features, then apply selection.

3. **Use mutual information for initial filter**: Fast, captures non-linear dependencies, good first pass.

4. **Validate with permutation importance**: MDI/Gain can be biased. Permutation importance on held-out data is more reliable.

5. **Use SHAP for final model interpretation**: Provides both global and local explanations — critical for clinical applications.

6. **Target 10-15 features for embedded deployment**: Enough for good accuracy, small enough for MCU inference.

7. **Include both time and frequency domain features**: They capture complementary information (amplitude vs frequency content).

8. **Remove correlated features**: Redundant features don't help and can hurt (multicollinearity). Use correlation threshold r > 0.95.

## Potential Pitfalls

- **Data leakage**: Fit scalers/selector on training data only, transform test data.
- **Overfitting with too many features**: Use cross-validation to detect. Rule of thumb: n_samples / n_features > 10.
- **MDI bias**: Tree-based importance favors high-cardinality features. Always validate with permutation importance.
- **Ignoring feature interactions**: Some features only matter in combination. Use SHAP interaction values.
- **Domain-irrelevant features**: Not all statistical features are clinically meaningful. Involve domain experts.
- **Static feature selection**: Feature importance can shift with data drift. Monitor and re-evaluate periodically.

## Sources

1. [Feature Engineering Toolkit for Predictive Analytics (IEEE)](https://doi.org/10.1109/rams48127.2025.10935234)
2. [Machine Learning-Based Feature Extraction and Selection (MDPI)](https://www.mdpi.com/2076-3417/14/15/6567)
3. [Automated data processing and feature engineering (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S2949715924000027)
4. [Automated feature engineering for AutoML (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S0950705125007178)
5. [Leveraging Feature Extraction for Time-Efficient Selection (MDPI)](https://www.mdpi.com/2076-3417/15/15/8196)
6. [EF²RB: Ensemble Feature Selection (Springer)](https://link.springer.com/article/10.1007/s10115-026-02871-6)
7. [BSD-FE: Automated Feature Engineering (IOPscience)](https://google.iopscience.iop.org/article/10.1088/2632-2153/ae2e7c)
8. [Data Preprocessing and Feature Engineering (MDPI)](https://www.mdpi.com/2673-2688/6/10/257)
9. [AutoMAN: Automated Feature Engineering (arXiv)](https://arxiv.org/pdf/2406.04153)
10. [Feature Engineering in Machine Learning (IJITMIS)](https://doi.org/10.34218/ijitmis_16_03_001)
11. [A Review of Feature Selection Methods (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9580915/)
12. [Feature Selection Techniques (GeeksforGeeks)](https://www.geeksforgeeks.org/machine-learning/feature-selection-techniques-in-machine-learning/)
13. [What is Feature Selection? (IBM)](https://www.ibm.com/think/topics/feature-selection)
14. [Feature Importance in Random Forests & XGBoost (PrimeLearnPoint)](https://primelearnpoint.com/explainable-ai-xai/feature-importance-in-random-forests-xgboost/)
15. [Classifying Motorcyclist Behaviour with XGBoost (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10857319/)

## For Next Agent

This research directly supports the `host_scripts/feature_extract.py` and `host_scripts/model.py` in this project. Key takeaways:

- **Pipeline**: Extract 50-100 features → VarianceThreshold → Correlation filter → Mutual Information → Permutation Importance → Top 15-20 features
- **Tools**: Use `tsfresh` for automatic extraction, `scikit-learn` for selection, `shap` for interpretation
- **Validation**: Always use permutation importance or SHAP on held-out data, not just MDI
- **Embedded target**: Final feature set should be 10-15 features for ESP32 deployment
- **Clinical relevance**: Dominant frequency, tremor power, power ratio, spectral entropy are most clinically validated
- **Avoid leakage**: Fit all transformers on training data only
- **Monitor drift**: Feature importance can shift with new patients or conditions
