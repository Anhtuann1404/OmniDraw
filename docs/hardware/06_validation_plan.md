<!-- scope-migration-20261002 -->
> **Phạm vi ngày 02/10/2026:** Tài liệu hardware hỗ trợ. Nội dung thiết kế/đo/review bên dưới giữ đúng phạm vi và ngày của nó; không đồng nghĩa đã mua máy, đã hiệu chuẩn hoặc đã nghiệm thu hướng nghiên cứu mới. Nghiên cứu dùng máy vẽ phẳng hai trục khi sẵn sàng, ghi cơ cấu/bộ điều khiển/bút/giấy theo run. Concept A4 một bút là phương án tham khảo hiện tại, không yêu cầu AxiDraw/CoreXY hay nhiều màu.
> Kế hoạch hiện hành: [Docs 30](../30_research_development_plan.md); đặc tả [Docs 31](../31_joint_solver_contract.md) và [Docs 32](../32_research_api_and_artifact_contract.md). Thông báo GVHD đồng ý hướng không thay sign-off kỹ thuật hoặc duyệt tham số.

# Hardware Validation Plan

**Subsystem:** System-Wide Hardware Verification  
**Document Version:** V1.2 (Q4C.3 dock and cable-chain gates)
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
| **TP-07** | Passive Dock Retention & Four-Bay Release/Pickup | Frozen Q2 dock / Q3 receiver / Q4 motion | Measure force margin and complete ≥100 cycles without dropped or jammed tools; numerical force threshold pending review | PHYSICAL TEST PENDING |
| **TP-08** | Two-Stage Cable-Chain Fit & Full-Travel Sweep | Q4 left Y bracket / X carriage | Selected chain/end links fit and clear the full 450 × 375 mm travel with supplier bend radius respected | SUPPLIER DATA & PHYSICAL TEST PENDING |
| **TP-09** | Q4C.3 Integrated CAD / Motor-Mount Regression | Q4 frame, motors, gantry, Q1–Q3 interfaces | Saved STEP topology and frozen hashes pass; motor/mount overlap = 0; sampled XY is clear, but the dock's rigid stop collides with coupled-tool +Y approach/−Y pickup. Chain details also remain open. | CAD DOCK-PATH FAIL / VIRTUAL RELEASE OPEN |

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

### 3.7 TP-07: Passive Dock Retention & Release/Pickup Test
- **Objective:** Determine whether the frozen passive dock actually retains each tool when the receiver withdraws in Machine −Y. CAD clearance alone does not prove this force balance.
- **Apparatus:** Printed dock, tool sleeves and receiver from the same revision; selected magnets; push-pull force gauge; four-bay motion fixture or assembled machine; video/force log.
- **Procedure:** Measure receiver/tool separation force and parked-tool pullout force in the actual release direction for each bay. Record the full force–displacement curves, not only peak values. Run at least 100 release/pickup cycles across the four bays, including worst-case commanded acceleration, and log drops, jams, mis-seating and visible wear.
- **Acceptance:** No dropped or jammed tool in the test run, and a documented dock-retention margin over the measured release disturbance with an agreed safety factor. **The numerical force threshold and safety factor must be approved before testing; neither 18–22 N coupling preload nor CAD interference may be substituted for them.** If this cannot be met, open a formal Q2 interface-change decision rather than silently adding a latch or magnet.

### 3.8 TP-08: Cable-Chain Vendor Fit & Motion Test
- **Objective:** Replace the straight CAD route corridors with a selected, articulated chain and verify that both stages can follow all commanded motion.
- **Apparatus:** Purchased J10-class chain and connector-end datasheet, printed left-bracket/carriage mounting coupons, cable harness, assembled gantry.
- **Procedure:** Measure connector hole pitch, end-link footprint, link pitch, minimum bend radius and real cable fill. Finish both mounting hole patterns only after matching that data. Model both moving loops and their swept envelopes; run X = 0–450 mm and Y = 0–375 mm including all corners, then repeat on hardware at low speed while watching snagging, pinch points, end-link rotation and load transfer into the frozen Q3 slider.
- **Acceptance:** Full motion without snagging or interference; supplier bend radius and fill limits met; no cable load into the Q3 floating Z assembly. The former 300/340 mm cut lengths and R18 assumption are **not acceptance values**.

### 3.9 TP-09: Q4C.3 Integrated CAD and Two-Level Release Gate
- **Automated evidence:** Run `cad/q4c3_verification.py` on regenerated STEP. Check the 14 frozen Q1–Q3 hashes, monolithic printed parts, motor/deck and A-shaft/base clearances, MGN12H holes, 41 tensioner positions, sampled XY B-Rep states, staged tool trajectories, and sampled endstop contacts. Record test spacing and numerical tolerance; a finite grid is not a continuous collision proof.
- **Virtual fabrication gate:** Requires zero forbidden overlap in the accepted model, a demonstrated dock insertion/retention/release path, selected and fitted cable-chain end links including the actual bend envelope, and reconciled part drawings. The current Q4C.3 model **fails this gate**: its Q4 fork now reproduces Q2's geometric −Y stop, but the rigid lip intersects the coupled tool during the specified +Y approach (24 mm³ at Y=363, bay 1). The reverse pickup path is likewise blocked; the connector can be 18 or 20 mm pitch and its final tab height is unresolved.
- **Physical final-freeze gate:** On the assembled prototype, measure 18–22 N *axial coupling* pull-off force; demonstrate nib-position repeatability ≤0.05 mm over at least 100 automated tool-change cycles; demonstrate no dropped/mis-seated tool at commanded acceleration 3000 mm/s². Record measurements and method. These proposed targets are not results and do not replace TP-07's separate dock-retention force margin, which still needs a numeric threshold and safety factor approved before test.

---

## Traceability

- **System Architecture:** [01_hardware_architecture.md](01_hardware_architecture.md)
- **Tool Changer Spec:** [02_tool_changer_spec.md](02_tool_changer_spec.md)
- **Carriage & Lifter Spec:** [03_carriage_and_lifter_spec.md](03_carriage_and_lifter_spec.md)
- **CoreXY Spec:** [04_corexy_frame_spec.md](04_corexy_frame_spec.md)
- **Decision History:** [hardware_decision_log.md](hardware_decision_log.md)
