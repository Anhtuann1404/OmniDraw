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
| [HW-DEC-Q4-001](#hw-dec-q4-001-corexy-frame--xy-motion-architecture-definition) | 2026-09-22 | CoreXY / Frame | CoreXY Frame & XY Motion Architecture Definition | ARCHITECTURE BASELINE (Q4A) |
| [HW-DEC-Q4-002](#hw-dec-q4-002-q4b-dimensional-packaging--corexy-force-budget-baseline) | 2026-09-22 | CoreXY / Sizing | Q4B Dimensional Packaging & CoreXY Force-Budget Baseline | BASELINE (Q4B.2) |
| [HW-DEC-Q4-003](#hw-dec-q4-003-corexy-detailed-mechanical-cad-assembly-collision-audit--packaging-baseline-q4c) | 2026-09-22 | CoreXY / CAD Baseline | CoreXY Detailed Mechanical CAD Assembly, Collision Audit & Packaging Baseline | CAD BASELINE (Q4C) |
| [HW-DEC-Q4-004](#hw-dec-q4-004-q4c3-corrective-cad-and-release-gate) | 2026-09-26 | CoreXY / Q4 Release | Q4C.3 Corrective CAD and Release Gate | PROVISIONAL / NO FINAL FREEZE |
| [HW-DEC-Q4-005](#hw-dec-q4-005-passive-dock-redesign-prototype) | 2026-09-26 | Tool Changer / Q4 Dock | Passive Dock Redesign Prototype | CONCEPT / NOT FROZEN |

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
  - Pocket Geometry: $\varnothing 8.200\text{ mm}$ diameter, depth $2.200\text{ mm}$ ($0.200\text{ mm}$ recess below mating faces).
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

---

### HW-DEC-Q4-001: CoreXY Frame & XY Motion Architecture Definition
- **Status:** `ARCHITECTURE BASELINE (Q4A — DETAILED GEOMETRY NOT YET FROZEN)`
- **Date:** 2026-09-22
- **Scope:** CoreXY Motion Architecture, Frame Topology, Guide Selection, Belt Planes, Gantry Interface to Q3, and Dock Integration
- **Context & Problem Statement:**
  Following the design freeze of the Q3 Z-Carriage and Cam Lifter, the machine requires a mechanically coherent planar XY motion platform to position the carriage across the drawing bed and into the rear tool docking bay ($Y = Y_{max}$). This architecture must establish kinematic topologies, belt paths, guide types, coordinate conventions, and interface envelopes before detailed dimensional CAD modeling in Q4B.
- **Alternatives Evaluated:**
  1. *Motion Topology:* CoreXY vs H-Bot vs Cartesian (bed-slinger / dual Y). H-Bot was rejected due to intrinsic racking moments that flex the gantry. Cartesian bed-slinger was rejected due to dynamic ink-flow disturbances from moving the paper. CoreXY was selected for stationary frame-mounted motors, lowest gantry inertia, and balanced belt loads.
  2. *Belt Routing:* Same-plane crossed CoreXY vs Two-plane stacked/uncrossed CoreXY. Stacked dual-plane CoreXY was selected to eliminate belt-on-belt rubbing and maintain strictly orthogonal, linear belt runs without pitch distortion.
  3. *Linear Guidance:* Dual V-slot wheels vs MGN12 linear rails for Y; V-slot vs MGN9 vs MGN12 for X. MGN12 was selected as primary candidate for X and Y for candidate high rigidity, pitch moment resistance under Q3 carriage overhang, and long-term repeatability without wheel wear.
  4. *Homing Corner:* Rear-Left vs Front-Left. Front-Left $(X_{min}, Y_{min})$ was selected because nominal homing motion proceeds directly away from the rear tool dock ($Y_{max}$), reducing dock collision exposure.
- **Key Architectural Baselines Established:**
  1. **Coordinate Convention:** Global Machine Origin $(0, 0, 0)$ at Front-Left travel datum ($X=0$ left datum, $Y=0$ front datum, $Z=0$ drawing paper). $+X$ horizontal right, $+Y$ longitudinal rear (toward dock), $+Z$ vertical upward. Homing corner at Front-Left $(X_{min}, Y_{min}) = (0, 0)$. Rear dock horizontal position is centered at derived positive global coordinate $X_{dock\_center} = \text{TBD Q4B}$ (local bay span $\pm 62.000\text{ mm}$).
  2. **Kinematic Equations:** $\Delta X = (\Delta A + \Delta B)/2$, $\Delta Y = (\Delta A - \Delta B)/2$.
  3. **Belt Routing Architecture:** Two-plane stacked / uncrossed GT2 6 mm timing belts (Upper Plane 1: Belt A; Lower Plane 2: Belt B). Belt plane vertical separation $\Delta Z_{belt}$ is classified as a preliminary packaging target (TBD Q4B, provisional guideline $\sim 9 - 10\text{ mm}$).
  4. **Idler Engagement Principle:** Toothed idler pulleys on all high-wrap toothed turns; smooth flanged idlers on smooth back turns.
  5. **X/Y Guides:** Primary candidate MGN12 linear rails (Twin Y with master-slave mounting to reduce sensitivity to parallelism error, single X on gantry front face with MGN12H block). Exact manufacturer, preload grade, and SKU remain TBD.
  6. **Q3 Interface Accommodation:** Q3 Baseplate rear face datum at $Y_{Q3} = -27.000\text{ mm}$, 4x M3 mount holes ($36 \times 64\text{ mm}$ pattern at $X_{Q3} = \pm 18.0, Z_{Q3} = \pm 32.0\text{ mm}$). Q4 X-carriage bracket must include dedicated clearance relief cutouts for the protruding MG90S servo body ($X_{Q3} < -14.0\text{ mm}, Y_{Q3} \in [-33.0, -27.0]\text{ mm}$) and cam sweep ($Z_{Q3} < -5.0\text{ mm}$). All Q3 dimensions are interface-local coordinates.
  7. **Belt Tensioning:** Independent screw-driven belt clamps mounted to the front/top of the X-carriage plate.
  8. **Quad Dock Integration:** Dock bay centered at rear crossmember ($Y = Y_{max}$) at $X_{dock\_center}$. Approach corridor across $[X_{dock\_center}-75.0, X_{dock\_center}+75.0]\text{ mm}$ is a preliminary packaging requirement that must be verified collision-free in Q4B CAD.
  9. **Moving Mass Separation:** Q3 floating Z-moving mass is $52.92 - 82.27\text{ g}$ (parametric Q3 estimate). Total Q3 package mass carried by XY and total moving masses ($m_{X\_total}, m_{Y\_total}$) are TBD Q4B. Acceleration limits $a_{X\_max}, a_{Y\_max}$ are TBD Q4B/Q4C based on traceable mass and force budgets.
- **Explicitly Unfrozen Parameters (Deferred to Q4B/Q4C):**
  - Final extrusion lengths, frame outer dimensions, and corner gusset details.
  - Final motor holding torque and commercial SKU (NEMA 17 candidate; $40 - 45\text{ N}\cdot\text{cm}$ is illustrative procurement band only).
  - Drive pulley tooth count (candidate 16T vs 20T GT2).
  - Belt preload target (TBD Q4B/Q4C).
  - Exact rail manufacturer, preload grade, and SKU.
  - Final media footprint baseline (A4 vs A3 dimensional sizing).
- **Traceability:**
  - Specification: [04_corexy_frame_spec.md](04_corexy_frame_spec.md)
  - Tool Changer Dock: [02_tool_changer_spec.md](02_tool_changer_spec.md)
  - Carriage & Lifter: [03_carriage_and_lifter_spec.md](03_carriage_and_lifter_spec.md)
  - CAD Implementation: `cad/build_q3c_cad_assembly.py`

---

### HW-DEC-Q4-002: Q4B Dimensional Packaging & CoreXY Force-Budget Baseline
- **Status:** `BASELINE (Q4B.2 HOTFIX ACCEPTED — READY FOR Q4C CAD AUTHORIZATION)`
- **Date:** 2026-09-22
- **Scope:** Media Footprint Selection, Dimensional Stacks, Traceable Mass Budgets, Gantry Extrusion Sizing, Drive Pulley Evaluation, Tangent-Aware Belt Geometry, CoreXY Virtual Work Force Sizing, and Belt Preload Logic.
- **Context & Problem Statement:**
  Following acceptance of the Q4A CoreXY architecture, quantitative dimensional packaging and dynamic force budgets were required to dimension the frame, select candidate structural profiles and drive pulleys, establish non-overlapping tangent belt routing geometry, and size the motion actuators before detailed 3D fabrication CAD in Q4C.
- **Alternatives Evaluated:**
  1. *Media Footprint Baseline:* ISO A4 ($210 \times 297\text{ mm}$) vs ISO A3 Landscape ($420 \times 297\text{ mm}$). A3 Landscape was selected as the primary packaging baseline to provide professional plotting versatility, complete forward compatibility (A4 and A3 both supported), and an optimal aspect ratio matching CoreXY gantry dynamics.
  2. *Gantry Structural Extrusion:* 2020 aluminum extrusion vs 2040 extrusion (oriented horizontally: $40\text{ mm}$ width, $20\text{ mm}$ height) using Misumi 5-series catalog properties (HFS5-2020 and HFS5-2040). Analytical beam bending calculations across a 5-case dynamic load sensitivity table ($0.50\text{ N}$ nominal Y-accel to $25.00\text{ N}$ overload sensitivity) demonstrated that 2020 flexes $122.7\ \mu\text{m}$ under $15\text{ N}$ combined dynamic load over a $580\text{ mm}$ span (failing the $\le 50\ \mu\text{m}$ design target). In contrast, 2040 oriented horizontally flexes only $17.0\ \mu\text{m}$ ($7.22\times$ stiffer horizontally, $6.61\times$ stiffer in torsion), remaining under $30\ \mu\text{m}$ flexure even under worst-case overload. 2040 was selected as the Primary Analytical Structural Candidate (validation pending Q4C FEA and physical testing).
  3. *Drive Pulley Tooth Count:* 16T GT2 vs 20T GT2. 20T GT2 was selected as the Provisional Primary Packaging Candidate. At $300\text{ mm/s}$ travel, 20T operates at $450\text{ RPM}$, reducing stepper back-EMF frequency and cyclic belt tooth bending strain around a larger pitch radius ($r_p = 6.366\text{ mm}$), while providing a $12.5\ \mu\text{m}$ nominal command increment at 1/16 microstepping. 16T provides $25\%$ mechanical torque leverage ($0.509$ vs $0.637\text{ N}\cdot\text{cm/N}$) but operates at $562.5\text{ RPM}$. Final dynamic superiority remains TBD pending the selected motor torque-speed curve.
- **Key Baselines Established:**
  1. **Global Datums & Travel:** Global Origin $(0, 0, 0)$ at Front-Left travel limit. Transverse travel $X_{travel} = 450.000\text{ mm}$, longitudinal travel $Y_{travel} = 375.000\text{ mm}$. Active A3 plotting area across $X \in [15.0, 435.0]\text{ mm}, Y \in [15.0, 312.0]\text{ mm}$ with $15.0\text{ mm}$ hold-down borders.
  2. **Rear Quad Dock Global Placement:** Dock center derived as positive coordinate $X_{dock\_center} = 225.000\text{ mm}$. Bay centers at $X_1 = 177.0, X_2 = 209.0, X_3 = 241.0, X_4 = 273.0\text{ mm}$ ($P = 32.000\text{ mm}$). Dock mating position $Y_{DOCK\_MATE} = 365.000\text{ mm}, Z_{DOCK\_MATE} = +6.500\text{ mm}$. Dock approach corridor feasibility indicated by dimensional pre-check ($35\text{ mm}$ nominal datum gap; full tool/barrel/platen collision clearance pending Q4C assembly CAD).
  3. **Traceable Dimensional Stacks:**
     - $FRAME\_INNER\_X = 600.000\text{ mm}, FRAME\_OUTER\_X = 640.000\text{ mm}$ ($2020\text{ mm}$ side extrusions, length $525.000\text{ mm}$).
     - $FRAME\_INNER\_Y = 485.000\text{ mm}, FRAME\_OUTER\_Y = 525.000\text{ mm}$ ($2020\text{ mm}$ crossmember extrusions, length $600.000\text{ mm}$).
     - Gantry beam clear span: $580.000\text{ mm}$.
     - Linear rails: X-rail length $= 550.000\text{ mm}$ (usable stroke $484.6\text{ mm} > 450.0\text{ mm}$); Y-rail length $= 450.000\text{ mm}$ (usable stroke $394.6\text{ mm} > 375.0\text{ mm}$).
     - Single MGN12H block architecture verified: Representative MGN12H catalog comparison indicates applied pitch moment is small relative to representative static capacity; single-block architecture remains PRIMARY CANDIDATE; exact capacity margin TBD SELECTED SKU / Q4C.
  4. **Tangent-Aware Belt Routing & Node Geometry (Belt A & Belt B):** Belt A Installed Path (Upper Plane, $Z_A = +5.0\text{ mm}$) and Belt B Installed Path (Lower Plane, $Z_B = -5.0\text{ mm}$) defined via mathematically proven tangent node tables with single continuous circular arcs (B2 CW wrap around $(+475.634, Y_G - 21.366)$; B6 CCW wrap around $(-43.634, Y_G - 8.634)$). Full belt-face continuity proven with zero twist: each belt engages exactly 1 smooth idler on the smooth backside (gantry lead-in A2/B2) and 4 toothed wheels on the toothed face (front turnaround A3/B3, drive pulley A4/B4, rear frame A5/B5, and gantry return A6/B6). Separate inner and outer Y-lanes ($18.0\text{ mm} = 2 R_{front}$ lane separation) eliminate same-plane self-overlap. Invariant straight tangent segment sum $= 1881.072\text{ mm}$, wrap arcs $= 68.274\text{ mm}$, yielding identical nominal installed path length $L_A = L_B = 1949.346\text{ mm}$ ($|L_A - L_B| = 0.000\text{ mm}$ exact symmetry; nominal packaging range $1940 - 1960\text{ mm}$; Q4B estimate, not fabrication cut freeze; roll order $\sim 2200\text{ mm}$). Belt plane separation $\Delta Z_{belt} = 10.000\text{ mm}$ derived from dual COTS idler stack ($\sim 8.5\text{ mm}$ body height + $1.0 - 1.5\text{ mm}$ shim) as a provisional candidate (status: TBD Q4C procurement).
  5. **Traceable Mass Budgets & Synchronized 4-Case Sizing Envelope:**
     - Preserved upstream frozen Q3 floating mass sensitivity: $52.92 - 82.27\text{ g}$ (Nominal $62.13\text{ g}$) traced strictly to `03_carriage_and_lifter_spec.md` Section 3.7 and `HW-DEC-Q3-FINAL-001`. Retained Q4B B-Rep solid volume estimate as non-authoritative packaging check ($56.40 - 68.35\text{ g}$, with `Receiver_Plate_V1` updated to $5945.42\text{ mm}^3$).
     - Authoritative 4-case structure synchronized between docs and calculations script:
       - Conservative carried Q3 package: LOW $121.09\text{ g}$, NOMINAL $135.74\text{ g}$, HIGH_PLA $158.15\text{ g}$, HIGH_PETG $159.48\text{ g}$.
       - Total X-moving mass: $m_{X\_total}$ = LOW $294.09\text{ g}$, NOMINAL $332.74\text{ g}$ ($\mathbf{0.333\text{ kg}}$), HIGH_PLA $383.15\text{ g}$, HIGH_PETG $384.48\text{ g}$.
       - Total Y-moving mass: $m_{Y\_total}$ = LOW $1633.59\text{ g}$, NOMINAL $1737.24\text{ g}$ ($\mathbf{1.737\text{ kg}}$), HIGH_PLA $1852.65\text{ g}$, HIGH_PETG $1853.98\text{ g}$ with 2040 gantry. Moving mass ratio $m_Y / m_X \approx 5.22\times$.
     - All COTS masses classified with catalog datasheets or explicit `ENGINEERING PACKAGING ESTIMATE`. Pen mass classified as estimate ($8 - 15\text{ g}$), not measured.
  6. **Dynamic Force Transformation & Required Torque:** Derived via virtual work: $f_A = (F_X + F_Y)/2, f_B = (F_X - F_Y)/2$. Due to strong moving mass asymmetry ($m_Y / m_X \approx 5.22\times$), at $45^\circ$ diagonal motion $F_Y \gg F_X$, requiring Motor B to actively exert balancing force ($f_B \neq 0$). Required running motor torque across $500 - 3000\text{ mm/s}^2$ acceleration is $\tau_{req} \approx 3.78 - 5.84\text{ N}\cdot\text{cm}$ (with $\eta = 0.85$ and $SF = 1.5$). Standard $40 - 45\text{ N}\cdot\text{cm}$ NEMA 17 steppers provide a standard packaging baseline, but usable dynamic torque margin is classified as TBD pending motor torque-speed curve and 24V driver bench testing.
  7. **Belt Preload Logic:** Symbolic slack prevention condition $T_0 > |\Delta T_{peak}|/2$. Static numeric preload target classified as `STATIC BELT PRELOAD NUMERIC TARGET = TBD PROCUREMENT / Q4C`; trial band of $20.0 - 35.0\text{ N}$ classified strictly as `ENGINEERING TRIAL RANGE / NOT DERIVED / NOT FROZEN`. Radial loads evaluated parametrically ($21.2 - 49.6\text{ N}$ across $15 - 35\text{ N}$ preload); supplier bearing limits classified as TBD procurement.
- **Explicitly Unfrozen Parameters (Deferred to Q4C / Physical Validation):**
  - Detailed bracket CAD, corner gusset geometry, and fastener callouts.
  - Final motor vendor and dynamic torque-speed curve validation.
  - Final rail manufacturer, preload class, and commercial SKU.
  - Final idler pulley SKU and exact axial stack spacing $\Delta Z_{belt}$.
  - Prototype acoustic belt preload frequency tuning.
- **Traceability:**
  - Specification: [04_corexy_frame_spec.md](04_corexy_frame_spec.md) (V2.4 Baseline)
  - Calculation Script: `cad/q4b_calculations.py`
  - Upstream Architecture: [01_hardware_architecture.md](01_hardware_architecture.md)
  - Tool Changer Dock: [02_tool_changer_spec.md](02_tool_changer_spec.md)
  - Carriage & Lifter: [03_carriage_and_lifter_spec.md](03_carriage_and_lifter_spec.md)
  - Downstream CAD Implementation: `cad/build_q3c_cad_assembly.py`

---

#### HW-DEC-Q4-003: CoreXY Detailed Mechanical CAD Assembly, Fabrication Realization & Continuous Collision Baseline (Q4C.1 Hotfix)
- **Status:** `CAD BASELINE (Q4C.1 HOTFIX — BLOCKED BY UPSTREAM RELEASE KINEMATICS | Q4 FINAL FREEZE PENDING INDEPENDENT REVIEW)`
- **Date:** 2026-09-22
- **Scope:** Complete 3D Parametric CAD Assembly, Multi-Body Solids Separation, Fabrication Realization, 28T GT2 Pitch Geometry, Global Z Datum, Rail Engagement Closure, Continuous Collision Grid Audit, and STEP Exports
- **Context & Problem Statement:**
  Following the acceptance of the analytical dimensional stack and force budget (Q4B.2), the CoreXY motion platform required physical realization as a parametric 3D mechanical CAD assembly (`cad/build_q4c_corexy_assembly.py`) built around the immutable frozen Q3 Z-carriage subsystem. Following review of the initial Q4C baseline, this Q4C.1 hotfix resolves the exact 28T turnaround idler pitch geometry, restores the frozen Quad Dock base width ($144.000\text{ mm}$), closes the global paper Z datum ($Z_{paper} = 0.000\text{ mm}$), eliminates Home block overhang on the Y linear rails, adds real fabrication/fastener features to all custom parts, and executes systematic continuous XY motion grid and 4-bay tool-change path audits.
- **Key Technical Decisions & Physical Realizations:**
  1. **Zero Q1/Q2/Q3 Geometry Modification:** The frozen Q1/Q2/Q3 subsystem (`cad/export/*.step` and `cad/build_q3c_cad_assembly.py`) remains strictly 100% immutable (0 lines changed).
  2. **Mathematically Exact Front Turnaround Idler Pitch Geometry:**
     - GT2 pitch $p = 2.000\text{ mm}$, tooth count $N = 28$.
     - Exact pitch radius: $r_p = \frac{28 \times 2}{2\pi} = \frac{28}{\pi} \approx \mathbf{8.912676813\text{ mm}}$ ($D_p \approx \mathbf{17.825353626\text{ mm}}$).
     - Inner/outer lane separation: $\Delta X_{lane} = 2 r_p = \mathbf{17.825353626\text{ mm}}$ (replaces the rounded $18.000\text{ mm}$ candidate).
     - Inner Y-lanes: Left Inner $X = -32.174646\text{ mm}$, Right Inner $X = +482.174646\text{ mm}$.
     - Front Idler Centers: Left $(-41.087323, -25.000)\text{ mm}$, Right $(+491.087323, -25.000)\text{ mm}$.
     - Gantry Idler Centers: Left Smooth A-2 $(-25.808449, Y_G + 8.633802)\text{ mm}$, Right Smooth B-2 $(+475.808449, Y_G - 21.366198)\text{ mm}$.
     - Installed Belt Lengths: $L_A = L_B = \mathbf{1949.245065\text{ mm}}$ ($\Delta L = -0.101\text{ mm}$ from Q4B.2 $1949.346\text{ mm}$), verified invariant across all carriage positions.
  3. **Restored Quad Dock Base Geometry:**
     - Restored overall Quad Dock base width to exactly $\mathbf{144.000\text{ mm}}$ ($X \in [153.000, 297.000]\text{ mm}$), correcting the unauthorized $146.0\text{ mm}$ deviation.
     - 4 bays at pitch $P = 32.000\text{ mm}$ ($X \in [177, 209, 241, 273]\text{ mm}$, active span $124.000\text{ mm}$, side margins $10.000\text{ mm}$).
  4. **Global Machine Z Datum Closure & Representative Pen Modeling:**
     - Machine $Z = 0.000\text{ mm}$ is defined strictly at the nominal upper paper surface.
     - Bed platen top is at $Z = -0.100\text{ mm}$ ($5.0\text{ mm}$ plate spanning $Z \in [-5.100, -0.100]\text{ mm}$).
     - CoreXY mechanism elevated by $\Delta Z_{global} = +45.000\text{ mm}$ (frame centerline at $Z = +45.000\text{ mm}$, Belt A at $Z = +50.000\text{ mm}$, Belt B at $Z = +40.000\text{ mm}$).
     - Representative pen ($\varnothing 12.0\text{ mm}$ body in $\varnothing 12.5\text{ mm}$ bore) modeled touching $Z = 0.000\text{ mm}$ in `DRAW_NOMINAL`.
     - In `PEN_UP`, pen nib retracts to $Z = +8.000\text{ mm}$.
     - Lowest moving carriage part (cam lobe at park $120^\circ$) is at Machine $Z = +4.360\text{ mm}$, providing $+4.460\text{ mm}$ clearance above the bed platen.
  5. **Linear Guide Rail Home Engagement Closure:**
     - $450.0\text{ mm}$ Y-rails repositioned to span $Y \in \mathbf{[-30.000, +420.000]\text{ mm}}$ (center $Y = +195.000\text{ mm}$).
     - At Home ($Y = 0.0\text{ mm}$), $45.4\text{ mm}$ MGN12H block spans $Y \in [-22.7, +22.7]\text{ mm} \implies \mathbf{+7.300\text{ mm}}$ front rail margin.
     - At Max Stroke ($Y = 375.0\text{ mm}$), block spans $Y \in [352.3, 397.7]\text{ mm} \implies \mathbf{+22.300\text{ mm}}$ rear rail margin.
     - X-rail ($550.0\text{ mm}$) provides $+27.300\text{ mm}$ end margins at both stroke limits.
  6. **Gantry Beam Orientation & Structural Clearance:**
     - 2040 gantry beam oriented vertically ($20\text{ mm Y} \times 40\text{ mm Z}$) to fit within belt lanes with $+4.310\text{ mm}$ side air clearance and $7.22\times$ vertical stiffness increase.
  7. **Dual-Deck Rear Motor / Return-Idler Axial Stacking:**
     - Rear-Left: Motor A mounted inverted (shaft down to $Z = +50.0\text{ mm}$); stationary Idler B-5 on lower deck ($Z = +40.0\text{ mm}$).
     - Rear-Right: Motor B mounted upright (shaft up to $Z = +40.0\text{ mm}$); stationary Idler A-5 on upper deck ($Z = +50.0\text{ mm}$).
     - Independent stationary M5 shoulder axles provide $1.750\text{ mm}$ axial air gap, ensuring zero shaft coupling.
  8. **Custom Parts Fabrication Realization:**
     - `X_CARRIAGE_ADAPTER`: 4x M3 Q3 mount holes ($36 \times 64\text{ mm}$), 4x M3 counterbore holes for MGN12H block ($20 \times 20\text{ mm}$), deep servo and cam sweep relief cutouts, tensioner guide slots, drag chain tab.
     - `BELT_TENSIONERS`: 4x independent sliders with GT2 toothed clamping channels, captive hex M3 nut pockets, M3 jackscrews, anti-rotation guide tongues ($\pm 10\text{ mm}$ stroke).
     - `MOTOR_MOUNT_A` & `B`: NEMA 17 4-hole pattern ($31 \times 31\text{ mm}$, M3), $\varnothing 22\text{ mm}$ pilot bore, frame M5 holes, stationary idler axle boss with inner-race support.
     - `IDLER_MOUNTS`: M5 axle holes, bearing inner-race support bosses ($\varnothing 7.0 \times 0.5\text{ mm}$), flange clearance recesses ($\varnothing 24\text{ mm}$).
     - `GANTRY_END_BRACKETS`: 2040 beam end bolts (2x M5), MGN12H block holes (4x M3), idler axle holes, drag chain bracket interface.
     - `WORK_BED`: 3-point kinematic leveling pads at $(60, 30)$, $(390, 30)$, $(225, 300)\text{ mm}$ with M4 thumbscrews and spring reference envelopes.
  9. **Continuous Collision Grid Audit (Q4-Internal Closure):**
     - 31 static pairwise checks: all CLEARANCE pairs report $0.0000\text{ mm}^3$ intersection volume and positive distance.
     - 54-state XY motion grid sweeps ($X \in [0, 450]\text{ mm}$, $Y \in [0, 375]\text{ mm}$): moving belts regenerated dynamically; Belt A vs Belt B gap $\ge 4.000\text{ mm}$; zero frame/gantry/bed collisions.
     - Pulley flange axial clearance: $1.250\text{ mm}$ symmetric clearance across all 10 wheels.
     - Fastener tool access: line-of-sight clearance verified for all fasteners; 12-stage sequential assembly order verified with zero trapped permanent fasteners.
  10. **Autonomous Tool Release Vector Kinematic Block Finding:**
      - The unauthorized $\Delta Y = -2\dots -5\text{ mm}$ override was deleted.
      - Tested the exact authoritative upstream frozen simultaneous coupled vector:
        $$\Delta Y(t) = -1.000 \cdot t, \quad \Delta Z(t) = +1.500 \cdot t \quad (t \in [0, 1] \text{ in } 0.05 \text{ steps})$$
      - **Result:** Across all 4 bays, a mechanical collision of **$1.316\text{ mm}^3$** (peak $1.422\text{ mm}^3$) occurs between the `Receiver_Plate_V1` Key Pin and the `Tool_Sleeve_V1_1` notch ceiling.
      - **Root Cause:** The Key Pin has $1.457\text{ mm}$ engagement into the blind notch along $Y$. Retracting only $1.000\text{ mm}$ in $Y$ leaves $0.457\text{ mm}$ of pin inside the notch while the cam elevates $1.500\text{ mm}$ against only $0.300\text{ mm}$ ceiling clearance.
      - **Status:** **BLOCKED BY UPSTREAM FROZEN INTERFACE.** Q4 cannot alter frozen tool/receiver geometry.
- **Deliverables & Clean Archive:**
  - Exported 11 component STEP files, full assembly `Q4C_FULL_ASSEMBLY.step`, and 6 operational state assemblies.
  - Packaged `cad/cad.zip` with verified zero macOS metadata, `.DS_Store`, or `__pycache__` artifacts (36 clean files).
  - Engineering report generated at `cad/Q4C_ENGINEERING_REPORT.md`.
- **Traceability:**
  - CAD Implementation: `cad/build_q4c_corexy_assembly.py`
  - Collision Audit: `cad/q4c_collision_audit.py`
  - Calculations: `cad/q4b_calculations.py`
  - Specification: [04_corexy_frame_spec.md](04_corexy_frame_spec.md) (V2.4 Baseline)
  - Upstream Decision: [HW-DEC-Q4-002](hardware_decision_log.md#hw-dec-q4-002-q4b-dimensional-packaging--corexy-force-budget-baseline)

---

### HW-DEC-Q3-AMEND-001: Q3 Tool-Release Motion Sequence Amendment
- **Status:** `FROZEN AMENDMENT (GEOMETRY IMMUTABLE — MOTION SEQUENCE AMENDED)`
- **Date:** 2026-09-23
- **Scope:** Kinematic Motion Sequence for Tool Release and Reverse Autonomous Pickup
- **Context & Problem Statement:**
  In Q4C.1, testing the frozen simultaneous tool-release vector ($\Delta Y = -1.000\text{ mm}, \Delta Z = +1.500\text{ mm}$) revealed a $1.316\text{ mm}^3$ collision between the frozen `Receiver_Plate_V1` Key Pin and the frozen `Tool_Sleeve_V1_1` notch ceiling. The Key Pin engages $1.457\text{ mm}$ along $Y$ into the sleeve notch, while vertical ceiling clearance is only $0.300\text{ mm}$. Retracting only $1.000\text{ mm}$ in $Y$ left $0.457\text{ mm}$ of the pin trapped beneath the ceiling when elevated $1.500\text{ mm}$.
- **Resolution & Decision:**
  1. **Strict Immutability Guarantee:** All 14 frozen Q1/Q2/Q3 STEP files and CAD scripts remain 100% untouched and SHA-256 hash verified.
  2. **Authorized Staged Decoupled Motion Sequence:**
     - **Phase A (Horizontal Disengagement):** Carriage retreats along $-Y$ by $\Delta Y = -2.500\text{ mm}$ ($1.457\text{ mm}$ geometric pin engagement $+ 1.043\text{ mm}$ safety margin) at fixed $Z$ ($Z = Z_{DOCK\_MATE} = +6.500\text{ mm}$).
     - **Phase B (Vertical Elevation):** Z-lifter elevates $\Delta Z = +1.500\text{ mm}$ to $Z_{DOCK\_RELEASE} = +8.000\text{ mm}$ with $Y$ held fixed at $\Delta Y = -2.500\text{ mm}$. Clearance to tool notch ceiling is $\ge 1.800\text{ mm}$.
     - **Phase C (Safe Departure):** Carriage departs along $-Y$ into the active plotting envelope.
     - **Autonomous Reverse Pickup:** Exact kinematic reverse ($\text{Approach at } Z = +8.000\text{ mm} \to \text{Descend } \Delta Z = -1.500\text{ mm} \to \text{Advance } \Delta Y = +2.500\text{ mm} \to \text{Kinematic Seat & Magnetic Lock}$).
  3. **Audit Results Across All 4 Bays ($X = 177, 209, 241, 273\text{ mm}$):**
     - Phase A Retreat Overlap: $\mathbf{0.000000\text{ mm}^3}$ (PASS)
     - Phase B Lift Overlap: $\mathbf{0.000000\text{ mm}^3}$ (PASS)
     - Adjacent parked tools clearance: $\mathbf{\ge 2.374\text{ mm} \ge 1.500\text{ mm}}$ (PASS)
     - Passive dock geometric capture: **PASS** (shoulders and slot walls constrain tool sleeve).
     - Magnetic holding force: Classified as `PHYSICAL TEST PENDING`.
- **Traceability:**
  - Amended Specification: [03_carriage_and_lifter_spec.md](03_carriage_and_lifter_spec.md) Section 3.6
  - Verification Script: `cad/q4c_collision_audit.py` (Audit 8)

---

### HW-DEC-Q4-003: Q4C.2 Consolidated Mechanical Closure & Verification Baseline
- **Status:** `100% ALL ACCEPTANCE GATES PASS — Q4 FINAL FREEZE AUTHORIZED`
- **Date:** 2026-09-23
- **Scope:** Monolithic Custom CAD Part Closure, Translating Tensioner Mechanics, 6,916-State Dense XY Motion Grid Audit, 4-Bay Tool-Change & Pickup Verification, B-Rep Endstop Safety Margins, and Clean Archive Export
- **Context & Problem Statement:**
  Consolidates and closes the three independently confirmed Q4 blockers: (1) disconnected/non-manufacturable custom CAD parts (`X_CARRIAGE_ADAPTER`, `MOTOR_MOUNT_A`, `MOTOR_MOUNT_B`), (2) translating tensioner slider/housing clearance and stroke audit, and (3) 4-bay staged tool-change and B-Rep endstop verification.
- **Key Technical Decisions & Physical Realizations:**
  1. **Monolithic Custom Part Topology Closure:**
     - `X_CARRIAGE_ADAPTER.step`: Reduced to **exactly 1 connected solid** ($V = 79,810.09\text{ mm}^3$) by adding a continuous $8.0\text{ mm}$ top bridge deck ($Z \in [65.5, 73.5]\text{ mm}$) spanning over the 2040 beam, rear vertical drop tab ($Z \in [33.0, 69.5]\text{ mm}$), L-bracket trigger flag, and cleanly bounded servo/cam cutouts.
     - `MOTOR_MOUNT_A.step` & `MOTOR_MOUNT_B.step`: Reduced to **exactly 1 connected solid each** ($V = 56,850.50\text{ mm}^3$ and $54,723.89\text{ mm}^3$) by adding continuous vertical load-bearing sidewalls/gussets connecting the frame base, motor deck, and stationary idler axle boss.
     - `BELT_TENSIONERS.step`: Modeled as **4 independent translating sliders** ($14.0 \times 7.4 \times 9.0\text{ mm}$) inside guide channels with captive M3 hex nut pockets, toothed GT2 clamping channels, and M3 jackscrews. Zero floating solids (**PASS**).
  2. **Translating Tensioner Full-Stroke Audit:**
     - Audited 25 stroke steps across $[-6.0, +6.0]\text{ mm}$ in $0.5\text{ mm}$ steps.
     - Max forbidden overlap volume: $\mathbf{0.000000\text{ mm}^3}$ (PASS).
     - Minimum sliding clearance to housing: $\mathbf{0.2000\text{ mm}}$ (design nominal $0.200\text{ mm}$, PASS).
  3. **Dense 6,916-State XY Motion Grid Swept-Volume Audit:**
     - Sampled $X \in [0.0, 450.0]\text{ mm}$ (91 steps) and $Y \in [0.0, 375.0]\text{ mm}$ (76 steps) at $5.0\text{ mm}$ regular grid.
     - Evaluated 48,305 B-Rep boolean pairs across all moving and stationary assemblies.
     - Max forbidden overlap volume: $\mathbf{0.000000\text{ mm}^3}$ (Target: $\le 1.0\times 10^{-4}\text{ mm}^3$).
     - Global minimum clearance: $\mathbf{0.5000\text{ mm}}$ at Adapter vs Gantry Beam ($X=0, Y=0$).
     - Boolean failures or skips: $\mathbf{0}$ (**PASS**).
  4. **Four-Bay Staged Tool Release & Reverse Pickup:**
     - Phase A retreat ($\Delta Y = -2.500\text{ mm}$), Phase B lift ($\Delta Z = +1.500\text{ mm}$), Phase C departure, and reverse pickup evaluated across all 4 bays ($X \in [177, 209, 241, 273]\text{ mm}$).
     - Max overlap: $\mathbf{0.000000\text{ mm}^3}$ across all phases and all bays (**PASS**).
     - Minimum clearance to adjacent tools: $\mathbf{2.374\text{ mm} \ge 1.500\text{ mm}}$ (**PASS**).
     - Passive dock geometric capture: **PASS**.
  5. **B-Rep Endstop Sensor Envelopes & Tolerance Stack:**
     - Modeled KW12 microswitches, mounts on gantry/corner brackets, elastomeric bumpers, and moving trigger flags.
     - Applied conservative tolerance stack: $\Delta_{stack} = \pm 0.800\text{ mm}$ ($\pm 0.25\text{ mm}$ switch actuation, $\pm 0.05\text{ mm}$ repeatability, $\pm 0.20\text{ mm}$ mount holes, $\pm 0.30\text{ mm}$ fabrication).
     - X-Axis: Trigger at $X = 0.0\text{ mm}$, bumper at $X = -6.0\text{ mm}$, rigid crash at $X = -12.0\text{ mm}$. Worst-case margin $= 12.0 - 0.8 = \mathbf{11.200\text{ mm} \ge 2.000\text{ mm}}$ (**PASS**).
     - Y-Axis: Trigger at $Y = 0.0\text{ mm}$, bumper at $Y = -6.0\text{ mm}$, rigid crash at $Y = -14.0\text{ mm}$. Worst-case margin $= 14.0 - 0.8 = \mathbf{13.200\text{ mm} \ge 2.000\text{ mm}}$ (**PASS**).
  6. **Frame Rear Beam Extension:**
     - Rear 2020 extrusion moved to $Y = 470.0\text{ mm}$ (side rail lengths $545.0\text{ mm}$), eliminating frame-to-dock overlap and providing $+9.0\text{ mm}$ clearance to dock and $+4.357\text{ mm}$ clearance to Q3 at $Y = 375.0\text{ mm}$.
  7. **Clean Archive & Exports:**
     - All 11 dedicated STEP files, 1 full assembly, and 6 operational state assemblies exported to `cad/export_q4c/`.
     - Verified clean `cad/cad.zip` (38 files, zero macOS metadata, zero `__pycache__`).
- **Physical Validation Disclaimers (Strictly Maintained):**
  - Magnetic holding force: `PHYSICAL VALIDATION PENDING`.
  - Printed tolerance & shrinkage: `PHYSICAL VALIDATION PENDING`.
  - Belt tension calibration: `PHYSICAL VALIDATION PENDING`.
  - Microswitch repeatability: `PHYSICAL VALIDATION PENDING`.
- **Traceability:**
  - CAD Implementation: `cad/build_q4c_corexy_assembly.py`
  - Collision Audit: `cad/q4c_collision_audit.py`
  - Engineering Report: `cad/Q4C_ENGINEERING_REPORT.md`
  - Specification: [04_corexy_frame_spec.md](04_corexy_frame_spec.md) (V2.5 Baseline)
  - Tool Release Amendment: [HW-DEC-Q3-AMEND-001](hardware_decision_log.md#hw-dec-q3-amend-001-q3-tool-release-motion-sequence-amendment)

### HW-DEC-Q4-004: Q4C.3 Corrective CAD and Release Gate
- **Status:** `PROVISIONAL CAD CANDIDATE / Q4 FINAL FREEZE NOT AUTHORIZED`
- **Date:** 2026-09-26
- **Decision:** Supersede the Q4C.2 **release verdict**, not its historical record. Use `cad/build_q4c_corexy_assembly.py`, `cad/q4c3_verification.py`, and `cad/Q4C3_HOTFIX_REPORT.md` as the current Q4C.3 CAD and test evidence. Q1–Q3 exported STEP geometry remains unchanged.
- **Corrective scope:** Enlarge the frame to 760 × 665 mm and gantry/rail to 700/670 mm; add front-idler flange reliefs, four M3 Y-block holes per gantry bracket, and a provisional **left** cable-chain tab. The tab extends to X = −183 mm, so frame dimensions are not the whole-machine envelope. The older Q4C.2 dimensions, 1949 mm belt length, and 6,916-state PASS do not validate this changed geometry.
- **Evidence:** Q4C.3 verifier checks all 14 frozen upstream STEP hashes, saved STEP topology, M3/pocket features, 41 tensioner positions over ±10 mm, 304 sampled XY states at 25 mm, four staged dock bay paths, and sampled X/Y endstop geometry. This is sampled B-Rep evidence, not continuous swept-volume or physical reliability proof.
- **Open release gates:** (1) dock retention in −Y and measured receiver separation versus dock holding force, then at least 100 release/pickup cycles; (2) actual idler, MGN12H, fastener and drag-chain supplier fit; (3) articulated cable bend/connector and continuous collision proof; (4) physical belt, endstop, printed-part and structural testing. No purchased SKU, magnet grade, force target or chain cut length is frozen by this record.
- **Q2 discrepancy:** [02_tool_changer_spec.md](02_tool_changer_spec.md) historically mentions an auxiliary rear dock magnet, but the team's latest input specifies none. The Q4C.3 four-bay dock now copies the frozen Q2 mechanical fork-entry stop after correcting an over-cut Q4-only entrance. Resolve the contradictory magnet text through a separate explicit Q2 clarification; this record does **not** change Q2 STEP geometry or establish physical release reliability.
- **2026-09-26 system-test response:** The team now proposes no auxiliary dock magnet, N52 as the tool/receiver grade, 18–22 N axial coupling force, ≤0.05 mm nib repeatability over ≥100 cycles, and no drop/mis-seat at 3000 mm/s². These are input criteria, not measured results or a Q2 geometry change. The response repeats the superseded 550 mm X rail; current Q4C.3 remains 670 mm. A prior endpoint-only 5 mm dock check missed the frozen Q2 stop lip at intermediate −Y displacement; the Q4 copy has been repaired to match Q2. **The rigid stop then blocks the specified coupled-tool +Y approach/−Y pickup, so the active verifier must fail and fabrication release remains blocked.** Motor A/B seating and A-shaft/base clearance were corrected in source and added to the active verifier. The 18/20 mm chain connector pitch and proposed Z 55–65 tab location await a selected supplier drawing and integrated fit test.
- **Traceability:** [04_corexy_frame_spec.md](04_corexy_frame_spec.md) V2.6; [06_validation_plan.md](06_validation_plan.md) TP-07/TP-08; `cad/Q4C3_HOTFIX_REPORT.md`.

### HW-DEC-Q4-005: Passive Dock Redesign Prototype
- **Status:** `CONCEPT / NOT FROZEN / NO FABRICATION RELEASE`
- **Date:** 2026-09-26
- **Authority:** The team authorized reopening the dock design to resolve Q4C.3's rigid entrance/pickup contradiction. This record does not overwrite historical HW-DEC-002/006 or change any Q1–Q3 STEP, tool sleeve, receiver, or lifter geometry.
- **Candidate:** A separate 160 mm four-bay dock base with 36 mm bay pitch (X = 171, 207, 243, 279 mm), without the rigid front lip, plus one replaceable, laterally deflecting right-hand finger per bay. The 3.0 mm free-tip movement is modeled as two kinematic envelopes; no physical spring is qualified. The separate concept source and STEP exports live under `cad/q4c4_passive_dock_prototype.py` and `cad/export_q4c4_prototype/`. These Q2 packaging changes are **not approved baseline dimensions**.
- **Evidence and blockers:** The concept's source B-Reps pass seated/rest capture and open-state approach sampling for all four bays, preserving the 14 Q1–Q3 STEP hashes. It does **not** provide a carriage-actuated unlatch for automatic pickup; minimum nominal finger/base clearance remains 0.25–0.30 mm; root clamp, spring force/strain, fatigue and hardware testing remain open. It is not integrated into `Q4C_FULL_ASSEMBLY.step` and does not supersede Q4C.3's FAIL verdict. See `cad/Q4C4_PASSIVE_DOCK_PROTOTYPE_REPORT.md`.

### HW-DEC-Q4-006: User-directed moving four-pen/four-servo architecture
- **Status:** `ARCHITECTURE REBASELINE IN PROGRESS / NO FABRICATION RELEASE`
- **Date:** 2026-09-27
- **Decision:** The intended OmniDraw machine carries all four pens on the X/Y carriage. Each pen has an independently controlled servo/slider; color selection raises every pen before lowering the selected one, and drawing coordinates include calibrated nib offsets. A rear tool pickup/drop-off dock is **not** part of this intended architecture. The Q4C.3 and Q4C.4 dock paths remain historical candidates, not Q4D release evidence. The archived Q1–Q3 STEP files are preserved unchanged for traceability but their single-tool architecture is not an active Q4D head interface.
- **Measured reference:** `hardware_3d/omnidraw_quad_pen_assembly_full.stl` contains four slider and four servo-body meshes at X = −36, −12, +12, +36 mm; the saved pose advances only the first slider by 10 mm. The STL has no editable source or verified nib/cam/fastener datums.
- **Current evidence and blockers:** The Q4D parametric reference STEP matches the 110 × 110 × 45 mm external envelope but is not a printable part. Q4 X rail length can contain the required carriage X −21..471 mm. The old Y rail overhangs by 13.2 mm; shifting both rails 20 mm forward leaves 6.8 mm front block margin in the candidate. The old X cable corridor intersects the reference head by 1647 mm³ and the old right bracket intersects its outer slider by 72 mm³ at the right plotting limit. Separate provisional rear cable corridors and 5.5 mm right-plate relief eliminate these simplified head intersections in nine sampled poses, but do not prove cable articulation or bracket strength. Servo actuation, head mount, endstops, nib contact, control interlock and physical tests remain open. See [08_four_servo_head_rebaseline.md](08_four_servo_head_rebaseline.md).

### HW-DEC-Q4-007: Q4D X-rail reserve and four-nib coordinate contract
- **Status:** `Q4D PACKAGING DECISION / CONTROLLER CONTRACT PROVISIONAL / NO FABRICATION RELEASE`
- **Date:** 2026-09-27
- **Decision:** Keep the 670 mm X rail with the 760 mm outer-X frame from the current parametric candidate while developing Q4D. Do not reintroduce the older 550 mm X rail/640 mm frame/580 mm gantry purchasing-list combination. For the provisional pen X centers −36, −12, +12, +36 mm and full 15..435 mm drawing X span, the carriage must reach −21..471 mm. A centered 670 mm rail and 45.4 mm MGN12H block leave 66.3 mm per rail end; a centered 550 mm rail leaves only 6.3 mm, below the provisional 20 mm rail-end reserve target. This is packaging arithmetic, not endstop or frame-strength proof.
- **Coordinate/control rule:** The selected nib's carriage target equals the drawing target minus its **measured** X/Y nib offset. The STL X centers are only provisional proxies, while Y/Z nib datums remain unmeasured. Color change must stop XY, raise all pens, confirm up, travel under the new offset while all are up, then lower exactly one. Bare `T0`–`T3` or repeated `G10 L2 P1` commands do not implement the four-servo interlock. No firmware pinout or servo-driver integration is released.
- **Evidence:** `cad/q4d_kinematic_budget.py`, `cad/q4d_color_change_contract.py`, 31 tests in `tests/test_q4d_*`, and `cad/q4d_head_fit_verification.py`. The latter passed a 225-pose × four-state **reference-proxy** candidate bracket/cable-corridor grid, but exits 2 because machine/fabrication release is still blocked. Actual servo linkage, head-to-X-block mount, nib geometry, articulated chain, endstops, mass/acceleration and physical validation remain open.

### HW-DEC-Q4-008: Q4D X-block/head mount space claim and Y datum correction
- **Status:** `PARAMETRIC FIT STUDY / NO FABRICATION RELEASE`
- **Date:** 2026-09-27
- **Decision:** Keep the Q1–Q3 exports and Q4C adapter untouched. The first Q4D Y+50 head pose left the slider proxy occupying the space needed by an X-block mounting plate. Move the Q4D head datum to gantry Y+58 and propose shifting the two Y rails 28 mm forward. This retains the modeled 6.8 mm front Y-block rail-end margin, conditional on an unmeasured nib datum and unfinished endstops.
- **Candidate geometry:** `cad/q4d_xblock_head_mount_concept.py` exports one valid B-Rep solid with four nominal Ø3.4 MGN12H 20 × 20 through-bores, two 4-mm inter-pen struts, and a front U-frame. Four holes on the head side are a **new-base proposal**, not measured legacy-STL holes. The closest modeled slider clearance is 1.5 mm; actual FDM and motion tolerances and strut strength remain unverified.
- **Evidence:** Saved STEP and integrated view-only frame STEP pass topology inspection; the 225 XY-pose × four active-pen-state proxy grid reports no positive-volume collision with the mount, relieved right bracket or straight cable corridors. This does not prove continuous sweep, stiffness, screw engagement/access, servo horn motion, real cable bend, nib reach, or physical reliability. See [08_four_servo_head_rebaseline.md](08_four_servo_head_rebaseline.md) and `tests/test_q4d_mount_concept.py`.

### HW-DEC-Q4-009: Named Q4D purchasing targets, not a drop-in fit claim
- **Status:** `PROCUREMENT-DESIGN BASELINE / PHYSICAL FIT AND FABRICATION RELEASE OPEN`
- **Date:** 2026-09-27
- **Decision:** Design the new four-pen head around four genuine TowerPro MG90S digital servos and four Zebra Sarasa Clip 0.5 pens (JJ15 family). The X carriage/rail target is genuine HIWIN standard MGN12H with a matching MGN12 rail at 670 mm length, not MGN12H-0, MGN12C, the old 550 mm rail or an unverified clone. Sources and nominal dimensions are recorded in [08_four_servo_head_rebaseline.md](08_four_servo_head_rebaseline.md#32-procurement-design-baseline-for-the-next-cad-iteration).
- **Non-interchangeable details:** An `MG90S` or `MGN12H` marketplace label alone does not prove the actual servo ears/shaft/horn geometry or rail/block variant. The pen's published Ø11 mm is not a clamp-zone/nib datum. The head should use replaceable/adjustable pen clamps and servo brackets rather than a claimed exact-fit monolith. Seek a dimensioned drawing and seller confirmation before committing a full set; the printed fit coupon is only a material/pen-hole calibration artifact.
- **Release condition:** No assertion of complete fit, FDM dimensional accuracy, servo force, ≥100-cycle reliability or print-and-assemble readiness until purchased samples and an integrated physical prototype pass the gates in the Q4D specification. Frozen Q1–Q3 exports remain untouched.
- **Body-layout refinement (2026-09-27):** `cad/q4d_mg90s_packaging_study.py` orients the published 12.2 mm body side along the 24 mm pen-pitch X direction. The resulting four body envelopes have 11.8 mm nominal inter-body clearance and zero B-Rep overlap against four sampled slider-active choices. This replaces the earlier 1.2 mm gap concern for a 22.8 mm-X orientation, **not** the unresolved ear/horn/shaft/linkage fit gate. The layout STEP is not a printable head.
- **Chassis concept (2026-09-27):** `cad/q4d_head_chassis_concept.py` and `cad/q4d_head_with_chassis_study.py` add a connected open guide frame, four servo body pockets and removable rear retainer bars to make the missing support geometry explicit. The saved chassis is one valid solid and 11 sampled slider positions per bay clear it in nominal B-Rep checks. PETG tolerance, retainer screws, MG90S ears/horn/shaft, linkage, actual nib and X-block attachment remain open; these STEP files do not authorize printing or purchase of a full set.
- **Pin-slot actuation study (2026-09-27):** `cad/q4d_pin_slot_actuation_study.py` proposes a 7.071 mm crank radius and a transverse follower slot. An assumed −45°..+45° sweep gives monotonic 0..10 mm slider travel, and nominal sampled B-Rep checks find no positive-volume collision with the current chassis/body proxies. Servo shaft datum, available angle, horn radius/strength, pin retention, force, hard stops and physical fit remain unverified. The new STEP is a study, not an approved print or full-BOM release.
- **One-bay fit-test draft (2026-09-27):** Trial frame, driven slider and removable servo retainer now have separate STEP/STL exports plus a six-part nominal assembly. Paired frame stops intercept ±1 mm overtravel beyond the 0..10 mm nominal slider motion, and a top Ø1.7 mm pilot proposes a flush M2 pen set screw. Saved STL meshes are watertight; sampled minimum walls are 1.752/1.6/1.654 mm, respectively. Default-orientation FDM support estimates for frame and slider are high, so this is **not** a print release. Real MG90S ear/shaft/horn, pen clamp zone, strength, threads, torque, head mount and physical fit remain open. See [08_four_servo_head_rebaseline.md](08_four_servo_head_rebaseline.md#36-one-bay-petg-fit-test-draft-not-a-complete-machine-head).

### HW-DEC-A4-001: Budget handwriting prototype replaces Q4D as the active build target
- **Status:** `ACTIVE RESEARCH DIRECTION / KIT SKU AND PHYSICAL FIT PENDING`
- **Date:** 2026-09-30
- **Decision:** Prioritize an A4 landscape, one-pen, one-servo prototype for Vietnamese handwriting research within the user's limited budget. The Q4D four-pen moving head and Q4C dock/CoreXY machine remain preserved design studies, not current purchasing or fabrication authority. No frozen Q1–Q3 files are edited by this decision.
- **Reuse:** Paper/world datum, pen-up/pen-down motion concept, removable pen-clamp idea, endstop safety and physical calibration protocol. Do not reuse Q4D's four-bay mechanism, 670 mm rail, idler stack, four-servo control or 24 V electronics as mandatory A4 parts.
- **Provisional evidence:** `cad/a4_single_pen_reference.py` and its STEP show a 400 × 320 mm 2020-frame envelope with A4 paper and one head proxy. Analytical checks cover nominal paper fit and box-envelope travel reserves only. Exact DIY kit SKU, V-wheel and carriage interfaces, pen/servo fit, firmware command path, electrical current and moving-belt clearance remain unverified. See [10_a4_single_pen_budget_rebaseline.md](10_a4_single_pen_budget_rebaseline.md).
