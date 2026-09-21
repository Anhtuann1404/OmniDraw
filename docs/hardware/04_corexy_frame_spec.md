# CoreXY & Frame Specification

**Subsystem:** CoreXY Motion & Base Frame  
**Document Version:** V1.0  
**Status:** SYSTEM CONCEPT BASELINE  

---

## 1. Purpose

The CoreXY Motion and Base Frame subsystem provides the structural chassis and two-degree-of-freedom ($XY$) planar positioning platform for OmniDraw Plotter V1. It translates coordinated rotary motion from two stationary stepper motors into high-speed, precise Cartesian translation of the X-axis carriage across the drawing bed and into the rear tool docking bay.

---

## 2. Frame Architecture

```
         +===================================================+
         | [NEMA 17 Motor A]               [NEMA 17 Motor B] |
         |        \                             /            |
         |         \=== [QUAD-PEN DOCK BAY] ===/             |  <-- Machine +Y (Rear / Ymax)
         |                                                   |
         |  [Y-Left Rail]                     [Y-Right Rail] |
         |       |                                  |        |
         |       |        [X-GANTRY BEAM]           |        |
         |       +==============[X]=================+        |  <-- Machine X Span
         |                       |                           |
         |                  [Carriage]                       |
         |                                                   |
         |                                                   |
         |                                                   |  <-- Active Drawing Bed (A3)
         |                                                   |
         |                                                   |
         +===================================================+
                                                                <-- Machine -Y (Front / Ymin)
```

### 2.1 Structural Members
- **Primary Extrusions:** Standard $2020\text{ mm}$ (and optional $2040\text{ mm}$ for X-gantry) V-slot or T-slot aluminum structural extrusions (`SYSTEM CONCEPT`).
- **Corner Brackets:** Die-cast aluminum corner gussets and internal hidden L-brackets for maximum joint orthogonality.
- **Base Footprint Target:** $\approx 550\text{ mm}$ (Width $X$) $\times 450\text{ mm}$ (Depth $Y$) $\times 120\text{ mm}$ (Height $Z$) (`PROPOSED CONCEPT / NOT FROZEN`).
- **Target Active Work Area:**
  - Standard A3 Landscape Drawing Area: $420.0\text{ mm} \times 297.0\text{ mm}$.
  - Tool Docking Overtravel Zone along $+Y$: Additional $+40.0\text{ mm} - +50.0\text{ mm}$ overtravel along $+Y$ to access the rear tool changer dock without compromising active paper margins (`PROPOSED / TBD`).

### 2.2 Linear Guidance
- **X-Axis (Gantry Beam):** Linear guide rail (e.g. MGN9H / MGN12H) or precision V-slot polycarbonate wheels mounted on 2020/2040 extrusion (`TBD`).
- **Y-Axes (Dual Side Rails):** Twin parallel linear rails (MGN9/12) or V-slot wheel carriages mechanically synchronized across both side extrusions (`TBD`).

---

## 3. CoreXY Motion Architecture

### 3.1 Kinematic Principle
Two stationary stepper motors (Motor A and Motor B) mounted rigidly to the rear frame corners drive two independent, closed-loop timing belts:

$$\begin{aligned}
\Delta X &= \frac{\Delta A + \Delta B}{2} \\
\Delta Y &= \frac{\Delta A - \Delta B}{2}
\end{aligned}$$

*(Note: Sign conventions depend on motor wiring polarity and pulley layout).*

- **Pure X-Motion:** Motors A and B rotate in the **same** direction with equal speed.
- **Pure Y-Motion:** Motors A and B rotate in **opposite** directions with equal speed.
- **Diagonal Motion:** One motor rotates while the other remains stationary.

### 3.2 Belt Routing & Pulleys
- **Timing Belt Spec:** GT2 timing belt, $2.000\text{ mm}$ tooth pitch, $6.000\text{ mm}$ width, fiberglass or Kevlar reinforced neoprene (`SYSTEM CONCEPT`).
- **Routing Configuration:** Stacked dual-plane belt routing (Upper Belt loop A, Lower Belt loop B) to prevent belt crossing interference.
- **Drive Pulleys:** GT2 16-tooth or 20-tooth aluminum timing pulleys mounted to motor shafts ($\phi 5\text{ mm}$ D-shaft).
- **Idler Pulleys:** Flanged smooth and toothed idler pulleys with precision dual ball bearings ($\phi 3\text{ mm} / \phi 5\text{ mm}$ axle bolts).
- **Belt Tensioning:** Integrated screw-adjustable tensioning blocks on the X-carriage belt anchors (`TBD`).
- **Target Belt Tension:** Tuned to avoid tooth skipping and minimize belt stretch (`PROPOSED RANGE 35 - 50 N / TBD`).

### 3.3 Stepper Motors
- **Frame Size:** NEMA 17 ($42 \times 42\text{ mm}$ faceplate).
- **Holding Torque Target:** $40 - 45\text{ N}\cdot\text{cm}$ holding torque (`PROPOSED STARTING RANGE / TBD`).
- **Step Angle:** $1.8^\circ$ per full step ($200\text{ steps/rev}$) with $16\times$ or $32\times$ microstepping via silent stepper drivers.

---

## 4. Preliminary Dynamic & Performance Targets

| Parameter | Proposed Target | Status | Notes |
| :--- | :--- | :--- | :--- |
| **Max Travel Speed ($v_{max}$)** | $150 - 250\text{ mm/s}$ | PROPOSED TARGET | Rapid non-drawing positioning |
| **Drawing Speed ($v_{draw}$)** | $40 - 100\text{ mm/s}$ | PROPOSED TARGET | Tuned for pen ink flow |
| **Max Acceleration ($a_{max}$)** | $1000 - 2000\text{ mm/s}^2$ | PROPOSED TARGET | S-curve acceleration profile |
| **Dock Approach Speed** | $10 - 20\text{ mm/s}$ | PROPOSED TARGET | Controlled docking engagement |
| **Belt Pitch Resolution** | $\approx 0.0125\text{ mm/microstep}$ | THEORETICAL | 16T pulley (32 mm/rev), 1/16 microstepping |
| **Frame / CoreXY Orthogonality Acceptance Criterion** | TBD Q4 ($\Delta D = |D_1 - D_2|$) | TBD / REQUIRES Q4 DESIGN REVIEW | Measured across bed corners |

---

## 5. Subsystem Interfaces

- **Carriage Interface:** The X-carriage platform mounts directly to the X-axis linear guide block and anchors both belt ends, as specified in [03_carriage_and_lifter_spec.md](03_carriage_and_lifter_spec.md).
- **Rear Dock Interface:** The stationary Quad-Pen Dock bay mounts rigidly across the rear 2020 extrusion at $Y = Y_{max}$, with interface dimensions frozen in [02_tool_changer_spec.md](02_tool_changer_spec.md).
- **Electronics & Endstops:** Mechanical microswitches or sensorless stall-detection pins interface with the main controller board as described in [05_electronics_spec.md](05_electronics_spec.md).

---

## Traceability

- **System Architecture:** [01_hardware_architecture.md](01_hardware_architecture.md)
- **Carriage & Lifter:** [03_carriage_and_lifter_spec.md](03_carriage_and_lifter_spec.md)
- **Tool Changer Dock:** [02_tool_changer_spec.md](02_tool_changer_spec.md)
- **Validation Matrix:** [06_validation_plan.md](06_validation_plan.md)
