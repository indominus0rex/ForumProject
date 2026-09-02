# Remove Anatomical Placement Texts from Wiring Diagram

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Remove the anatomical placement description texts from the wiring diagram notes section while preserving all connection diagrams, component labels, legends, specifications, and configuration notes.

**Architecture:** Modify the HTML file to delete specific paragraph elements containing anatomical placement references while maintaining all other diagram elements and technical details.

**Tech Stack:** HTML file modification using precise text removal.

---

### Task 1: Remove Anatomical Placement Paragraph from Notes Section

**Objective:** Delete the anatomical placement suggestions paragraph from the notes section of the wiring diagram HTML file, keeping all other content intact.

**Files:**
- Modify: `C:\ForumProject\wearable_tremor_wiring_diagram.html`

**Step 1: Identify exact text to remove**

Locate the anatomical placement paragraph in the notes section:
```html
<h3>Anatomical Placement (suggested):</h3>
<p>
    • IMU1: Dorsal hand center (global motion)<br>
    • IMU2: Thenar eminence (thumb movement)<br>
    • IMU3: Thumb CMC joint (thumb rotation)<br>
    • IMU4: Forearm proximal wrist (wrist flexion/extension)<br>
    • LRA1: Dorsal hand (position feedback)<br>
    • LRA2: Palmar - thenar (thumb feedback)<br>
    • LRA3: Palmar - hypothenar (pinky finger feedback)
</p>
```

**Step 2: Write the modification**

Replace the anatomical placement paragraph with an empty paragraph or remove it entirely while keeping the h3 header if desired, or remove both. Based on context, removing just the paragraph content while keeping the header as "Anatomical Placement (suggested):" with no content below seems appropriate, but the user said "remove the position just only connections" which suggests removing the positional/textual descriptions entirely.

Actually, re-reading the user request: "remove the position just only connections" - they want to keep ONLY the connections, implying they want to remove all labels/text except the connection lines themselves. But looking at the history, they previously said "the wire aren't properly connected" and wanted a diagram with "clear connections and labels", then said "it doesn't open for me" and we fixed that, then said "the wire aren't properly connected" and we improved it, and now they want to "remove the position just only connections".

Given the context, I believe they want to remove the anatomical placement descriptive texts (the labels explaining where each sensor goes on the hand) but keep:
- Component labels (IMU1, LRA1, etc.)
- Pin labels (GPIO22, SCL, etc.)
- Connection lines
- Legend
- Specifications table
- Configuration notes
- Power/ground rails

So specifically, remove the anatomical placement paragraph from the notes.

**Step 3: Implement the change**

Remove the following block from lines 383-391:
```html
            <h3>Anatomical Placement (suggested):</h3>
            <p>
                • IMU1: Dorsal hand center (global motion)<br>
                • IMU2: Thenar eminence (thumb movement)<br>
                • IMU3: Thumb CMC joint (thumb rotation)<br>
                • IMU4: Forearm proximal wrist (wrist flexion/extension)<br>
                • LRA1: Dorsal hand (position feedback)<br>
                • LRA2: Palmar - thenar (thumb feedback)<br>
                • LRA3: Palmar - hypothenar (pinky finger feedback)
            </p>
```

Replace with nothing (complete removal) or replace with a placeholder comment. Complete removal is cleaner.

**Step 4: Verify the change**

After removal, verify that:
- All SVG components and connections remain intact
- Legend is still present
- Specifications table is still present
- Configuration notes are still present
- Only the anatomical placement descriptive text is removed
- HTML structure remains valid

**Step 5: Run validation**

Open the modified HTML in a web browser to confirm:
- Diagram renders correctly
- All connections are visible
- No anatomical placement texts appear
- All other labels (component names, pin names, legend, specs) remain

**Step 6: Commit**

```bash
git add C:\ForumProject\wearable_tremor_wiring_diagram.html
git commit -m "docs: remove anatomical placement texts from wiring diagram notes per user request"
```

---

## Files Likely to Change

- `C:\ForumProject\wearable_tremor_wiring_diagram.html` (primary modification)

## Tests / Validation

**Validation checks:**
1. Anatomical placement texts removed: Verify the specific phrases "Dorsal hand center", "Thenar eminence", "Thumb CMC joint", "Forearm proximal wrist", "Dorsal hand", "Palmar - thenar", "Palmar - hypothenar" are no longer present in the file
2. Diagram integrity: Confirm all SVG elements (components, connections, labels) remain present and correctly positioned
3. Legend preservation: Verify power/ground/I2C/PWM/LED legend items still exist
4. Specifications table: Confirm component specifications table is unchanged
5. Configuration notes: Verify firmware configuration notes remain intact
6. HTML validity: Ensure no broken tags or structural issues introduced

**Manual verification steps:**
- Open `C:\ForumProject\wearable_tremor_wiring_diagram.html` in Chrome/Firefox/Edge
- Visually confirm anatomical placement descriptions are gone from notes
- Confirm all connection lines and component labels are still visible
- Verify legend, specifications, and configuration notes sections are intact
- Check that removing the text didn't affect layout or cause overlapping elements

## Risks, Tradeoffs, and Open Questions

**Risks:**
- Accidentally removing similar-looking text that should remain (e.g., in component labels)
- Breaking HTML structure if removal is not precise
- User may actually want more text removed than just anatomical placement

**Tradeoffs:**
- Less contextual information about ideal sensor placement
- Cleaner, more focused diagram on pure electrical connections
- May require external documentation for placement guidance

**Open questions:**
- Should the "Anatomical Placement (suggested):" header also be removed, or just the paragraph below it?
- Are there any other textual descriptions in the diagram that should be considered for removal?
- Does the user want to keep ANY textual labels, or just the connection lines themselves?

**Assumptions:**
- The anatomical placement texts are exclusively located in the notes section as identified
- User wants to keep all other labels (component names, pin names, legend, etc.)
- Only the descriptive placement sentences should be removed, not the structural diagram elements