# Hardware Architecture

**Document Version:** V1.1  
**Status:** SYSTEM CONCEPT BASELINE / PARTIAL FREEZE  

---

## 1. System Purpose

The **OmniDraw Plotter V1** is an autonomous, multi-color computer-numeric-controlled (CNC) drawing plotter designed for automated comic creation, artwork reproduction, and technical drafting. The core differentiator of the system is a **passive 4-slot Kinematic Tool Changer** mounted along the rear boundary of the machine, enabling the motion carriage to autonomously switch between four drawing pens without manual intervention or active per-slot motorization.

---

## 2. Major Subsystems

The hardware system is organized into ten distinct modular subsystems:

1. **Base Frame Subsystem:** Rigid rectangular chassis constructed from 2020 aluminum V-slot extrusions with corner gussets and leveling feet (`CONCEPT / TBD`).
2. **CoreXY XY Motion Subsystem:** Dual-motor planar motion system utilizing continuous GT2 6 mm timing belts and stationary stepper motors (`SYSTEM CONCEPT / TBD`).
3. **X Gantry Subsystem:** Lightweight transverse bridge riding on twin Y-axis linear guides, carrying the X-axis carriage (`CONCEPT / TBD`).
4. **Moving Carriage Subsystem:** X-axis carriage platform housing the Z-lifter, guide bearings, and mounting the tool interface (`ACTIVE DESIGN / Q3`).
5. **Z / Pen-Lift Compliance Subsystem:** Linear vertical guide assembly with return springs for controlled drawing compliance and pen lift (`ACTIVE DESIGN / Q3`).
6. **Carriage Receiver Plate Subsystem:** Precision interface plate mounted to the Z-carriage, carrying 3 kinematic steel balls, 3 magnets, and orientation key (`Receiver Plate V1` — `FROZEN DESIGN BASELINE`, compatible with Tool Interface V1.1).
7. **Pen Slider / Tool Sleeve Subsystem:** Interchangeable sleeve holding the pen body, featuring 3 radial V-grooves, 3 mating magnets, and dock wings (`FROZEN DESIGN BASELINE V1.1`).
8. **Quad-Pen Docking Bay Subsystem:** Stationary 4-slot dock mounted at the rear machine boundary ($Y = Y_{max}$) with passive mechanical U-forks (`FROZEN INTERFACE / DOCK DETAIL TBD`).
9. **Overhead Camera Mount Subsystem:** Fixed overhead vision bracket supporting a top-down camera for paper registration and visual inspection (`CONCEPT / TBD`).
10. **Electronics & Wiring Subsystem:** Motion controller board, stepper drivers, servo power regulation, endstops, and cable routing (`CONCEPT / TBD`).

---

## 3. Machine Coordinate System

The global machine coordinate frame $\mathcal{F}_{machine} = \{X, Y, Z\}$ is established as follows:

```
                      [Machine +Y (Rear / Dock Bay Ymax)]
                                       ^
                                       |
                                       |
        [Left]                         |                         [Right]
   Machine -X <-----------------------(0,0)-----------------------> Machine +X
                                       |
                                       |
                                       v
                      [Machine -Y (Front / User Access)]

   Machine +Z : Pointing UPWARD (away from drawing bed)
   Machine -Z : Pointing DOWNWARD (into drawing surface / paper contact)
```

### Coordinate Definitions
- **Machine $+X$ (Horizontal Right):** Transverse motion of the carriage along the X-gantry.
- **Machine $+Y$ (Depth / Rear):** Longitudinal motion of the X-gantry towards the rear docking bay ($Y = Y_{max}$).
- **Machine $+Z$ (Vertical Up):** Pen lift elevation away from the paper.
- **Machine $-Z$ (Vertical Down):** Pen descent towards the drawing surface.
- **Drawing Orientation:** When drawing, the pen is held vertically with its tip pointing in the **Machine $-Z$** direction.

### Coordinate Mapping between Tool Local and Machine Frames
In the Tool Sleeve frame $\mathcal{F}_{tool} = \{X_{tool}, Y_{tool}, Z_{tool}\}$:
- **$\text{Tool Local }+X \longrightarrow \text{Machine }+X$** (Horizontal span)
- **$\text{Tool Local }+Y \longrightarrow \text{Machine }-Z$** (Tool axis pointing downwards towards paper; Pen Tip at $+Y$)
- **$\text{Tool Local }+Z \longrightarrow \text{Machine }+Y$** (Mating face Datum A facing forward towards Carriage)

---

## 4. Mechanical Architecture

- **Chassis Structure:** Rectangular frame assembled from 2020 V-slot aluminum extrusions (`SYSTEM CONCEPT`).
- **Envelope Target:** Nominal frame footprint $\approx 550 \times 450 \times 120\text{ mm}$ (`CONCEPT TARGET / NOT FROZEN`).
- **Work Area Target:** Targeted for standard A3 paper ($420 \times 297\text{ mm}$) and comic strip panels (`TARGET / NOT YET VERIFIED`).
- **Drawing Surface:** Flat composite bed plate with hold-down fixtures (`TBD`).

---

## 5. Tool-Changer Architecture

- **Architecture Type:** **Passive Mechanical Dock + Magnetic Kinematic Coupling**.
- **Dock Location:** Stationed along the rear rail at Machine $Y = Y_{max}$, mounted upright.
- **Dock Capacity:** 4 interchangeable tool slots spaced at a frozen pitch of $P = 32.000\text{ mm}$.
- **Coupling Mechanism:** Maxwell 3 V-groove kinematic coupling providing 6-DOF constraint in the evaluated rigid-body model.
- **Preload:** 3 pairs of neodymium N52 $\phi 8 \times 2\text{ mm}$ magnets providing non-contact magnetic clamping force.
- **Separation Principle:** 
  - **Tool Pick:** Direct axial pull along Machine $-Y$ ($F_{carriage} > F_{dock\_retention} + m_{tool}g$).
  - **Tool Drop:** Mechanical U-fork captures tool wings; carriage performs a controlled shear/peel motion to release magnetic coupling.

---

## 6. Motion Architecture

- **Drive Kinematics:** CoreXY belt routing geometry driven by two stationary stepper motors located at the rear corners (`SYSTEM CONCEPT`).
- **Kinematic Equations:**
  $$\Delta X = \frac{\Delta A + \Delta B}{2}, \quad \Delta Y = \frac{\Delta A - \Delta B}{2}$$
  *(Note: Sign conventions depend on final pulley layout and motor wiring).*
- **Belt Drive:** GT2 6 mm timing belts (`SYSTEM CONCEPT`).
- **Linear Guidance:** Linear guide rails or V-slot dual-bearing wheels on all axes (`TBD`).

---

## 7. Camera Architecture

- **Mounting Style:** Overhead stationary top-down bracket mounted above the drawing bed (`CONCEPT`).
- **Function:** Workspace calibration, homing offset verification, paper boundary registration, and live inspection.
- **Field of View (FOV):** Sized to cover the active drawing area (`TBD`).

---

## 8. Electronics Architecture

- **Mainboard:** CNC motion controller candidate (ESP32-based or 8-bit CNC shield candidate) (`TBD`).
- **Motor Drivers:** Silent stepper drivers (TMC2208 / TMC2209 candidate) (`TBD`).
- **Z-Lifter Actuator:** Pen-lift actuator powered by dedicated regulated supply (`CONCEPT / TBD`).
- **Sensors:** Endstop switches on X and Y minimum boundaries for repeatable homing (`TBD`).
- **Power Supply:** Industrial DC switching power supply (`TBD`).

---

## 9. Design Assumptions

1. The Quad-Pen Dock is stationary; all tool change dynamics are executed solely by coordinated CoreXY and Z-carriage movements.
2. The pen sleeve geometry accommodates standard technical drawing pens and markers ($\phi 8.0 - \phi 12.0\text{ mm}$) clamped via an M3 screw.
3. FDM 3D printing tolerances on PETG/ABS are treated as `PROTOTYPE DIMENSIONAL TARGETS / TO BE VERIFIED ON PRINT COUPONS`.

---

## 10. Current Status

- **System Architecture Status:** `SYSTEM CONCEPT BASELINE / PARTIAL FREEZE`
- **Subsystem Breakdown:**
  - Subsystems 6 & 7 (Receiver Plate & Pen Slider): `FROZEN DESIGN BASELINE (V1.1)`
  - Subsystem 5 (Z-Carriage / Lifter): `ACTIVE DESIGN (Q3 — NOT STARTED)`
  - Subsystems 1, 2, 3, 8, 9, 10: `CONCEPT / TBD`

---

## Traceability

- **Source:** Engineering review phases Q1 through Q2B.8.
- **Related Specifications:**
  - [02_tool_changer_spec.md](02_tool_changer_spec.md)
  - [03_carriage_and_lifter_spec.md](03_carriage_and_lifter_spec.md)
  - [04_corexy_frame_spec.md](04_corexy_frame_spec.md)
