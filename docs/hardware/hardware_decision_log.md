# Hardware Decision Log

**Project:** OmniDraw Plotter V1
**Document Version:** V1.1
**Status:** ACTIVE

---

## 1. Purpose

This log records all formal architectural, mathematical, and mechanical interface decisions for the OmniDraw Plotter V1 hardware. Every modification to frozen baselines must be documented here with clear problem statements, alternatives evaluated, mathematical justifications, and downstream impacts.

---

## 2. Decision Index

| Decision ID | Date | Scope | Title | Status |
| :--- | :--- | :--- | :--- | :--- |
| [HW-DEC-001](#hw-dec-001-maxwell-3-v-groove-kinematic-coupling-selection) | 2026-09 | Tool Changer | Maxwell 3 V-Groove Kinematic Coupling Selection | FROZEN |
| [HW-DEC-002](#hw-dec-002-passive-4-slot-rear-docking-bay-architecture) | 2026-09 | Tool Changer | Passive 4-Slot Rear Docking Bay Architecture | FROZEN |
| [HW-DEC-003](#hw-dec-003-tool-pad-envelope--pen-bore-geometry) | 2026-09 | Pen Slider | Tool Pad Envelope & Pen Bore Geometry | FROZEN |
| [HW-DEC-004](#hw-dec-004-tool-local-coordinate-frame--datum-a-definition) | 2026-09 | Pen Slider | Tool Local Coordinate Frame & Datum A Definition | FROZEN |
| [HW-DEC-005](#hw-dec-005-tool--receiver-magnet-specifications--pocket-depth) | 2026-09 | Interface | Tool & Receiver Magnet Specifications & Pocket Depth | FROZEN |
| [HW-DEC-006](#hw-dec-006-quad-dock-slot-pitch--bay-envelope) | 2026-09 | Docking Bay | Quad Dock Slot Pitch & Bay Envelope | FROZEN |
| [HW-DEC-007](#hw-dec-007-tool-side-wings-span--dock-engagement-shoulders) | 2026-09 | Pen Slider | Tool Side Wings Span & Dock Engagement Shoulders | FROZEN |
| [HW-DEC-008](#hw-dec-008-v-groove-asymmetric-layout--edge-clearance-correction) | 2026-09 | Pen Slider | V-Groove Asymmetric Layout & Edge-Clearance Correction | FROZEN |
| [HW-DEC-009](#hw-dec-009-v-groove-v11-profile-expansion--lead-in-chamfer) | 2026-09 | Pen Slider | V-Groove V1.1 Profile Expansion & Lead-in Chamfer | FROZEN |
| [HW-DEC-010](#hw-dec-010-receiver-plate-coordinate-system--2d-in-plane-transform) | 2026-09 | Receiver Plate | Receiver Plate Coordinate System & 2D In-Plane Transform | FROZEN |
| [HW-DEC-011](#hw-dec-011-receiver-ball-seat-conical-shoulder--adhesivevent-channel) | 2026-09 | Receiver Plate | Receiver Ball-Seat Conical Shoulder & Adhesive/Vent Channel | FROZEN |
| [HW-DEC-012](#hw-dec-012-poka-yoke-key-pin--mechanical-notch-geometry) | 2026-09 | Interface | Poka-Yoke Key Pin & Mechanical Notch Geometry | FROZEN |
| [HW-DEC-013](#hw-dec-013-legacy-active-servo-dock-deprecation) | 2026-09 | Architecture | Legacy Active Servo Dock Deprecation | FROZEN |
| [HW-DEC-Q3-FINAL-001](#hw-dec-q3-final-001-q3-z-carriage--cam-lifter-final-design-freeze) | 2026-09-22 | Z-Carriage / Lifter | Q3 Z-Carriage & Cam Lifter Final Design Freeze | FROZEN |

---

## 3. Detailed Decision Records

### HW-DEC-001: Maxwell 3 V-Groove Kinematic Coupling Selection
- **Status:** `FROZEN`
- **Context:** The tool changer requires an autonomous coupling interface that achieves high repositioning repeatability without manual locking levers or active electromechanical latches on the moving carriage.
- **Alternatives Considered:**
  1. *Kelvin Coupling (3 Spheres into Cone, V-groove, Flat):* High precision, but asymmetric machining/printing complexity and non-uniform load distribution.
  2. *Flat Magnetic Face-Coupling with Dowel Pins:* Prone to jamming, sliding friction wear, and over-constraint.
  3. *Maxwell Coupling (3 V-Grooves oriented toward coupling center):* Maxwell coupling provides six independent constraints in the evaluated ideal rigid-body contact model with 6 deterministic point contacts, provides deterministic self-centering, and balances contact loads.
- **Decision:** Adopt Maxwell 3 V-groove kinematic coupling with 3 hardened steel balls ($\phi 6.000\text{ mm}$) and 3 pairs of $\varnothing 8.000 \times 2.000\text{ mm}$ NdFeB-class disc magnets. Exact magnetic grade remains BOM CANDIDATE / TBD. N52 may be evaluated as a candidate during procurement/validation.
- **Traceability:** [02_tool_changer_spec.md](02_tool_changer_spec.md).

---

### HW-DEC-002: Passive 4-Slot Rear Docking Bay Architecture
- **Status:** `FROZEN`
- **Context:** Multi-pen drafting requires rapid switching between 4 colors/line widths. Active tool changers with dedicated per-slot servos increase wiring complexity and moving mass.
- **Decision:** Implement a 100% passive docking bay located along the rear machine rail at $Y = Y_{max}$.
  - Tool pickup/dropoff is executed entirely by coordinated CoreXY and Z-carriage motions.
- **Traceability:** [01_hardware_architecture.md](01_hardware_architecture.md), [02_tool_changer_spec.md](02_tool_changer_spec.md).

---

### HW-DEC-003: Tool Pad Envelope & Pen Bore Geometry
- **Status:** `FROZEN`
- **Context:** Establish standardized envelope for the 3D-printable Pen Slider sleeve holding drawing pens.
- **Decision:** Freeze Tool Pad envelope at $22.000\text{ mm} \times 48.000\text{ mm} \times 5.000\text{ mm}$ ($Z \in [4.200, 9.200]\text{ mm}$) and central Pen Bore at $\phi 12.500\text{ mm}$ centered at $(X = 0, Z = 14.500)\text{ mm}$.
- **Traceability:** [02_tool_changer_spec.md](02_tool_changer_spec.md) Section 4.1.

---

### HW-DEC-004: Tool Local Coordinate Frame & Datum A Definition
- **Status:** `FROZEN`
- **Context:** Prior sketches had ambiguities regarding the pen tip pointing direction ($+Y$ vs $-Y$) and the mating datum plane.
- **Decision:** Freeze the Tool Sleeve coordinate frame $\mathcal{F}_{tool}$:
  - **Tool Datum A:** Local $Z = 4.200\text{ mm}$.
  - **Tool Local $+Y$:** Points along the tool body towards the **Pen Tip** ($\text{Local }+Y \to \text{Machine }-Z$).
  - **Tool Local $+X$:** Points horizontally across the tool pad ($\text{Local }+X \to \text{Machine }+X$).
  - **Tool Local $+Z$:** Points through the sleeve towards the rear spine ($\text{Local }+Z \to \text{Machine }+Y$).
- **Traceability:** [02_tool_changer_spec.md](02_tool_changer_spec.md) Section 3.1.

---

### HW-DEC-005: Tool & Receiver Magnet Specifications & Pocket Depth
- **Status:** `FROZEN`
- **Context:** Coupling retention requires strong clamping without face collision between magnets.
- **Decision:** Adopt 3 pairs of $\varnothing 8.000 \times 2.000\text{ mm}$ NdFeB-class disc magnets.
  - Magnet Geometry: $\varnothing 8.000 \times 2.000\text{ mm}$ disc geometry is FROZEN.
  - Magnet Grade: Exact magnetic grade remains BOM CANDIDATE / TBD. N52 may be evaluated as a candidate during procurement/validation.
  - Pocket depth: $2.200\text{ mm}$ ($0.200\text{ mm}$ recess below mating faces).
  - Nominal face gap: $1.843\text{ mm}$.
  - Nominal magnetic gap: $2.243\text{ mm}$.
  - Preload force target: $18.0 - 22.0\text{ N}$ (`ASPIRATIONAL / UNMEASURED TARGET`).
- **Traceability:** [02_tool_changer_spec.md](02_tool_changer_spec.md) Section 4.3 & 6.3.

---

### HW-DEC-006: Quad Dock Slot Pitch & Bay Envelope
- **Status:** `FROZEN`
- **Context:** Inter-slot spacing must prevent collisions between adjacent parked pens during carriage approach.
- **Decision:** Freeze Dock Pitch at $P = 32.000\text{ mm}$, yielding $4.000\text{ mm}$ clearance between $28.000\text{ mm}$ wings, an active 4-slot envelope of $124.000\text{ mm}$, and an overall base width of $144.000\text{ mm}$ ($10.000\text{ mm}$ side margins).
- **Traceability:** [02_tool_changer_spec.md](02_tool_changer_spec.md) Section 10.

---

### HW-DEC-007: Tool Side Wings Span & Dock Engagement Shoulders
- **Status:** `FROZEN`
- **Context:** Passive docking requires positive mechanical capture surfaces on the tool sleeve.
- **Decision:** Implement integrated side wings with total span $28.000\text{ mm}$ ($3.000\text{ mm}$ protrusion/side, length $16.000\text{ mm}$, thickness $4.000\text{ mm}$ at $Z \in [10.000, 14.000]\text{ mm}$).
- **Traceability:** [02_tool_changer_spec.md](02_tool_changer_spec.md) Section 9.

---

### HW-DEC-008: V-Groove Asymmetric Layout & Edge-Clearance Correction
- **Status:** `FROZEN`
- **Context:** Symmetric $120^\circ$ radial spacing interfered with the central $\phi 12.500\text{ mm}$ pen bore. Shifting $V2/V3$ to $X = \pm 7.500\text{ mm}$ resulted in oriented groove cutouts violating the $1.500\text{ mm}$ side edge web margin.
- **Decision:** Shift $V2$ and $V3$ center positions to:
  - $V1 = (0.000, +15.000, 4.200)\text{ mm}$ (Orientation: $0.00^\circ$ from $+Y$).
  - $V2 = (-6.000, -12.000, 4.200)\text{ mm}$ (Orientation: $26.57^\circ$ from $+Y$).
  - $V3 = (+6.000, -12.000, 4.200)\text{ mm}$ (Orientation: $-26.57^\circ$ from $+Y$).
  - Resulting angular distribution: $153.43^\circ / 153.43^\circ / 53.13^\circ$.
  - Preserves $1.556\text{ mm}$ solid side-wall web and $1.650\text{ mm}$ bore ceiling web.
- **Traceability:** [02_tool_changer_spec.md](02_tool_changer_spec.md) Section 4.2.

---

### HW-DEC-009: V-Groove V1.1 Profile Expansion & Lead-in Chamfer
- **Status:** `FROZEN`
- **Context:** The original groove profile ($W = 4.500\text{ mm}, D = 2.250\text{ mm}$) provided only a marginal $0.129\text{ mm}$ contact lip clearance for a $\phi 6.000\text{ mm}$ ball, making it vulnerable to FDM printing edge rounding.
- **Decision:** Upgrade to V-Groove V1.1 profile:
  - **Mouth Width:** $W = 4.800\text{ mm}$ ($+0.300\text{ mm}$).
  - **Depth:** $D = 2.400\text{ mm}$ ($+0.150\text{ mm}$).
  - **Apex:** $Z_{apex} = 4.200 + 2.400 = 6.600\text{ mm}$.
  - **Ball Center Engagement:** $Z_{ball\_center} = 2.357\text{ mm}$.
  - **Contact Lip Margin:** Increased to $0.279\text{ mm}$ per side.
  - **Lead-in Chamfer:** $0.200\text{ mm} \times 45.0^\circ$ (physical mouth opening $W_{phys} = 5.200\text{ mm}$).
- **Traceability:** [02_tool_changer_spec.md](02_tool_changer_spec.md) Section 4.2.

---

### HW-DEC-010: Receiver Plate Coordinate System & 2D In-Plane Transform
- **Status:** `FROZEN`
- **Context:** Coordinate confusion existed between Receiver plate thickness axis and in-plane axes.
- **Decision:** Establish Receiver Local Frame $\mathcal{F}_{receiver}$:
  - $R_X \in [-11.000, +11.000]\text{ mm}$ (Horizontal across plate).
  - $R_Z \in [-24.000, +24.000]\text{ mm}$ (Vertical along plate).
  - $R_Y \in [-6.000, 0.000]\text{ mm}$ (Plate thickness / normal axis).
  - Front mating plane: $\text{RECEIVER\_DATUM\_A} \implies R_Y = 0.000\text{ mm}$.
  - Back mounting plane: $R_Y = -6.000\text{ mm}$.
  - In-plane 2D transformation matrix:
    $$\begin{bmatrix} R_X \\ R_Z \end{bmatrix} = \begin{bmatrix} 1 & 0 \\ 0 & -1 \end{bmatrix} \begin{bmatrix} X_{tool} \\ Y_{tool} \end{bmatrix}$$
- **Traceability:** [02_tool_changer_spec.md](02_tool_changer_spec.md) Section 3.2 & 3.3.

---

### HW-DEC-011: Receiver Ball-Seat Conical Shoulder & Adhesive/Vent Channel
- **Status:** `FROZEN`
- **Context:** Precision locating of $\phi 6.000\text{ mm}$ steel balls in 3D-printed plastic requires unambiguous seated height without depending on flat bottom stops.
- **Decision:** Define 3-stage ball-seat geometry:
  1. $\phi 6.100\text{ mm}$ cylindrical guide bore ($R_Y \in [-1.193, 0.000]\text{ mm}$).
  2. $90.0^\circ$ conical centering shoulder (tangent contact ring at $R_Y = -2.121\text{ mm}$, contact diameter $\phi 4.243\text{ mm}$).
  3. $\phi 2.500\text{ mm}$ through-bore adhesive/vent channel ($R_Y \in [-6.000, -2.993]\text{ mm}$).
  - Locks seated ball center strictly at $R_Y = 0.000\text{ mm}$ ($\text{RECEIVER\_DATUM\_A}$).
- **Traceability:** [02_tool_changer_spec.md](02_tool_changer_spec.md) Section 6.2.

---

### HW-DEC-012: Poka-Yoke Key Pin & Mechanical Notch Geometry
- **Status:** `FROZEN`
- **Context:** Symmetrical or accidental $180^\circ$ reversed docking presentation could cause magnet snapping and damage to printed features.
- **Decision:** Implement asymmetric mechanical Poka-Yoke:
  - **Tool Notch:** Cutout $3.000 \times 3.000\text{ mm}$, depth $2.000\text{ mm}$ at $(+9.500, +22.500, 4.200)\text{ mm}$.
  - **Receiver Key Pin:** Monolithic pin $2.400 \times 2.400\text{ mm}$, height $3.300\text{ mm}$ ($R_Y \in [0.000, +3.300]\text{ mm}$) at $(+9.500, -22.500)\text{ mm}$.
  - **Clearance Margins:** $0.300\text{ mm}$ per side, $+0.213\text{ mm}$ bottom axial clearance.
  - **Early-Intercept Safety:** In $180^\circ$ reversed insertion, Key Pin intercepts flat tool pad at $+0.170\text{ mm}$ before any steel ball enters a groove mouth.
- **Traceability:** [02_tool_changer_spec.md](02_tool_changer_spec.md) Section 8.

---

### HW-DEC-013: Legacy Active Servo Dock Deprecation
- **Status:** `FROZEN`
- **Context:** The original conceptual dock design in early sketches included cavities for four SG90 micro-servos to actuate mechanical retention latches.
- **Decision:** Formally deprecate the active 4-servo dock in favor of the 100% passive U-fork dock architecture with magnetic kinematic coupling (HW-DEC-002).
- **Traceability:** [02_tool_changer_spec.md](02_tool_changer_spec.md) Section 16.

---

### HW-DEC-Q3-FINAL-001: Q3 Z-Carriage & Cam Lifter Final Design Freeze
- **Status:** `FROZEN` (V1 Baseline Architecture & CAD Geometry Frozen | Physical Validation Pending)
- **Date:** 2026-09-22
- **Scope:** Z-Carriage, Gravity-Floating Pen Axis, Cam Lifter, Fixed Baseplate Relief, & Dock Interaction
- **Context & Problem Statement:**
  Following the freeze of the Tool Interface V1.1 and Receiver Plate V1 (Q1–Q2), the Z-Carriage and lifter subsystem required a definitive mechanical architecture to achieve reliable drafting contact, high-speed vertical retraction, autonomous tool change, and positive mechanical stops without over-constraining the pen nib.
- **Revision History & Architectural Evolution:**
  1. *Q3A & Q3B.8 Baseline:* Established the gravity-dominant floating Z-carriage architecture, Archimedean cam lift profile ($k = 6.6845\text{ mm/rad}$), and coupled shear+normal tool separation kinematics.
  2. *Q3C-A.4 CAD Implementation:* Created the first unified parametric CAD model (`cad/build_q3c_cad_assembly.py`) packaging the MG90S-class servo reference envelope, MR84ZZ roller follower, MGN9 rail/block, receiver plate, and hard stops.
  3. *Q3C-A.5 / Q3C-A.6 Cam-Path & Baseplate Audit:* An exhaustive continuous sweep audit exposed a $46.14\text{ mm}^3$ solid collision between the cam lobe and fixed baseplate when advancing past $\gamma_{cam} \ge +25^\circ$. Q3C-A.6 added a targeted primary relief pocket in the baseplate ($X \in [-18.5, -14.0]\text{ mm}, Z \in [-35.0, -5.0]\text{ mm}$) and proposed parking at $\gamma_{cam} = +90.000^\circ$.
  4. *Q3C-A.7 Final Lower-Stop & Free-Draw Closure:* Independent B-Rep audit revealed that at $\gamma_{cam} = +90.000^\circ$, the cam contacted the follower at $Z \approx -1.783\text{ mm}$, acting as an unintended hard stop and voiding the mechanical lower stop at $Z = -2.500\text{ mm}$ (5.236 mm³ interference). Rotating to $\gamma_{cam} \ge +116^\circ$ drove the cam lobe toward $Z = -40.6\text{ mm}$, colliding with the Q3C-A.6 baseplate bottom shelf.
  5. *Q3C-A.7 Resolution:* Authorized targeted baseplate relief extended to the bottom boundary ($Z = -40.0\text{ mm}$) and added a lower-left clearance notch ($X \in [-26.0, -18.5]\text{ mm}, Z \in [-40.0, -33.0]\text{ mm}$) to preserve single-solid body continuity. Established authoritative FREE_DRAW park at $\gamma_{cam} = +120.000^\circ$.
- **Key Frozen Decisions & Geometry:**
  1. **Gravity-Dominant Floating Architecture:** Pen downforce in `STATE_DRAW` is provided passively by moving mass under gravity. No default downward spring is included. Cam is fully disengaged in `FREE_DRAW_PARK`.
  2. **Authoritative FREE_DRAW Park Orientation ($\gamma_{cam} = +120.000^\circ$):**
     - Provides $+0.435\text{ mm}$ follower clearance at the mechanical lower stop ($Z = -2.500\text{ mm}$).
     - The mechanical lower hard stop engages FIRST at $Z = -2.500\text{ mm}$; hard-stop authority is 100% restored.
     - Provides $+1.304\text{ mm}$ to $+4.086\text{ mm}$ follower clearance across the entire functional compliance band ($Z \in [-1.500, +1.500]\text{ mm}$).
     - Enables a continuous monotonic path from park ($\phi_{servo} = 0.000^\circ$) to `STATE_PEN_UP` ($\phi_{servo} = 120.000^\circ$).
  3. **Fixed Baseplate Cam-Sweep Relief:**
     - Primary pocket: $X \in [-18.5, -14.0]\text{ mm}, Z \in [-40.0, -5.0]\text{ mm}$.
     - Lower-left continuity notch: $X \in [-26.0, -18.5]\text{ mm}, Z \in [-40.0, -33.0]\text{ mm}$.
     - Preserves strictly 1 connected solid (Volume = $22,009.57\text{ mm}^3$, 96.84% material retention).
     - Classification: CAD GEOMETRY = FROZEN | STRUCTURAL STRENGTH = PENDING FEA / PHYSICAL VALIDATION.
  4. **Operational Command Mapping:**
     $$\phi_{servo} = 120.000^\circ - \gamma_{cam}$$
     - System travel requirement: $\Delta \phi_{servo} = 120.000^\circ$. A candidate actuator must provide at least this usable calibrated travel plus implementation margin. Exact available travel must be verified for the selected servo SKU ($180^\circ$ is cited only as an illustrative candidate rating, not a verified component capability).
     - State angles: Park ($0.0^\circ$), Contact Low ($38.64^\circ$), Contact Nom ($51.50^\circ$), Contact High ($64.35^\circ$), Dock Mate ($107.21^\circ$), Pen Up ($120.0^\circ$).
  5. **Continuous Collision-Free Status:**
     - 723 operational states audited across $\gamma_{cam} \in [120^\circ, 0^\circ]$ in $\le 0.5^\circ$ increments for $Z_{init} \in \{-1.5, 0, +1.5\}\text{ mm}$.
     - Result: Zero forbidden positive-volume overlaps across all component pairs (CAD VERIFIED).
  6. **Coupled Tool Release Motion:**
     - Coordinated 2-axis vector: Machine $\Delta Z = +1.500\text{ mm}, \Delta Y = -1.000\text{ mm}$ ($\Delta T_Y = -1.500\text{ mm}, \Delta T_Z = -1.000\text{ mm}$).
     - Classification: **COUPLED SHEAR + NORMAL SEPARATION**. "Peel release" terminology is formally deprecated.
  7. **Universal Guide-Friction Allowance Formula:**
     $$F_{guide\_allow} = \min(100.0\text{ gf} - F_{gravity},\ F_{gravity} - 50.0\text{ gf}) = \min(100.0 - m_{total},\ m_{total} - 50.0)\text{ gf}$$
     - Supported moving mass window for $10.0\text{ gf}$ target: $60.0\text{ g} \le m_{total} \le 90.0\text{ g}$.
- **Explicitly Unfrozen Parameters (Pending Physical Validation):**
  - Actual moving assembly mass and printed-part mass (TBD — must be measured).
  - Guide breakaway and running friction (TBD — physical test required).
  - Real nib force on paper (TBD — physical test required).
  - Power-off gravity drop reliability (TBD — physical test required).
  - Commercial servo model, vendor, and thermal performance (TBD — candidate MG90S).
  - Commercial linear rail model, vendor, and preload grade (TBD — candidate MGN9C).
  - Commercial follower bearing supplier and SKU (TBD — candidate MR84ZZ).
  - Permanent magnet grade (TBD — candidate NdFeB disc $\varnothing 8 \times 2\text{ mm}$; N52 is candidate only).
  - Repositioning repeatability target $\le 0.050\text{ mm}$ (`DESIGN TARGET / UNVALIDATED`).
- **Formal Deprecations Recorded:**
  - Deprecated: $\gamma_{cam} = -90^\circ$ and $\gamma_{cam} = +90^\circ$ FREE_DRAW park angles.
  - Deprecated: Average slope $dz/d\phi = 8.775\text{ mm/rad}$ (superseded by local derivative $6.6845\text{ mm/rad}$).
  - Deprecated: Generic universal guide friction $\le 12\text{ gf}$ (superseded by mass-dependent formula).
  - Deprecated: "Peel release" terminology (superseded by "Coupled shear + normal separation").
- **Traceability:**
  - Specification: [03_carriage_and_lifter_spec.md](03_carriage_and_lifter_spec.md)
  - Tool Interface: [02_tool_changer_spec.md](02_tool_changer_spec.md)
  - CAD Implementation: `cad/build_q3c_cad_assembly.py` / `cad/export/*.step`
  - Engineering Reports: Q3C-A.7 & Q3C-B.3R Verified Baseline.
