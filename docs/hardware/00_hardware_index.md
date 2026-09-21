# Hardware Source-of-Truth Index

**Project:** OmniDraw Plotter V1  
**Directory:** `OmniDraw/docs/hardware/`  
**Current Baseline:** V1.1  
**Last Updated:** 2026-09-21  

---

## 1. Purpose

This directory serves as the definitive **Hardware Source-of-Truth** for the OmniDraw Plotter V1 project. All mechanical interfaces, coordinate systems, kinematic parameters, and system specifications that have been analyzed, peer-reviewed, and mathematically verified are documented here.

From phase Q3 onward, all hardware modifications, additions, and architectural decisions must be committed directly to this documentation structure.

---

## 2. Document Master Table

| Document | Title | Status | Scope |
| :--- | :--- | :--- | :--- |
| [00_hardware_index.md](00_hardware_index.md) | **Hardware Index** | ACTIVE | Master index, status tracking, documentation rules |
| [01_hardware_architecture.md](01_hardware_architecture.md) | **Hardware Architecture** | SYSTEM CONCEPT BASELINE / PARTIAL FREEZE | Global system overview, machine coordinate frame, subsystem list |
| [02_tool_changer_spec.md](02_tool_changer_spec.md) | **Tool Changer Specification** | FROZEN DESIGN BASELINE (V1.1) | Pen Slider V1.1, Receiver Plate V1, Kinematic Coupling, Poka-Yoke |
| [03_carriage_and_lifter_spec.md](03_carriage_and_lifter_spec.md) | **Carriage & Z-Lifter Specification** | ACTIVE DESIGN (Q3 — NOT STARTED) | X-Carriage assembly, Z-axis compliance, pen lift mechanism |
| [04_corexy_frame_spec.md](04_corexy_frame_spec.md) | **CoreXY & Frame Specification** | SYSTEM CONCEPT BASELINE | 2020 extrusion chassis, CoreXY belt routing, gantry mechanics |
| [05_electronics_spec.md](05_electronics_spec.md) | **Electronics Specification** | SYSTEM CONCEPT / TBD | Controller candidate, stepper drivers, power regulation, wiring |
| [06_validation_plan.md](06_validation_plan.md) | **Hardware Validation Plan** | PROPOSED VALIDATION PLAN / TBD | Experimental test procedures, validation matrices, target criteria |
| [hardware_decision_log.md](hardware_decision_log.md) | **Hardware Decision Log** | ACTIVE | Architectural decisions, interface freeze history, change rationale |

---

## 3. Status Definitions

To maintain absolute clarity between frozen geometry and active/unreviewed design domains, all specifications adhere to the following status tiers:

- **`FROZEN DESIGN BASELINE`**: The component interface has undergone complete mathematical consistency verification, clearance checks, and engineering freeze review. Any modification requires an explicit entry in `hardware_decision_log.md` and a version bump.
- **`ACTIVE DESIGN (Q3 — NOT STARTED)`**: The subsystem is currently scheduled for engineering design and mathematical formalization. Parameter ranges are provisional and subject to change.
- **`SYSTEM CONCEPT BASELINE`**: Architectural concepts and structural layouts established at the system level. Specific numerical dimensions and performance ratings are design targets awaiting detailed modeling.
- **`PROPOSED / TBD`**: Engineering values, component selections, or test thresholds that serve as starting points but require formal vendor datasheet verification or bench testing.

---

## 4. Documentation Revision Rules

1. **Relative Links Only**: All intra-documentation cross-references must use clean relative Markdown links (e.g., `[Tool Changer Spec](02_tool_changer_spec.md)`). No absolute file system paths.
2. **Interface Preservation**: Subsystems marked `FROZEN DESIGN BASELINE` (specifically Tool Changer V1.1 and Receiver Plate V1) cannot have their feature coordinates, datum references, or mating clearances altered without formal change approval.
3. **Traceability**: Every major engineering choice, geometry correction, and interface adjustment must be documented in `hardware_decision_log.md`.
4. **Empirical Honesty**: Unmeasured performance claims (e.g., repeatability, retention force, runout) must be labeled `DESIGN TARGET / TO BE EXPERIMENTALLY VALIDATED`.
