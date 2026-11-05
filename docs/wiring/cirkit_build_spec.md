# Cirkit Designer Build Spec — 4-IMU Tremor Monitor (no LRA)

Source of truth: cad/connections_4imu.csv + docs/pin_assignments.md + firmware/common/config.py.
Build manually in Cirkit Designer: place parts, then run the nets top to bottom.

## Parts (Cirkit library search names)

- ESP32-DevKitC 38-pin
- TCA9548A I2C multiplexer breakout
- 4x MPU6050 GY-521 breakout
- MT3608 boost converter module (output pre-trimmed to 5.0V)
- TP4056 LiPo charger module (bench charging only, not wired to load)
- 1S LiPo 3.7V 450mAh, JST-PH 2.0
- PPTC resettable fuse 900mA hold (~1.8A trip)
- Slide switch SS22D07 3A SPDT (COM = center pin)
- LED + 220 ohm resistor (status, GPIO2)
- 4x 0.1uF ceramic (one per IMU VCC; plus one at TCA VCC)
- 2x 10uF ceramic (MT3608 input bulk + output bulk)
- 2x 4.7k resistor (I2C SDA/SCL pullups to 3V3)
- 10-100uF bulk on 3V3 rail near ESP32 (recommended)

## Nets

### Discharge path (wearable power)
1. LiPo+ (red) -> PPTC IN
2. PPTC OUT -> switch COM
3. Switch NO -> MT3608 IN+
4. LiPo- (black) -> star GND -> MT3608 IN-
5. MT3608 OUT+ -> ESP32 VIN (5V)
6. MT3608 OUT- -> star GND
7. 10uF across MT3608 IN+/IN- (input bulk)
8. 10uF across MT3608 OUT+/OUT- (output bulk)

### 3V3 distribution (from ESP32 onboard AMS1117)
9. ESP32 3V3 -> TCA9548A VCC (0.1uF across TCA VCC/GND)
10. 3V3 rail -> all 4 IMU VCC in star (0.1uF at each IMU VCC)
11. All GNDs (ESP32, TCA, 4x IMU) -> star GND rail, not daisy-chained

### I2C bus (400 kHz, GPIO21/22)
12. ESP32 GPIO21 -> TCA SDA; 4.7k SDA -> 3V3
13. ESP32 GPIO22 -> TCA SCL; 4.7k SCL -> 3V3
14. TCA A0/A1/A2 -> GND (address 0x70); TCA EN -> 3V3
15. TCA SD0/SC0 -> IMU0 SDA/SCL (CH0 dorsal wrist, blue)
16. TCA SD1/SC1 -> IMU1 SDA/SCL (CH1 thenar volar, green)
17. TCA SD2/SC2 -> IMU2 SDA/SCL (CH2 thumb proximal phalanx 20 deg tilt, yellow)
18. TCA SD3/SC3 -> IMU3 SDA/SCL (CH3 index proximal phalanx, orange)
19. All IMU AD0 -> GND (all at 0x68; mux channels isolate them)
20. Keep I2C leads under 15 cm; twist SDA/SCL pairs on runs over 10 cm

### Status LED
21. ESP32 GPIO2 -> 220 ohm -> LED anode; LED cathode -> GND

### Charge path (bench only, off to the side, NOT connected to load)
22. TP4056 BAT+ -> LiPo+ ; TP4056 BAT- -> LiPo-
23. USB 5V -> TP4056 input only when charging

### Deferred (leave NC, label on schematic)
- GPIO25/18/19/20 unconnected — no LRA this build

## Bench bring-up order
1. USB bank into ESP32 USB first; sensor side before battery side.
2. Meter MT3608 OUT = 5.0V unloaded before connecting ESP32 VIN.
3. Single IMU direct on GPIO21/22: I2C scan shows 0x68.
4. TCA only: scan shows 0x70. Add IMUs one channel at a time;
   mux.scan_channel(n) shows [0x68] for n = 0..3.
5. Flash via Thonny: common files, then stages, embedded_main last.

## Open issues
- TP4056 default 1A charge = ~2.2C for the 450mAh pack. DEFERRED by user
  decision: charge attended-only, pull at full LED. Proper fix is 10k PROG
  resistor (~130mA). Revisit before routine use.
- connections_4imu.csv rows 26-28 route the LED resistor top to the 3V3 rail;
  wire as GPIO2 -> resistor -> LED -> GND instead. CSV fix pending user confirm.
