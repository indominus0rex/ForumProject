# Obsidian Vault Structure for Forum Project

**Goal:** Define the folder hierarchy, file placement rules, and linking conventions for organizing the Forum Project's files into an Obsidian vault.

**Assumptions:**
- Vault location is user's choice (not specified here).
- Vault is personal knowledge management — not a git mirror of the repo.
- `Datasets/` (~200k+ files) cannot reasonably be copied; it must be indexed.
- Binary files (`.py`, `.csv`, `.FCStd`, `.png`, `.exe`, `.html`) stay in the repo; vault references them.
- Markdown/text docs can be either copied or linked depending on whether they're "living notes" or "source docs."

---

## Vault Folder Structure

```
Obsidian Vault/
├── .obsidian/                    # App config (auto-created)
│   ├── app.json
│   ├── appearance.json
│   └── core-plugins.json
├── _Attachments/                 # Images, embedded files
├── _Templates/                   # Note templates
├── 00-Home/                      # MOC + entry points
│   ├── Home.md                   # Main landing page
│   └── MOC.md                    # Map of Content index
├── 01-Project-Overview/          # What + why
│   ├── Project Overview.md
│   ├── System Architecture.md
│   ├── Session Log.md
│   └── Data and Datasets.md
├── 02-Hardware/                  # Physical build
│   ├── Hardware Index.md
│   ├── Strap and LRA Design.md
│   ├── Breathable IMU Mount Design.md
│   ├── Strapping Materials.md
│   ├── Assembly Checklist.md
│   ├── Validation Test Procedures.md
│   ├── LRA Assembly Guide.md
│   ├── LRA Mounting Instructions.md
│   ├── LRA Wiring Instructions.md
│   ├── IMU LRA Placement.md
│   ├── Component Positions.md
│   ├── Refined Hardware Design.md
│   ├── Hardware Design Research.md
│   ├── Integration Guide.md
│   ├── PIN Assignments.md
│   ├── Wiring Diagram Design.md
│   ├── Wiring Diagrams.md
│   ├── Diagram Prompt Summary.md
│   ├── Wiring Diagram Completion Summary.md
│   └── Embed README.md
├── 03-Firmware/                  # ESP32 code + docs
│   ├── Firmware Index.md
│   ├── CLAUDE.md
│   ├── CLAUDE-root.md
│   ├── AGENTS.md
│   ├── Original README.md
│   ├── System Architecture Improvements.md
│   ├── Multi-IMU Abstraction Plan.md
│   ├── Multi-IMU Abstraction Design.md
│   └── Session Changes Summary.md
├── 04-Host-Scripts/              # Python training/analysis
│   ├── Host Scripts Index.md
│   └── Automation Recommendations.md
├── 05-Data-Analysis/             # Analysis outputs
│   └── Analysis Index.md
├── 06-Research/                  # Literature + findings
│   ├── Research Index.md
│   ├── Knowledge Base.md
│   ├── Web Research 2026-08-27.md
│   ├── Image Plan.md
│   └── Preferences.md
├── 07-CAD/                       # 3D models + drawings
│   └── CAD Index.md
├── 08-Media/                     # Images, diagrams, prompts
│   └── Media Index.md
└── 09-Archive/                   # Superseded + historical
    └── Archive Index.md
```

---

## File Placement Rules

### Rule 1: Copy vs. Link

| File Type | Strategy | Rationale |
|-----------|----------|-----------|
| Markdown docs (`.md`) | **Copy** into vault | Living notes; may annotate in vault |
| Text files (`.txt`) | **Copy** + rename to `.md` | Obsidian renders `.md` better |
| Code (`.py`) | **Link** via `file://` URI | Source of truth is repo |
| Data (`.csv`) | **Link** | Too large; repo owns data |
| CAD (`.FCStd`, `.swp`) | **Link** | Binary; repo owns files |
| Images (`.png`, `.jpg`, `.svg`) | **Copy** to `_Attachments/` if embedded in notes; **Link** if standalone | Obsidian embeds better from attachments |
| HTML diagrams | **Link** | View in browser, not Obsidian |
| Executables (`.exe`) | **Link** | Not vault content |

### Rule 2: Naming Conventions

- **Notes (`.md`):** Title Case, no date prefix — e.g., `Strap and LRA Design.md`
- **Index/MOC files:** `<Folder Name> Index.md` or just `Index.md` — e.g., `Hardware Index.md`
- **Dates in filenames:** Avoid (Obsidian has date properties)
- **Spaces in filenames:** Allowed (Obsidian handles them)
- **Special characters:** Avoid `<>:"/\|?*` in note names

### Rule 3: Folder Numbering

- `00-` prefix for entry points (Home)
- `01-` through `09-` for content categories
- Numbers create deterministic sort order in Obsidian's file explorer
- Gaps allow future insertion (e.g., `05b-` if needed)

### Rule 4: Index/MOC Convention

Every folder except `_Attachments` and `_Templates` gets an `Index.md` that:
- Lists all notes in that folder with `[[wikilinks]]`
- Briefly describes each note's purpose
- Links to related folders' indexes

---

## Linking Strategy

### Internal Vault Links (wikilinks)

```markdown
[[Strap and LRA Design]]
[[Hardware Index]]
[[Project Overview]]
```

### External Links (repo files)

```markdown
[file:: C:\ForumProject\firmware\embedded_main_hsp.py]
```

Or use Obsidian's URI format:

```markdown
[Open in Editor](file:///C:/ForumProject/firmware/embedded_main_hsp.py)
```

### Image Embeds

For images copied to `_Attachments/`:

```markdown
![[wiring_diagram_4imu_minimalist.png]]
```

For images linked from repo:

```markdown
![C:\ForumProject\images\wiring_diagram_4imu_minimalist.png](file:///C:/ForumProject/images/wiring_diagram_4imu_minimalist.png)
```

---

## Tag Conventions

Apply these tags in note frontmatter or inline:

```yaml
---
tags:
  - hardware
  - firmware
  - host
  - research
  - cad
  - data
  - diagram
  - deferred
  - locked
  - superseded
  - index
---
```

| Tag | Meaning |
|-----|---------|
| `hardware` | Physical components, mounting, wiring |
| `firmware` | ESP32 code, MicroPython, HSP pipeline |
| `host` | Python scripts, training, analysis |
| `research` | Literature, findings, sources |
| `cad` | 3D models, drawings, manufacturing |
| `data` | Datasets, CSVs, pilot sessions |
| `diagram` | Visual references, schematics |
| `deferred` | Planned but not yet built |
| `locked` | Decisions that should not change |
| `superseded` | Replaced by newer docs |
| `index` | MOC/index note |

---

## Frontmatter Template

Every note should have:

```yaml
---
title: <Note Title>
created: <YYYY-MM-DD>
modified: <YYYY-MM-DD>
tags: []
source: <original file path in repo, or "vault-created">
---
```

---

## Source File → Vault Mapping

This table defines exactly where each file in the repo maps to in the vault.

| Repo Path | Vault Path | Action |
|-----------|------------|--------|
| `CLAUDE.md` | `03-Firmware/CLAUDE-root.md` | Copy |
| `docs/CLAUDE.md` | `03-Firmware/CLAUDE.md` | Copy |
| `docs/AGENTS.md` | `03-Firmware/AGENTS.md` | Copy |
| `docs/README.md` | `03-Firmware/Original README.md` | Copy |
| `docs/SYSTEM_ARCHITECTURE_IMPROVEMENTS.md` | `03-Firmware/System Architecture Improvements.md` | Copy |
| `docs/superpowers/plans/2026-08-27-multi-imu-sensor-abstraction.md` | `03-Firmware/Multi-IMU Abstraction Plan.md` | Copy |
| `docs/superpowers/specs/2026-08-27-multi-imu-sensor-abstraction-design.md` | `03-Firmware/Multi-IMU Abstraction Design.md` | Copy |
| `docs/session_changes_summary.md` | `03-Firmware/Session Changes Summary.md` | Copy |
| `docs/strap_and_lra_design.md` | `02-Hardware/Strap and LRA Design.md` | Copy |
| `docs/assembly_checklist.md` | `02-Hardware/Assembly Checklist.md` | Copy |
| `docs/breathable_imu_mount_design.md` | `02-Hardware/Breathable IMU Mount Design.md` | Copy |
| `docs/LRA-Assembly-Guide.md` | `02-Hardware/LRA Assembly Guide.md` | Copy |
| `docs/lra-mounting-instructions.md` | `02-Hardware/LRA Mounting Instructions.md` | Copy |
| `docs/lra-wiring-instructions.md` | `02-Hardware/LRA Wiring Instructions.md` | Copy |
| `docs/validation_test_procedures_elastic_strap_velcro.md` | `02-Hardware/Validation Test Procedures.md` | Copy |
| `docs/imu_lra_placement.txt` | `02-Hardware/IMU LRA Placement.md` | Copy + rename |
| `docs/component_positions.txt` | `02-Hardware/Component Positions.md` | Copy + rename |
| `docs/strapping_materials.txt` | `02-Hardware/Strapping Materials.md` | Copy + rename |
| `docs/refined_hardware_design.md` | `02-Hardware/Refined Hardware Design.md` | Copy |
| `docs/hardware_design_research.md` | `02-Hardware/Hardware Design Research.md` | Copy |
| `docs/integration_guide.md` | `02-Hardware/Integration Guide.md` | Copy |
| `docs/EMBED_README.md` | `02-Hardware/Embed README.md` | Copy |
| `docs/image-plan.md` | `06-Research/Image Plan.md` | Copy |
| `docs/research_web_2026-08-27.md` | `06-Research/Web Research 2026-08-27.md` | Copy |
| `PIN_ASSIGNMENTS.md` | `02-Hardware/PIN Assignments.md` | Copy |
| `WIRING_DIAGRAM_DESIGN.md` | `02-Hardware/Wiring Diagram Design.md` | Copy |
| `DIAGRAM_PROMPT_SUMMARY.md` | `02-Hardware/Diagram Prompt Summary.md` | Copy |
| `WIRING_DIAGRAM_COMPLETION_SUMMARY.md` | `02-Hardware/Wiring Diagram Completion Summary.md` | Copy |
| `AUTOMATION_RECOMMENDATIONS.md` | `04-Host-Scripts/Automation Recommendations.md` | Copy |
| `knowledge.md` | `06-Research/Knowledge Base.md` | Copy |
| `preference.md` | `06-Research/Preferences.md` | Copy |
| `wearable_tremor_wiring_diagram.html` | `08-Media/` (linked) | Link |
| `images/wiring_diagram_4imu_minimalist.png` | `_Attachments/` or `08-Media/` | Copy or link |
| `images/wiring_diagram_4imu_minimalist.svg` | `_Attachments/` or `08-Media/` | Copy or link |
| `images/wiring_diagram_v2.png` | `_Attachments/` or `08-Media/` | Copy or link |
| `images/wiring_diagram.jpg` | `_Attachments/` or `08-Media/` | Copy or link |
| `images/circuit.jpg` | `_Attachments/` or `08-Media/` | Copy or link |
| `images/tremor_examples.png` | `_Attachments/` or `08-Media/` | Copy or link |
| `images/graph_1.png` | `_Attachments/` or `08-Media/` | Copy or link |
| `images/circuit_multiplexer.excalidraw` | `08-Media/` | Link |
| `docs/images/assembled-wearable-device.png` | `_Attachments/` | Copy |
| `docs/images/assembled-wearable-device.svg` | `_Attachments/` | Copy |
| `docs/images/lra-pocket-diagram.svg` | `_Attachments/` | Copy |
| `docs/images/strap-layout.svg` | `_Attachments/` | Copy |
| `docs/images/wiring-overview.svg` | `_Attachments/` | Copy |
| `firmware/**` | `03-Firmware/` (linked) | Link |
| `host_scripts/**` | `04-Host-Scripts/` (linked) | Link |
| `analysis/**` | `05-Data-Analysis/` (linked) | Link |
| `cad/**` | `07-CAD/` (linked) | Link |
| `Datasets/**` | `01-Project-Overview/Data and Datasets.md` (indexed) | Index only |
| `tools/**` | `07-CAD/` or `04-Host-Scripts/` (linked) | Link |
| `sessions/**` | `09-Archive/` (linked) | Link |
| `session-ses_fbc7.md` | `09-Archive/` (linked) | Link |
| `test.html` | — | Exclude |
| `data.txt` | `01-Project-Overview/Data and Datasets.md` (indexed) | Index only |
| `wiring_diagram_prompt_*.txt` | `08-Media/` (linked) | Link |
| `REVISED_WIRING_DIAGRAM_PROMPT.txt` | `09-Archive/` (linked) | Link |
| `wearable_tremor_wiring_diagram.html.backup` | `09-Archive/` (linked) | Link |
| `preference` (no ext) | — | Exclude (duplicate of `.md`) |

---

## Vault Config Files

### `.obsidian/app.json`

```json
{
  "alwaysUpdateLinks": true,
  "useMarkdownLinks": false,
  "newLinkFormat": "shortest",
  "attachmentFolderPath": "_Attachments",
  "defaultViewMode": "source",
  "livePreview": true,
  "showLineNumber": true,
  "readableLineLength": true
}
```

### `.obsidian/appearance.json`

```json
{
  "theme": "moonstone",
  "accentColor": "",
  "baseFontSize": 16
}
```

### `.obsidian/core-plugins.json`

```json
[
  "file-explorer",
  "global-search",
  "switcher",
  "graph",
  "backlink",
  "canvas",
  "outgoing-link",
  "tag-pane",
  "page-preview",
  "daily-notes",
  "templates",
  "note-composer",
  "command-palette",
  "editor-status",
  "bookmarks",
  "outline",
  "word-count",
  "file-recovery"
]
```

---

## Home Note Template

```markdown
---
title: Forum Project — Home
created: 2026-09-01
tags:
  - index
---

# Forum Project

Wearable Parkinson's tremor monitoring system: IMU sensing → feature extraction → ML classification → haptic feedback.

## Maps of Content

- [[Hardware Index|Hardware]]
- [[Firmware Index|Firmware]]
- [[Host Scripts Index|Host Scripts]]
- [[Analysis Index|Data Analysis]]
- [[Research Index|Research]]
- [[CAD Index|CAD]]
- [[Media Index|Media]]
- [[Archive Index|Archive]]
- [[Session Log]]
- [[Data and Datasets]]

## Quick Facts

| Field | Value |
|-------|-------|
| Repo | `C:\ForumProject` |
| Branch | ASUS |
| Build | 4-IMU (locked 2026-08-27) |
| LRAs | Deferred |
| Firmware | MicroPython ESP32 |
| Host | Python 3.11 + scikit-learn |
```

---

## Index Note Template

```markdown
# <Folder Name> Index

## Notes

- [[<Note Name>]] — <one-line description>

## External Links

- `C:\ForumProject\<path>` — <description>
```

---

## Open Questions

1. **Vault location:** Where should the vault live? (e.g., `C:\Users\Admin\Documents\Obsidian Vault`, `C:\Users\Admin\Obsidian\ForumProject`, etc.)
2. **Copy vs. link for docs:** Should markdown docs be copied (allowing vault annotations) or linked (single source of truth)?
3. **Image handling:** Copy images to `_Attachments/` for better Obsidian embedding, or link to repo to save space?
4. **Git for vault:** Should the vault itself be a git repo to track note changes?
5. **Daily notes:** Enable daily notes plugin for POSN study session logging?
6. **Canvas:** Use Obsidian Canvas for system architecture visualization?

---

## Risks & Tradeoffs

| Risk | Impact | Mitigation |
|------|--------|------------|
| Copied docs drift out of sync | Vault becomes stale | Periodic re-copy script; or link-only for volatile docs |
| `file://` links break on repo move | Broken links in vault | Use relative paths if vault is sibling to repo |
| Too many index notes | Clutter | Only create indexes for folders with 3+ items |
| Tag inconsistency | Poor discoverability | Enforce tag conventions in templates |
| Vault bloat from images | Slow sync | Link large images; only copy small SVGs |
