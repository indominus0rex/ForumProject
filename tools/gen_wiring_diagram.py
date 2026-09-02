#!/usr/bin/env python3
"""Generate minimalist 4-IMU wiring diagram (box schematic + hand inset)."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# --- Canvas ---
fig, ax = plt.subplots(figsize=(16, 9), dpi=150)
ax.set_xlim(0, 100)
ax.set_ylim(0, 56)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor("white")

# --- Colors per channel ---
C = {
    "ch0": "#2196F3",  # blue
    "ch1": "#4CAF50",  # green
    "ch2": "#FFC107",  # yellow/amber
    "ch3": "#FF9800",  # orange
    "pwr": "#F44336",  # red
    "gnd": "#212121",  # near-black
    "led": "#FFEB3B",  # yellow
    "nc":  "#9E9E9E",  # grey
    "i2c": "#1565C0",  # dark blue for SCL bundle
    "sda": "#2E7D32",  # dark green for SDA bundle
}

# =============================================================================
# MAIN BOX SCHEMATIC (left 85%)
# =============================================================================

def draw_box(ax, x, y, w, h, label, sublabel="", color="#E3F2FD", lw=1.5):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3",
                           facecolor=color, edgecolor="#333", linewidth=lw)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, label, ha="center", va="center",
            fontsize=9, fontweight="bold", color="#222")
    if sublabel:
        ax.text(x + w/2, y + h/2 - 2.2, sublabel, ha="center", va="center",
                fontsize=6.5, color="#555", style="italic")

# --- Power rail (top) ---
ax.plot([8, 82], [52, 52], color=C["pwr"], lw=3, solid_capstyle="round")
ax.plot([8, 82], [49, 49], color=C["gnd"], lw=3, solid_capstyle="round")
ax.text(6, 52.6, "3.3V", fontsize=7, color=C["pwr"], fontweight="bold", ha="right")
ax.text(6, 49.6, "GND", fontsize=7, color=C["gnd"], fontweight="bold", ha="right")
ax.text(83, 52.6, "0.1µF per IC  ·  10–100µF bulk", fontsize=6, color="#888", ha="left")

# --- ESP32 box ---
draw_box(ax, 14, 38, 18, 10, "ESP32-DevKitC", "I2C0  SDA=GPIO21  SCL=GPIO22  LED=GPIO2", color="#E8EAF6")
# ESP32 pins
pins_esp = [
    (17, 48, "3.3V", C["pwr"]), (19, 48, "GND", C["gnd"]),
    (21, 48, "GPIO21\nSDA", C["sda"]), (23, 48, "GPIO22\nSCL", C["i2c"]),
    (25, 48, "GPIO2\nLED", C["led"]), (28, 48, "GPIO25\nNC", C["nc"]),
    (30, 48, "18/19/20\nNC", C["nc"]),
]
for px, py, lbl, clr in pins_esp:
    ax.plot(px, py, "o", color=clr, markersize=4)
    ax.text(px, py + 1.3, lbl, ha="center", va="bottom", fontsize=5.5, color=clr, fontweight="bold")

# --- TCA9548A box ---
draw_box(ax, 38, 38, 16, 10, "TCA9548A", "@0x70  A0/A1/A2→GND  EN→3.3V", color="#E0F2F1")
tca_pins = [(41, 48, "SCL", C["i2c"]), (43, 48, "SDA", C["sda"]),
            (50, 48, "CH0-3", "#555"), (52, 48, "CH4-7 NC", C["nc"])]
for px, py, lbl, clr in tca_pins:
    ax.plot(px, py, "o", color=clr, markersize=4)
    ax.text(px, py + 1.3, lbl, ha="center", va="bottom", fontsize=5.5, color=clr, fontweight="bold")

# --- I2C bus wires ESP32 -> TCA ---
ax.plot([23, 41], [48, 48], color=C["i2c"], lw=2, linestyle="-")
ax.plot([21, 43], [48, 48], color=C["sda"], lw=2, linestyle="-")
ax.text(32, 48.8, "I2C @400kHz", ha="center", va="bottom", fontsize=6, color="#444")

# --- Four GY-521 IMU boxes ---
imu_labels = [
    ("IMU0  CH0", "dorsal wrist proximal\n(primary, Keba 2025)", C["ch0"], "#E3F2FD"),
    ("IMU1  CH1", "thenar volar", C["ch1"], "#E8F5E9"),
    ("IMU2  CH2", "thumb proximal phalanx\n20° dorsal-radial [PILL 4-6Hz]", C["ch2"], "#FFF8E1"),
    ("IMU3  CH3", "index proximal phalanx\ndorsal [ET 6-8Hz]", C["ch3"], "#FFF3E0"),
]
imu_y = [31, 24.5, 18, 11.5]
for i, (lbl, sub, clr, bg) in enumerate(imu_labels):
    y = imu_y[i]
    draw_box(ax, 62, y - 2.5, 18, 5, lbl, sub, color=bg)
    # AD0->GND note
    ax.text(71, y - 1.3, "GY-521 0x68  AD0→GND", ha="center", va="center",
            fontsize=5.5, color="#666")
    # Wire from TCA to IMU
    ax.plot([50, 62], [43, y], color=clr, lw=2, linestyle="-")
    ax.text(56, (43 + y)/2 + 0.5, f"CH{i}", fontsize=6, color=clr, fontweight="bold")

# --- LED top-right ---
ax.plot([88, 88], [40, 44], color=C["led"], lw=2)
ax.plot(88, 44, "o", color=C["led"], markersize=6)
ax.text(88, 45.5, "LED\nGPIO2", ha="center", va="bottom", fontsize=6, color=C["led"], fontweight="bold")
ax.plot([88, 88], [36, 40], color=C["gnd"], lw=2)
ax.text(88, 35.3, "220Ω", ha="center", va="center", fontsize=6, color="#555")

# --- NC deferred box ---
nc_box = FancyBboxPatch((82, 38), 7, 4, boxstyle="round,pad=0.2",
                         facecolor="#F5F5F5", edgecolor=C["nc"], linewidth=1, linestyle="--")
ax.add_patch(nc_box)
ax.text(85.5, 40, "DEFERRED\nno LRA", ha="center", va="center",
        fontsize=6, color=C["nc"], fontweight="bold")

# =============================================================================
# LEGEND (top-right, below LED) =============================================================================
legend_items = [
    ("CH0 dorsal wrist", C["ch0"]), ("CH1 thenar", C["ch1"]),
    ("CH2 thumb phalanx", C["ch2"]), ("CH3 index phalanx", C["ch3"]),
    ("3.3V", C["pwr"]), ("GND", C["gnd"]), ("LED", C["led"]), ("NC / deferred", C["nc"]),
]
ax.text(91, 50, "LEGEND", fontsize=7, fontweight="bold", color="#333", ha="center")
for j, (name, clr) in enumerate(legend_items):
    yy = 48 - j * 1.6
    ax.plot([84, 86], [yy, yy], color=clr, lw=2.5, solid_capstyle="round")
    ax.text(86.5, yy, name, va="center", ha="left", fontsize=6, color="#333")

# =============================================================================
# HAND INSET (top-right corner, 12%)
# =============================================================================
inset = fig.add_axes([0.78, 0.62, 0.20, 0.33])
inset.set_xlim(0, 10)
inset.set_ylim(0, 10)
inset.axis("off")
inset.set_facecolor("white")
# Dashed border
inset.add_patch(FancyBboxPatch((0.2, 0.2), 9.6, 9.6, boxstyle="round,pad=0.1",
                                facecolor="white", edgecolor="#888",
                                linewidth=1, linestyle="--"))
inset.text(5, 9.3, "Anatomical Reference", ha="center", va="center",
           fontsize=6, fontweight="bold", color="#555")
inset.text(5, 8.7, "Not Wiring", ha="center", va="center",
           fontsize=5.5, color="#888", style="italic")

# Hand outline (simplified dorsal)
hand_x = [3, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8, 7, 6, 5, 4, 3, 2.5, 2, 2.5, 3]
hand_y = [1, 2, 3, 4, 5, 6, 7, 7.5, 8, 8.5, 9, 9, 8.5, 8, 7.5, 7, 6, 5, 3, 1]
inset.fill(hand_x, hand_y, color="#E0E0E0", alpha=0.5)
inset.plot(hand_x, hand_y, color="#666", lw=1)

# Volar ghost (thenar)
inset.fill([3, 4, 5, 5.5, 5, 4, 3.5, 3], [2, 2.5, 3.5, 5, 6, 5.5, 4, 2],
          color="#C8E6C9", alpha=0.3, linestyle="--", edgecolor="#81C784")

# IMU dots
dots = [
    (6.5, 7.5, "0", C["ch0"]),   # dorsal wrist
    (4.2, 4.5, "1", C["ch1"]),   # thenar
    (3.2, 6.5, "2", C["ch2"]),   # thumb phalanx
    (7.2, 6.0, "3", C["ch3"]),   # index phalanx
]
for dx, dy, num, clr in dots:
    inset.plot(dx, dy, "o", color=clr, markersize=5, zorder=5)
    inset.annotate(num, (dx, dy), xytext=(dx + 0.8, dy + 0.5),
                   fontsize=6, fontweight="bold", color=clr,
                   arrowprops=dict(arrowstyle="-", color=clr, lw=0.8))

# =============================================================================
# TITLE + SPECS
# =============================================================================
ax.text(50, 54.5, "4-IMU Tremor Monitor — Wiring Diagram",
        ha="center", va="center", fontsize=14, fontweight="bold", color="#222")
ax.text(50, 53.2, "ESP32 + TCA9548A + 4× GY-521 (MPU6050)  ·  LRAs deferred",
        ha="center", va="center", fontsize=8, color="#666")

# Specs footer
ax.text(50, 0.5,
        "SAMPLES 128 @100Hz  ·  I2C 400kHz  ·  TCA9548A 0x70  ·  GY-521 0x68 (AD0→GND) via mux  ·  pill 4-6Hz + ET 6-8Hz  ·  cad/connections_4imu.csv",
        ha="center", va="center", fontsize=6, color="#888")

# --- Save ---
out = r"C:\ForumProject\images\wiring_diagram_4imu_minimalist.svg"
import os
os.makedirs(os.path.dirname(out), exist_ok=True)
fig.savefig(out, format="svg", bbox_inches="tight", facecolor="white")
# Also PNG
fig.savefig(out.replace(".svg", ".png"), format="png", dpi=200, bbox_inches="tight", facecolor="white")
print(f"Saved: {out}")
print(f"Saved: {out.replace('.svg', '.png')}")
plt.close()
