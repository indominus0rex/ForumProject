# Drawing checklist

For the SLDDRW (SolidWorks) or technical drawing (FreeCAD TechDraw):

## Sheet 1: Assembly Drawing

- [ ] A3 landscape, scale 1:1
- [ ] Standard 3-view (front, top, right side)
- [ ] Isometric view
- [ ] Title block:
  - [ ] Title: "Tremor Detector — Wiring Assembly 3D"
  - [ ] Drawn by: ___
  - [ ] Date: ___
  - [ ] Sheet 1 of 1
  - [ ] Scale: 1:1
- [ ] Component balloons (numbered callouts):
  - [ ] ESP32-S3-Kaluga-1
  - [ ] GY-521 (MPU6050) ×4
  - [ ] 2N7000
  - [ ] 1N4148
  - [ ] RES 220Ω
  - [ ] RES 10kΩ
  - [ ] LED (red, 5mm)
  - [ ] LRA (coin) — **deferred, not this build**
  - [ ] Perfboard
- [ ] Wire color legend (red, black, yellow, blue)
- [ ] Notes:
  - [ ] All dimensions in mm
  - [ ] I2C: 400 kHz fast-mode
  - [ ] MPU6050: ±2g, DLPF 94 Hz
  - [ ] LRA driven low-side via GPIO25 PWM
  - [ ] Flyback diode protects against LRA back-EMF

## Optional Sheet 2: Schematic

- [ ] ESP32 pin map table (GPIO, function, connection)
- [ ] Power rail table (3V3, GND sources/sinks)

## Optional Sheet 3: BOM

- [ ] Part number, description, quantity, vendor
- [ ] ESP32-S3-Kaluga-1 x1
- [ ] GY-521 x4
- [ ] 2N7000 x1
- [ ] 1N4148 x1
- [ ] RES 220Ω x1
- [ ] RES 10kΩ x1
- [ ] LED 5mm red x1
- [ ] LRA coin (model-specific) — **deferred, not this build**
- [ ] Perfboard 30x15 holes x1
