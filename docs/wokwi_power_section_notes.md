# Wokwi Diagram — 4-IMU ESP32 Tremor Monitor

The Wokwi diagram file is at `docs/wokwi_diagram_4imu.json`.

## How to Open

1. Go to https://wokwi.com
2. Click "New Project" → "ESP32 Arduino"
3. Replace the entire contents of `diagram.json` with the contents of `docs/wokwi_diagram_4imu.json`
4. The simulator will show the ESP32 + TCA9548A + 4× MPU6050 wired together

## What's in the Wokwi Diagram

The Wokwi diagram shows the **signal path** and **power distribution**:

| Component | ID | Notes |
|---|---|---|
| ESP32-DevKit V1 | `esp` | Represents ESP32-DevKitC 38-pin (Wokwi uses DevKit as proxy) |
| TCA9548A | `mux` | I2C multiplexer @0x70, channels CH0-CH3 |
| MPU6050 #1 | `imu0` | CH0 @0x68 — Dorsal Wrist |
| MPU6050 #2 | `imu1` | CH1 @0x68 — Thenar Volar |
| MPU6050 #3 | `imu2` | CH2 @0x68 — Thumb Phalanx 20° |
| MPU6050 #4 | `imu3` | CH3 @0x68 — Index Phalanx |
| LED + 220Ω | `led` + `rled` | Status LED on GPIO2 |
| 4.7kΩ pullups | `rsda` + `rscl` | I2C SDA/SCL pullups to 3.3V |

### Connections Summary

```
ESP32 GPIO21 (SDA) ──── TCA9548A SDA ──── SD0/SD1/SD2/SD3 ──── 4× MPU6050 SDA
ESP32 GPIO22 (SCL) ──── TCA9548A SCL ──── SC0/SC1/SC2/SC3 ──── 4× MPU6050 SCL
ESP32 3V3 ───────────── TCA9548A VCC ─── 4× MPU6050 VCC ──── 4.7kΩ pullups
ESP32 GND ────────────── TCA9548A GND ─── 4× MPU6050 GND
ESP32 GPIO2 ──────────── LED anode ────── 220Ω ─────────────── GND
```

## Power Section (NOT in Wokwi)

Wokwi doesn't have TP4056 or MT3608 parts, so the power section is documented here separately.

### Correct Power Topology for ESP32-DevKitC 38-pin

```
USB 5V ──── TP4056 VCC ──── TP4056 PROG ──── 1.2kΩ ──── GND
                          │
                          └──── TP4056 BAT+ ──── LiPo+ (JST red)
LiPo+ (JST red) ──────────── MT3608 IN+ (input)
LiPo- (JST black) ────────── MT3608 IN- (input) ─── Star GND
MT3608 OUT+ ──────────────── VIN pin (5V to DevKit)
MT3608 OUT- ──────────────── GND
                                            ├──── TCA9548A VCC
                                            ├──── 4× GY-521 VCC
                                            └──── 4.7kΩ pullups (SDA, SCL)

10µF cap across MT3608 IN+/IN- (input bulk)
10µF cap across MT3608 OUT+/OUT- (output bulk)
0.1µF cap per IC (ESP32, TCA9548A, 4× GY-521)
```

### CRITICAL: TP4056 Does NOT Connect to the Load

The TP4056 is a **charger IC only**. It cannot pass battery voltage to its output. The battery positive goes **directly** to the MT3608 IN+ pin. The TP4056's only job is to charge the battery from USB 5V.

### MT3608 Boost Converter Pinout

```
        ┌─────┐
  IN+ ─┤1   3├─ OUT+
        │     │
  IN- ─┤2   4├─ OUT-
        └─────┘
```

Pin 1 = IN+ (from battery+)
Pin 2 = IN- (to star ground)
Pin 3 = OUT+ (5V to DevKit VIN)
Pin 4 = OUT- (GND)

### Bill of Materials (Power Section)

| Ref | Component | Value | Notes |
|-----|-----------|-------|-------|
| U7 | TP4056 module | LiPo charger 1A | With DW01 protection |
| R_prog | Resistor | 1.2kΩ | Sets ~1A charge current (use 10kΩ for ~130mA) |
| BT1 | LiPo battery | 3.7V 500mAh+ | JST-PH 2.0 connector |
|| U8 | MT3608 | Boost converter 5V | IN+/IN-, OUT+/OUT- |
| C1 | Capacitor | 10µF | Input bulk on MT3608 IN+ |
| C2 | Capacitor | 10µF | Output bulk on MT3608 OUT+ |
| C3-C8 | Capacitor | 0.1µF | One per IC decoupling |

### Operating Parameters

| Parameter | Value |
|-----------|-------|
| VCC | 3.3V (onboard AMS1117-3.3 from VIN) |
| I2C clock | 400kHz |
| Sampling rate | 100Hz |
| FFT window | 128 samples |
| TCA9548A address | 0x70 (A0-A2→GND, EN→3.3V) |
| IMU addresses | All 0x68 (AD0→GND, multiplexed via TCA) |
| Max wire length | <15cm |

### I2C Address Map

| Device | Address | Connected via |
|--------|---------|---------------|
| TCA9548A | 0x70 | Direct to ESP32 I2C0 |
| GY-521 #0 (Dorsal Wrist) | 0x68 | TCA9548A CH0 |
| GY-521 #1 (Thenar Volar) | 0x68 | TCA9548A CH1 |
| GY-521 #2 (Thumb Phalanx) | 0x68 | TCA9548A CH2 |
| GY-521 #3 (Index Phalanx) | 0x68 | TCA9548A CH3 |

### Firmware Pin Assignment (matches `embedded_main.py`)

| Signal | ESP32 GPIO | Notes |
|--------|------------|-------|
| I2C0 SDA | GPIO21 | To TCA9548A SDA |
| I2C0 SCL | GPIO22 | To TCA9548A SCL |
| LED | GPIO2 | Status LED via 220Ω |
| I2C1 SDA | GPIO19 | Reserved for LRA haptics (not used) |
| I2C1 SCL | GPIO23 | Reserved for LRA haptics (not used) |
| LRA PWM | GPIO25 | Reserved for LRA haptics (not used) |
| LRA [0] | GPIO18 | Reserved for LRA haptics (not used) |
