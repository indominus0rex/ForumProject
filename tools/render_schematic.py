#!/usr/bin/env python3
"""Render Excalidraw schematic to PNG using Pillow."""
import json
import math
from PIL import Image, ImageDraw, ImageFont

INPUT = r"C:\ForumProject\docs\images\tremor_monitor_schematic_v2.excalidraw"
OUTPUT = r"C:\ForumProject\docs\images\tremor_monitor_schematic_v2.png"

with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

elements = data["elements"]

# Canvas size
W, H = 1400, 900
SCALE = 2  # for high DPI
img = Image.new("RGB", (W * SCALE, H * SCALE), "white")
draw = ImageDraw.Draw(img)

# Try to get a decent font
try:
    font = ImageFont.truetype("arial.ttf", 14 * SCALE)
    font_small = ImageFont.truetype("arial.ttf", 12 * SCALE)
    font_title = ImageFont.truetype("arial.ttf", 24 * SCALE)
except:
    try:
        font = ImageFont.truetype("/c/Windows/Fonts/arial.ttf", 14 * SCALE)
        font_small = ImageFont.truetype("/c/Windows/Fonts/arial.ttf", 12 * SCALE)
        font_title = ImageFont.truetype("/c/Windows/Fonts/arial.ttf", 24 * SCALE)
    except:
        font = ImageFont.load_default()
        font_small = font
        font_title = font


def scale(x, y):
    return x * SCALE, y * SCALE


def draw_rounded_rect(draw, xy, fill, outline, width=2, radius=8):
    radius = radius * SCALE
    x0, y0, x1, y1 = [c * SCALE for c in xy]
    draw.rounded_rectangle(xy=(x0, y0, x1, y1), radius=radius, fill=fill, outline=outline, width=width * SCALE)


def draw_text_in_box(draw, box, text, font, fill="black", align="center"):
    x, y, w, h = box
    x *= SCALE
    y *= SCALE
    w *= SCALE
    h *= SCALE
    lines = text.split("\n")
    line_height = font.size * 1.2
    total_height = line_height * len(lines)
    for i, line in enumerate(lines):
        ty = y + (h - total_height) / 2 + i * line_height
        if align == "center":
            draw.text((x + w / 2, ty), line, fill=fill, font=font, anchor="mt")
        else:
            draw.text((x + 5 * SCALE, ty), line, fill=fill, font=font)


# Draw elements in order
for elem in elements:
    etype = elem["type"]
    eid = elem["id"]
    x = elem.get("x", 0)
    y = elem.get("y", 0)
    w = elem.get("width", 0)
    h = elem.get("height", 0)

    stroke = elem.get("strokeColor", "#1e1e1e")
    fill = elem.get("backgroundColor", "transparent")
    sw = elem.get("strokeWidth", 2)

    if etype == "text":
        text = elem.get("text", "")
        font_size = elem.get("fontSize", 16)
        fill_color = elem.get("strokeColor", "#1e1e1e")
        align = elem.get("textAlign", "left")
        # Use appropriate font
        if font_size >= 20:
            use_font = font_title
        elif font_size <= 12:
            use_font = font_small
        else:
            use_font = font
        # For text without container, draw at x,y
        if not elem.get("containerId"):
            draw.text(scale(x, y), text, fill=fill_color, font=use_font)
        continue

    if etype == "rectangle":
        # Check if it has bound text
        has_text = any(b["type"] == "text" for b in elem.get("boundElements", []))
        rect_fill = fill if fill != "transparent" else None
        draw_rounded_rect(draw, (x, y, x + w, y + h), rect_fill, stroke, sw)
        continue

    if etype == "ellipse":
        ellipse_fill = fill if fill != "transparent" else None
        draw.ellipse([x * SCALE, y * SCALE, (x + w) * SCALE, (y + h) * SCALE],
                      fill=ellipse_fill, outline=stroke, width=sw * SCALE)
        continue

    if etype == "arrow":
        points = elem.get("points", [[0, 0], [0, 0]])
        # Points are relative to x,y
        abs_points = [(x + p[0], y + p[1]) for p in points]
        px = [p[0] * SCALE for p in abs_points]
        py = [p[1] * SCALE for p in abs_points]
        draw.line(list(zip(px, py)), fill=stroke, width=sw * SCALE)
        # Draw arrowhead at end
        end_x, end_y = px[-1], py[-1]
        prev_x, prev_y = px[-2], py[-2]
        angle = math.atan2(end_y - prev_y, end_x - prev_x)
        arrow_len = 10 * SCALE
        arrow_angle = math.pi / 6
        a1 = (end_x - arrow_len * math.cos(angle - arrow_angle),
              end_y - arrow_len * math.sin(angle - arrow_angle))
        a2 = (end_x - arrow_len * math.cos(angle + arrow_angle),
              end_y - arrow_len * math.sin(angle + arrow_angle))
        draw.polygon([(end_x, end_y), a1, a2], fill=stroke)
        continue

    if etype == "line":
        points = elem.get("points", [[0, 0], [0, 0]])
        abs_points = [(x + p[0], y + p[1]) for p in points]
        px = [p[0] * SCALE for p in abs_points]
        py = [p[1] * SCALE for p in abs_points]
        draw.line(list(zip(px, py)), fill=stroke, width=sw * SCALE)
        continue

# Now draw bound text elements
text_map = {e["id"]: e for e in elements if e["type"] == "text"}
for elem in elements:
    for binding in elem.get("boundElements", []):
        if binding["type"] == "text":
            text_id = binding["id"]
            if text_id in text_map:
                t = text_map[text_id]
                text = t.get("text", "")
                font_size = t.get("fontSize", 16)
                fill_color = t.get("strokeColor", "#1e1e1e")
                align = t.get("textAlign", "left")
                va = t.get("verticalAlign", "top")

                # Determine font
                if font_size >= 20:
                    use_font = font_title
                elif font_size <= 12:
                    use_font = font_small
                else:
                    use_font = font

                # Get the container (parent element) bounds
                container = elem
                cx, cy = container["x"], container["y"]
                cw = container.get("width", 0)
                ch = container.get("height", 0)

                if align == "center":
                    tx = cx + cw / 2
                    anchor = "mt"
                else:
                    tx = cx + 3 * SCALE
                    anchor = "lt"

                if va == "middle":
                    ty = cy + ch / 2
                    if anchor == "mt":
                        anchor = "mm"
                    else:
                        anchor = "lm"
                elif va == "bottom":
                    ty = cy + ch - 3 * SCALE
                else:
                    ty = cy + 2 * SCALE

                draw.text(scale(tx, ty), text, fill=fill_color, font=use_font, anchor=anchor)

img.save(OUTPUT, "PNG")
print(f"Saved {OUTPUT}")
print(f"Size: {img.size}")
