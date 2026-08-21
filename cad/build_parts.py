"""Parametric parts for the tremor-detection wiring diagram.

Run inside FreeCAD:
    freecadcmd build_parts.py

Or paste into FreeCAD Python console.

Generates STEP + STL in parts/ for each component. Vendor parts (ESP32, GY-521)
need manual STEP import from GrabCAD/TraceParts - see README.
"""
import os
import sys
from pathlib import Path

import FreeCAD as App
import Part
import Sketcher
import Import

sys.path.insert(0, str(Path(__file__).parent))
from _lib.parse_connections import load_connections

OUT_DIR = Path(__file__).parent / "parts"
OUT_DIR.mkdir(exist_ok=True)

# All dimensions in mm
PARTS = {}


def make_perfboard(cols=30, rows=15, pitch=2.54, hole_dia=1.0, thickness=1.6):
    """Perforated board with grid of holes."""
    doc = App.newDocument("perfboard")
    width = (cols - 1) * pitch
    height = (rows - 1) * pitch
    half_w = width / 2
    half_h = height / 2

    # Body sketch on XY plane
    body = doc.addObject("Part::Box", "Board")
    body.Length = width
    body.Width = height
    body.Height = thickness
    body.Placement = App.Placement(
        App.Vector(-half_w, -half_h, 0), App.Rotation()
    )

    # Holes as cylinders, then cut
    hole = doc.addObject("Part::Cylinder", "HoleMaster")
    hole.Radius = hole_dia / 2
    hole.Height = thickness * 2  # overshoot to ensure clean cut
    hole.Placement = App.Placement(App.Vector(0, 0, -thickness / 2), App.Rotation())

    # Compound with master hole
    compound = doc.addObject("Part::MultiFuse", "MasterCompound")
    compound.Shapes = [hole]

    # Pattern: linear in X and Y
    # FreeCAD doesn't have a direct "linear pattern of a feature" like SW.
    # Workaround: create N holes manually, fuse, then cut.
    holes = [hole]
    for ix in range(cols):
        for iy in range(rows):
            if ix == 0 and iy == 0:
                continue
            h = doc.addObject("Part::Cylinder", f"Hole_{ix}_{iy}")
            h.Radius = hole_dia / 2
            h.Height = thickness * 2
            h.Placement = App.Placement(
                App.Vector(
                    -half_w + ix * pitch,
                    -half_h + iy * pitch,
                    -thickness / 2,
                ),
                App.Rotation(),
            )
            holes.append(h)

    all_holes = doc.addObject("Part::MultiFuse", "AllHoles")
    all_holes.Shapes = holes

    # Cut holes from board
    cut = doc.addObject("Part::Cut", "BoardCut")
    cut.Base = body
    cut.Tool = all_holes
    doc.recompute()

    # Color FR4 green
    cut.ViewObject.ShapeColor = (0.0, 0.4, 0.0)

    export_part(doc, "perfboard")
    return doc


def make_resistor(name, body_len=6.3, body_dia=2.3, lead_len=15, lead_dia=0.6):
    """Axial through-hole resistor (carbon film / metal film style)."""
    doc = App.newDocument(name)
    body = doc.addObject("Part::Cylinder", "Body")
    body.Radius = body_dia / 2
    body.Height = body_len
    body.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(1, 0, 0), 90))
    # Cylinder is along Z by default - rotate so axis is along X
    body.ViewObject.ShapeColor = (0.85, 0.75, 0.55)

    # Leads (two cylinders along X axis)
    for i, sign in enumerate((-1, 1)):
        lead = doc.addObject("Part::Cylinder", f"Lead{i}")
        lead.Radius = lead_dia / 2
        lead.Height = lead_len + body_len / 2
        lead.Placement = App.Placement(
            App.Vector(sign * body_len / 4, 0, 0),
            App.Rotation(App.Vector(0, 1, 0), 90),
        )
        lead.ViewObject.ShapeColor = (0.75, 0.75, 0.75)

    # Fuse body + leads
    fused = doc.addObject("Part::MultiFuse", "ResistorBody")
    fused.Shapes = [body] + [doc.getObject(f"Lead{i}") for i in range(2)]
    doc.recompute()

    export_part(doc, name)
    return doc


def make_led(name, body_len=8.6, body_dia=5.0, flange_dia=5.6, flange_h=1.0, lead_len=15):
    """5mm standard LED with flange."""
    doc = App.newDocument(name)
    # Dome
    dome = doc.addObject("Part::Sphere", "Dome")
    dome.Radius = body_dia / 2
    dome.Placement = App.Placement(App.Vector(0, 0, flange_h + body_dia / 2 - 0.5), App.Rotation())

    # Flange (cylinder)
    flange = doc.addObject("Part::Cylinder", "Flange")
    flange.Radius = flange_dia / 2
    flange.Height = flange_h
    flange.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation())

    # Fuse
    body = doc.addObject("Part::MultiFuse", "Body")
    body.Shapes = [dome, flange]
    body.ViewObject.ShapeColor = (1.0, 0.0, 0.0)  # red LED (can recolor later)
    body.ViewObject.Transparency = 40

    # Leads - anode (longer) and cathode (shorter, with flag)
    for i, sign in enumerate((-1, 1)):
        lead = doc.addObject("Part::Cylinder", f"Lead{i}")
        lead.Radius = 0.5 / 2
        lead.Height = lead_len + flange_h
        lead.Placement = App.Placement(
            App.Vector(sign * 1.27, 0, -lead_len / 2 + flange_h / 2),
            App.Rotation(App.Vector(1, 0, 0), 90),
        )
        lead.ViewObject.ShapeColor = (0.75, 0.75, 0.75)

    fused = doc.addObject("Part::MultiFuse", "LedFull")
    fused.Shapes = [body] + [doc.getObject(f"Lead{i}") for i in range(2)]
    doc.recompute()

    export_part(doc, name)
    return doc


def make_to92(name):
    """TO-92 transistor package (2N7000). Half-cylinder body, 3 leads."""
    doc = App.newDocument(name)
    # Body: half-cylinder (D shape)
    # Easier: full cylinder, then add a flat side via cut
    body_cyl = doc.addObject("Part::Cylinder", "BodyRaw")
    body_cyl.Radius = 2.4 / 2
    body_cyl.Height = 4.0
    body_cyl.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(1, 0, 0), 90))

    # Cut box from one side to make D-shape
    cutter = doc.addObject("Part::Box", "Cutter")
    cutter.Length = 5
    cutter.Width = 5
    cutter.Height = 5
    cutter.Placement = App.Placement(
        App.Vector(-2.5, 0, -2.5),
        App.Rotation(App.Vector(0, 0, 1), 0),
    )
    body = doc.addObject("Part::Cut", "Body")
    body.Base = body_cyl
    body.Tool = cutter
    body.ViewObject.ShapeColor = (0.1, 0.1, 0.1)

    # 3 leads
    for i, x_off in enumerate((-1.27, 0, 1.27)):
        lead = doc.addObject("Part::Cylinder", f"Lead{i}")
        lead.Radius = 0.45 / 2
        lead.Height = 15
        lead.Placement = App.Placement(
            App.Vector(x_off, 0, -7.5),
            App.Rotation(App.Vector(1, 0, 0), 90),
        )
        lead.ViewObject.ShapeColor = (0.75, 0.75, 0.75)

    fused = doc.addObject("Part::MultiFuse", "Full")
    fused.Shapes = [body] + [doc.getObject(f"Lead{i}") for i in range(3)]
    doc.recompute()

    export_part(doc, name)
    return doc


def make_do35(name):
    """DO-35 axial diode (1N4148). Glass body with band."""
    doc = App.newDocument(name)
    body = doc.addObject("Part::Cylinder", "Body")
    body.Radius = 1.85 / 2
    body.Height = 3.6
    body.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(1, 0, 0), 90))
    body.ViewObject.ShapeColor = (0.95, 0.95, 0.95)
    body.ViewObject.Transparency = 30

    # Leads
    for i, sign in enumerate((-1, 1)):
        lead = doc.addObject("Part::Cylinder", f"Lead{i}")
        lead.Radius = 0.5 / 2
        lead.Height = 30
        lead.Placement = App.Placement(
            App.Vector(sign * 1.0, 0, 0),
            App.Rotation(App.Vector(0, 1, 0), 90),
        )
        lead.ViewObject.ShapeColor = (0.75, 0.75, 0.75)

    # Cathode band (small black ring near one end)
    band = doc.addObject("Part::Cylinder", "Band")
    band.Radius = 1.85 / 2 + 0.05
    band.Height = 1.0
    band.Placement = App.Placement(
        App.Vector(1.3, 0, 0),
        App.Rotation(App.Vector(0, 1, 0), 90),
    )
    band.ViewObject.ShapeColor = (0.05, 0.05, 0.05)

    fused = doc.addObject("Part::MultiFuse", "Full")
    fused.Shapes = [body, band] + [doc.getObject(f"Lead{i}") for i in range(2)]
    doc.recompute()

    export_part(doc, name)
    return doc


def make_lra(name, dia=10.0, height=2.7):
    """Coin-type Linear Resonant Actuator. Simple cylinder with two pads."""
    doc = App.newDocument(name)
    body = doc.addObject("Part::Cylinder", "Body")
    body.Radius = dia / 2
    body.Height = height
    body.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(1, 0, 0), 90))
    body.ViewObject.ShapeColor = (0.6, 0.6, 0.65)
    body.ViewObject.ShapeColor = (0.7, 0.7, 0.72)

    # Two pads (solder tabs) on top face
    for i, x_off in enumerate((-3.0, 3.0)):
        pad = doc.addObject("Part::Cylinder", f"Pad{i}")
        pad.Radius = 1.2
        pad.Height = 0.3
        pad.Placement = App.Placement(
            App.Vector(x_off, 0, height / 2 + 0.15),
            App.Rotation(App.Vector(1, 0, 0), 90),
        )
        pad.ViewObject.ShapeColor = (0.85, 0.85, 0.85)

    # Leads
    for i, x_off in enumerate((-3.0, 3.0)):
        lead = doc.addObject("Part::Cylinder", f"Lead{i}")
        lead.Radius = 0.4
        lead.Height = 8
        lead.Placement = App.Placement(
            App.Vector(x_off, 0, height / 2 + 4),
            App.Rotation(App.Vector(1, 0, 0), 90),
        )
        lead.ViewObject.ShapeColor = (0.75, 0.75, 0.75)

    fused = doc.addObject("Part::MultiFuse", "Full")
    fused.Shapes = (
        [body]
        + [doc.getObject(f"Pad{i}") for i in range(2)]
        + [doc.getObject(f"Lead{i}") for i in range(2)]
    )
    doc.recompute()

    export_part(doc, name)
    return doc


def export_part(doc, name):
    """Save doc as STEP and STL."""
    doc.recompute()
    step_path = OUT_DIR / f"{name}.step"
    stl_path = OUT_DIR / f"{name}.stl"
    Import.export([doc.Objects[-1]], str(step_path))
    # STL via mesh
    import Mesh
    Mesh.export([doc.Objects[-1]], str(stl_path))
    print(f"  -> {step_path.name}, {stl_path.name}")
    doc.saveAs(str(OUT_DIR / f"{name}.FCStd"))


def main():
    print("Building parts...")
    make_perfboard()
    make_resistor("RES_220")
    make_resistor("RES_10K")
    make_led("LED_5MM")
    make_to92("2N7000")
    make_do35("1N4148")
    make_lra("LRA_COIN")
    print(f"\nAll parts in {OUT_DIR}")
    print("Vendor parts (ESP32-DevKitC, GY-521): import STEP manually from GrabCAD/TraceParts")


if __name__ == "__main__":
    main()
