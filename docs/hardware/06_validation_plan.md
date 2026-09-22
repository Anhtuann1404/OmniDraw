# Hardware Validation Plan

**Subsystem:** System-Wide Hardware Verification  
**Document Version:** V1.1  
**Status:** PROPOSED VALIDATION PLAN / TBD  

---

## 1. Purpose

This document defines the experimental verification protocols, bench test setups, measurement instruments, and target criteria required to validate the physical performance, kinematic repeatability, structural rigidity, and operational reliability of OmniDraw Plotter V1.

---

## 2. Test Verification Matrix

| Test ID | Test Description | Target Subsystem | Acceptance Criterion | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TP-01** | Kinematic Coupling Repeatability | Tool Changer V1.1 / Receiver V1 | Target: $< 10\,\mu\text{m}$ (`TARGET / NOT VALIDATED`) | PROPOSED TEST PROTOCOL |
| **TP-02** | Magnetic Preload & Separation Force | Tool Changer V1.1 / Dock | Preload $18 - 22\text{ N}$ (`TARGET / TO BE VALIDATED`) | PROPOSED TEST PROTOCOL |
| **TP-03** | Automated Tool-Change Cycle Reliability | Tool Changer & CoreXY | Zero drop failures across test run (`TARGET / TBD`) | PROPOSED TEST PROTOCOL |
| **TP-04** | Z-Lifter Compliance & Nib Pressure | Z-Lifter & Carriage | Nib force $50 - 100\text{ gf}$ ($\approx 0.49 - 0.98\text{ N}$) (`CONCEPT TARGET / TO BE VALIDATED IN Q3`) | PROPOSED TEST PROTOCOL |
| **TP-05** | CoreXY Orthogonality & Dimensional Error | CoreXY Gantry & Chassis | Orthogonality Acceptance Criterion: TBD Q4 | PROPOSED TEST PROTOCOL |
| **TP-06** | Poka-Yoke Reverse-Orientation Rejection | Receiver Key Pin / Tool Notch | Positive mechanical interception before ball engagement (Margin: $+0.170\text{ mm}$) | PROPOSED TEST PROTOCOL |

---

## 3. Detailed Test Protocols

### 3.1 TP-01: Kinematic Coupling Repeatability Test
- **Objective:** Measure the 6-DOF repositioning repeatability of the Pen Slider V1.1 when repeatedly coupled to the Carriage Receiver Plate V1.
- **Apparatus:** 
  - Precision digital dial indicator ($0.001\text{ mm} / 1\,\mu\text{m}$ resolution) or high-magnification optical inspection microscope.
  - Rigid mounting fixture clamping the Receiver Plate.
- **Procedure:**
  1. Secure the Receiver Plate in the rigid bench fixture.
  2. Dock the Pen Slider sleeve and zero the indicator probe against the reference datum block.
  3. Automatically or manually undock the tool sleeve, rotate/disturb slightly, and re-engage the coupling.
  4. Record the indicator deviation across 30 consecutive docking cycles for $X, Y$, and $Z$ axes.
- **Research / Aspirational Design Target:**
  - Repositioning Repeatability: $< 10\,\mu\text{m}$
  - **Status:** `TARGET / NOT VALIDATED`
  - **Formal Acceptance Criterion:** `TBD after prototype measurement capability is confirmed.`

### 3.2 TP-02: Magnetic Preload & Separation Force Test
- **Objective:** Quantify the actual static clamping force and the dynamic shear-release force between the tool sleeve and receiver plate.
- **Apparatus:** Digital push-pull force gauge ($0.01\text{ N}$ resolution) with axial and lateral load attachments.
- **Procedure:**
  1. Measure pure axial pull-off force normal to Datum A ($R_Y$ axis).
  2. Measure lateral shear release force along $R_X$ and peel release torque around the top ball pivot.
- **Target Criterion:**
  - Axial Clamping Preload: $18.0\text{ N} - 22.0\text{ N}$ (`DESIGN TARGET / TO BE VALIDATED`).
  - Dock Shear Separation Force: `PROPOSED TEST THRESHOLD — REQUIRES DESIGN REVIEW`.

### 3.3 TP-03: Automated Tool-Change Cycle Reliability Test
- **Objective:** Validate endurance and reliability of the passive docking bay under automated G-code execution.
- **Apparatus:** Fully assembled CoreXY gantry running automated tool-change looping script.
- **Procedure:**
  1. Program a continuous tool-changing routine cycling through all 4 dock bays (Slot 1 $\to$ Slot 2 $\to$ Slot 3 $\to$ Slot 4 $\to$ Slot 1).
  2. Execute continuous cycles while monitoring for misalignments, incomplete seating, or dropped tools.
- **Target Criterion:** Continuous unattended cycles without docking stall or seating error (`PROPOSED TEST THRESHOLD — REQUIRES DESIGN REVIEW`).

### 3.4 TP-04: Z-Lifter Compliance & Nib Pressure Test
- **Objective:** Measure line weight consistency and verify pen compliance stroke across varying paper thicknesses.
- **Apparatus:** Precision digital scale / load cell under the drawing bed and stepped shims ($0.1\text{ mm} - 1.0\text{ mm}$).
- **Procedure:**
  1. Command the Z-lifter servo to the drawing position against the load cell.
  2. Insert shims to simulate substrate height variations and measure reaction force changes.
- **Target Criterion:**
  - Nominal Spring / Pen Preload: $50 - 100\text{ gf}$ ($\approx 0.49 - 0.98\text{ N}$)
  - **Status:** `CONCEPT TARGET / TO BE VALIDATED IN Q3` (Recomputed in Q3 based on pen type, spring rate, and compliance stroke).

### 3.5 TP-05: CoreXY Orthogonality & Dimensional Accuracy Test
- **Objective:** Verify frame squareness, belt tension symmetry, and Cartesian positioning accuracy.
- **Apparatus:** Precision drafting pen, digital vernier caliper, and calibrated optical scanner.
- **Procedure:**
  1. Plot a standard geometric calibration pattern: $400\text{ mm} \times 280\text{ mm}$ bounding rectangle, diagonal crosshairs, and nested concentric circles.
  2. Measure diagonal lengths ($D_1, D_2$) to compute gantry orthogonality:
     $$\Delta D = |D_1 - D_2|$$
- **Target Criterion:**
  - Frame / CoreXY Orthogonality Acceptance Criterion: `TBD Q4`
  - Numerical Acceptance Limit: `TBD / REQUIRES Q4 DESIGN REVIEW`

### 3.6 TP-06: Poka-Yoke Reverse-Orientation Rejection Test
- **Objective:** Verify that inverted ($180^\circ$ yaw) tool presentation is physically prevented from magnetic pull-in or ball-groove contact.
- **Apparatus:** Receiver Plate V1 and Pen Slider V1.1 physical prototypes.
- **Procedure:**
  1. Present the Tool Slider rotated $180^\circ$ toward the Receiver Plate.
  2. Check that the monolithic Key Pin ($2.4 \times 2.4 \times 3.3\text{ mm}$) makes contact with the flat mating pad at an early-intercept clearance of $+0.170\text{ mm}$ before any steel ball touches a groove mouth.
- **Target Criterion:**
  - Positive mechanical interception before kinematic ball engagement under the evaluated tolerance stack.
  - Derived worst-case early-intercept margin: $+0.170\text{ mm}$.
  - **Status:** `DERIVED / BENCH CONFIRMATION REQUIRED`
  - **Formal Reliability Acceptance Criterion:** `TBD`

---

## Traceability

- **System Architecture:** [01_hardware_architecture.md](01_hardware_architecture.md)
- **Tool Changer Spec:** [02_tool_changer_spec.md](02_tool_changer_spec.md)
- **Carriage & Lifter Spec:** [03_carriage_and_lifter_spec.md](03_carriage_and_lifter_spec.md)
- **CoreXY Spec:** [04_corexy_frame_spec.md](04_corexy_frame_spec.md)
- **Decision History:** [hardware_decision_log.md](hardware_decision_log.md)
