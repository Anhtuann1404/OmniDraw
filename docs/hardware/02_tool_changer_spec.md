# Tool Changer Specification

**Subsystem:** OmniDraw Quad-Pen Tool Changer  
**Interface Revision:** V1.1  
**Status:** FROZEN DESIGN BASELINE  

---

## 1. Purpose

The Quad-Pen Tool Changer is the central mechanical subsystem of OmniDraw Plotter V1. It provides an automated, kinematically constrained coupling between the moving X/Z-Carriage and up to four interchangeable drawing tool sleeves stationed in a passive docking bay at Machine $Y = Y_{max}$.

---

## 2. Subsystem Architecture

The tool changer consists of three primary physical components:
1. **Pen Slider / Tool Sleeve V1.1:** Standardized sleeve holding the pen body, featuring 3 radial V-grooves, 3 embedded N52 magnets, dual side wings, and a mechanical orientation notch.
2. **Carriage Receiver Plate V1:** Fixed kinematic interface plate bolted to the Z-Carriage via a 4x M3 grid, carrying 3 hardened steel balls $\phi 6.000\text{ mm}$, 3 matching N52 magnets, and a monolithic Poka-Yoke key.
3. **Stationary Quad Dock:** 4-slot passive docking bay featuring U-fork retention shoulders, mechanical Z-stops, and auxiliary rear seating magnets.

```
       [Carriage Receiver Plate V1]
                  |
     (3 × Steel Balls Ø6 mm + 3 × Magnets N52)
                  |  <-- 6-DOF Maxwell Kinematic Coupling
     (3 × V-Grooves 90° + 3 × Magnets N52)
                  |
       [Pen Slider / Tool Sleeve V1.1]
                  |
        (Dual Side Wings 28 mm)
                  |  <-- Passive Capture / Shear Release
       [Stationary Quad Dock U-Fork]
```

---

## 3. Coordinate Systems

### 3.1 Tool Sleeve Local Frame ($\mathcal{F}_{tool}$)
- **Origin ($O_{tool}$):** Center of the Tool Mating Pad on Datum A.
- **$\text{Local }+X$:** Horizontal axis across the tool pad ($X \in [-11.000, +11.000]\text{ mm}$).
- **$\text{Local }+Y$:** Longitudinal axis along the pen body towards the **Pen Tip** ($Y \in [-24.000, +24.000]\text{ mm}$).
- **$\text{Local }+Z$:** Normal axis directed through the sleeve body towards the back spine ($Z \in [4.200, 27.000]\text{ mm}$).
- **Tool Datum A Plane:** Primary mating face defined at $\mathbf{\text{Local } Z = 4.200\text{ mm}}$.

### 3.2 Receiver Plate Local Frame ($\mathcal{F}_{receiver}$)
- **Origin ($O_{receiver}$):** Center of the Receiver Mating Face on Datum A.
- **Trục $+R_X$ (Horizontal):** Aligned with Machine $+X$ ($R_X \in [-11.000, +11.000]\text{ mm}$).
- **Trục $+R_Z$ (Vertical):** Aligned with Machine $+Z$ ($R_Z \in [-24.000, +24.000]\text{ mm}$).
- **Trục $+R_Y$ (Plate Normal):** Thickness axis directed forward towards the Tool ($R_Y \in [-6.000, 0.000]\text{ mm}$).
- **RECEIVER_DATUM_A:** Front mating plane defined at $\mathbf{R_Y = 0.000\text{ mm}}$.
- **Rear Mounting Plane:** Back face defined at $\mathbf{R_Y = -6.000\text{ mm}}$.

### 3.3 2D In-Plane Interface Transformation
When the Carriage Receiver directly faces the Tool Sleeve:

$$\begin{bmatrix} R_X \\ R_Z \end{bmatrix} = \begin{bmatrix} 1 & 0 \\ 0 & -1 \end{bmatrix} \begin{bmatrix} X_{tool} \\ Y_{tool} \end{bmatrix} \implies \begin{cases} R_X = +X_{tool} \\ R_Z = -Y_{tool} \end{cases}$$

The plate-normal coordinate $R_Y$ is defined independently along the thickness axis, with $R_Y = 0.000\text{ mm}$ establishing RECEIVER_DATUM_A and $R_Y = -6.000\text{ mm}$ establishing the rear mounting plane. The nominal face-to-face separation between RECEIVER_DATUM_A ($R_Y = 0.000\text{ mm}$) and Tool Datum A ($Z_{tool} = 4.200\text{ mm}$) when fully seated is $G_{face} = 1.843\text{ mm}$.

---

## 4. Pen Slider / Tool Sleeve V1.1

### 4.1 Body Dimensions & Pen Bore
- **Mating Pad Dimensions:** $22.000\text{ mm}$ (Width $X$) $\times 48.000\text{ mm}$ (Length $Y$) $\times 5.000\text{ mm}$ (Thickness, $Z \in [4.200, 9.200]\text{ mm}$).
- **Pen Bore Cylinder:** $\phi 12.500\text{ mm}$ continuous through-bore along Local $Y \in [-24.000, +24.000]\text{ mm}$, centered at $(X = 0.000, Z = 14.500)\text{ mm}$. Lowest point of bore wall is at $Z = 8.250\text{ mm}$.
- **Top M3 Clamp Boss:** Cylindrical boss $\phi 9.000\text{ mm}$ located at $X = 0.000, Y = +2.000\text{ mm}$, spanning $Z \in [22.000, 27.000]\text{ mm}$, with a through-hole $\phi 3.200\text{ mm}$ along Local $Z$ for an M3 clamping bolt.

### 4.2 Tool V-Groove Interface V1.1
- **Profile:** $90.0^\circ$ included angle (symmetric $45.0^\circ$ flank slopes).
- **Dimensions:** Nominal mouth width $W = 4.800\text{ mm}$, depth $D = 2.400\text{ mm}$, length $L = 5.000\text{ mm}$.
- **Lead-in Chamfer:** $0.200\text{ mm} \times 45.0^\circ$ along outer mouth edges (physical outermost opening $W_{phys} = 5.200\text{ mm}$).
- **V-Groove Centers & Orientations on Datum A ($Z = 4.200\text{ mm}$):**
  - **`TOOL_V_GROOVE_V1`:** $(X = 0.000, Y = +15.000, Z = 4.200)\text{ mm}$, axis along Local $+Y$ ($0.00^\circ$ from $+Y / 90.00^\circ$ from $+X$).
  - **`TOOL_V_GROOVE_V2`:** $(X = -6.000, Y = -12.000, Z = 4.200)\text{ mm}$, axis oriented at $26.57^\circ$ from $+Y$ ($63.43^\circ$ from $+X$), pointing toward coupling center $C(0,0,4.2)$.
  - **`TOOL_V_GROOVE_V3`:** $(X = +6.000, Y = -12.000, Z = 4.200)\text{ mm}$, axis oriented at $-26.57^\circ$ from $+Y$ ($116.57^\circ$ from $+X$), pointing toward coupling center $C(0,0,4.2)$.
- **Angular Distribution:** Asymmetric isosceles configuration $153.43^\circ / 153.43^\circ / 53.13^\circ$.
- **Structural Web Checks:**
  - Remaining solid web below $V1$ apex to pen bore: $8.250 - (4.200 + 2.400) = 1.650\text{ mm}$ (passes current prototype design target, exceeds $1.500\text{ mm}$ minimum).
  - Remaining side edge web at $V2/V3$: $11.000 - (6.000 + 3.444) = 1.556\text{ mm}$ (passes current prototype design target, exceeds $1.500\text{ mm}$ minimum).

### 4.3 Tool Magnets
- **Quantity & Spec:** 3 × Neodymium N52 $\phi 8.000 \times 2.000\text{ mm}$.
- **Pocket Dimensions:** $\phi 8.200\text{ mm} \times$ depth $2.200\text{ mm}$ (recessed $0.200\text{ mm}$ below Datum A).
- **Pattern Centers on Datum A ($Z = 4.200\text{ mm}$):**
  - `TOOL_MAGNET_M1_PATTERN`: $(X = 0.000, Y = -2.000)\text{ mm}$ (North pole facing outward).
  - `TOOL_MAGNET_M2_PATTERN`: $(X = -5.000, Y = +6.000)\text{ mm}$ (South pole facing outward).
  - `TOOL_MAGNET_M3_PATTERN`: $(X = +5.000, Y = +6.000)\text{ mm}$ (South pole facing outward).
- **Physical 3D Centers:**
  - `TOOL_MAGNET_M1_CENTER_3D`: $(X = 0.000, Y = -2.000, Z = 5.400)\text{ mm}$.
  - `TOOL_MAGNET_M2_CENTER_3D`: $(X = -5.000, Y = +6.000, Z = 5.400)\text{ mm}$.
  - `TOOL_MAGNET_M3_CENTER_3D`: $(X = +5.000, Y = +6.000, Z = 5.400)\text{ mm}$.
- **Web Thickness to Pen Bore:** $8.250 - 6.400 = 1.850\text{ mm}$ solid plastic behind $M1$ pocket ceiling.

### 4.4 Mechanical Orientation Notch (Poka-Yoke)
- **Geometry:** Rectangular cutout $3.000\text{ mm} \times 3.000\text{ mm}$, depth $2.000\text{ mm}$ into Datum A ($Z \in [4.200, 6.200]\text{ mm}$).
- **Location:** Centered at $(X = +9.500, Y = +22.500, Z = 4.200)\text{ mm}$ (top-right corner of tool pad).

---

## 5. Kinematic Coupling

- **Type:** 6-point Maxwell Kinematic Coupling (3 V-grooves mating with 3 spherical balls).
- **Theoretical Contact Geometry:**
  - Ball radius: $R = 3.000\text{ mm}$.
  - Tangential contact depth below Tool Datum A: $z_{contact} = D - R\sin(45^\circ) = 2.400 - 2.121 = 0.279\text{ mm}$.
  - Contact point horizontal separation: $2R\cos(45^\circ) = 4.243\text{ mm}$.
  - Lip margin per flank: $(4.800 - 4.243)/2 = 0.279\text{ mm}$.
  - Apex clearance (bottom pole of ball to groove apex): $D - (z_{ball\_center} + R - Z_{datum\_A}) = 1.243\text{ mm}$ (nominally clear, no bottoming out).
- **Jacobian Conditioning Model:**
  - Constraint matrix $J$ ($6 \times 6$) evaluated with normalized radius $R_0 = 15.000\text{ mm}$.
  - **Constraint Rank:** $\mathbf{\text{Rank} = 6}$ (Full rank 6-DOF, non-singular in the evaluated rigid-body model).
  - **Spectral Condition Number:** $\kappa_2(J) = 3.2306$ (`INFORMATIONAL METRIC`, demonstrates well-balanced multi-directional constraint).

---

## 6. Receiver Plate V1

### 6.1 Envelope & Coordinate Frame
- **Envelope:** $22.000\text{ mm}$ (Width $R_X$) $\times 48.000\text{ mm}$ (Height $R_Z$) $\times 6.000\text{ mm}$ (Thickness, $R_Y \in [-6.000, 0.000]\text{ mm}$).
- **Material Target:** FDM printed PETG / ABS / ASA ($0.16\text{ mm}$ layer height, 4 perimeters).

### 6.2 Steel Balls & Hard Geometric Seat Architecture
- **Steel Balls:** 3 × Hardened Chrome Steel Balls $\phi 6.000\text{ mm}$ (G28 nominal specification).
- **Nominal Ball Centers:**
  - `RECEIVER_BALL_B1`: $(R_X = 0.000, R_Y = 0.000, R_Z = -15.000)\text{ mm}$ (Mates with $V1$).
  - `RECEIVER_BALL_B2`: $(R_X = -6.000, R_Y = 0.000, R_Z = +12.000)\text{ mm}$ (Mates with $V2$).
  - `RECEIVER_BALL_B3`: $(R_X = +6.000, R_Y = 0.000, R_Z = +12.000)\text{ mm}$ (Mates with $V3$).
- **Seat Architecture:**
  - **Guide Bore:** $\phi 6.100\text{ mm}$ ($R = 3.050\text{ mm}$) spanning $R_Y \in [-1.193, 0.000]\text{ mm}$ ($1.193\text{ mm}$ depth).
  - **Conical Centering Shoulder:** $90.0^\circ$ included angle spanning $R_Y \in [-2.993, -1.193]\text{ mm}$. Theoretical apex at $R_Y = -4.243\text{ mm}$. Tangential contact circle at $R_Y = -2.121\text{ mm}$ with diameter $\phi 4.243\text{ mm}$.
  - **Rear Adhesive / Vent Channel:** $\phi 2.500\text{ mm}$ through-hole spanning $R_Y \in [-6.000, -2.993]\text{ mm}$ (channel length $\approx 3.007\text{ mm}$ surrounded by annular plate material).
- **Datum Control:**
  - $R_X, R_Z$ controlled by $90^\circ$ conical centering shoulder + $\phi 6.10\text{ mm}$ guide bore.
  - $R_Y$ controlled by hard tangential contact ring on conical slope setting ball center at $R_Y = 0.000\text{ mm}$ (Datum A).
  - Adhesive (Epoxy/CA): **RETENTION ONLY**, does not establish positional datum.
- **Nominal Ball Protrusion:** $3.000\text{ mm}$ hemisphere protruding past RECEIVER_DATUM_A ($R_Y \in [0.000, +3.000]\text{ mm}$).

### 6.3 Receiver Magnets
- **Quantity & Spec:** 3 × Neodymium N52 $\phi 8.000 \times 2.000\text{ mm}$.
- **Pocket Dimensions:** $\phi 8.200\text{ mm} \times$ depth $2.200\text{ mm}$ (recessed $0.200\text{ mm}$ below Datum A).
- **Pattern Centers on Datum A ($R_Y = 0.000\text{ mm}$):**
  - `RECEIVER_MAGNET_M1_PATTERN`: $(R_X = 0.000, R_Z = +2.000)\text{ mm}$ (South pole facing outward).
  - `RECEIVER_MAGNET_M2_PATTERN`: $(R_X = -5.000, R_Z = -6.000)\text{ mm}$ (North pole facing outward).
  - `RECEIVER_MAGNET_M3_PATTERN`: $(R_X = +5.000, R_Z = -6.000)\text{ mm}$ (North pole facing outward).
- **Physical 3D Centers:**
  - `RECEIVER_MAGNET_M1_CENTER_3D`: $(R_X = 0.000, R_Y = -1.200, R_Z = +2.000)\text{ mm}$.
  - `RECEIVER_MAGNET_M2_CENTER_3D`: $(R_X = -5.000, R_Y = -1.200, R_Z = -6.000)\text{ mm}$.
  - `RECEIVER_MAGNET_M3_CENTER_3D`: $(R_X = +5.000, R_Y = -1.200, R_Z = -6.000)\text{ mm}$.

### 6.4 Mounting Interface to Z-Carriage (Input for Q3)
- **Pattern:** 4 × M3 counterbore holes arranged symmetrically on a $12.000\text{ mm} \times 40.000\text{ mm}$ rectangular grid.
- **Hole Centers on Datum A:**
  - `MOUNT_HOLE_H1` (Top-Left): $(R_X = -6.000, R_Z = +20.000)\text{ mm}$
  - `MOUNT_HOLE_H2` (Top-Right): $(R_X = +6.000, R_Z = +20.000)\text{ mm}$
  - `MOUNT_HOLE_H3` (Bottom-Left): $(R_X = -6.000, R_Z = -20.000)\text{ mm}$
  - `MOUNT_HOLE_H4` (Bottom-Right): $(R_X = +6.000, R_Z = -20.000)\text{ mm}$
- **Hole Dimensions:** Through-hole $\phi 3.400\text{ mm}$ ($R_Y \in [-6.000, 0.000]\text{ mm}$); rear counterbore $\phi 6.200\text{ mm}$ depth $3.000\text{ mm}$ ($R_Y \in [-6.000, -3.000]\text{ mm}$).

---

## 7. Magnetic Preload System

- **Nominal Face-to-Face Air Gap:** $G_{face} = 1.843\text{ mm}$ (Calculated from engaged ball depth; nominally clear, no plastic face contact).
- **Nominal Magnetic Pole-to-Pole Gap:** $G_{magnetic} = G_{face} + 0.200 + 0.200 = 2.243\text{ mm}$.
- **Preload Force Target:** $18.0 - 22.0\text{ N}$ (`ASPIRATIONAL DESIGN TARGET / NOT MEASURED / BENCH TEST REQUIRED`).
- **Kinematic Contact Rule:** Magnets remain non-contact across the nominal $2.243\text{ mm} $ air gap.

---

## 8. Poka-Yoke Mechanical Orientation Lock

- **Key Pin:** $2.400 \times 2.400\text{ mm}$, height $H_{key} = 3.300\text{ mm}$ past RECEIVER_DATUM_A ($R_Y \in [0.000, +3.300]\text{ mm}$), centered at $(R_X = +9.500, R_Z = -22.500)\text{ mm}$.
- **Monolithic Edge-Tab Root:** Reinforced base extending to plate boundary ($R_X \in [+8.300, +11.000]\text{ mm}$, $R_Z \in [-24.000, -21.000]\text{ mm}$, $R_Y \in [-6.000, 0.000]\text{ mm}$).
- **Correct Orientation Engagement:**
  - Pin insertion depth into Tool notch: $H_{key} - G_{face} = 3.300 - 1.843 = 1.457\text{ mm}$.
  - Nominal bottom clearance: $2.000 - 1.457 = 0.543\text{ mm}$.
  - Worst-case calculated bottom clearance: $+0.213\text{ mm} > 0$ (positive under stated prototype tolerance assumptions).
- **Wrong 180° Orientation Early-Intercept:**
  - Key pin contacts Tool flat face at $G_{face} = 3.300\text{ mm}$.
  - Nominal early-intercept margin before ball touch: $3.300 - 3.000 = +0.300\text{ mm}$.
  - Worst-case calculated early-intercept margin: $+0.170\text{ mm} > 0$ (positive under stated prototype tolerance assumptions).

---

## 9. Docking Interface & Side Wings

- **Side Wings Geometry:** Centered at $Y = 0.000, Z = 12.000\text{ mm}$ on Tool Sleeve.
- **Total Span:** $28.000\text{ mm}$ ($X \in [-14.000, +14.000]\text{ mm}$).
- **Protrusion per Side:** $3.000\text{ mm}$ beyond sleeve body.
- **Wing Thickness & Length:** Thickness = $4.000\text{ mm}$ ($Z \in [10.000, 14.000]\text{ mm}$), Length = $16.000\text{ mm}$ ($Y \in [-8.000, +8.000]\text{ mm}$).
- **Dock Passive U-Fork:** Dual capture prongs treading into the $3.000\text{ mm}$ side wings with lead-in chamfers.
- **Auxiliary Rear Dock Magnet:** Neodymium $\phi 6.000 \times 2.000\text{ mm}$ embedded in tool spine at $(X = 0.000, Y = 0.000, Z = 23.800)\text{ mm}$, providing $\approx 4.5 - 5.5\text{ N}$ seating retention (`TARGET / TO BE VALIDATED`).

---

## 10. Quad Dock Layout

- **Dock Pitch ($P$):** $32.000\text{ mm}$ between adjacent slot centers.
- **Inter-Tool Clearance:** $32.000 - 28.000 = 4.000\text{ mm}$ free clearance between parked tools.
- **Active 4-Tool Envelope:** $(4 - 1) \times 32.000 + 28.000 = 124.000\text{ mm}$.
- **Recommended Quad Base Width:** $144.000\text{ mm}$.
- **Outer Edge Margins:** $(144.000 - 124.000)/2 = 10.000\text{ mm}$ per side.
- **Static Neighbor Approach Clearance:** $7.000\text{ mm}$ between approaching Receiver ($R_X = +11.0$) and adjacent parked tool wing ($X = +18.0$).

---

## 11. Pick / Drop Principle

### 11.1 Tool Pick Sequence
1. Carriage moves in $X$ to target slot center and approaches along Machine $+Y$.
2. Kinematic balls mate with V-grooves; magnetic preload clamps carriage to tool ($F_{preload}$ design target $18 - 22\text{ N}$, actual value `TO BE MEASURED`).
3. Carriage withdraws along Machine $-Y$.
4. **Governing Equilibrium:** $F_{carriage\_preload} > F_{dock\_retention} + F_{friction} + m_{tool}g$.

### 11.2 Tool Drop Sequence
1. Carriage advances along $+Y$ into target dock slot until Tool Side Wings seat against dock U-fork shoulders.
2. Carriage executes a controlled shear/peel separation motion along Machine $X$ or Machine $-Z$.
3. U-fork reaction force balances separation shear load: $F_{reaction\_dock} = F_{shear\_applied}$.
4. Auxiliary dock magnet retains parked tool securely in bay after carriage departs.

---

## 12. Manufacturing Targets

- **3D Printing Material:** PETG / ABS / ASA ($0.16\text{ mm}$ layer height, 4 perimeters, 40% gyroid infill).
- **Print Orientation:** Mating faces oriented UPWARD/FLAT on print bed to optimize V-groove and seat accuracy.
- **Prototype Dimensional Targets:** $\pm 0.08\text{ mm}$ on bearing seats, $\pm 0.10\text{ mm}$ on pad outlines (`TO BE VERIFIED ON PRINT COUPONS`).

---

## 13. Validation Requirements

1. **Bench Force Test:** Measure magnetic preload force vs air gap curve for 3 pairs N52 $\phi 8 \times 2\text{ mm}$ magnets.
2. **Coupling Repeatability Test:** Measure multi-cycle 6-DOF repositioning repeatability using dial test indicators.
3. **Drop Separation Shear Test:** Measure peak motor force required for shear/peel tool release.
4. **Full Swept-Volume Validation:** `PENDING Q3` 3D trajectory simulation.

---

## 14. Frozen Parameter Table

| Parameter | Specification Value | Status Category | Traceability Reference |
|---|---|---|---|
| Tool Datum A Plane | $\text{Local } Z = 4.200\text{ mm}$ | `FROZEN` | HW-DEC-004 |
| Tool Pad Envelope | $22.000 \times 48.000 \times 5.000\text{ mm}$ | `FROZEN` | HW-DEC-003 |
| Pen Bore Diameter | $\phi 12.500\text{ mm}$ | `MEASURED / FROZEN` | Q1 STL Audit |
| Tool V-Groove Profile | $90^\circ$ V, $W=4.8, D=2.4, L=5.0\text{ mm}$, Chamfer $0.2\times 45^\circ$ | `FROZEN (V1.1)` | HW-DEC-009 |
| V-Groove Centers | $V1(0, 15, 4.2), V2(-6, -12, 4.2), V3(6, -12, 4.2)\text{ mm}$ | `FROZEN` | HW-DEC-008 |
| Tool Magnets Spec | 3 × N52 $\phi 8.0 \times 2.0\text{ mm}$, recessed $0.2\text{ mm}$ | `FROZEN` | HW-DEC-005 |
| Tool Magnet Physical 3D | $M1(0, -2, 5.4), M2(-5, 6, 5.4), M3(5, 6, 5.4)\text{ mm}$ | `DERIVED` | Q2B.8 |
| Tool Side Wings Span | $28.000\text{ mm}$ (protrusion $3.000\text{ mm}$/side) | `FROZEN` | HW-DEC-007 |
| Quad Dock Pitch | $32.000\text{ mm}$ | `FROZEN` | HW-DEC-006 |
| Quad Base Width | $144.000\text{ mm}$ (edge margin $10.000\text{ mm}$/side) | `FROZEN` | Q2A.6 |
| Receiver Envelope | $22.000 \times 48.000 \times 6.000\text{ mm}$ ($R_Y \in [-6, 0]$) | `FROZEN` | Q2B |
| Receiver Datum A | $R_Y = 0.000\text{ mm}$ | `FROZEN` | Q2B.7 |
| Receiver Balls Spec | 3 × Hardened Chrome Steel $\phi 6.000\text{ mm}$ G28 | `FROZEN` | Q2B |
| Receiver Ball Centers | $B1(0, 0, -15), B2(-6, 0, 12), B3(6, 0, 12)\text{ mm}$ | `DERIVED` | Q2B.7 |
| Ball Seat Geometry | Guide $\phi 6.1$ + $90^\circ$ Cone + Rear $\phi 2.5\text{ mm}$ Channel | `FROZEN` | HW-DEC-011 |
| Ball Center Datum | Hard conical shoulder contact at $R_Y = -2.121\text{ mm} \implies R_Y = 0$ | `FROZEN` | Q2B.8 |
| Ball Protrusion | $3.000\text{ mm}$ past RECEIVER_DATUM_A | `DERIVED` | Q2B.8 |
| Nominal Face-to-Face Gap | $1.843\text{ mm}$ (Nominally clear) | `DERIVED` | Q2B.6 |
| Receiver Magnets Spec | 3 × N52 $\phi 8.0 \times 2.0\text{ mm}$, recessed $0.2\text{ mm}$ | `FROZEN` | Q2B.6 |
| Receiver Magnet Physical 3D | $M1(0, -1.2, 2), M2(-5, -1.2, -6), M3(5, -1.2, -6)\text{ mm}$ | `DERIVED` | Q2B.8 |
| Magnetic Pole Gap | $2.243\text{ mm}$ | `DERIVED` | Q2B.6 |
| Magnetic Preload Target | $18.0 - 22.0\text{ N}$ | `TARGET / TO BE VALIDATED` | Q2B.6 |
| Poka-Yoke Key Pin | $2.4 \times 2.4 \times 3.300\text{ mm}$ at $(+9.5, -22.5)\text{ mm}$ | `FROZEN` | HW-DEC-012 |
| Poka-Yoke Root Base | Edge-Tab: $R_X \in [+8.3, +11], R_Z \in [-24, -21], R_Y \in [-6, 0]$ | `FROZEN` | HW-DEC-012 |
| Worst-Case Bottom Clear. | $+0.213\text{ mm} > 0$ | `DERIVED` | Q2B.7 |
| Worst-Case Early Intercept | $+0.170\text{ mm} > 0$ | `DERIVED` | Q2B.7 |
| Z-Carriage Mount Holes | 4 × M3 on $12.0 \times 40.0\text{ mm}$ grid ($R_X=\pm 6, R_Z=\pm 20$) | `FROZEN` | Q2B |
| Static Neighbor Clearance | $7.000\text{ mm}$ | `DERIVED` | Q2B |
| Swept-Volume Status | `PENDING Q3 VALIDATION` | `TO BE VALIDATED` | Q2B.7 |
| Jacobian Model Metrics | Rank = 6, $\kappa_2(J) = 3.2306$ ($R_0 = 15\text{ mm}$) | `DERIVED` | Q2B.7 |

---

## 15. Known Risks & Mitigation

1. **FDM Surface Friction on V-Grooves:** Layer lines can create micro-ratcheting during ball seating.  
   *Mitigation:* Print with fine layer height ($0.12 - 0.16\text{ mm}$), orient grooves upwards, wet-sand with 1000-grit paper over a $\phi 6\text{ mm}$ rod.
2. **Magnetic Preload Deficit at 2.24 mm Air Gap:** If measured pull force is below target, tool may vibrate under high drawing acceleration.  
   *Mitigation:* Provision for raised magnet bosses to reduce gap to $1.0\text{ mm}$, or upgrade to thicker $\phi 8 \times 3\text{ mm}$ magnets.

---

## 16. Legacy Geometry

- **Legacy 4 × SG90 Servo Dock:** Former active docking bay concept featured cavities for four SG90 micro-servos to actuate lock pins. Formally `DEPRECATED / LEGACY` under HW-DEC-013.

---

## 17. Revision History

| Revision | Date | Author / Context | Changes |
|---|---|---|---|
| V1.0 | 2026-09-20 | Review Q2A–Q2A.7 | Frozen Pen Slider V1 interface (V-grooves $4.5\times 2.25$, Pad $22\times 48\times 5$, Datum A $Z=4.2$). |
| V1.1 | 2026-09-21 | Review Q2B.5–Q2B.8 | Updated V-grooves to $W=4.8, D=2.4, L=5.0\text{ mm}$ + $0.2\text{ mm}$ chamfer. Recomputed face gap ($1.843\text{ mm}$), magnetic gap ($2.243\text{ mm}$), Poka-Yoke pin height ($3.3\text{ mm}$) and conical shoulder ball seat. |

---

## Traceability

- **Source:** Engineering review phases Q1 through Q2B.8.
- **Decision References:** [hardware_decision_log.md](hardware_decision_log.md) (`HW-DEC-001` through `HW-DEC-013`).
