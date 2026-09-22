# Carriage & Z-Lifter Specification

**Subsystem:** Z-Carriage, Gravity-Floating Pen Axis & Cam Lifter
**Document Version:** V2.0
**Status:** Q3 Z-CARRIAGE / CAM LIFTER: FINAL DESIGN FREEZE — CAD VERIFIED | PHYSICAL VALIDATION PENDING
**Baseline Date:** 2026-09-22
**CAD Source of Truth:** `cad/build_q3c_cad_assembly.py` / `cad/export/*.step`

---

## 1. Subsystem Purpose & Architecture

### 1.1 Architectural Model: Gravity-Dominant Floating Z-Carriage
The OmniDraw Z-Carriage implements a **Gravity-Dominant Floating Z-Carriage** architecture:
1. **Passive Gravity Drawing:** Drawing downforce on the pen nib during drafting is primarily provided by the unconstrained moving mass of the carriage and tool under gravity.
2. **Springless Baseline:** No default downward spring is included in the frozen baseline. Downward travel is completely compliant across a continuous vertical window.
3. **Disengaged Cam Lifter:** During the normal drafting state (`STATE_DRAW`), the actuating cam is parked in a disengaged clearance orientation (`FREE_DRAW_PARK`), fully decoupling actuator dynamics from pen-paper contact.
4. **Active Vertical Retraction:** An electric actuator rotates the cam to lift the carriage along a single-acting vertical kinematic chain for non-drawing rapid travel (`STATE_PEN_UP`) and autonomous tool-changing sequences (`STATE_DOCK_MATE`).
5. **Real Downforce Dependency:** Gravity force is not treated as identically equal to actual nib force. Real nib force depends on:
   - Gravity force of the moving mass: $F_{gravity} = m_{total} \cdot g$
   - Vertical linear guide running friction and breakaway stiction ($F_{guide}$)
   - Dynamic reaction of the drawing paper and backing platen
   - Real moving mass as manufactured and assembled.
6. **Contingencies:** Counterbalancing or auxiliary ballast are unfrozen design contingencies, reserved only if physical validation of manufactured moving mass or guide friction requires adjustment.

```
                    +------------------------------------+
                    |  CoreXY X-Gantry Mounting Datum   |
                    +------------------------------------+
                                       |
                 +---------------------+---------------------+
                 |                                           |
    [MG90S-Class Servo Envelope]                 [MGN9 Linear Rail]
     (Machine X=-17.40, Y=-11.00)                 (Machine X=0.00, Y=-21.00)
                 |                                           |
      [Archimedean Roller Cam]                   [MGN9C Carriage Block]
        (k = 6.6845 mm/rad)                                  |
                 |                                           |
                 | (Single-Acting Contact)                   |
                 v                                           v
       [MR84ZZ Roller Follower] <------------------ [ZC_Moving_Slider]
                                                             |
                                               [Receiver_Plate_V1 Body]
                                                             |
                                         (3x Kinematic Balls Ø6 + 3x Magnets)
                                                             |
                                                 [Tool_Sleeve_V1_1 Pad]
                                                             |
                                                     [Drawing Pen Nib]
```

---

## 2. Category A: Frozen V1 Geometry

### 2.1 Final Operational Z-States & Vertical Travel
All vertical positions are referenced to Machine $Z = 0.000\text{ mm}$ (nominal drawing paper datum):

| State Parameter | Value (Machine Z) | Description / Kinematic Function | Status |
| :--- | :--- | :--- | :--- |
| **$Z_{DRAW0}$** | $0.000\text{ mm}$ | Nominal flat drafting reference plane | `FROZEN` |
| **$Z_{COMPLIANCE\_LOW}$** | $-1.500\text{ mm}$ | Lower bound of functional surface compliance | `FROZEN` |
| **$Z_{COMPLIANCE\_HIGH}$** | $+1.500\text{ mm}$ | Upper bound of functional surface compliance | `FROZEN` |
| **Compliance Span** | $3.000\text{ mm}$ | Total free-floating vertical travel window | `FROZEN` |
| **$Z_{DOCK\_APPROACH}$** | $+6.500\text{ mm}$ | Approach height for dock U-fork wing capture | `FROZEN` |
| **$Z_{DOCK\_MATE}$** | $+6.500\text{ mm}$ | Dock retention shoulder engagement height | `FROZEN` |
| **$Z_{DOCK\_RELEASE}$** | $+8.000\text{ mm}$ | Carriage height after coupled release separation | `FROZEN` |
| **$Z_{PEN\_UP}$** | $+8.000\text{ mm}$ | High-speed travel retraction clearance | `FROZEN` |
| **$Z_{LOWER\_STOP}$** | $-2.500\text{ mm}$ | Physical lower hard-stop shelf contact face | `FROZEN` |
| **$Z_{UPPER\_STOP}$** | $+10.000\text{ mm}$ | Physical upper hard-stop shelf contact face | `FROZEN` |
| **Hard-Stop Span** | $12.500\text{ mm}$ | Total physical travel between positive stops | `FROZEN` |

### 2.2 Physical Hard-Stop Geometry & Authority
Hard stops are monolithic features integrated into the fixed baseplate and moving slider on the right side ($X \in [+13.000, +18.000]\text{ mm}$):
- **Lower Mechanical Stop ($Z = -2.500\text{ mm}$):**
  - Slider stop face at Machine $Z = -24.000\text{ mm}$ contacts baseplate shelf at Machine $Z = -26.500\text{ mm}$.
  - Epsilon verified in CAD: $Z = -2.450\text{ mm}$ is clear ($50\ \mu\text{m}$ gap); $Z = -2.500\text{ mm}$ establishes first contact ($< 1.0\ \mu\text{m}$); $Z = -2.550\text{ mm}$ creates $0.5000\text{ mm}^3$ solid interference.
  - At the authoritative park angle ($\gamma_{cam} = +120.000^\circ$), Cam-to-Follower clearance at $Z = -2.500\text{ mm}$ is $+0.435\text{ mm}$.
  - **Authority Verdict:** The mechanical shelf is the FIRST and EXCLUSIVE downward stop. The cam never becomes an unintended travel stop.
- **Upper Mechanical Stop ($Z = +10.000\text{ mm}$):**
  - Slider top face at Machine $Z = +24.000\text{ mm}$ contacts baseplate top shelf at Machine $Z = +34.000\text{ mm}$.
  - Epsilon verified in CAD: $Z = +9.950\text{ mm}$ is clear; $Z = +10.000\text{ mm}$ establishes first contact; $Z = +10.050\text{ mm}$ creates $0.5000\text{ mm}^3$ solid interference.

### 2.3 Cam Profile & Follower Body Geometry
The physical cam profile is an Archimedean spiral with circular dwells:
- **Cam Axis Location:** Machine Frame $(-17.400, -11.000, -24.508)\text{ mm}$.
- **Cam Thickness:** $2.800\text{ mm}$, centered at Machine $X = -16.000\text{ mm}$ ($X \in [-17.400, -14.600]\text{ mm}$).
- **Profile Formulation:**
  $$r_p(\theta_{profile}) = r_{p0} + k \cdot \theta_{profile}$$
  - Base radius: $r_{p0} = 12.000\text{ mm}$
  - Maximum active radius: $r_{pmax} = 22.500\text{ mm}$
  - Nominal vertical rise: $L_{nominal} = 10.500\text{ mm}$
  - Profile pitch constant: $k = \frac{10.500\text{ mm}}{\pi / 2\text{ rad}} = 6.6845076\text{ mm/rad}$
  - Pitch parameter domain: $0^\circ \le \theta_{profile} \le 90^\circ$ ($0 \le \theta_{profile} \le \frac{\pi}{2}\text{ rad}$)
- **Follower Roller Reference:** MR84ZZ-class miniature ball bearing:
  - Outside diameter: $\text{OD} = 8.000\text{ mm}$ ($R_f = 4.000\text{ mm}$)
  - Bore diameter: $\text{ID} = 4.000\text{ mm}$
  - Width: $W = 3.000\text{ mm}$ ($X \in [-17.500, -14.500]\text{ mm}$)
- **Follower Shoulder Pin:** Monolithic steel pin with $\varnothing 6.0 \times 1.5\text{ mm}$ head, $\varnothing 4.0 \times 3.0\text{ mm}$ shoulder, and $\varnothing 3.4 \times 3.5\text{ mm}$ threaded shank.

### 2.4 Fixed Baseplate Cam-Sweep Relief Geometry
The fixed baseplate (`ZC_Fixed_Baseplate.step`) incorporates targeted relief envelopes to accommodate the full cam swing down to $\gamma_{cam} = +120.000^\circ$:
- **Primary Cam Relief Pocket:**
  - Width: $4.500\text{ mm}$ ($X \in [-18.500, -14.000]\text{ mm}$, centered at $X = -16.250\text{ mm}$).
  - Height: $35.000\text{ mm}$ ($Z \in [-40.000, -5.000]\text{ mm}$, centered at $Z = -22.500\text{ mm}$).
  - Through-cut depth: $6.000\text{ mm}$ through full baseplate plate thickness ($Y \in [-27.000, -21.000]\text{ mm}$).
  - Relief opens directly through the bottom plate edge ($Z = -40.000\text{ mm}$).
- **Lower-Left Boundary Notch:**
  - Width: $7.500\text{ mm}$ ($X \in [-26.000, -18.500]\text{ mm}$, centered at $X = -22.250\text{ mm}$).
  - Height: $7.000\text{ mm}$ ($Z \in [-40.000, -33.000]\text{ mm}$, centered at $Z = -36.500\text{ mm}$).
  - Eliminates corner isolation, preserving strictly 1 structurally continuous solid.
- **Physical Solid Properties:**
  - Solid Count: EXACTLY 1 solid (`assert len(solids) == 1`).
  - Solid Volume: $22,009.57\text{ mm}^3$ (96.84% volume retention vs A.4 original).
  - Solid web to MGN9 rail mounting datum ($X = -4.500\text{ mm}$): $9.500\text{ mm}$.
  - Solid web above pocket to top boundary ($Z = +40.000\text{ mm}$): $45.000\text{ mm}$.
  - Solid web to right hard stops ($X = +13.000\text{ mm}$): $27.000\text{ mm}$.

### 2.5 Tool Sleeve V1.1 & Receiver Plate V1 Frozen Baselines
Preserved exactly from the accepted V1.1 kinematic baseline without modification:
- **Tool Sleeve V1.1 (`Tool_Sleeve_V1_1.step`):**
  - Tool Datum A: Local $Z = 4.200\text{ mm}$.
  - Tool Pad: $22.000 \times 48.000 \times 5.000\text{ mm}$.
  - Pen Bore: $\varnothing 12.500\text{ mm}$, centered at $(X = 0, Z = 14.500)\text{ mm}$.
  - Side Wings: Total span $28.000\text{ mm}$ ($X \in [-14.0, +14.0]\text{ mm}$), thickness $4.000\text{ mm}$, length $16.000\text{ mm}$.
  - Maxwell V-Grooves (3x):
    - $V1$: Center $(0.000, +15.000, 4.200)\text{ mm}$, axis $0.00^\circ$ from $+Y$.
    - $V2$: Center $(-6.000, -12.000, 4.200)\text{ mm}$, axis $+26.57^\circ$ from $+Y$ toward $+X$.
    - $V3$: Center (+6.000, -12.000, 4.200)\text{ mm}$, axis $-26.57^\circ$ from $+Y$ toward $+X$.
    - Profile: $90^\circ$ included angle, mouth width $W = 4.800\text{ mm}$, depth $D = 2.400\text{ mm}$, length $L = 5.000\text{ mm}$, lead-in chamfer $0.200\text{ mm} \times 45^\circ$.
  - Magnets: Magnet geometry $\varnothing 8.000 \times 2.000\text{ mm}$; 3x pockets $\varnothing 8.200\text{ mm}$ diameter, depth $= 2.200\text{ mm}$.
- **Receiver Plate V1 (`Receiver_Plate_V1.step`):**
  - Main Body: $22.000 \times 48.000 \times 6.000\text{ mm}$.
  - Balls: 3x $\varnothing 6.000\text{ mm}$ hardened chrome steel balls (G28 design spec), centers at $RY = 0.000\text{ mm}$ (protrusion $3.000\text{ mm}$):
    - $B1$: $(RX = 0.000, RZ = -15.000)\text{ mm}$
    - $B2$: $(RX = -6.000, RZ = +12.000)\text{ mm}$
    - $B3$: $(RX = +6.000, RZ = +12.000)\text{ mm}$
  - Ball Seats: Guide bore $\varnothing 6.100\text{ mm}$ ($RY\ 0 \to -1.193$), $90^\circ$ conical shoulder ($RY\ -1.193 \to -2.993$), apex $RY = -4.242641\text{ mm}$, contact ring diameter $\varnothing 4.242641\text{ mm}$ at $RY = -2.121320\text{ mm}$, adhesive/vent channel $\varnothing 2.500\text{ mm}$ ($RY\ -2.993 \to -6.000$).
  - Nominal Mating Gap: $G_{face} = 1.842641\text{ mm} \approx 1.843\text{ mm}$.
  - Magnet Pockets: Magnet geometry $\varnothing 8.000 \times 2.000\text{ mm}$; 3x pockets $\varnothing 8.200\text{ mm}$ diameter, depth $= 2.200\text{ mm}$ at:
    - $M1$: $(RX = 0.000, RY = -1.200, RZ = +2.000)\text{ mm}$
    - $M2$: $(RX = -5.000, RY = -1.200, RZ = -6.000)\text{ mm}$
    - $M3$: $(RX = +5.000, RY = -1.200, RZ = -6.000)\text{ mm}$
- **Poka-Yoke Interface:**
  - Receiver Key Pin: Monolithic pin $2.400 \times 2.400\text{ mm}$, height $3.300\text{ mm}$ ($R_Y \in [0.000, +3.300]\text{ mm}$) centered at $(R_X = +9.500\text{ mm}, R_Z = -22.500\text{ mm})$.
  - Tool Notch: Cutout $3.000 \times 3.000\text{ mm}$, depth $2.000\text{ mm}$ centered at $(T_X = +9.500\text{ mm}, T_Y = +22.500\text{ mm})$ on Tool Datum A at local $Z = 4.200\text{ mm}$.
  - Coordinate Frame Note: The sign and axis mapping ($R_X = T_X$, $R_Z = -T_Y$) is the direct physical consequence of the frozen Tool-to-Receiver in-plane coordinate transformation ($R_Z = -Y_{tool}$).
  - Nominal insertion: $1.457\text{ mm}$; nominal bottom clearance: $0.543\text{ mm}$ (worst-case prototype clearance $+0.213\text{ mm}$).
- **Dock U-Fork Interface:**
  - Slot width: $P = 32.000\text{ mm}$ pitch between adjacent bays.
  - Active 4-tool envelope: $124.000\text{ mm}$; base reference width: $144.000\text{ mm}$.
  - U-fork slot thickness: $4.400\text{ mm}$ (captures $4.000\text{ mm}$ tool wings with nominal $0.400\text{ mm}$ clearance).

---

## 3. Category B: Derived Analytical Values & Kinematic Rules

### 3.1 Angular Coordinates & Operational Mapping
Three distinct angular variables govern the mechanism and must not be conflated:
- $\gamma_{cam}$: Physical rotation of the cam solid in Machine Frame about Machine $+X$. $\gamma_{cam} = 0.000^\circ$ at `STATE_PEN_UP`.
- $\phi_{servo}$: Actuator command coordinate in firmware. $\phi_{servo} = 0.000^\circ$ at `FREE_DRAW_PARK`.
- $\theta_{profile}$: Archimedean pitch angle along the physical cam lobe ($0^\circ \le \theta_{profile} \le 90^\circ$).

$$\phi_{servo} = 120.000^\circ - \gamma_{cam}$$

| Operational State | $\phi_{servo}$ | $\gamma_{cam}$ | $\theta_{profile}$ | $Z_{slider}$ | Mechanism Behavior |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FREE_DRAW_PARK** | $0.000^\circ$ | $+120.000^\circ$ | N/A (Root Dwell) | $-1.500 .. +1.500\text{ mm}$ | Fully disengaged; free-floating gravity drafting |
| **CONTACT_START (Low)** | $38.640^\circ$ | $+81.360^\circ$ | $8.640^\circ$ | $-1.500\text{ mm}$ | Tangent contact initiation at lower compliance bound |
| **CONTACT_START (Nom)** | $51.497^\circ$ | $+68.503^\circ$ | $21.497^\circ$ | $0.000\text{ mm}$ | Tangent contact initiation at nominal drafting plane |
| **CONTACT_START (High)**| $64.354^\circ$ | $+55.646^\circ$ | $34.354^\circ$ | $+1.500\text{ mm}$ | Tangent contact initiation at upper compliance bound |
| **STATE_DOCK_MATE** | $107.211^\circ$ | $+12.789^\circ$ | $77.211^\circ$ | $+6.500\text{ mm}$ | Tool wing engagement with Dock U-Fork |
| **STATE_PEN_UP** | $120.000^\circ$ | $0.000^\circ$ | $90.000^\circ$ | $+8.000\text{ mm}$ | Full vertical lift retraction onto high dwell arc |

- **Required Operational Angular Stroke:** $\Delta \phi_{servo} = 120.000^\circ$. (System travel requirement: A candidate actuator must provide at least this usable calibrated travel plus implementation margin. Exact available travel must be verified for the selected servo SKU; $180^\circ$ serves only as an illustrative candidate specification, not a verified component capability).

### 3.2 Floating Contact Kinematics (Lost Motion)
Because the pen axis floats freely under gravity prior to cam engagement, contact initiation is position-dependent:
- Prior to contact ($\phi < \phi_{contact}(Z)$): The slider position is governed entirely by gravity, pen drag, and paper topography.
- At contact ($\phi = \phi_{contact}(Z)$): The cam profile achieves zero-clearance tangency with the follower bearing.
- After contact ($\phi > \phi_{contact}(Z)$): The cam positively drives carriage lift.
- The angular span $\Delta \phi \in [0.0^\circ, \phi_{contact}]$ constitutes an intentional lost-motion zone that guarantees complete decoupling during drafting.

### 3.3 Active Lift Kinematics & Pressure Angle
During the active rise phase ($\phi \ge \phi_{contact}$):
- **Local Kinematic Derivative:**
  $$\left| \frac{dz_{slider}}{d\phi_{servo}} \right| = +k = +6.6845\text{ mm/rad} = +0.0066845\text{ m/rad}$$
- **Maximum Pressure Angle:**
  $$\alpha_{max} \approx 29.12^\circ \quad (\text{at } \theta_{profile} = 0.000^\circ)$$
- **Operational Pressure Angles:** $\alpha(Z=-1.5\text{ mm}) = 27.23^\circ$, $\alpha(Z=0\text{ mm}) = 24.74^\circ$, $\alpha(Z=+6.5\text{ mm}) = 17.66^\circ$, $\alpha(Z=+8.0\text{ mm}) = 15.47^\circ$.
- **Evaluation:** Meets the current analytical pressure-angle design criterion ($\alpha < 30.0^\circ$ across the evaluated active rise). Physical running friction, backdrive and binding behavior remain subject to prototype validation.

### 3.4 B-Rep Clearance Verification in FREE_DRAW_PARK ($\gamma_{cam} = +120.000^\circ$)
- At $Z_{slider} = +1.500\text{ mm}$ (Compliance High): Follower clearance $= +4.086\text{ mm}$ (Clear).
- At $Z_{slider} =  0.000\text{ mm}$ (DRAW Nominal): Follower clearance $= +2.673\text{ mm}$ (Clear).
- At $Z_{slider} = -1.500\text{ mm}$ (Compliance Low): Follower clearance $= +1.304\text{ mm}$ (Clear).
- At $Z_{slider} = -2.500\text{ mm}$ (Lower Hard Stop): Follower clearance $= +0.435\text{ mm}$ (Clear).

### 3.5 Continuous Operating Sweep Verification
Exhaustively audited across 241 angular steps ($\le 0.5^\circ$ increments) from $\gamma = +120^\circ \to 0^\circ$ across all 3 initial floating conditions ($Z_{init} \in \{-1.5, 0.0, +1.5\}\text{ mm}$):
- Cam vs Fixed Baseplate: $0.000000\text{ mm}^3$ collision across all 723 evaluated states.
- Cam vs Moving Slider: $0.000000\text{ mm}^3$ collision.
- Cam vs MG90S Reference Envelope: $0.000000\text{ mm}^3$ collision.
- MG90S Reference vs Moving Slider: $0.000000\text{ mm}^3$ collision.
- Cam vs Follower Bearing: Pure tangent contact (penetration volume $\le 0.0016\text{ mm}^3$, within numerical CAD tolerance).
- **Collision Verdict:** CAD VERIFIED — ZERO FORBIDDEN POSITIVE-VOLUME OVERLAPS.

### 3.6 Coupled Shear + Normal Tool Release Motion
Tool release from the carriage receiver into the dock bay is executed as a coordinated 2-axis CoreXY/Z motion:
- **Machine Displacements:** $\Delta Z = +1.500\text{ mm}$, $\Delta Y = -1.000\text{ mm}$.
- **Tool-Relative Motion:** $\Delta T_Y = -1.500\text{ mm}$ (axial shear along V-groove), $\Delta T_Z = -1.000\text{ mm}$ (normal separation).
- **Separation Mechanism:** **COUPLED SHEAR + NORMAL SEPARATION**.
- **Theoretical Separation Clearance:** $+0.066\text{ mm}$ minimum clearance under assumed prototype tolerances.

### 3.7 Parametric Moving Mass Estimates (Sensitivity Baseline)
Values are parametric mass estimates only (not physically measured):
- Reference Non-Printed Subtotal: $29.51\text{ g}$ (REFERENCE ANALYTICAL SUBTOTAL — NOT MEASURED — NOT FROZEN).
- LOW Scenario: $52.92\text{ g}$ total moving mass ($F_{gravity} = 0.5190\text{ N}$).
- NOMINAL Scenario: $62.13\text{ g}$ total moving mass ($F_{gravity} = 0.6093\text{ N}$).
- HIGH (PLA) Scenario: $81.62\text{ g}$ total moving mass ($F_{gravity} = 0.8004\text{ N}$).
- HIGH (PETG) Scenario: $82.27\text{ g}$ total moving mass ($F_{gravity} = 0.8068\text{ N}$).

### 3.8 Guide Friction & Pen Downforce Mechanics
- **Nib Force Target:** $50\text{ gf} \le F_{nib} \le 100\text{ gf}$ ($\approx 0.49 - 0.98\text{ N}$).
- **Allowable Guide Drag Formula:**
  $$F_{guide\_allow} = \min(100.0\text{ gf} - F_{gravity},\ F_{gravity} - 50.0\text{ gf}) = \min(100.0 - m_{total},\ m_{total} - 50.0)\text{ gf}$$
- **Supported Mass Window for $10.0\text{ gf}$ Guide Friction:**
  $$60.0\text{ g} \le m_{total} \le 90.0\text{ g}$$
- For NOMINAL ($62.13\text{ g}$) and HIGH ($81.62\text{ g}$), $10\text{ gf}$ drag natively passes.
- For unballasted LOW ($52.92\text{ g}$), allowable drag is only $2.92\text{ gf}$; ballast required: $m_{ballast} \ge 7.08\text{ g}$.

### 3.9 Ideal Static Actuator Torque
Evaluated using the verified local derivative $|dz/d\phi| = 0.0066845\text{ m/rad}$:
- **NOMINAL ($62.13\text{ g}$ w/ $10\text{ gf}$ drag):** $\tau_{ideal} = 0.473\text{ N}\cdot\text{cm}$ ($0.048\text{ kgf}\cdot\text{cm}$). Pure-gravity hold: $0.407\text{ N}\cdot\text{cm}$.
- **HIGH PLA ($81.62\text{ g}$ w/ $10\text{ gf}$ drag):** $\tau_{ideal} = 0.601\text{ N}\cdot\text{cm}$ ($0.061\text{ kgf}\cdot\text{cm}$). Pure-gravity hold: $0.535\text{ N}\cdot\text{cm}$.
- **DOCK_MATE Torque ($\phi = 107.211^\circ$):** $0.473\text{ N}\cdot\text{cm}$ (NOMINAL) / $0.601\text{ N}\cdot\text{cm}$ (HIGH PLA).

### 3.10 Poka-Yoke Tolerance Margins
- **Normal Docking Engagement:**
  - Key protrusion: $3.300 \pm 0.080\text{ mm}$ ($[3.220, 3.380]\text{ mm}$).
  - Face gap: $G_{face} = 1.843\text{ mm}$.
  - Tool notch depth: $2.000 \pm 0.100\text{ mm}$ ($[1.900, 2.100]\text{ mm}$).
  - Bottom clearance: Nominal $= 0.543\text{ mm}$; Worst-case minimum $= +0.213\text{ mm} > 0$.
- **Reversed $180^\circ$ Presentation Intercept:**
  - Ball protrusion: $3.000 \pm 0.050\text{ mm}$ ($[2.950, 3.050]\text{ mm}$).
  - Worst-case lead: $\text{Lead}_{min} = 3.220 - 3.050 = +0.170\text{ mm} > 0$ (Nominal $= +0.300\text{ mm}$).
  - Key pin intercepts the flat tool pad $+0.170\text{ mm}$ before any steel ball can enter a groove mouth.

### 3.11 Dock U-Fork Engagement Tolerance
- Tool wing thickness: $4.00 \pm 0.15\text{ mm}$ ($[3.85, 4.15]\text{ mm}$).
- Dock U-fork slot: $4.40 \pm 0.15\text{ mm}$ ($[4.25, 4.55]\text{ mm}$).
- Wing-to-fork clearance: Nominal $= 0.400\text{ mm}$; Minimum $= 0.100\text{ mm}$; Maximum $= 0.700\text{ mm}$.

---

## 4. Category C: Candidate Commercial Components (Unfrozen Procurement)

The following components represent CAD packaging baselines. Exact commercial manufacturer, vendor, model number, and grade remain unfrozen:

| Function | Candidate Class / Specification | Packaging Envelope in CAD | Procurement Status |
| :--- | :--- | :--- | :--- |
| **Z-Axis Guide** | MGN9-class miniature linear rail + MGN9C carriage block | Rail $9 \times 6.5\text{ mm}$, Block $20 \times 28.9 \times 10\text{ mm}$ | PRIMARY CANDIDATE / Exact SKU TBD |
| **Roller Follower** | MR84ZZ-class miniature deep-groove ball bearing | $\text{OD } 8.0\text{ mm}, \text{ID } 4.0\text{ mm}, \text{Width } 3.0\text{ mm}$ | Q3 CANDIDATE / Exact SKU TBD |
| **Actuator** | MG90S-class 9g metal-gear micro servo | $28.5\text{ mm } (X) \times 32.5\text{ mm } (Y) \times 12.2\text{ mm } (Z)$ | Q3 CANDIDATE / Exact SKU TBD |
| **Coupling Balls** | Chrome steel bearing balls $\varnothing 6.000\text{ mm}$ | Grade 28 design specification | DESIGN SPEC / Vendor TBD |
| **Coupling Magnets** | Sintered NdFeB disc magnets $\varnothing 8.000 \times 2.000\text{ mm}$ | Pockets $\varnothing 8.200\text{ mm} \times 2.200\text{ mm}$ depth | BOM CANDIDATE / Grade TBD |

### 4.1 Provisional Actuator Selection Targets
- Continuous Holding Torque: $\tau_{cont} \ge 1.50\text{ N}\cdot\text{cm}$
- Peak / Stall Torque: $\tau_{stall} \ge 8.00\text{ N}\cdot\text{cm}$
- Operational Electrical / Mechanical Travel: $\Delta \phi \ge 120.0^\circ$ (plus firmware calibration margin).

---

## 5. Category D: Physical & Experimental Validation Register (Open TBD Items)

The following parameters are explicitly NOT frozen by CAD or analytical results and require physical bench measurement on prototype hardware:

1. **Actual Printed / Assembled Moving Mass:** Physical scale measurement of printed slider, receiver, follower, and fasteners.
2. **Linear Guide Friction & Stiction:** Breakaway and running friction measurement across full Z-stroke under moment load.
3. **Real Pen Downforce:** Load-cell measurement of actual nib force on paper across $Z \in [-1.5, +1.5]\text{ mm}$.
4. **Passive Gravity Drop Functionality:** Verification that carriage drops freely without hanging up on rail stiction.
5. **Actuator Selection & Thermal Stability:** Current draw and temperature rise during continuous holding at `STATE_PEN_UP`.
6. **Dynamic Actuation Torque & Current:** Dynamic actuation torque and current during commanded lift/transit motion — motion profile and acceptable transit time TBD.
7. **Magnetic Preload & Separation Force:** Force-displacement curve measurement for carriage and dock magnetic couplings.
8. **Coupling Repositioning Repeatability:** Verification of the $\le 0.050\text{ mm}$ repositioning target using dial test indicators (`DESIGN TARGET / UNVALIDATED`).
9. **Poka-Yoke Reversed Rejection Test:** Physical verification that $180^\circ$ reversed docking is mechanically arrested without magnetic snapping.
10. **Coupled Release Test:** Multi-cycle confirmation of smooth tool drop-off without jamming or dock deflection.
11. **Baseplate & Dock Structural Rigidity:** Physical deflection testing under magnetic release loads (FEA / physical validation).
12. **Endurance Cycling:** Endurance cycling of cam, follower and kinematic ball seats; cycle count and acceptance criteria TBD before test.

---

## 6. Category E: Deprecated & Superseded Specifications

The following historical parameters, concepts, and terminology are formally deprecated and must not appear in current documentation:

| Deprecated Parameter / Concept | Superseded Value | Authoritative Frozen Baseline | Rationale for Deprecation |
| :--- | :--- | :--- | :--- |
| **FREE_DRAW Cam Park Angle** | $\gamma_{cam} = -90.0^\circ$ | $\gamma_{cam} = +120.0^\circ$ ($\phi_{servo} = 0.0^\circ$) | Disconnected state mapping; incompatible with monotonic rise |
| **FREE_DRAW Cam Park Angle** | $\gamma_{cam} = +90.0^\circ$ | $\gamma_{cam} = +120.0^\circ$ ($\phi_{servo} = 0.0^\circ$) | Blocked mechanical lower stop at $Z \approx -1.783\text{ mm}$ |
| **Archimedean Rise Rate** | Average $8.775\text{ mm/rad}$ | Uniform local derivative $+6.6845\text{ mm/rad}$ | Average secant slope conflated dwell with active Archimedean rise |
| **Universal Guide Friction Limit** | Generic $\le 12\text{ gf}$ | Variable limit: $F_{guide} \le \min(100 - m, m - 50)\text{ gf}$ | Friction margin depends strictly on actual moving mass |
| **Tool Release Terminology** | "Peel Release" | "Coupled Shear + Normal Separation" | Release motion is a coordinated diagonal CoreXY/Z vector ($\Delta Z=+1.5, \Delta Y=-1.0\text{ mm}$) |
| **Poka-Yoke Key Dimensions** | $2.6 \times 2.6\text{ mm}$, $1.5\text{ mm}$ protrusion | $2.4 \times 2.4\text{ mm}$, $3.3\text{ mm}$ protrusion | Inadequate clearance and failed early reversed intercept |
| **Coupling Terminology** | "Kelvin Coupling" | "Maxwell-Type Kinematic Coupling" | OmniDraw utilizes 3 V-grooves oriented to center, strictly Maxwell configuration |
| **Compliance Springs** | Dual compression springs | Gravity-dominant floating carriage | Springs eliminated in favor of passive gravity downforce |
| **Magnet Sizes** | $\varnothing 6 \times 3\text{ mm}$ | $\varnothing 8 \times 2\text{ mm}$ (3 pairs) | Standardized magnet geometry |
| **Ball Grades** | Grade 25 balls | Grade 28 design specification | Corrected design specification baseline |

---

## 7. Traceability Matrix

- **Upstream Architecture:** [01_hardware_architecture.md](01_hardware_architecture.md)
- **Mating Tool Changer Baseline:** [02_tool_changer_spec.md](02_tool_changer_spec.md)
- **Downstream Motion Platform:** [04_corexy_frame_spec.md](04_corexy_frame_spec.md)
- **Validation Procedures:** [06_validation_plan.md](06_validation_plan.md)
- **Engineering Decision History:** [hardware_decision_log.md](hardware_decision_log.md) (Decision HW-DEC-Q3-FINAL-001)
- **CAD Implementation:** `cad/build_q3c_cad_assembly.py`
