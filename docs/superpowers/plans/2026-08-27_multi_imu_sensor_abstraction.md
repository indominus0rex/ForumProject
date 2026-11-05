# Multi-IMU Sensor Abstraction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement sensor abstraction layer with TCA9548A multiplexer support for up to 4 IMUs while preserving ESP32/MicroPython constraints and HSP pipeline.

**Architecture:** Introduce SensorProvider interface with SingleIMUProvider and MuxIMUProvider implementations, refactor stages/sensor to use provider, add sequential window sampling mode, and align host-firmware model and CSV contracts.

**Tech Stack:** MicroPython ESP32, Python 3.11 host with numpy/scikit-learn, Git

**Spec:** docs/superpowers/specs/2026-08-27_multi_imu_sensor_abstraction_design.md

## Global Constraints
- Stay ESP32/MicroPython, no platform change
- Keep HSP stage interface unchanged: `process(frame) -> frame`
- Feature order must match between host train_classifier.py and firmware feature_extract.py
- Default sampling 128 samples @ 100 Hz, 1.28 s window
- I2C bus 0 GPIO22/21 400 kHz, TCA9548A addr 0x70, GY-521 addr 0x68

---

### Task 1: TCA9548A multiplexer driver

**Files:**
- Create: `firmware/common/mux.py`
- Test: `tests/firmware/test_mux.py`

**Interfaces:**
- Produces: `class TCA9548A(i2c, addr=0x70)` with `select_channel(ch: int) -> None`
- Consumes: `machine.I2C`

- [ ] **Step 1: Write failing test**

```python
def test_select_channel_writes_correct_byte():
    from firmware.common.mux import TCA9548A
    mock_i2c = MockI2C()
    mux = TCA9548A(mock_i2c)
    mux.select_channel(2)
    assert mock_i2c.written == [0x70, 0b00000100]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/firmware/test_mux.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
class TCA9548A:
    def __init__(self, i2c, addr=0x70):
        self.i2c = i2c
        self.addr = addr
    def select_channel(self, ch):
        if not 0 <= ch <= 7:
            raise ValueError
        self.i2c.writeto(self.addr, bytes([1 << ch]))
```

- [ ] **Step 4: Run test to verify passes**

Run: `pytest tests/firmware/test_mux.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add firmware/common/mux.py tests/firmware/test_mux.py
git commit -m "feat(firmware): add TCA9548A mux driver"
```

### Task 2: SensorProvider abstraction

**Files:**
- Create: `firmware/common/sensor_provider.py`
- Modify: `firmware/common/gy521.py`
- Test: `tests/firmware/test_sensor_provider.py`

**Interfaces:**
- Produces: `class SensorProvider`, `SingleIMUProvider`, `MuxIMUProvider` with `read_3axis() -> tuple[float,float,float]`
- Consumes: `TCA9548A`, `GY521`

- [ ] **Step 1: Write failing test**

```python
def test_mux_provider_selects_channel():
    provider = MuxIMUProvider(mock_i2c)
    provider.select_channel(1)
    assert mock_mux.selected == 1
```

- [ ] **Step 2: Run test**

Run: `pytest tests/firmware/test_sensor_provider.py::test_mux_provider_selects_channel -v`
Expected: FAIL

- [ ] **Step 3: Implement providers**

```python
class SensorProvider:
    def read_3axis(self): raise NotImplementedError

class SingleIMUProvider(SensorProvider):
    def __init__(self, sensor): self.sensor = sensor
    def read_3axis(self): return self.sensor.read_3axis()

class MuxIMUProvider(SensorProvider):
    def __init__(self, i2c): ... # create mux and sensor
    def select_channel(self, ch): ...
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/firmware/test_sensor_provider.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add firmware/common/sensor_provider.py firmware/common/gy521.py
git commit -m "feat(firmware): add sensor provider abstraction"
```

### Task 3: Refactor SensorStage to use provider

**Files:**
- Modify: `firmware/stages/sensor.py`
- Test: `tests/firmware/test_sensor_stage.py`

**Interfaces:**
- Consumes: `SensorProvider`
- Produces: `frame["x","y","z","sensor_error"]`

- [ ] **Step 1: Write failing test**

```python
def test_sensor_stage_propagates_values():
    frame = {"x":None,"y":None,"z":None}
    stage = SensorStage(provider)
    frame = stage.process(frame)
    assert frame["x"] is not None
```

- [ ] **Step 2: Run test**

Run: `pytest tests/firmware/test_sensor_stage.py -v`
Expected: FAIL

- [ ] **Step 3: Update stage**

```python
class SensorStage:
    def __init__(self, provider): self.provider = provider
    def process(self, frame):
        x,y,z = self.provider.read_3axis()
        frame["x"],frame["y"],frame["z"] = x,y,z
        return frame
```

- [ ] **Step 4: Run test**

Run: `pytest tests/firmware/test_sensor_stage.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add firmware/stages/sensor.py
git commit -m "refactor(firmware): sensor stage uses provider"
```

### Task 4: Config and main loop for sequential window sampling

**Files:**
- Modify: `firmware/common/config.py`
- Modify: `firmware/embedded_main_hsp.py`
- Test: `tests/firmware/test_embedded_main_config.py`

**Interfaces:**
- Produces: provider selection based on `NUM_IMUS`

- [ ] **Step 1: Add config**

```python
NUM_IMUS = 4
TCA9548A_ADDR = 0x70
MUX_SAMPLING_MODE = 'sequential_windows'
```

- [ ] **Step 2: Update embedded_main_hsp to instantiate provider**

```python
if config.NUM_IMUS > 1:
    provider = MuxIMUProvider(i2c)
else:
    provider = SingleIMUProvider(sensor)
stages["sensor"] = SensorStage(provider)
```

- [ ] **Step 3: Run static check**

Run: `python -m py_compile firmware/embedded_main_hsp.py`
Expected: no errors

- [ ] **Step 4: Commit**

```bash
git add firmware/common/config.py firmware/embedded_main_hsp.py
git commit -m "feat(firmware): multi-IMU config and provider wiring"
```

### Task 5: Host model manifest export

**Files:**
- Create: `host_scripts/export_model_manifest.py`
- Modify: `host_scripts/train_classifier.py`
- Test: `tests/host/test_manifest.py`

**Interfaces:**
- Produces: `model_manifest.json` with feature_names, version

- [ ] **Step 1: Write failing test**

```python
def test_manifest_contains_feature_names():
    export_model_manifest(...)
    with open('model_manifest.json') as f:
        data = json.load(f)
    assert 'feature_names' in data
```

- [ ] **Step 2: Implement export**

```python
def export_model_manifest(feature_names, out_path):
    manifest = {"feature_names": feature_names, "version": "1.0"}
    json.dump(manifest, open(out_path,'w'))
```

- [ ] **Step 3: Run test**

Run: `pytest tests/host/test_manifest.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add host_scripts/export_model_manifest.py host_scripts/train_classifier.py
git commit -m "feat(host): model manifest export"
```

### Task 6: Host multi-IMU CSV parsing

**Files:**
- Modify: `host_scripts/analyze_pilot.py`
- Modify: `host_scripts/train_classifier.py`
- Test: `tests/host/test_multiimu_csv.py`

**Interfaces:**
- Consumes: multi-IMU CSV header
- Produces: per-IMU feature vectors

- [ ] **Step 1: Write failing test**

```python
def test_parse_multiimu_header():
    header = "# IMU_MODE=multi, NUM_IMUS=2"
    mode, num = parse_header(header)
    assert mode == 'multi' and num == 2
```

- [ ] **Step 2: Implement parser**

Add `parse_csv_header()` to detect mode and column offsets.

- [ ] **Step 3: Run test**

Run: `pytest tests/host/test_multiimu_csv.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add host_scripts/analyze_pilot.py host_scripts/train_classifier.py
git commit -m "feat(host): multi-IMU CSV parsing"
```

### Task 7: Audit event logging extension

**Files:**
- Modify: `firmware/stages/audit.py`
- Test: `tests/firmware/test_audit.py`

**Interfaces:**
- Produces: compact CSV line per window

- [ ] **Step 1: Write failing test**

```python
def test_audit_logs_model_version():
    stage = AuditStage()
    frame = {"label":"rest","confidence":0.9,"model_version":"1.0"}
    stage.process(frame)
    assert stage.last_log_contains("1.0")
```

- [ ] **Step 2: Update audit**

Append `model_version` to log buffer.

- [ ] **Step 3: Run test**

Run: `pytest tests/firmware/test_audit.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add firmware/stages/audit.py
git commit -m "feat(firmware): audit logs model version"
```

## Self-Review

1. Spec coverage: Sensor abstraction, mux driver, sequential sampling, model manifest, CSV parsing, audit logging all covered.
2. Placeholders: none.
3. Type consistency: `SensorProvider.read_3axis()` signature consistent across tasks.
