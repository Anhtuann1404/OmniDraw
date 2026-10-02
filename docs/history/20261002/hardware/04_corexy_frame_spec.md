# CoreXY Frame & XY Motion Specification

**Subsystem:** CoreXY Frame & XY Motion Platform
**Document Version:** V2.6 (Q4C.3 Corrective CAD Candidate)
**Status:** Q4C.3 PROVISIONAL CAD CANDIDATE | Q4 FINAL FREEZE NOT AUTHORIZED

> **Architecture notice (2026-09-27):** The frame dimensions below come from the historical one-pen/rear-dock Q4C candidate. The user-directed Q4D four-pen/four-servo head changes the carriage travel, Y-rail/endstop packaging, bracket clearance and cable routing; no whole-machine Q4D freeze exists. See [08_four_servo_head_rebaseline.md](08_four_servo_head_rebaseline.md).
**Baseline Date:** 2026-09-23
**Upstream Frozen Subsystems:** Q1 Tool Interface V1.1 (`FROZEN`), Q2 Receiver Plate V1 (`FROZEN`), Q3 Z-Carriage & Cam Lifter (`FINAL DESIGN FREEZE CLOSED`)
**Q4 Mechanical CAD Source of Truth:** `cad/build_q4c_corexy_assembly.py` / `cad/export_q4c/*.step`
**Collision & Motion Audit Source:** `cad/q4c3_verification.py` (`cad/q4c_collision_audit.py` is historical Q4C.2 evidence)
**Analytical Calculation Source:** `cad/q4b_calculations.py`
**Engineering Report:** `cad/Q4C3_HOTFIX_REPORT.md` (`cad/Q4C_ENGINEERING_REPORT.md` is historical)

> **Q4C.3 authority amendment (2026-09-26):** Sections below that describe Q4B/Q4C.2 dimensions or PASS/Final Freeze claims are historical and do not authorize fabrication. The current source and verifier are linked above. The Q4C.3 frame is 760 × 665 mm outside, the gantry beam is 700 mm, the X rail is 670 mm, the rear frame beam is at Y = 540 mm, and the two belt paths are approximately 2429.245 mm each. Travel remains 450 × 375 mm and the dock base remains 144 mm wide. The provisional cable-chain tab is on the **left** gantry bracket (X reaches −183 mm); thus 760 mm is the frame width, not a frozen whole-machine envelope. The 25 mm XY grid, dock path and endstop checks are sampled geometric evidence, not continuous swept-volume, actual switch, cable-bend or dock-retention proof. Q1–Q3 STEP geometry remains immutable. See [the Q4C.3 report](../../cad/Q4C3_HOTFIX_REPORT.md) for exact tests and open gates.

---

## 1. Subsystem Purpose & Scope

The **CoreXY Frame and XY Motion Subsystem (Q4)** provides the rigid structural chassis and two-degree-of-freedom ($XY$) planar positioning platform for the OmniDraw Plotter V1. It converts coordinated rotary motion from two stationary, frame-mounted stepper motors into high-speed, precise Cartesian translation of the X-axis carriage across the drawing bed and into the rear passive tool docking bay.

### 1.1 Architectural Scope & Authority Progression
- **Architecture Baseline (Q4A.1 — Closed):** Established physical motion topology, stacked two-plane belt scheme, MGN12 linear guide architecture, front-left homing convention, and Q3 interface accommodations.
- **Analytical Consistency & Belt-Geometry Hotfix (Q4B.2 — Closed / Accepted):** Replaced center-based routing with tangent-aware geometry, resolved front turnaround overlap via separate inner/outer Y-lanes, proved CoreXY differential kinematics analytically from path derivatives, established conservative Q3 carried envelopes uniting frozen Q3 mass with Q4B fixed mass, refined gantry structural analysis with a 5-case load sensitivity table, and confirmed identical installed belt lengths $L_A = L_B = 1949.346\text{ mm}$.
- **Detailed Mechanical CAD Realization (Q4C.1):** Realized the parametric 3D B-Rep CAD assembly, exact 28T GT2 front turnaround idler brackets ($r_p = 8.912677\text{ mm}, 2r_p = 17.825354\text{ mm}$), 3D swept timing belts ($L_A = L_B = 1949.245\text{ mm}$), and global paper datum ($Z=0.000\text{ mm}$, bed top at $Z=-0.100\text{ mm}$). Identified three critical blockers: non-manufacturable disconnected custom parts, unverified tensioner sliding mechanics, and simultaneous tool-release collision.
- **Consolidated Mechanical Closure Hotfix (Q4C.2 — Historical Baseline, Superseded):** Records the earlier closure claims; the Q4C.3 amendment above controls current release status:
  1. *Topology & Custom Part Connectivity:* Rebuilt `X_CARRIAGE_ADAPTER` (top bridge deck over 2040 beam, rear vertical drop tab, cleanly bounded servo/cam cutouts $\implies$ **exactly 1 connected solid**), `MOTOR_MOUNT_A` and `MOTOR_MOUNT_B` (continuous structural load-bearing webs connecting base, motor deck, and idler boss $\implies$ **exactly 1 connected solid each**), and `BELT_TENSIONERS` (**4 independent translating sliders** inside guide housings with zero floating bodies).
  2. *Translating Tensioner Mechanism:* Rebuilt tensioners into translating sliders ($14.0 \times 7.4 \times 9.0\text{ mm}$) inside fixed guide housings ($14.4 \times 7.8 \times 9.4\text{ mm}$) with $+0.200\text{ mm}$ clearance on all sliding faces, M3 jackscrew through-holes, and captive nut pockets. Full stroke audit across $[-6.0, +6.0]\text{ mm}$ (25 steps at $0.5\text{ mm}$) achieves $0.000000\text{ mm}^3$ overlap and $0.2000\text{ mm}$ min sliding clearance.
  3. *Dense 6,916-State XY Motion Grid Swept-Volume Audit:* Exhaustively sweeps $X \in [0.0, 450.0]\text{ mm}$ (91 samples) and $Y \in [0.0, 375.0]\text{ mm}$ (76 samples) at $5.0\text{ mm}$ step ($91 \times 76 = 6,916$ states). Evaluates 48,305 B-Rep boolean pairs: Max forbidden overlap volume $= \mathbf{0.000000\text{ mm}^3}$, global minimum clearance $= \mathbf{0.5000\text{ mm}}$ (adapter to gantry beam), zero boolean failures or skips (**PASS**).
  4. *Staged 4-Bay Tool Change & Reverse Pickup:* Authorized staged motion sequence (`HW-DEC-Q3-AMEND-001`) implemented across all 4 bays ($X = 177, 209, 241, 273\text{ mm}$): Phase A horizontal retreat $\Delta Y = -2.500\text{ mm}$ ($0.000000\text{ mm}^3$ overlap), Phase B vertical lift $\Delta Z = +1.500\text{ mm}$ ($0.000000\text{ mm}^3$ overlap), Phase C departure, and reverse pickup. Clearance to neighboring parked tools $\ge 2.374\text{ mm} \ge 1.500\text{ mm}$ (**PASS** across all 4 bays).
  5. *B-Rep Endstops & Rigid Crash Margins:* Modeled KW12 microswitches, mounts, moving trigger flags, and elastomeric bumpers. Evaluated with $\pm 0.8\text{ mm}$ conservative tolerance stack: X worst-case margin $= 11.200\text{ mm} \ge 2.0\text{ mm}$, Y worst-case margin $= 13.200\text{ mm} \ge 2.0\text{ mm}$ (**PASS**).
  6. *Frame Rear Beam Extension:* Extended side extrusions to $545.0\text{ mm}$ placing rear 2020 beam at $Y = 470.0\text{ mm}$, eliminating frame-to-dock overlap and providing $+9.0\text{ mm}$ clearance to dock and $+4.357\text{ mm}$ clearance to Q3 at maximum rear travel ($Y=375.0\text{ mm}$).
  7. *Immutability:* All 14 frozen Q1/Q2/Q3 STEP files remain 100% SHA-256 hash verified.
- **Downstream Immutability:** Upstream Q1/Q2/Q3 CAD geometry remains strictly untouched. Q4C.3 collision checks cover the sampled states defined in the active verifier, not all continuous operating poses.

---

## 2. Machine Coordinate System & Global Reference Datums

### 2.1 Global Machine Coordinate Definition
The global machine coordinate frame $\mathcal{F}_{machine} = \{X, Y, Z\}$ is established with a single, consistent origin:

```
                    [Machine +Y (Rear / Quad Dock Bay at Ymax)]
                                       ^
                                       |
                                       |
        [Left]                         |                         [Right]
   (X=0, Y=Y_travel) ------------------+----------------- (X=X_travel, Y=Y_travel)
                                       |
                                       |
                                       v
                    [Machine -Y (Front / User Loading)]
   (X=0, Y=0) -------------------------+----------------- (X=X_travel, Y=0)
   [HOME / ORIGIN]

   Machine +X : Pointing RIGHTWARD (transverse carriage motion)
   Machine +Y : Pointing REARWARD (longitudinal gantry motion toward dock)
   Machine +Z : Pointing UPWARD (vertical retraction away from paper)
```

- **Global Machine Origin $(0, 0, 0)$:** Established at the front-left boundary / home-side travel datum of the pen centerline:
  - $X = 0.000\text{ mm}$ at left travel limit of pen reference point.
  - $Y = 0.000\text{ mm}$ at front travel limit of pen reference point.
  - $Z = 0.000\text{ mm}$ at nominal upper surface of drawing paper.
- **Travel Stroke Envelope (ISO A3 Landscape Baseline):**
  - Transverse stroke: $X \in [0.000, 450.000]\text{ mm}$ ($X_{travel} = 450.000\text{ mm}$).
  - Longitudinal stroke: $Y \in [0.000, 375.000]\text{ mm}$ ($Y_{travel} = 375.000\text{ mm}$).
- **Active Plotting Bed Coordinates (ISO A3 Paper: $420.0 \times 297.0\text{ mm}$):**
  - Paper Left Edge: $X = 15.000\text{ mm}$; Paper Right Edge: $X = 435.000\text{ mm}$ ($X_{active} = 420.000\text{ mm}$).
  - Paper Front Edge: $Y = 15.000\text{ mm}$; Paper Rear Edge: $Y = 312.000\text{ mm}$ ($Y_{active} = 297.000\text{ mm}$).
  - Paper Hold-Down / Border Margins: $15.000\text{ mm}$ on all four borders.

### 2.2 Rear Quad Dock Global Coordinates
The rear Quad Dock is centered symmetrically across the useful carriage travel span:
- **Dock Center Global Coordinate:**
  $$X_{dock\_center} = \frac{X_{travel}}{2} = \frac{450.000}{2} = \mathbf{225.000\text{ mm}}$$
- **Individual Tool Bay Coordinates (Frozen Pitch $P = 32.000\text{ mm}$):**
  - Bay 1 Center: $X_{DOCK\_1} = 225.000 - 1.5 \times 32.000 = \mathbf{177.000\text{ mm}}$
  - Bay 2 Center: $X_{DOCK\_2} = 225.000 - 0.5 \times 32.000 = \mathbf{209.000\text{ mm}}$
  - Bay 3 Center: $X_{DOCK\_3} = 225.000 + 0.5 \times 32.000 = \mathbf{241.000\text{ mm}}$
  - Bay 4 Center: $X_{DOCK\_4} = 225.000 + 1.5 \times 32.000 = \mathbf{273.000\text{ mm}}$
- **Dock Mating Coordinates:**
  - Dock Mating Y-position: $Y_{DOCK\_MATE} = \mathbf{365.000\text{ mm}}$ (leaving $10.000\text{ mm}$ overtravel margin to $Y_{travel} = 375.000\text{ mm}$).
  - Dock Mating Z-height: $Z_{DOCK\_MATE} = \mathbf{+6.500\text{ mm}}$ (frozen upstream in HW-DEC-006 / Q3C-A.7).
  - Coordinated Release Stroke: $\Delta Z = +1.500\text{ mm}$ (to $Z = +8.000\text{ mm}$), $\Delta Y = -1.000\text{ mm}$ (to $Y = 364.000\text{ mm}$).
- **Reachability Verification:** All 4 bays ($X \in [177.0, 273.0]\text{ mm}$) lie well within the carriage travel span $[0.0, 450.0]\text{ mm}$, leaving a massive $177.000\text{ mm}$ clearance margin to both left and right frame limits.

### 2.3 Homing Corner & Endstop Strategy
- **Selected Homing Location: FRONT-LEFT $(X_{min}, Y_{min}) = (0, 0)$**.
- **Homing Direction:** Negative $X$ (left) and negative $Y$ (front).
- **Safety Rationale:** Homing directs motion strictly *away* from parked tools in the rear dock ($Y = 365\text{ mm}$), avoiding dock collision exposure during power-up or homing cycles.
- **Sensors:** Precision mechanical microswitches with roller levers or optical slot sensors (`CANDIDATE / SKU TBD`). Sensorless stall homing is deprecated on the primary prototype to avoid impact loads on printed gantry parts.

---

## 3. CoreXY Kinematic Topology

### 3.1 Drive Architecture & Schematic
The planar motion platform employs the classic two-motor CoreXY differential belt architecture. Two stationary stepper motors (Motor A and Motor B) are mounted rigidly to the frame at the rear corners:

```
       [Motor A (Rear-Left)]                         [Motor B (Rear-Right)]
              |                                               |
         (Upper Belt A)                                 (Lower Belt B)
              \                                               /
               \======== [QUAD-PEN DOCK BAY (Y=365)] =========/
               |                                             |
        [Y-Left Guide]                                [Y-Right Guide]
               |                                             |
               |             [X-Gantry Beam]                 |
               +==================[===]======================+
               |              [X-Carriage]                   |
               |                                             |
               |       [Active Plotting Bed (A3)]            |
               |                                             |
       [Front-Left Idler]                           [Front-Right Idler]
```

### 3.2 Forward & Inverse Kinematics
Let $\Delta A$ and $\Delta B$ represent the linear belt displacements imparted by Motor A and Motor B respectively (positive displacement pulls belt toward motor):

$$\begin{aligned}
\Delta X &= \frac{\Delta A + \Delta B}{2} \\
\Delta Y &= \frac{\Delta A - \Delta B}{2}
\end{aligned}$$

Inverse kinematics for motor step execution:

$$\begin{aligned}
\Delta A &= \Delta X + \Delta Y \\
\Delta B &= \Delta X - \Delta Y
\end{aligned}$$

### 3.3 Kinematic Motion States
- **Pure $+X$ Translation (Right):** $\Delta A = \Delta B > 0 \implies \Delta X > 0, \Delta Y = 0$. Both motors rotate forward at identical velocity.
- **Pure $-X$ Translation (Left):** $\Delta A = \Delta B < 0 \implies \Delta X < 0, \Delta Y = 0$. Both motors rotate reverse at identical velocity.
- **Pure $+Y$ Translation (Rearward toward Dock):** $\Delta A = -\Delta B > 0 \implies \Delta X = 0, \Delta Y > 0$. Motors rotate in opposite directions.
- **Pure $-Y$ Translation (Forward toward Home):** $\Delta A = -\Delta B < 0 \implies \Delta X = 0, \Delta Y < 0$. Motors rotate in opposite directions.
- **Diagonal $+45^\circ$ Motion ($+X, +Y$):** Kinematically, Motor A rotates forward ($\Delta A > 0$); Motor B remains locked ($\Delta B = 0$). *Dynamic Note:* While kinematic displacement $\Delta B = 0$, the holding motor B must exert active dynamic balancing force ($f_B \neq 0$) due to $X/Y$ moving mass asymmetry (see Section 9.1).
- **Diagonal $-45^\circ$ Motion ($+X, -Y$):** Kinematically, Motor B rotates forward ($\Delta B > 0$); Motor A remains locked ($\Delta A = 0$). Dynamically, $f_A \neq 0$ due to mass asymmetry.

---

## 4. Belt Routing, Node Tables & Belt-Plane Strategy

### 4.1 Stacked Dual-Plane CoreXY Routing & Separate Y-Lanes
The motion platform implements a **Two-Plane Stacked / Uncrossed CoreXY** architecture with **explicitly separated longitudinal tangent lanes**:
- **Upper Belt Plane (Plane 1, $Z_A = +50.000\text{ mm}$):** Carries **Belt A Installed Path**, driven by Motor A (Rear-Left).
- **Lower Belt Plane (Plane 2, $Z_B = +40.000\text{ mm}$):** Carries **Belt B Installed Path**, driven by Motor B (Rear-Right).
- **Resolution of Same-Plane Self-Overlap:**
  In a physical CoreXY system, a $180^\circ$ turnaround idler (front idlers A-3 and B-3) requires two physically distinct tangent lanes separated by $2 r_p$. For an exact 28T GT2 profile ($p = 2.000\text{ mm}, N = 28$):
  $$r_p = \frac{28 \times 2}{2\pi} = \frac{28}{\pi} \approx \mathbf{8.912676813\text{ mm}}, \quad \Delta X_{lane} = 2 r_p \approx \mathbf{17.825353626\text{ mm}}$$
  - **Left Longitudinal Lanes:**
    - Outer Lane: $X_{L,out} = -50.000\text{ mm}$ (runs from Front Turnaround Idler A-3 to Rear-Left Motor Pulley A-4).
    - Inner Lane: $X_{L,in} = -50.000 + 17.825354 = \mathbf{-32.174646\text{ mm}}$ (runs from Left Gantry Idler A-2 to Front Turnaround Idler A-3).
    - Lane Separation: $\Delta X_L = |-50.000 - (-32.174646)| = \mathbf{17.825354\text{ mm}} = 2 r_p$.
    - Clearance Verification: Gantry Idler A-2 is located at $X = -25.808449\text{ mm}$ with outer tangent at $X = -32.174646\text{ mm}$. The outer belt line ($X = -50.000\text{ mm}$) bypasses Gantry Idler A-2 with a clear $17.825\text{ mm}$ corridor, eliminating same-plane interference across the entire Y-stroke.
  - **Right Longitudinal Lanes:**
    - Outer Lane: $X_{R,out} = +500.000\text{ mm}$ (runs from Front Turnaround Idler B-3 to Rear-Right Motor Pulley B-4).
    - Inner Lane: $X_{R,in} = 500.000 - 17.825354 = \mathbf{+482.174646\text{ mm}}$ (runs from Right Gantry Idler B-2 to Front Turnaround Idler B-3).
    - Lane Separation: $\Delta X_R = |500.000 - 482.174646| = \mathbf{17.825354\text{ mm}} = 2 r_p$.
    - Clearance Verification: Gantry Idler B-2 outer tangent at $X = +482.174646\text{ mm}$ clears outer lane $X = +500.000\text{ mm}$ by $17.825\text{ mm}$.
- **Transverse Lanes:**
  - Front Turnaround Centerline: $Y_{front} = -25.000\text{ mm}$.
  - Rear Transverse Crossover Lane: $Y_{rear} = +420.000\text{ mm}$.
  - Carriage Anchor Transverse Lanes: $Y_{anch\_A} = Y_G + 15.000\text{ mm}$ (Upper Plane), $Y_{anch\_B} = Y_G - 15.000\text{ mm}$ (Lower Plane).
- **Belt Topology:** Belts are open-ended timing belts terminating at carriage clamp/tensioner blocks (**Belt A Installed Path** and **Belt B Installed Path**).

### 4.2 Exact Tangent-Aware Belt Node Tables

#### Belt A Installed Path (Upper Plane 1, $Z_A = +50.000\text{ mm}$)
Driven by Motor A (Rear-Left). Belt ends terminate at independent screw tensioners on the X-Carriage.

| Node ID | Physical Component | Motion Type | Center $(X, Y)$ (mm) | Pitch Radius $r$ (mm) | Incoming Tangent $(X, Y)$ (mm) | Outgoing Tangent $(X, Y)$ (mm) | Wrap Angle | Contact Surface |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A-1** | Carriage Left Anchor | Moving with XY | — | — | — | $(X_C - 20.000, Y_G + 15.000)$ | $0^\circ$ | Clamp Anchor |
| **A-2** | Left Gantry Idler 1 | Moving with Y | $(-25.808, Y_G + 8.634)$ | $6.366$ (20T) | $(-25.808, Y_G + 15.000)$ | $(-32.175, Y_G + 8.634)$ | $90^\circ\text{ CCW}$ | Smooth Idler |
| **A-3** | Front-Left Frame Idler | Fixed to Frame | $(-41.087, -25.000)$ | $8.913$ (28T) | $(-32.175, -25.000)$ | $(-50.000, -25.000)$ | $180^\circ\text{ CW}$ | Toothed Idler |
| **A-4** | Rear-Left Motor Pulley | Fixed to Frame | $(-43.634, +413.634)$ | $6.366$ (20T) | $(-50.000, +413.634)$ | $(-43.634, +420.000)$ | $90^\circ\text{ CW}$ | Toothed Motor Pulley |
| **A-5** | Rear-Right Frame Idler | Fixed to Frame | $(+493.634, +413.634)$ | $6.366$ (20T) | $(+493.634, +420.000)$ | $(+500.000, +413.634)$ | $90^\circ\text{ CW}$ | Toothed Idler |
| **A-6** | Right Gantry Idler 1 | Moving with Y | $(+493.634, Y_G + 21.366)$ | $6.366$ (20T) | $(+500.000, Y_G + 21.366)$ | $(+493.634, Y_G + 15.000)$ | $90^\circ\text{ CW}$ | Toothed Idler |
| **A-7** | Carriage Right Anchor | Moving with XY | — | — | $(X_C + 20.000, Y_G + 15.000)$ | — | $0^\circ$ | Clamp Anchor |

#### Belt B Installed Path (Lower Plane 2, $Z_B = +40.000\text{ mm}$) [Q4C.1 HOTFIX BASELINE]
Driven by Motor B (Rear-Right). Belt ends terminate at independent screw tensioners on the X-Carriage.

| Node ID | Physical Component | Motion Type | Center $(X, Y)$ (mm) | Pitch Radius $r$ (mm) | Incoming Tangent $(X, Y)$ (mm) | Outgoing Tangent $(X, Y)$ (mm) | Wrap Angle | Contact Surface |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **B-1** | Carriage Right Anchor | Moving with XY | — | — | — | $(X_C + 20.000, Y_G - 15.000)$ | $0^\circ$ | Clamp Anchor |
| **B-2** | Right Gantry Idler 2 | Moving with Y | $(+475.808, Y_G - 21.366)$ | $6.366$ (20T) | $(+475.808, Y_G - 15.000)$ | $(+482.175, Y_G - 21.366)$ | $90^\circ\text{ CW}$ | Smooth Idler |
| **B-3** | Front-Right Frame Idler | Fixed to Frame | $(+491.087, -25.000)$ | $8.913$ (28T) | $(+482.175, -25.000)$ | $(+500.000, -25.000)$ | $180^\circ\text{ CCW}$ | Toothed Idler |
| **B-4** | Rear-Right Motor Pulley | Fixed to Frame | $(+493.634, +413.634)$ | $6.366$ (20T) | $(+500.000, +413.634)$ | $(+493.634, +420.000)$ | $90^\circ\text{ CCW}$ | Toothed Motor Pulley |
| **B-5** | Rear-Left Frame Idler | Fixed to Frame | $(-43.634, +413.634)$ | $6.366$ (20T) | $(-43.634, +420.000)$ | $(-50.000, +413.634)$ | $90^\circ\text{ CCW}$ | Toothed Idler |
| **B-6** | Left Gantry Idler 2 | Moving with Y | $(-43.634, Y_G - 8.634)$ | $6.366$ (20T) | $(-50.000, Y_G - 8.634)$ | $(-43.634, Y_G - 15.000)$ | $90^\circ\text{ CCW}$ | Toothed Idler |
| **B-7** | Carriage Left Anchor | Moving with XY | — | — | $(X_C - 20.000, Y_G - 15.000)$ | — | $0^\circ$ | Clamp Anchor |

### 4.3 Tangent-Based Belt Length & Kinematic Derivative Proof

#### Straight Tangent Segments Formulation (Belt A)
Calculating the exact Euclidean distance between adjacent tangent points for Belt A:
1. $L_{A, 12} = \text{A-1 to A-2} = (X_C - 20.000) - (-25.808) = X_C + 5.808\text{ mm}$
2. $L_{A, 23} = \text{A-2 to A-3} = (Y_G + 8.634) - (-25.000) = Y_G + 33.634\text{ mm}$
3. $L_{A, 34} = \text{A-3 to A-4} = 413.634 - (-25.000) = 438.634\text{ mm}$
4. $L_{A, 45} = \text{A-4 to A-5} = 493.634 - (-43.634) = 537.268\text{ mm}$
5. $L_{A, 56} = \text{A-5 to A-6} = 413.634 - (Y_G + 21.366) = 392.268 - Y_G\text{ mm}$
6. $L_{A, 67} = \text{A-6 to A-7} = 493.634 - (X_C + 20.000) = 473.634 - X_C\text{ mm}$

Summing the straight segments for Belt A:
$$\begin{aligned}
L_{straight, A} &= L_{A, 12} + L_{A, 23} + L_{A, 34} + L_{A, 45} + L_{A, 56} + L_{A, 67} \\
&= (X_C + 5.808) + (Y_G + 33.634) + 438.634 + 537.268 + (392.268 - Y_G) + (473.634 - X_C) \\
&= 5.808 + 33.634 + 438.634 + 537.268 + 392.268 + 473.634 \\
&= \mathbf{1881.245\text{ mm}}
\end{aligned}$$

#### Straight Tangent Segments Formulation (Belt B)
Calculating the exact Euclidean distance between adjacent tangent points for Belt B:
1. $L_{B, 12} = \text{B-1 to B-2} = 475.808 - (X_C + 20.000) = 455.808 - X_C\text{ mm}$
2. $L_{B, 23} = \text{B-2 to B-3} = (Y_G - 21.366) - (-25.000) = Y_G + 3.634\text{ mm}$
3. $L_{B, 34} = \text{B-3 to B-4} = 413.634 - (-25.000) = 438.634\text{ mm}$
4. $L_{B, 45} = \text{B-4 to B-5} = 493.634 - (-43.634) = 537.268\text{ mm}$
5. $L_{B, 56} = \text{B-5 to B-6} = 413.634 - (Y_G - 8.634) = 422.268 - Y_G\text{ mm}$
6. $L_{B, 67} = \text{B-6 to B-7} = (X_C - 20.000) - (-43.634) = X_C + 23.634\text{ mm}$

Summing the straight segments for Belt B:
$$\begin{aligned}
L_{straight, B} &= L_{B, 12} + L_{B, 23} + L_{B, 34} + L_{B, 45} + L_{B, 56} + L_{B, 67} \\
&= (455.808 - X_C) + (Y_G + 3.634) + 438.634 + 537.268 + (422.268 - Y_G) + (X_C + 23.634) \\
&= 455.808 + 3.634 + 438.634 + 537.268 + 422.268 + 23.634 \\
&= \mathbf{1881.245\text{ mm}}
\end{aligned}$$

Notice that for both belts, $X_C$ and $Y_G$ cancel out identically: $+X_C - X_C = 0$ and $+Y_G - Y_G = 0$. The total straight path length is strictly invariant across all carriage and gantry positions.

#### Pulley Wrap Arc Lengths & Installed Path Length
- 4x $90^\circ$ wraps on 20T pulleys ($r_p = 6.366\text{ mm}$): $4 \times \left(\frac{\pi}{2} \times 6.366\right) = 2\pi \times 6.366 = 40.000\text{ mm}$.
- 1x $180^\circ$ wrap on 28T front idler ($r_p = 28/\pi\text{ mm}$): $\pi \times \frac{28}{\pi} = \mathbf{28.000\text{ mm}}$.
- Total Wrap Length: $L_{wraps} = 40.000 + 28.000 = \mathbf{68.000\text{ mm}}$.

$$L_{installed, A} = L_{installed, B} = 1881.245 + 68.000 = \mathbf{1949.245\text{ mm}}$$
Difference $|L_A - L_B| = \mathbf{0.000\text{ mm}}$ (exact geometric symmetry).

- **Nominal Packaging Range:** $L_{installed} \in [1940.0, 1960.0]\text{ mm}$.
- **Classification:** `Q4C REALIZED BELT LENGTH BASELINE`.
- **Recommended Roll Order:** $\approx 2200\text{ mm}$ per belt ($4.4 - 4.5\text{ m}$ total roll order), preserving $200 - 250\text{ mm}$ lead-in for carriage clamp and screw tensioner installation.
- **Tensioner Stroke:** $\pm 10.000\text{ mm}$ adjustment travel ($20.0\text{ mm}$ total jackscrew stroke).

#### Belt Face Continuity & Idler Tooth Contact Proof (Zero-Twist Rule)
A single timing belt features one continuous toothed inner face and one smooth outer back face. Without artificial twists:
1. **Belt A (Upper Plane):**
   - Motor Pulley A-4 engages belt teeth with clockwise (CW) wrap.
   - Therefore, all clockwise bends engage the **TOOTHED** face, while counter-clockwise bends engage the **SMOOTH** back face.
   - **A-2 (Left Gantry Idler 1):** CCW wrap ($90^\circ$) $\implies$ contacts **SMOOTH** back face $\implies$ **Smooth Flanged Idler**.
   - **A-3 (Front-Left Frame Idler):** CW wrap ($180^\circ$) $\implies$ contacts **TOOTHED** face $\implies$ **Toothed Idler**.
   - **A-4 (Rear-Left Motor Pulley):** CW wrap ($90^\circ$) $\implies$ contacts **TOOTHED** face $\implies$ **Toothed Drive Pulley**.
   - **A-5 (Rear-Right Frame Idler):** CW wrap ($90^\circ$) $\implies$ contacts **TOOTHED** face $\implies$ **Toothed Idler**.
   - **A-6 (Right Gantry Idler 1):** CW wrap ($90^\circ$) $\implies$ contacts **TOOTHED** face $\implies$ **Toothed Idler**.
2. **Belt B (Lower Plane):**
   - Motor Pulley B-4 engages belt teeth with counter-clockwise (CCW) wrap.
   - Therefore, all counter-clockwise bends engage the **TOOTHED** face, while clockwise bends engage the **SMOOTH** back face.
   - **B-2 (Right Gantry Idler 2):** CW wrap ($90^\circ$) $\implies$ contacts **SMOOTH** back face $\implies$ **Smooth Flanged Idler**.
   - **B-3 (Front-Right Frame Idler):** CCW wrap ($180^\circ$) $\implies$ contacts **TOOTHED** face $\implies$ **Toothed Idler**.
   - **B-4 (Rear-Right Motor Pulley):** CCW wrap ($90^\circ$) $\implies$ contacts **TOOTHED** face $\implies$ **Toothed Drive Pulley**.
   - **B-5 (Rear-Left Frame Idler):** CCW wrap ($90^\circ$) $\implies$ contacts **TOOTHED** face $\implies$ **Toothed Idler**.
   - **B-6 (Left Gantry Idler 2):** CCW wrap ($90^\circ$) $\implies$ contacts **TOOTHED** face $\implies$ **Toothed Idler**.
3. **Hardware Allocation:**
   - **Drive Pulleys (2x):** 20T GT2 drive pulleys (A-4, B-4).
   - **Smooth Flanged Idlers (2x):** Gantry lead-in idlers A-2 and B-2.
   - **Toothed Idlers (6x):** Front turnaround idlers A-3 and B-3 ($R=9.0\text{ mm}$ toothed), rear frame idlers A-5 and B-5 (20T toothed), gantry return idlers A-6 and B-6 (20T toothed).

#### Physical CoreXY Kinematic Verification from Path Derivatives
Let $S_{A,left}$ represent the belt segment length from carriage left anchor A-1 through idlers A-2 and A-3 to motor pulley A-4, and $S_{A,right}$ represent the segment from motor pulley A-4 through A-5 and A-6 to carriage right anchor A-7:
$$\begin{aligned}
S_{A,left} &= (X_C + 5.634) + (Y_G + 33.634) + 438.634 + \text{arcs} \\
&\implies \frac{\partial S_{A,left}}{\partial X_C} = +1, \quad \frac{\partial S_{A,left}}{\partial Y_G} = +1 \\
S_{A,right} &= 537.268 + (392.268 - Y_G) + (473.634 - X_C) + \text{arcs} \\
&\implies \frac{\partial S_{A,right}}{\partial X_C} = -1, \quad \frac{\partial S_{A,right}}{\partial Y_G} = -1
\end{aligned}$$

When Motor A rotates by linear displacement $\Delta A$ (feeding belt into the right branch and pulling from the left branch):
$$\Delta A = \Delta X_C + \Delta Y_G$$

Similarly, for Belt B (driven by Motor B at Rear-Right, with Left branch $S_{B,left}$ and Right branch $S_{B,right}$):
$$\begin{aligned}
S_{B,left} &= 537.268 + (422.268 - Y_G) + (X_C + 23.634) + \text{arcs} \\
&\implies \frac{\partial S_{B,left}}{\partial X_C} = +1, \quad \frac{\partial S_{B,left}}{\partial Y_G} = -1 \\
S_{B,right} &= (455.634 - X_C) + (Y_G + 3.634) + 438.634 + \text{arcs} \\
&\implies \frac{\partial S_{B,right}}{\partial X_C} = -1, \quad \frac{\partial S_{B,right}}{\partial Y_G} = +1 \\
&\implies \Delta B = \Delta X_C - \Delta Y_G
\end{aligned}$$

Solving the linear system confirms the classic differential CoreXY forward kinematics:
$$\Delta X = \frac{\Delta A + \Delta B}{2}, \quad \Delta Y = \frac{\Delta A - \Delta B}{2}$$
This proves that the corrected tangent routing strictly produces physical CoreXY motion without parasitic coupling.

### 4.4 Belt Plane Separation ($\Delta Z_{belt}$) & Axial Stack Derivation
The required vertical separation between Plane 1 ($Z = +5.0\text{ mm}$) and Plane 2 ($Z = -5.0\text{ mm}$) is governed by the physical axial stack of the gantry idlers:
1. **Belt Width ($W_{belt}$):** $6.000\text{ mm}$ (GT2 6 mm timing belt).
2. **Representative COTS Idler Stack:**
   - Standard 20T dual-bearing idlers have an overall flange-to-flange body height of $\approx 8.500\text{ mm}$ (bearing boss to flange edge).
   - Precision shim/washer between stacked bearings: $1.000 - 1.500\text{ mm}$ (DIN 988 precision spacer).
   - Total axial stack pitch: $8.500 + 1.000\text{ mm} = 9.500\text{ mm}$ (compact) to $8.500 + 1.500 + \text{clearance} \approx 11.500\text{ mm}$.
3. **Provisional Primary Packaging Candidate:**
   $$\Delta Z_{belt} = \mathbf{10.000\text{ mm}} \quad (\text{center-to-center pitch})$$
   - Edge-to-edge belt clearance: $\text{Clearance} = \Delta Z_{belt} - W_{belt} = 10.000 - 6.000 = \mathbf{4.000\text{ mm}}$.
4. **Status:** `PROVISIONAL PRIMARY CANDIDATE / TBD Q4C PROCUREMENT & DETAILED CAD STACK VERIFICATION`. Exact spacing will be frozen once the specific commercial idler pulley SKU is selected.

---

## 5. Linear Guidance Architecture

### 5.1 Guide Selection & Allocation
- **X-Axis Guide:** Single **MGN12-class linear rail** ($L = 550.0\text{ mm}$) mounted to the front face of the gantry beam, carrying a single long carriage block (**MGN12H**) (`PRIMARY CANDIDATE`).
- **Y-Axis Guides:** Twin parallel **MGN12-class linear rails** ($L = 450.0\text{ mm}$) mounted to the top faces of the left and right 2020 frame extrusions.

### 5.2 Single MGN12H Block Pitch Moment Verification
- Carriage + Q3 package nominal mass: $m_X \approx 0.332\text{ kg}$ ($F_{grav} \approx 3.26\text{ N}$).
- Center of mass overhang from rail ball center: $d_{overhang} \approx 25.0\text{ mm}$.
- Static pitch moment under gravity:
  $$M_{p\_static} = 3.26\text{ N} \times 0.025\text{ m} = \mathbf{0.0815\text{ N}\cdot\text{m}}$$
- Engineering docking load case ($10\text{ N}$ vertical at pen axis, $d \approx 45\text{ mm}$, engineering assumption, not measured force):
  $$M_{p\_dock} = 10.0\text{ N} \times 0.045\text{ m} = \mathbf{0.450\text{ N}\cdot\text{m}}$$
- **Catalog Reference Rating (MGN12H):** Basic static pitch moment $M_{p0} \approx 30.0 - 38.0\text{ N}\cdot\text{m}$ (Representative standard MGN12H catalog).
- **Moment Margin:** Representative MGN12H catalog comparison indicates the applied moment is small relative to representative static capacity; single-block architecture remains PRIMARY CANDIDATE; exact capacity margin TBD SELECTED SKU / Q4C.

### 5.3 Y-Rail Master-Slave Alignment Strategy
- **Master Rail (Left Y-Rail):** Fastened securely against the precision extrusion reference shoulder, defining the machine's primary $Y$-datum.
- **Slave Rail (Right Y-Rail):** Assembled with loose fasteners, swept through full stroke by the rigid gantry assembly, and tightened progressively to absorb extrusion straightness tolerances without ball binding.

---

## 6. X-Gantry Architecture & Structural Analysis

### 6.1 Extrusion Profile Evaluation: 2020 vs 2040
The gantry beam spans $L = 580.0\text{ mm}$ between the Y-carriage plates. Section properties are sourced from **Misumi 5-Series Aluminum Extrusions (HFS5-2020 and HFS5-2040)** in 6063-T5 aluminum ($E = 69\text{ GPa}, G = 26\text{ GPa}$):

| Parameter | 2020 Aluminum Extrusion (Misumi HFS5-2020) | 2040 Extrusion Oriented 40 mm Horizontal (Misumi HFS5-2040) | Performance Impact / Ratio | Traceability Source |
| :--- | :--- | :--- | :--- | :--- |
| **Linear Mass ($m_{lin}$)** | $0.48\text{ kg/m}$ ($278.4\text{ g}$ beam) | $0.95\text{ kg/m}$ ($551.0\text{ g}$ beam) | $+272.6\text{ g}$ mass penalty | Misumi Catalog |
| **Major Inertia ($I_z$, Horizontal)** | $0.72 \times 10^4\text{ mm}^4$ | $\mathbf{5.20 \times 10^4\text{ mm}^4}$ | **$7.22\times$ stiffer horizontally** | Misumi Catalog |
| **Minor Inertia ($I_y$, Vertical)** | $0.72 \times 10^4\text{ mm}^4$ | $\mathbf{1.40 \times 10^4\text{ mm}^4}$ | **$1.94\times$ stiffer vertically** | Misumi Catalog |
| **Torsional Constant ($J$)** | $0.28 \times 10^4\text{ mm}^4$ | $\mathbf{1.85 \times 10^4\text{ mm}^4}$ | **$6.61\times$ stiffer in torsion** | Misumi Catalog |
| **Vertical Sag ($\delta_v$, Self-wt + Rail + Carriage)** | $59.5\ \mu\text{m}$ ($0.060\text{ mm}$) | $\mathbf{37.6\ \mu\text{m}}$ ($0.038\text{ mm}$) | $37\%$ deflection reduction | Euler-Bernoulli Beam Model |
| **Torsional Tip Sag ($\delta_{tip}$, 40 mm Overhang)** | $10.4\ \mu\text{m}$ ($0.010\text{ mm}$) | $\mathbf{1.6\ \mu\text{m}}$ ($0.002\text{ mm}$) | Negligible angular twist | St. Venant Torsion Model |
| **Architectural Verdict** | REJECTED (Flexure exceeds budget) | **PRIMARY ANALYTICAL STRUCTURAL CANDIDATE** | $7.22\times$ horizontal stiffness | Analytical Sizing Candidate |

#### Horizontal Deflection Load Sensitivity Across Dynamic Cases
To evaluate gantry performance across actual operating regimes, mid-span horizontal beam deflection $\delta_h = \frac{F L^3}{48 E I_z}$ is evaluated across five distinct load cases (distinguishing derived operating loads from engineering sensitivity loads):

| Load Case Description | Load Category | Horizontal Force $F_h$ (N) | 2020 Flexure $\delta_h$ ($\mu\text{m}$) | 2040 Horiz. Flexure $\delta_h$ ($\mu\text{m}$) | Rigidity Ratio | Operational Relevance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Nominal Y-Accel ($1500\text{ mm/s}^2$)** | Derived operating load | $0.50\text{ N}$ | $4.1\ \mu\text{m}$ | **$0.6\ \mu\text{m}$** | $7.22\times$ | Nominal drawing strokes |
| **2. Peak Y-Accel ($3000\text{ mm/s}^2$)** | Derived operating load | $1.00\text{ N}$ | $8.2\ \mu\text{m}$ | **$1.1\ \mu\text{m}$** | $7.22\times$ | Rapid tool repositioning |
| **3. 10 N sensitivity** | Engineering sensitivity load | $10.00\text{ N}$ | $81.8\ \mu\text{m}$ | **$11.3\ \mu\text{m}$** | $7.22\times$ | Asymmetric belt vector load sensitivity |
| **4. 15 N sensitivity** | Engineering sensitivity load | $15.00\text{ N}$ | $122.7\ \mu\text{m}$ | **$17.0\ \mu\text{m}$** | $7.22\times$ | Combined dynamic load sensitivity |
| **5. 25 N overload sensitivity** | Engineering sensitivity load | $25.00\text{ N}$ | $204.6\ \mu\text{m}$ | **$28.3\ \mu\text{m}$** | $7.22\times$ | Worst-case overload sensitivity |

- **Selection Rationale:** Under combined dynamic loading ($15\text{ N}$), the 2020 profile flexes $122.7\ \mu\text{m}$, which severely compromises drawing line repeatability. Orienting the **2040 profile horizontally (40 mm width resisting horizontal Y-direction forces, 20 mm height resisting vertical Z-direction loads)** reduces horizontal flexure to just $17.0\ \mu\text{m}$ ($7.22\times$ stiffness improvement), maintaining mid-span deflection well below $30\ \mu\text{m}$ even under worst-case $25\text{ N}$ overload.
- **Classification:** **2040 Extrusion (Oriented 40 mm Horizontal) is designated as the PRIMARY ANALYTICAL STRUCTURAL CANDIDATE.**
- **Validation Caveat:** Rigidity and precision claims remain analytical predictions. Detailed deflection and vibrational mode verification remain pending Q4C finite element analysis (FEA) and physical prototype dial-indicator testing.

### 6.2 Q3 Interface Mounting & Clearance Relief
The immutable Q3 Z-carriage bolts directly to the front of the Q4 X-carriage adapter plate:
1. **Mounting Pattern:** 4x M3 clearance holes ($\varnothing 3.400\text{ mm}$) at $X_{Q3} = \pm 18.000\text{ mm}, Z_{Q3} = \pm 32.000\text{ mm}$ ($36 \times 64\text{ mm}$ rectangular pattern).
2. **Mounting Datum Face:** Rear face of `ZC_Fixed_Baseplate` at $Y_{Q3} = -27.000\text{ mm}$.
3. **Mandatory Carriage Relief Cutouts:**
   - *MG90S Servo Clearance:* The servo body extends rearward to $Y_{Q3} = -32.850\text{ mm}$ across $X_{Q3} \in [-42.700, -17.400]\text{ mm}$. The carriage plate must incorporate a clearance pocket/window of at least $6.0\text{ mm}$ depth behind $Y_{Q3} = -27.000\text{ mm}$ in this quadrant.
   - *Cam Sweep Clearance:* The Archimedean cam lobe sweeps through $Z_{Q3} \in [-40.000, -5.000]\text{ mm}$ across $X_{Q3} \in [-26.000, -14.000]\text{ mm}$. Carriage structure must remain clear of this envelope.

---

## 7. Moving-Mass Architecture & Traceable Mass Registers

### 7.1 Authoritative Q3 Mass Baseline & Conservative XY Sizing Union

#### Upstream Frozen Q3 Floating-Mass Analytical Sensitivity Baseline (03_carriage_and_lifter_spec.md / HW-DEC-Q3-FINAL-001)
The authoritative frozen baseline for the Q3 floating Z-slider mass remains strictly preserved from `docs/hardware/03_carriage_and_lifter_spec.md` Section 3.7 and Decision `HW-DEC-Q3-FINAL-001` (Q3C-B analytical baseline):
- **Low-Bound (Zero Infill / Thin Shells):** $\mathbf{52.92\text{ g}}$
- **Nominal Reference (Drafting Pen Baseline):** $\mathbf{62.13\text{ g}}$
- **High-Bound PLA (Dense / Heavy Tool):** $\mathbf{81.62\text{ g}}$
- **High-Bound PETG (Worst-Case Heavy Tool):** $\mathbf{82.27\text{ g}}$

#### Q4B Material-Based Packaging Re-Estimate (Non-Authoritative STEP Solid Audit Trail)
For independent cross-verification against CAD solid models, solid volumes from accepted Q3 STEP files (`cad/export/*.step`) were evaluated under polymer density variations ($1.05 - 1.27\text{ mg/mm}^3$):
- Fixed-to-XY Q3 Baseplate & Servo Mount: $68.17 - 77.21\text{ g}$ (Nominal $\mathbf{73.61\text{ g}}$).
- Floating Z-Slider Assembly Re-estimate: $56.40 - 68.35\text{ g}$ (Nominal $\mathbf{61.78\text{ g}}$, with `Receiver_Plate_V1` solid volume corrected to $5,945.42\text{ mm}^3$).
*(Designation: `Q4B MATERIAL-BASED PACKAGING RE-ESTIMATE` — audit trail only; does NOT replace the upstream frozen baseline).*

#### Conservative Total Q3 XY-Carried Mass Envelope (Synchronized 4-Case Model)
For conservative sizing of the Q4 motion platform, the total Q3 package mass carried by the XY carriage combines the frozen upstream floating mass sensitivity range with the fixed-to-XY carriage hardware across all 4 operational cases:
$$\begin{aligned}
\text{Total Carried Q3 Package (Low)} &= 52.92\text{ g (Frozen Low)} + 68.17\text{ g (Fixed Low)} = \mathbf{121.09\text{ g}} \\
\text{Total Carried Q3 Package (Nominal)} &= 62.13\text{ g (Frozen Nom)} + 73.61\text{ g (Fixed Nom)} = \mathbf{135.74\text{ g}} \\
\text{Total Carried Q3 Package (High PLA)} &= 81.62\text{ g (Frozen High PLA)} + 76.53\text{ g (Fixed High PLA)} = \mathbf{158.15\text{ g}} \\
\text{Total Carried Q3 Package (High PETG)} &= 82.27\text{ g (Frozen High PETG)} + 77.21\text{ g (Fixed High PETG)} = \mathbf{159.48\text{ g}}
\end{aligned}$$
- **Classification:** `CONSERVATIVE Q4 PACKAGING ENVELOPE` ($121.09 - 159.48\text{ g}$, Nominal $135.74\text{ g}$).

#### Detailed Q3 Component Mass Traceability Register

| Component / Sub-assembly | Material / Source | Solid Volume ($\text{mm}^3$) | Low Density ($1.05$) | Nominal ($1.20$) | High PLA ($1.24$) | High PETG ($1.27$) | Classification / Traceability |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ZC_Fixed_Baseplate** | Printed Polymer | $22,009.57$ | $23.11\text{ g}$ | $26.41\text{ g}$ | $27.29\text{ g}$ | $27.95\text{ g}$ | B-Rep Solid Volume |
| **ZC_Cam** | Printed Polymer | $915.37$ | $0.96\text{ g}$ | $1.10\text{ g}$ | $1.14\text{ g}$ | $1.16\text{ g}$ | B-Rep Solid Volume |
| **MG90S Servo** | Commercial Metal Gear | N/A (Envelope) | $13.00\text{ g}$ | $13.40\text{ g}$ | $14.00\text{ g}$ | $14.00\text{ g}$ | TowerPro MG90S Datasheet |
| **MGN9 Linear Rail (65 mm)** | Bearing Steel | $3,802.50$ | $24.70\text{ g}$ | $24.70\text{ g}$ | $24.70\text{ g}$ | $24.70\text{ g}$ | Standard MGN9 Catalog ($0.38\text{ kg/m}$) |
| **Q3 Fixed Fasteners / Inserts** | Steel / Brass | N/A | $6.40\text{ g}$ | $8.00\text{ g}$ | $9.40\text{ g}$ | $9.40\text{ g}$ | ENGINEERING PACKAGING ESTIMATE |
| **SUBTOTAL: Q3 Fixed Mass** | — | — | **$68.17\text{ g}$** | **$73.61\text{ g}$** | **$76.53\text{ g}$** | **$77.21\text{ g}$** | **Derived Fixed Subtotal** |
| **ZC_Moving_Slider** | Printed Polymer | $6,440.61$ | $6.76\text{ g}$ | $7.73\text{ g}$ | $7.99\text{ g}$ | $8.18\text{ g}$ | B-Rep Solid Volume |
| **Receiver_Plate_V1 Body** | Printed Polymer | $5,945.42$ | $6.24\text{ g}$ | $7.13\text{ g}$ | $7.37\text{ g}$ | $7.55\text{ g}$ | B-Rep Solid Volume (Corrected) |
| **Tool_Sleeve_V1_1 Body** | Printed Polymer | $10,113.19$ | $10.62\text{ g}$ | $12.14\text{ g}$ | $12.54\text{ g}$ | $12.84\text{ g}$ | B-Rep Solid Volume |
| **3x Steel Balls ($\varnothing 6\text{ mm}$)** | Chrome Steel | $339.30$ | $2.66\text{ g}$ | $2.66\text{ g}$ | $2.66\text{ g}$ | $2.66\text{ g}$ | Exact Solid ($7.85\text{ mg/mm}^3$) |
| **6x Magnets ($\varnothing 8 \times 2\text{ mm}$)** | NdFeB N35/N52 | $603.18$ | $4.52\text{ g}$ | $4.52\text{ g}$ | $4.52\text{ g}$ | $4.52\text{ g}$ | Exact Solid ($7.50\text{ mg/mm}^3$) |
| **MR84ZZ Follower + Pin** | Bearing + Steel Pin | $236.86$ | $1.60\text{ g}$ | $1.60\text{ g}$ | $1.60\text{ g}$ | $1.60\text{ g}$ | Representative Datasheet + Solid |
| **MGN9C Carriage Block** | Bearing Steel | $3,427.54$ | $16.00\text{ g}$ | $16.00\text{ g}$ | $16.00\text{ g}$ | $16.00\text{ g}$ | Representative MGN9C Datasheet |
| **Pen (Drawing Tool)** | Commercial Tool | N/A | $8.00\text{ g}$ | $10.00\text{ g}$ | $15.00\text{ g}$ | $15.00\text{ g}$ | ENGINEERING PACKAGING ESTIMATE |
| **SUBTOTAL: Q3 Floating Mass (B-Rep)** | — | — | **$56.40\text{ g}$** | **$61.78\text{ g}$** | **$67.68\text{ g}$** | **$68.35\text{ g}$** | **Q4B B-Rep Re-estimate** |
| **AUTHORITATIVE Q3 FLOATING BASELINE** | — | — | **$52.92\text{ g}$** | **$62.13\text{ g}$** | **$81.62\text{ g}$** | **$82.27\text{ g}$** | **03 Spec / HW-DEC-Q3-FINAL-001** |
| **CONSERVATIVE CARRIED Q3 PACKAGE** | — | — | **$121.09\text{ g}$** | **$135.74\text{ g}$** | **$158.15\text{ g}$** | **$159.48\text{ g}$** | **Frozen Floating + Fixed Q4B** |

### 7.2 Q4 X-Moving Mass Budget ($m_{X\_total}$)

| Component | Source / Rationale | Low Case | Nominal Case | High (PLA) | High (PETG) | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Total Q3 Carried Package** | Conservative envelope derived above | $121.09\text{ g}$ | $135.74\text{ g}$ | $158.15\text{ g}$ | $159.48\text{ g}$ | CONSERVATIVE UNION |
| **MGN12H Linear Guide Block** | Representative COTS MGN12H | $95.00\text{ g}$ | $100.00\text{ g}$ | $105.00\text{ g}$ | $105.00\text{ g}$ | Representative Datasheet |
| **Q4 X-Carriage Adapter Plate** | Aluminum plate ($70 \times 60 \times 4\text{ mm}$) | $45.00\text{ g}$ | $55.00\text{ g}$ | $65.00\text{ g}$ | $65.00\text{ g}$ | ENGINEERING PACKAGING ESTIMATE |
| **Belt Clamps & Screw Tensioners** | 2x tensioner sliders + M3 hardware | $15.00\text{ g}$ | $20.00\text{ g}$ | $25.00\text{ g}$ | $25.00\text{ g}$ | ENGINEERING PACKAGING ESTIMATE |
| **Fasteners & Inserts** | 8x M3 screws, washers, T-nuts | $10.00\text{ g}$ | $12.00\text{ g}$ | $15.00\text{ g}$ | $15.00\text{ g}$ | ENGINEERING PACKAGING ESTIMATE |
| **Cable Chain Carriage Bracket** | Moving umbilical bracket | $8.00\text{ g}$ | $10.00\text{ g}$ | $15.00\text{ g}$ | $15.00\text{ g}$ | ENGINEERING PACKAGING ESTIMATE |
| **TOTAL X-MOVING MASS ($m_{X\_total}$)**| **Complete carriage in X-motion** | **$294.09\text{ g}$** | **$332.74\text{ g}$** | **$383.15\text{ g}$** | **$384.48\text{ g}$** | **Traceable Mass Budget** |
| **Nominal Value for Sizing** | — | — | **$\mathbf{0.333\text{ kg}}$** | — | — | **Primary Sizing Baseline** |

### 7.3 Q4 Y-Moving Mass Budget ($m_{Y\_total}$)

| Component | Source / Rationale | Low Case | Nominal Case | High (PLA) | High (PETG) | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Total X-Moving Mass ($m_{X\_total}$)**| Carried entirely by gantry beam | $294.09\text{ g}$ | $332.74\text{ g}$ | $383.15\text{ g}$ | $384.48\text{ g}$ | Traceable Stack |
| **2040 Gantry Beam ($580\text{ mm}$)** | $0.95\text{ kg/m}$ aluminum extrusion | $551.00\text{ g}$ | $551.00\text{ g}$ | $551.00\text{ g}$ | $551.00\text{ g}$ | Misumi HFS5-2040 Catalog |
| **X-Axis MGN12 Rail ($550\text{ mm}$)** | $0.65\text{ kg/m}$ bearing steel rail | $357.50\text{ g}$ | $357.50\text{ g}$ | $357.50\text{ g}$ | $357.50\text{ g}$ | Standard MGN12 Catalog |
| **Gantry End Plates / Brackets** | 2x aluminum / composite brackets | $120.00\text{ g}$ | $140.00\text{ g}$ | $170.00\text{ g}$ | $170.00\text{ g}$ | ENGINEERING PACKAGING ESTIMATE |
| **Stacked Gantry Idlers (4x)** | 4x idlers ($14\text{ g}$ each: 2 toothed + 2 smooth) | $56.00\text{ g}$ | $56.00\text{ g}$ | $56.00\text{ g}$ | $56.00\text{ g}$ | Representative Datasheet |
| **2x Y-Axis MGN12H Blocks** | Left & right Y-guide carriage blocks | $180.00\text{ g}$ | $200.00\text{ g}$ | $210.00\text{ g}$ | $210.00\text{ g}$ | Representative Datasheet |
| **Assembly Fasteners & T-Nuts** | M3/M5 gantry clamping hardware | $35.00\text{ g}$ | $45.00\text{ g}$ | $55.00\text{ g}$ | $55.00\text{ g}$ | ENGINEERING PACKAGING ESTIMATE |
| **Cable Chains (Moving Portions)** | Moving loops of X and Y drag chains | $40.00\text{ g}$ | $55.00\text{ g}$ | $70.00\text{ g}$ | $70.00\text{ g}$ | Representative 10x10 Datasheet |
| **TOTAL Y-MOVING MASS ($m_{Y\_total}$)**| **Complete gantry in Y-motion** | **$1633.59\text{ g}$** | **$1737.24\text{ g}$** | **$1852.65\text{ g}$** | **$1853.98\text{ g}$** | **Traceable Mass Budget** |
| **Nominal Value for Sizing** | — | — | **$\mathbf{1.737\text{ kg}}$** | — | — | **Primary Sizing Baseline** |

*(Note: If 2020 gantry beam were used, $m_{Y\_total}$ nominal would be $1464.64\text{ g}$ / $1.465\text{ kg}$, but 2040 is selected for horizontal stiffness).*
- **Mass Ratio:** $\frac{m_{Y\_total}}{m_{X\_total}} = \frac{1.737}{0.333} \approx \mathbf{5.22\times}$.

---

## 8. Actuators, Pulleys & Dynamic Torque Sizing

### 8.1 Drive Pulley Comparison: 16T vs 20T GT2
Both standard pulleys were evaluated using GT2 belt pitch ($p = 2.000\text{ mm}$):

| Evaluation Metric | 16-Tooth GT2 Pulley | 20-Tooth GT2 Pulley | Impact & Selection Rationale |
| :--- | :--- | :--- | :--- |
| **Pitch Diameter ($D_p$)** | $10.186\text{ mm}$ | $\mathbf{12.732\text{ mm}}$ | Larger diameter reduces belt bending stress |
| **Pitch Radius ($r_p$)** | $5.093\text{ mm}$ | $\mathbf{6.366\text{ mm}}$ | Torque arm for motor shaft |
| **Linear Travel per Rev ($C$)** | $32.000\text{ mm/rev}$ | $\mathbf{40.000\text{ mm/rev}}$ | 20T yields $25\%$ higher speed per RPM |
| **Full-Step Command Inc (200 st)**| $160.0\ \mu\text{m}$ | $200.0\ \mu\text{m}$ | Nominal command increment |
| **1/16 Microstep Command Inc** | $10.00\ \mu\text{m}$ | $\mathbf{12.50\ \mu\text{m}}$ | Nominal command increment (NOT positioning accuracy proof) |
| **Motor RPM at $v = 100\text{ mm/s}$** | $187.5\text{ RPM}$ | $\mathbf{150.0\text{ RPM}}$ | 20T operates at lower motor speed |
| **Motor RPM at $v = 200\text{ mm/s}$** | $375.0\text{ RPM}$ | $\mathbf{300.0\text{ RPM}}$ | 20T stays within lower RPM band |
| **Motor RPM at $v = 300\text{ mm/s}$** | $562.5\text{ RPM}$ | $\mathbf{450.0\text{ RPM}}$ | Stepper torque decreases at higher RPM |
| **Torque per Unit Belt Force** | $0.509\text{ N}\cdot\text{cm/N}$ | $0.637\text{ N}\cdot\text{cm/N}$ | 16T provides $25\%$ mechanical torque leverage |
| **Belt Fatigue & Bending Strain**| Higher cyclic bending strain | **Lower cyclic bending strain** | Larger pitch radius reduces belt fatigue |
| **Selection Verdict** | ALTERNATE CANDIDATE | **PROVISIONAL PRIMARY CANDIDATE** | **Dynamic superiority TBD pending motor torque curve** |

- **Selection Trade-Off Analysis:**
  - **16T Pulley:** Provides $25\%$ mechanical torque leverage ($0.509\text{ N}\cdot\text{cm}$ torque required per Newton of belt force), demanding less holding/running motor torque for equivalent linear belt force. However, it requires $25\%$ higher motor rotational speed ($562.5\text{ RPM}$ at $300\text{ mm/s}$), operating deeper into the stepper back-EMF torque roll-off region, and imposes higher cyclic bending strain on the belt teeth around a smaller pitch diameter ($D_p \approx 10.2\text{ mm}$).
  - **20T Pulley:** Operates at lower motor rotational speed ($450.0\text{ RPM}$ at $300\text{ mm/s}$), reducing stepper pulse rates and cyclic tooth bending fatigue. However, its larger torque arm requires $25\%$ higher motor torque ($0.637\text{ N}\cdot\text{cm/N}$) for identical linear belt force.
  - **Classification:** 20T GT2 is designated as the **PROVISIONAL PRIMARY Q4B PACKAGING CANDIDATE**. Decisive dynamic superiority remains **TBD PENDING SELECTED MOTOR TORQUE-SPEED CURVE**.
  - **Precision Terminology Note:** The $12.5\ \mu\text{m}$ microstep value represents a *nominal controller command increment*, not physical positioning accuracy. Realized positioning accuracy in timing belt systems is governed by belt elastic elongation, tooth compliance, guide friction, and motor detent torque.

### 8.2 Speed & Motor RPM Envelope (20T GT2 Pulley)

| Linear Travel Speed ($v$) | Motor Rotational Speed ($\omega$) | Full-Step Frequency (200 st) | 1/16 Microstep Pulse Rate | Operational Status |
| :--- | :--- | :--- | :--- | :--- |
| **$100\text{ mm/s}$** | $150.0\text{ RPM}$ | $500\text{ Hz}$ | $8.0\text{ kHz}$ | High-precision linework / drafting |
| **$150\text{ mm/s}$** | $225.0\text{ RPM}$ | $750\text{ Hz}$ | $12.0\text{ kHz}$ | Standard infill / plotting |
| **$200\text{ mm/s}$** | $300.0\text{ RPM}$ | $1000\text{ Hz}$ | $16.0\text{ kHz}$ | High-speed plotting baseline |
| **$250\text{ mm/s}$** | $375.0\text{ RPM}$ | $1250\text{ Hz}$ | $20.0\text{ kHz}$ | Fast non-print slewing |
| **$300\text{ mm/s}$** | $450.0\text{ RPM}$ | $1500\text{ Hz}$ | $24.0\text{ kHz}$ | Rapid traverse / tool change approach |

### 8.3 Motor Torque Envelope & Holding Torque Caveat
- **MANDATORY SIZING RULE:** Holding torque is a static rating at zero velocity. It is **NOT** running torque at speed. Sizing steppers from holding torque alone is strictly prohibited.
- **Estimated Required Running Torque:** Dynamic running torque required per motor is $\mathbf{3.78 - 5.84\text{ N}\cdot\text{cm}}$ across $500 - 3000\text{ mm/s}^2$ acceleration (derived via virtual work below).
- **Candidate NEMA 17 Class:** Standard commercial $42\text{ mm}$ length NEMA 17 steppers with rated holding torque $40 - 45\text{ N}\cdot\text{cm}$ ($1.5\text{ A/phase}$) provide a standard commercial packaging envelope.
- **Validation Caveat:** Usable dynamic safety margin cannot be asserted without an explicit motor torque-speed curve under 24V chopper drive (e.g. TMC2209 at specified phase current). Dynamic torque margin remains: `TBD PENDING SELECTED MOTOR TORQUE-SPEED CURVE & 24V DRIVER BENCH TEST`.

---

## 9. CoreXY Dynamic Force Transformation & Belt Preload Logic

### 9.1 Principle of Virtual Work Force Transformation
From the kinematic displacement mapping:
$$\Delta X = \frac{\Delta A + \Delta B}{2}, \quad \Delta Y = \frac{\Delta A - \Delta B}{2}$$

The kinematic Jacobian matrix $J$ relating Cartesian velocities to motor belt velocities is:
$$\begin{bmatrix} \dot{X} \\ \dot{Y} \end{bmatrix} = \begin{bmatrix} 1/2 & 1/2 \\ 1/2 & -1/2 \end{bmatrix} \begin{bmatrix} \dot{A} \\ \dot{B} \end{bmatrix} \implies J = \begin{bmatrix} 1/2 & 1/2 \\ 1/2 & -1/2 \end{bmatrix}$$

By the Principle of Virtual Work ($\mathbf{F}_{XY}^T \delta \mathbf{X} = \mathbf{f}_{AB}^T \delta \mathbf{q}$), the generalized linear motor belt forces $\mathbf{f}_{AB} = [f_A, f_B]^T$ are related to Cartesian forces $\mathbf{F}_{XY} = [F_X, F_Y]^T$ by the transpose Jacobian $J^T$:
$$\begin{bmatrix} f_A \\ f_B \end{bmatrix} = J^T \begin{bmatrix} F_X \\ F_Y \end{bmatrix} = \begin{bmatrix} 1/2 & 1/2 \\ 1/2 & -1/2 \end{bmatrix} \begin{bmatrix} F_X \\ F_Y \end{bmatrix}$$

$$\begin{aligned}
f_A &= \frac{F_X + F_Y}{2} \\
f_B &= \frac{F_X - F_Y}{2}
\end{aligned}$$

#### Analysis of Primary Motion States & Dynamic Asymmetry:
1. **Pure $+X$ Acceleration:** $F_X > 0, F_Y = 0 \implies f_A = +F_X/2, f_B = +F_X/2$. Both motors share the inertial load equally.
2. **Pure $+Y$ Acceleration:** $F_X = 0, F_Y > 0 \implies f_A = +F_Y/2, f_B = -F_Y/2$. Both motors pull in opposite directions with equal magnitude.
3. **Diagonal $+45^\circ$ Motion ($a_X = a_Y = a/\sqrt{2}$):**
   $$\begin{aligned}
   f_A &= \frac{F_X + F_Y}{2} \\
   f_B &= \frac{F_X - F_Y}{2}
   \end{aligned}$$
   **CRITICAL ASYMMETRY NOTE:** The condition $f_B = 0$ holds **ONLY in the special symmetric case where $F_X = F_Y$**. In the OmniDraw architecture, moving masses and friction forces are strongly asymmetric: $m_{Y\_total} \approx 1.737\text{ kg} \gg m_{X\_total} \approx 0.333\text{ kg}$ (ratio $\sim 5.22\times$) and $F_{res\_Y} = 4.0\text{ N} > F_{res\_X} = 2.0\text{ N}$. Consequently, during $+45^\circ$ diagonal motion, $F_Y \gg F_X$. Motor B does NOT exert zero force; rather, $f_B = (F_X - F_Y)/2 < 0$. Motor B must actively apply balancing torque to maintain the diagonal trajectory (e.g., at $1500\text{ mm/s}^2$, $F_X = 2.35\text{ N}, F_Y = 5.84\text{ N} \implies f_A = +4.10\text{ N}, f_B = -1.74\text{ N}$).

### 9.2 Non-Inertial Resistive Forces
Total required Cartesian force incorporates friction, cable drag, and writing resistance:
$$F_X = m_{X\_total} \cdot a_X + F_{res\_X}$$
$$F_Y = m_{Y\_total} \cdot a_Y + F_{res\_Y}$$

- $F_{res\_X} = \mathbf{2.00\text{ N}}$ (Nominal estimate: MGN12 rail wiper friction $\sim 1.2\text{ N}$, Stage-2 cable chain drag $\sim 0.6\text{ N}$, pen normal friction $\sim 0.2\text{ N}$).
- $F_{res\_Y} = \mathbf{4.00\text{ N}}$ (Nominal estimate: Dual MGN12 rail friction $\sim 2.5\text{ N}$, Stage-1 cable chain drag $\sim 1.5\text{ N}$).

### 9.3 Acceleration Sensitivity Grid (Nominal Masses: $m_X = 0.333\text{ kg}, m_Y = 1.737\text{ kg}$)
Evaluated with Drivetrain Efficiency $\eta = 0.85$ and Engineering Safety Factor $SF = 1.5$ on 20T GT2 Pulley ($r_p = 6.366\text{ mm}$):

| Accel ($a$, $\text{mm/s}^2$) | Pure X: $F_X$ (N) | Pure Y: $F_Y$ (N) | Pure X: $f_A$ (N) | Pure Y: $f_A$ (N) | Diag $45^\circ$: $f_A$ (N) | Diag $45^\circ$: $f_B$ (N) | Peak Force $f_{max}$ (N) | Required Torque $\tau_{req}$ ($\text{N}\cdot\text{cm}$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **$500$** | $2.17\text{ N}$ | $4.87\text{ N}$ | $1.08\text{ N}$ | $2.43\text{ N}$ | $3.37\text{ N}$ | $-1.25\text{ N}$ | $3.37\text{ N}$ | **$3.78\text{ N}\cdot\text{cm}$** |
| **$1000$** | $2.33\text{ N}$ | $5.74\text{ N}$ | $1.17\text{ N}$ | $2.87\text{ N}$ | $3.73\text{ N}$ | $-1.50\text{ N}$ | $3.73\text{ N}$ | **$4.19\text{ N}\cdot\text{cm}$** |
| **$1500$ (Nominal)** | $2.50\text{ N}$ | $6.61\text{ N}$ | $1.25\text{ N}$ | $3.30\text{ N}$ | $4.10\text{ N}$ | $-1.74\text{ N}$ | $4.10\text{ N}$ | **$4.60\text{ N}\cdot\text{cm}$** |
| **$2000$** | $2.67\text{ N}$ | $7.47\text{ N}$ | $1.33\text{ N}$ | $3.74\text{ N}$ | $4.46\text{ N}$ | $-1.99\text{ N}$ | $4.46\text{ N}$ | **$5.01\text{ N}\cdot\text{cm}$** |
| **$2500$** | $2.83\text{ N}$ | $8.34\text{ N}$ | $1.42\text{ N}$ | $4.17\text{ N}$ | $4.83\text{ N}$ | $-2.24\text{ N}$ | $4.83\text{ N}$ | **$5.43\text{ N}\cdot\text{cm}$** |
| **$3000$** | $3.00\text{ N}$ | $9.21\text{ N}$ | $1.50\text{ N}$ | $4.61\text{ N}$ | $5.20\text{ N}$ | $-2.49\text{ N}$ | $5.20\text{ N}$ | **$5.84\text{ N}\cdot\text{cm}$** |

### 9.4 Belt Preload Logic & Slack Prevention
In a timing belt drive, the static installation tension $T_0$ must prevent the slack side of the belt from collapsing during peak acceleration:
$$T_{tight} = T_0 + \frac{\Delta T}{2}, \quad T_{slack} = T_0 - \frac{\Delta T}{2}$$
Where $\Delta T = |f_{motor}|$. To prevent tooth skipping, belt fluttering, and backlash:
$$T_{slack} > 0 \implies T_0 > \frac{|\Delta T_{peak}|}{2}$$

1. At peak acceleration $a = 3000\text{ mm/s}^2$, $|\Delta T_{peak}| \approx 5.20\text{ N} \implies T_0 > 2.60\text{ N}$.
2. **Numeric Target Status:** Sourced belt manufacturer tension specifications and precise acoustic frequency calibration targets are pending component selection.
   $$\mathbf{\text{STATIC BELT PRELOAD NUMERIC TARGET = TBD PROCUREMENT / Q4C}}$$
3. **Engineering Trial Range:** A trial installation band of **$T_0 \in [20.0, 35.0]\text{ N}$** is designated strictly as:
   $$\text{ENGINEERING TRIAL RANGE / NOT DERIVED / NOT FROZEN}$$

### 9.5 Parametric Motor Shaft & Idler Bearing Radial Loads
Because static preload $T_0$ is un-frozen, radial loads on motor shafts and idlers are evaluated parametrically across the candidate trial range ($T_0 \in [15.0, 35.0]\text{ N}$):
- Motor Shaft Radial Load ($90^\circ$ Wrap): $F_{rad\_motor\_static} = \sqrt{2} \cdot T_0$; Dynamic: $F_{rad\_motor\_dyn} = \sqrt{T_{tight}^2 + T_{slack}^2}$.
- $90^\circ$ Idler Bearing Load: $F_{bearing\_90} = \sqrt{2} \cdot T_0$.
- $180^\circ$ Turnaround Idler Load: $F_{bearing\_180} = 2 \cdot T_0$.

| Candidate $T_0$ (N) | $F_{rad\_motor\_static}$ (N) | $F_{rad\_motor\_dyn}$ (N, Peak) | $F_{rad\_idler\_90}$ (N) | $F_{rad\_idler\_180}$ (N) |
| :--- | :--- | :--- | :--- | :--- |
| **$15.0\text{ N}$** | $21.21\text{ N}$ | $21.53\text{ N}$ | $21.21\text{ N}$ | $30.00\text{ N}$ |
| **$20.0\text{ N}$** | $28.28\text{ N}$ | $28.52\text{ N}$ | $28.28\text{ N}$ | $40.00\text{ N}$ |
| **$25.0\text{ N}$ (Nominal Trial)**| $\mathbf{35.36\text{ N}}$ | $\mathbf{35.55\text{ N}}$ | $\mathbf{35.36\text{ N}}$ | $\mathbf{50.00\text{ N}}$ |
| **$30.0\text{ N}$** | $42.43\text{ N}$ | $42.59\text{ N}$ | $42.43\text{ N}$ | $60.00\text{ N}$ |
| **$35.0\text{ N}$** | $49.50\text{ N}$ | $49.63\text{ N}$ | $49.50\text{ N}$ | $70.00\text{ N}$ |

- **Supplier Rating Status:** Sourced supplier continuous radial load ratings for candidate stepper motor bearings and COTS idler ball bearings remain `TBD PROCUREMENT / Q4C VENDOR SELECTION`.

---

## 10. Frame Topology & Complete Dimensional Stacks

### 10.1 Complete X-Axis Dimensional Stack
Derivation of all transverse frame dimensions from first principles:

```
[Left Side Extrusion (20 mm)]
  |-- [Frame Inner Wall: X = -75.0]
  |     |-- Carriage clearance to wall: 7.3 mm
  |     |-- Left idler bracket & pulley stack: 20.0 mm
  |     |-- X-endstop & rubber bumper margin: 5.0 mm
  |     |-- Left Q3 carriage overhang (MG90S servo ear): 42.7 mm
  |-- [CARRIAGE TRAVEL MINIMUM DATUM: X = 0.0]
        |
        |================= PEN TRAVEL STROKE: 450.0 mm =================>
        |                                                                |
        |-- [Hold-down margin: 15.0 mm]                                  |
        |-- [ACTIVE PLOTTING AREA: X in [15.0, 435.0] mm (420.0 mm)]     |
        |-- [Hold-down margin: 15.0 mm]                                  |
        |                                                                |
                                        [CARRIAGE TRAVEL MAXIMUM: X = 450.0]
                                          |-- Right Q3 overhang (Baseplate): 24.0 mm
                                          |-- Right belt tensioner & clamp: 21.0 mm
                                          |-- Right idler bracket & pulley stack: 20.0 mm
                                          |-- Carriage clearance to wall: 10.0 mm
                                        [Frame Inner Wall: X = +525.0]
                                          |-- [Right Side Extrusion (20 mm)]
```

- **X Allowances:**
  - Left Allowance: $42.7 + 5.0 + 20.0 + 7.3 = \mathbf{75.000\text{ mm}}$
  - Right Allowance: $24.0 + 21.0 + 20.0 + 10.0 = \mathbf{75.000\text{ mm}}$
- **Derived Frame X Dimensions:**
  - $FRAME\_INNER\_X = 450.000 + 75.000 + 75.000 = \mathbf{600.000\text{ mm}}$
  - $FRAME\_OUTER\_X = 600.000 + 2 \times 20.000 = \mathbf{640.000\text{ mm}}$
  - $GANTRY\_BEAM\_LENGTH = \mathbf{580.000\text{ mm}}$ (Clear span between Y-carriage inner plates)
  - $X\_RAIL\_LENGTH = \mathbf{550.000\text{ mm}}$ (MGN12 standard; stroke capacity $= 550.0 - 45.4 - 20.0 = 484.6\text{ mm} > 450.0\text{ mm}$)

### 10.2 Complete Y-Axis Dimensional Stack
Derivation of all longitudinal frame dimensions from first principles:

```
[Front Crossmember Extrusion (20 mm)]
  |-- [Frame Inner Wall: Y = -45.0]
  |     |-- Front idler bracket & pulley stack: 25.0 mm
  |     |-- Front endstop & carriage bumper: 5.0 mm
  |     |-- Paper front margin: 15.0 mm
  |-- [CARRIAGE TRAVEL MINIMUM DATUM: Y = 0.0]
        |
        |================= PEN TRAVEL STROKE: 375.0 mm =================>
        |                                                                |
        |-- [ACTIVE PLOTTING AREA: Y in [15.0, 312.0] mm (297.0 mm)]     |
        |-- [Paper rear margin: 10.0 mm]                                 |
        |-- [Dock approach corridor: 43.0 mm]                            |
        |-- [DOCK MATING POSITION: Y = 365.0 mm]                         |
        |-- [Dock release stroke & soft limit margin: 10.0 mm]           |
        |                                                                |
                                        [CARRIAGE TRAVEL MAXIMUM: Y = 375.0]
                                          |-- Gantry depth stack (Extrusion + Rail): 33.0 mm
                                          |-- Dock base depth & rear idler mount: 20.0 mm
                                          |-- Rear motor envelope allowance: 12.0 mm
                                        [Frame Inner Wall: Y = +440.0]
                                          |-- [Rear Crossmember Extrusion (20 mm)]
```

- **Y Allowances:**
  - Front Allowance: $25.0 + 5.0 + 15.0 = \mathbf{45.000\text{ mm}}$
  - Rear Allowance: $33.0 + 20.0 + 12.0 = \mathbf{65.000\text{ mm}}$
- **Derived Frame Y Dimensions:**
  - $FRAME\_INNER\_Y = 375.000 + 45.000 + 65.000 = \mathbf{485.000\text{ mm}}$
  - $FRAME\_OUTER\_Y = 485.000 + 2 \times 20.000 = \mathbf{525.000\text{ mm}}$
  - $SIDE\_EXTRUSION\_LENGTH = \mathbf{525.000\text{ mm}}$
  - $Y\_RAIL\_LENGTH = \mathbf{450.000\text{ mm}}$ (MGN12 standard; stroke capacity $= 450.0 - 45.4 - 10.0 = 394.6\text{ mm} > 375.0\text{ mm}$)

---

## 11. Work Bed, Media Envelope & Clearances

### 11.1 Work Bed Dimensions & Placement
- **Physical Platen Size:** $460.000\text{ mm}$ (Width) $\times 330.000\text{ mm}$ (Depth) $\times 5.000\text{ mm}$ (Thickness).
- **Candidate Material:** Cast aluminum tooling plate (Mic6 $5\text{ mm}$) or cast acrylic sheet ($6\text{ mm}$) (`PRIMARY BED CANDIDATE`).
- **Paper Placement Coordinate:** Front-left paper corner is registered at $(X = 15.000\text{ mm}, Y = 15.000\text{ mm})$.
- **Machine Z Datum Stack:**
  - Nominal Paper Drawing Surface: Machine $Z = \mathbf{0.000\text{ mm}}$.
  - Paper Thickness: $t_{paper} = 0.100\text{ mm}$ ($80\text{ g/m}^2$ standard drafting paper).
  - Bed Platen Top Surface: Machine $Z_{bed\_top} = \mathbf{-0.100\text{ mm}}$.
  - Bed Platen Bottom Surface: Machine $Z_{bed\_bot} = \mathbf{-5.100\text{ mm}}$ ($5.000\text{ mm}$ thickness).
- **Platen Physical Envelope in Machine Space:**
  - $X \in [-5.000, 455.000]\text{ mm}$
  - $Y \in [0.000, 330.000]\text{ mm}$
  - $Z \in [-5.100, -0.100]\text{ mm}$
- **Dock Separation Gap:** The rear edge of the bed ($Y = 330.0\text{ mm}$) leaves an open physical gap of **$35.000\text{ mm}$** before the dock mating coordinate ($Y_{DOCK\_MATE} = 365.0\text{ mm}$). Moving carriage maintains $+4.460\text{ mm}$ vertical clearance above platen during drawing.

### 11.2 Bed Support & 3-Point Kinematic Leveling
- Supported by 2x transverse $2020\text{ mm}$ bottom crossmembers mounted at $Z \in [-25.0, -5.0]\text{ mm}$.
- 3-point kinematic leveling system modeled at:
  - Point 1 (Front-Left): $(X = 60.000\text{ mm}, Y = 30.000\text{ mm})$
  - Point 2 (Front-Right): $(X = 390.000\text{ mm}, Y = 30.000\text{ mm})$
  - Point 3 (Rear-Center): $(X = 225.000\text{ mm}, Y = 300.000\text{ mm})$
- Incorporates M4 countersunk screws through platen, spring/Belleville washer reference envelopes, and knurled adjustment thumbscrews accessible beneath the crossmembers.
- Bed mounting is fully decoupled from the side extrusions carrying the MGN12 rails.

---

## 12. Quad Dock Subsystem Integration & Approach Corridor

### 12.1 Dock Architecture & Coordinates
- **Restored Base Geometry (HW-DEC-006):** 4 bays, pitch $P = 32.000\text{ mm}$, active span $124.000\text{ mm}$, base width strictly $\mathbf{144.000\text{ mm}}$ ($X \in [153.000, 297.000]\text{ mm}$), side margins $10.000\text{ mm}$.
- **Horizontal Position:** Centered symmetrically at $X_{dock\_center} = \mathbf{225.000\text{ mm}}$.
- **Bay Centers:** $X_1 = 177.0\text{ mm}, X_2 = 209.0\text{ mm}, X_3 = 241.0\text{ mm}, X_4 = 273.0\text{ mm}$.
- **Vertical Height:** Dock base centered at $Z = \mathbf{+47.500\text{ mm}}$ ($Z \in [30.0, 65.0]\text{ mm}$).
- **Dock Mating Elevation:** $Z_{DOCK\_MATE} = \mathbf{+51.500\text{ mm}}$ (Machine $Z$ frame, corresponding to local Q3 $Z = +6.500\text{ mm}$).
- **Approach Corridor:** $X \in [150.000, 300.000]\text{ mm}$ along $Y \in [312.000, 365.000]\text{ mm}$.
- **Autonomous Tool Release Kinematic Defect:**
  Continuous trajectory simulation of the authoritative upstream simultaneous release vector ($\Delta Y(t) = -1.000 \cdot t, \Delta Z(t) = +1.500 \cdot t$) revealed a physical collision of **$1.316\text{ mm}^3$** between the `Receiver_Plate_V1` Key Pin and the `Tool_Sleeve_V1_1` notch ceiling across all 4 bays. Because Q1/Q2/Q3 geometry is frozen, Q4C.1 records this finding and flags upstream resolution.

---

## 13. Cable Management & Serviceability Strategy

### 13.1 Two-Stage Cable Management
- **Conductors:** MG90S servo 3-wire harness, X-endstop 2-wire, future pen sensor.
- **Stage 1 (Y-Axis Drag Chain):** Provisional $10 \times 10\text{ mm}$ chain along the left side from chassis to the left Y bracket. The former 300 mm length and R18 radius are estimates, not a released BOM; size from the selected chain and full 375 mm Y travel.
- **Stage 2 (X-Axis Drag Chain):** Provisional $10 \times 10\text{ mm}$ chain from the left gantry bracket to the Q4 carriage tab. The former 340 mm length and R18 radius are estimates, not a released BOM; size from the selected chain and full 450 mm X travel. CAD boxes are schematic route corridors, not articulated bend-clearance proof.
- **CABLE MECHANICAL ISOLATION REQUIREMENT:** Cable routing terminates on the fixed Q4 carriage plate and transmits no load into the Q3 floating Z slider.

### 13.2 Routine Service Access
- **Q3 Carriage Removal:** 4 front M3 socket-head screws through the baseplate ($36 \times 64\text{ mm}$ pattern) are directly accessible from the front, allowing complete Q3 removal without disturbing belt tension.
- **Belt Tensioning Adjustment:** Accessible from top/front via M3 jackscrews without dismounting Q3.
- **Motor Swap:** Motors unbolt via 4x M3 screws from above/below without disassembling the frame perimeter.

---

## 14. Historical Q4C.1 Parameter Table — Superseded for Q4C.3

The values below describe the earlier Q4C.1/Q4C.2 geometry. Current Q4C.3 dimensions and acceptance scope are in the amendment above and `cad/Q4C3_HOTFIX_REPORT.md`.

| Parameter Name | Value / Range | Units | Classification | Source | Next Validation Stage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Media Standard** | ISO A3 Landscape | — | `Q4B SELECTED BASELINE` | User / Sizing Study | Physical Template |
| **Active Plotting X** | $420.000$ | $\text{mm}$ | `DERIVED` | ISO 216 Standard | Bench Test |
| **Active Plotting Y** | $297.000$ | $\text{mm}$ | `DERIVED` | ISO 216 Standard | Bench Test |
| **Carriage Stroke X** | $450.000$ | $\text{mm}$ | `CAD VERIFIED` | Usable Guide Stroke | Limit Switch Tuning |
| **Carriage Stroke Y** | $375.000$ | $\text{mm}$ | `CAD VERIFIED` | Usable Guide Stroke | Limit Switch Tuning |
| **Global Origin Datum** | $(0.0, 0.0, 0.0)$ | $\text{mm}$ | `FROZEN CONVENTION` | Q4A.1 Baseline | Firmware Config |
| **Paper Datum Z** | $0.000$ | $\text{mm}$ | `FROZEN CONVENTION` | Machine Standard | Firmware Zero |
| **Bed Platen Top Z** | $-0.100$ | $\text{mm}$ | `CAD VERIFIED` | Paper Thickness Stack | Dial Indicator Survey |
| **Mechanism Elevation** | $+45.000$ | $\text{mm}$ | `CAD VERIFIED` | Global Z Transform | Assembly Gauge |
| **$X_{dock\_center}$** | $225.000$ | $\text{mm}$ | `DERIVED` | Carriage Centerline | Q4C Assembly CAD |
| **$X_{DOCK\_1..4}$** | $177, 209, 241, 273$ | $\text{mm}$ | `DERIVED` | $P = 32.0\text{ mm}$ Pitch | Q4C Assembly CAD |
| **$Y_{DOCK\_MATE}$** | $365.000$ | $\text{mm}$ | `CAD VERIFIED` | Mating Coordinate | Dock Sensor Test |
| **$Z_{DOCK\_MATE}$** | $+51.500$ (Local $+6.5$) | $\text{mm}$ | `FROZEN UPSTREAM` | HW-DEC-006 / Q3C | Prototype Dock Test |
| **Quad Dock Base Width** | $144.000$ | $\text{mm}$ | `RESTORED FROZEN` | HW-DEC-006 / Q2 | Fabrication Drawing |
| **FRAME_INNER_X** | $600.000$ | $\text{mm}$ | `DERIVED` | First Principles Stack | Frame Extrusion Cut |
| **FRAME_OUTER_X** | $640.000$ | $\text{mm}$ | `DERIVED` | $2020\text{ mm}$ Profile Stack | Frame Extrusion Cut |
| **FRAME_INNER_Y** | $485.000$ | $\text{mm}$ | `DERIVED` | First Principles Stack | Frame Extrusion Cut |
| **FRAME_OUTER_Y** | $525.000$ | $\text{mm}$ | `DERIVED` | $2020\text{ mm}$ Profile Stack | Frame Extrusion Cut |
| **Gantry Beam Profile** | 2040 (Vertical: $20\text{Y} \times 40\text{Z}$) | — | `CAD VERIFIED` | Belt Lane Gap & Sag | Physical Prototype |
| **Gantry Beam Length** | $580.000$ | $\text{mm}$ | `DERIVED` | Clear Span Stack | Fabrication Cut |
| **X-Rail Length** | $550.000$ | $\text{mm}$ | `CAD VERIFIED` | $X \in [-50, 500]\text{ mm}$ | Procurement Check |
| **Y-Rail Length** | $450.000$ | $\text{mm}$ | `CAD VERIFIED` | $Y \in [-30, 420]\text{ mm}$ | Procurement Check |
| **Front Idler Profile** | 28T GT2 ($r_p = 8.913\text{ mm}$) | — | `CAD VERIFIED` | Commercial GT2 Profile | Sourcing / SKU Check |
| **Lane Separation** | $17.825$ | $\text{mm}$ | `DERIVED` | $2 \times r_p$ (Exact) | CAD Model |
| **Belt Plane Spacing** | $10.000$ (Plane A=+50, B=+40) | $\text{mm}$ | `CAD VERIFIED` | Stacked Pulleys | Axle Assembly |
| **Timing Belt Spec** | GT2 $6\text{ mm}$ Neoprene | — | `PRIMARY CANDIDATE` | Industry Standard | Physical Procurement |
| **Drive Pulley Spec** | 20T GT2 ($r_p = 6.366\text{ mm}$) | — | `PROVISIONAL CANDIDATE` | Speed / Torque Analysis | TBD Motor Curve |
| **Installed Belt Length** | $1949.245$ ($L_A \equiv L_B$) | $\text{mm}$ | `EXACT TANGENT` | Tangent Geometry Proof | Sizing / Bench Check |
| **Q3 Floating Z-Mass** | $52.92 - 82.27$ (Nom 62.13) | $\text{g}$ | `FROZEN UPSTREAM` | 03 Spec / HW-DEC-Q3-FINAL-001 | Physical Scale Check |
| **Q3 Total Carried Package**| $121.09 - 159.48$ (Nom 135.74) | $\text{g}$ | `CONSERVATIVE UNION` | Frozen Floating + Q4B Fixed | Physical Scale Check |
| **$m_{X\_total}$** | $294.09 - 384.48$ (Nom 332.74)| $\text{g}$ | `TRACEABLE BUDGET` | First Principles Stack | Physical Scale Check |
| **$m_{Y\_total}$ (2040)** | $1633.59 - 1853.98$ (Nom 1737.24)| $\text{g}$ | `TRACEABLE BUDGET` | First Principles Stack | Physical Scale Check |
| **Required Running Torque** | $3.78 - 5.84$ | $\text{N}\cdot\text{cm}$ | `DERIVED ENVELOPE` | Virtual Work / Dynamics | Dyno / Bench Test |
| **Motor Class** | NEMA 17 ($40-45\text{ N}\cdot\text{cm}$) | — | `PACKAGING CANDIDATE` | Packaging Sizing | TBD Motor Curve / Dyno |
| **Static Belt Preload ($T_0$)** | $20.0 - 35.0$ (Trial Range) | $\text{N}$ | `TBD PROCUREMENT` | Slack-Prevention Logic | Prototype Frequency Test |
| **Motor Radial Load** | Parametric ($21.2 - 49.6$) | $\text{N}$ | `DERIVED (PARAMETRIC)` | Vector Belt Summation | TBD Supplier Rating Check |

---

## 15. Q4C.1 Component Classification & Status Register

| Component Group | Component Item | Classification | Status & Next Action |
| :--- | :--- | :--- | :--- |
| **Structural Frame** | Perimeter Extrusions ($2020\text{ mm}$) | `CAD VERIFIED` | Modeled at $Z = +45.0\text{ mm}$; STEP exported in `FRAME_ASSEMBLY.step` |
| **Structural Frame** | Gantry Extrusion ($2040\text{ mm}$, Vertical) | `CAD VERIFIED` | Modeled with belt clearance pockets; exported in `GANTRY_ASSEMBLY.step` |
| **Linear Motion** | X-Axis Linear Rail (MGN12, $550\text{ mm}$) | `CAD VERIFIED` | Span $X \in [-50, 500]\text{ mm}$; $+27.3\text{ mm}$ margin at endpoints |
| **Linear Motion** | Y-Axis Linear Rails (2x MGN12, $450\text{ mm}$) | `CAD VERIFIED` | Repositioned to $Y \in [-30, 420]\text{ mm}$; $+7.3\text{ mm}$ margin at Home |
| **Linear Motion** | X-Axis Carriage Block (1x MGN12H) | `CAD VERIFIED` | Bolted to adapter plate via 4x M3 counterbores; zero overhang |
| **Transmission** | Timing Belts (GT2 $6\text{ mm}$ Neoprene) | `CAD VERIFIED` | Swept 3D solids; $L_A = L_B = 1949.245\text{ mm}$; exported in STEP |
| **Transmission** | Front Turnaround Idlers (28T GT2, M5) | `CAD VERIFIED` | $r_p = 8.913\text{ mm}$, $D_p = 17.825\text{ mm}$; exported in `IDLER_MOUNTS.step` |
| **Transmission** | Dual-Deck Rear Motor Mounts | `CAD VERIFIED` | Inverted Motor A, upright Motor B, independent axles; exported in STEP |
| **Transmission** | Belt Tensioners (4x Sliders) | `CAD VERIFIED` | Toothed channel, M3 jackscrew, hex nut pocket; exported in STEP |
| **Carriage Interface**| X-Carriage Adapter Plate | `CAD VERIFIED` | Q3 M3 pattern, MGN12H pattern, servo & cam relief windows modeled |
| **Work Bed** | Tooling Plate & 3-Point Mounts | `CAD VERIFIED` | Platen top at $Z = -0.100\text{ mm}$, 3-point thumbscrews modeled |
| **Tool Changer** | Restored Quad Dock Subsystem | `CAD VERIFIED` | Base width $144.000\text{ mm}$; tool release path blocked by Q2/Q3 notch roof |

---

## 16. Preliminary Failure Mode Architecture Checklist (FMEA)

| Potential Failure Mode | Root Cause | Architectural Mitigation / Countermeasure | Verification Stage |
| :--- | :--- | :--- | :--- |
| **1. Belt Rubbing / Abrasion** | Crossed belt lines or misaligned pulleys | Stacked dual-plane routing ($\Delta Z_{belt} = 10.0\text{ mm}$); flanged idlers | PASS (CAD verified) |
| **2. Gantry Racking / Binding** | Unequal belt tension or Y-guide binding | Independent carriage tensioners; Master/Slave Y-rail mount | Prototype bench test |
| **3. Non-Orthogonal Frame ($X \not\perp Y$)** | Frame parallelogram distortion | Rigid corner gussets; diagonal check during squaring assembly | Assembly validation |
| **4. Premature Belt Tooth Wear** | Belt teeth running over smooth idlers | Strict rule: toothed idlers on all high-wrap toothed turns | PASS (CAD verified) |
| **5. Pitch / Roll Moment on Carriage** | Vertical offset between belt planes $\Delta Z_{belt}$ | Symmetrical gantry beam; MGN12H block moment stiffness | Q4C force analysis |
| **6. Q3 Servo Body Collision** | Carriage plate intrudes into servo pocket | Dedicated clearance cutout on carriage plate ($X \in [-45, -15]\text{ mm}$) | PASS (CAD verified) |
| **7. Dock U-Fork Ramming** | Inadvertent homing toward rear | Homing corner at Front-Left ($X_{min}, Y_{min}$), away from dock | Firmware config |
| **8. Dynamic Cable Drag on Pen** | Wiring harness pulls on floating slider | Cable routing terminates on fixed Q4 carriage plate | Prototype bench test |
| **9. Stepper Motor Step Loss** | Excessive Y-gantry mass at high accel | Firmware asymmetric acceleration limits ($a_{Y\_max} < a_{X\_max}$) | Dynamic validation |
| **10. Motor Pulley Slippage** | Set screws loosening on D-shaft | Dual set screws (one on flat, one on round) + threadlocker | Assembly procedure |
| **11. Extrusion Twist / Sag** | Span deflection under dynamic loads | 2040 beam ($40\text{ mm Z}$ orientation: $37.6\ \mu\text{m}$ vertical sag) | PASS (CAD verified) |
| **12. Bed Surface Waviness** | Thin un-supported bed material | 2x transverse frame crossmembers supporting bed plate | Bed flatness survey |
| **13. Tool Release Notch Collision** | Blind notch roof clips Key Pin in $\Delta Z$ | Upstream defect: requires open notch slot or $\Delta Y > 1.457\text{ mm}$ | **BLOCKED (Q2/Q3 review)** |

---

## 17. Historical Q4C.2 Mechanical Closure Register — Superseded for Q4C.3

### 17.1 Actual CAD Body Manifest
All parts are physically realized as distinct 3D B-Rep solids in `cad/build_q4c_corexy_assembly.py` and exported to `cad/export_q4c/`:
- `FRAME_ASSEMBLY.step`: 4x perimeter extrusions ($545\text{ mm}$ side rails, rear beam at $Y = 470\text{ mm}$), 2x bed crossmembers, 4x lower corner gussets.
- `GANTRY_ASSEMBLY.step`: 2040 gantry beam with belt relief pockets, MGN12 X-rail, Left & Right gantry end brackets.
- `X_CARRIAGE_ADAPTER.step`: **Monolithic structural solid (Solids = 1)** with top bridge deck, rear drop tab, all fastener counterbores, Q3 mount holes, servo pocket, and cam sweep window.
- `MOTOR_MOUNT_A.step` & `MOTOR_MOUNT_B.step`: **Monolithic dual-deck corner brackets (Solids = 1 each)** with NEMA 17 face pattern, pilot bore, T-slot mount holes, and stationary idler axle bosses.
- `IDLER_MOUNTS.step`: Front-Left and Front-Right 28T turnaround brackets with M5 axle holes and inner-race support bosses.
- `BELT_TENSIONERS.step`: **4 independent translating sliders (Solids = 4)** with toothed belt channels, captive hex nut recesses, and anti-rotation guide tongues.
- `WORK_BED_REFERENCE.step`: $460 \times 330 \times 5\text{ mm}$ tooling platen with 3-point leveling thumbscrews (Solids = 4).
- `QUAD_DOCK_REFERENCE.step`: Restored monolithic 4-bay dock fixture ($144.000\text{ mm}$ width, pitch $32.000\text{ mm}$, Solids = 1).
- `BELT_A_SOLID.step` & `BELT_B_SOLID.step`: Continuous 3D swept timing belts ($Z = +50.0\text{ mm}$ and $Z = +40.0\text{ mm}$).
- `Q4C_FULL_ASSEMBLY.step`: Complete machine assembly including moving carriage, endstops, and representative drafting pen.

### 17.2 Minimum Clearance & Verification Register
- **Topology & Connectivity:** All custom parts verified monolithic (Adapter: 1 solid, Mount A: 1 solid, Mount B: 1 solid, Tensioners: 4 sliders, Dock: 1 solid). Zero floating solids (**PASS**).
- **Translating Tensioner Full Stroke:** Audited 25 stroke steps in $[-6.0, +6.0]\text{ mm}$ ($0.5\text{ mm}$ step): Max forbidden overlap $= \mathbf{0.000000\text{ mm}^3}$, minimum sliding clearance $= \mathbf{0.2000\text{ mm}}$ (**PASS**).
- **Dense XY Motion Grid (6,916 states):** Swept $X \in [0, 450]\text{ mm}$ and $Y \in [0, 375]\text{ mm}$ at $5.0\text{ mm}$ regular grid. Evaluated 48,305 B-Rep pairs: Max overlap $= \mathbf{0.000000\text{ mm}^3}$, Global minimum clearance $= \mathbf{0.5000\text{ mm}}$ (Carriage Adapter vs Gantry Beam), zero boolean failures or skips (**PASS**).
- **Staged 4-Bay Tool Change:** Phase A retreat ($\Delta Y = -2.500\text{ mm}$, $0.000000\text{ mm}^3$ overlap), Phase B lift ($\Delta Z = +1.500\text{ mm}$, $0.000000\text{ mm}^3$ overlap), Phase C departure, and reverse pickup verified across Bays 1 to 4. Clearance to adjacent parked tools $\ge \mathbf{2.374\text{ mm} \ge 1.500\text{ mm}}$ (**PASS**).
- **B-Rep Endstop Safety Margins:** Modeled KW12 switches, mounts, bumpers, and trigger flags evaluated with $\pm 0.8\text{ mm}$ conservative tolerance stack:
  - X-Axis worst-case margin to rigid crash: $\mathbf{11.200\text{ mm} \ge 2.000\text{ mm}}$ (**PASS**).
  - Y-Axis worst-case margin to rigid crash: $\mathbf{13.200\text{ mm} \ge 2.000\text{ mm}}$ (**PASS**).
- **Upstream Immutability:** All 14 frozen Q1/Q2/Q3 STEP files remain 100% SHA-256 hash verified.

### 17.3 Fastener Serviceability & Assembly Sequence
All fasteners feature straight line-of-sight driver access. The 12-stage sequential assembly order verifies that no permanent fasteners are trapped by subsequent components.

### 17.4 Historical Q4C.2 Audit Verdict — Superseded by Q4C.3
The PASS and freeze statement immediately below records the prior Q4C.2 claim only. It is **withdrawn as current release authority** by the Q4C.3 amendment at the top of this document. Q4 Final Freeze remains **not authorized** pending the Q4C.3 open gates.
$$\mathbf{Q4C.2\ STATUS = PASS}$$
$$\mathbf{Q4\ FINAL\ FREEZE\ AUTHORIZED = YES}$$
- Frozen Q1 Hash Unchanged: **PASS**
- Frozen Q2 Hash Unchanged: **PASS**
- Frozen Q3 Hash Unchanged: **PASS**
- Adapter Connected Correctly: **PASS**
- Motor Mounts Connectivity: **PASS**
- Tensioner Full-Stroke Audit: **PASS**
- Dense XY Motion Grid Audit: **PASS**
- Staged 4-Bay Tool Change: **PASS**
- B-Rep Endstop Verification: **PASS**
- Physical Validation: **PENDING (Holding Force, Shrinkage, Belt Tension, Switch Repeatability)**

---

## 18. Traceability Matrix

- **Upstream Architecture:** [01_hardware_architecture.md](01_hardware_architecture.md)
- **Tool Changer Specification:** [02_tool_changer_spec.md](02_tool_changer_spec.md)
- **Carriage & Lifter Baseline:** [03_carriage_and_lifter_spec.md](03_carriage_and_lifter_spec.md)
- **Electronics & Firmware:** [05_electronics_spec.md](05_electronics_spec.md)
- **Validation Matrix:** [06_validation_plan.md](06_validation_plan.md)
- **Engineering Decision History:** [hardware_decision_log.md](hardware_decision_log.md) (Decisions HW-DEC-Q4-001, HW-DEC-Q4-002, HW-DEC-Q4-003)
- **CAD Implementation:** `cad/build_q4c_corexy_assembly.py`
- **Collision & Motion Audit:** `cad/q4c_collision_audit.py`
- **Analytical Calculation Script:** `cad/q4b_calculations.py`
- **Engineering Report:** `cad/Q4C_ENGINEERING_REPORT.md`
