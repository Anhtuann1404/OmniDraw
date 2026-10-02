<!-- scope-migration-20261002 -->
> **Phạm vi ngày 02/10/2026:** Tài liệu hardware hỗ trợ. Nội dung thiết kế/đo/review bên dưới giữ đúng phạm vi và ngày của nó; không đồng nghĩa đã mua máy, đã hiệu chuẩn hoặc đã nghiệm thu hướng nghiên cứu mới. Nghiên cứu dùng máy vẽ phẳng hai trục khi sẵn sàng, ghi cơ cấu/bộ điều khiển/bút/giấy theo run. Concept A4 một bút là phương án tham khảo hiện tại, không yêu cầu AxiDraw/CoreXY hay nhiều màu.
> Kế hoạch hiện hành: [Docs 30](../30_research_development_plan.md); đặc tả [Docs 31](../31_joint_solver_contract.md) và [Docs 32](../32_research_api_and_artifact_contract.md). Thông báo GVHD đồng ý hướng không thay sign-off kỹ thuật hoặc duyệt tham số.

# Hardware Source-of-Truth Index

**Project:** OmniDraw Plotter V1  
**Directory:** `docs/hardware/`
**Current Baseline:** A4 single-pen budget prototype is the active research direction; Q1–Q4C and Q4D four-pen CAD are retained as historical/optional studies, not fabrication releases
**Last Updated:** 2026-09-30

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
| [03_carriage_and_lifter_spec.md](03_carriage_and_lifter_spec.md) | **Carriage & Z-Lifter Specification** | Q3 DESIGN FROZEN / PHYSICAL VALIDATION PENDING | X-Carriage assembly, Z-axis compliance, pen lift mechanism |
| [04_corexy_frame_spec.md](04_corexy_frame_spec.md) | **CoreXY & Frame Specification** | Q4C.3 PROVISIONAL / NO FINAL FREEZE | 2020 extrusion chassis, CoreXY belt routing, gantry mechanics |
| [05_electronics_spec.md](05_electronics_spec.md) | **Electronics Specification** | SYSTEM CONCEPT / TBD | Controller candidate, stepper drivers, power regulation, wiring |
| [06_validation_plan.md](06_validation_plan.md) | **Hardware Validation Plan** | PROPOSED VALIDATION PLAN / TBD | Experimental test procedures, validation matrices, target criteria |
| [07_physical_calibration_protocol.md](07_physical_calibration_protocol.md) | **Physical Calibration Protocol** | ACTIVE BASELINE PROTOCOL | RQ3 physical calibration, ink bleed, clearance ladder, telemetry |
| [08_four_servo_head_rebaseline.md](08_four_servo_head_rebaseline.md) | **Four-Pen/Four-Servo Head Rebaseline** | USER-DIRECTED CANDIDATE / NO FABRICATION RELEASE | Current intended moving-head architecture, STL measurements, fit blockers and release gates |
| [09_modular_pen_adapter_study.md](09_modular_pen_adapter_study.md) | **Modular Pen Adapter Study** | FIT STUDY / NOT PRINT-READY | Replaceable liners, example pen envelopes, nominal clearances and physical-fit gates |
| [10_a4_single_pen_budget_rebaseline.md](10_a4_single_pen_budget_rebaseline.md) | **A4 Single-Pen Budget Rebaseline** | ACTIVE DIRECTION / KIT FIT PENDING | One-pen study model, minimal electrical stack, purchase and validation gates |
| [hardware_decision_log.md](hardware_decision_log.md) | **Hardware Decision Log** | ACTIVE | Architectural decisions, interface freeze history, change rationale |

---

## 3. Status Definitions

To maintain absolute clarity between frozen geometry and active/unreviewed design domains, all specifications adhere to the following status tiers:

- **`FROZEN DESIGN BASELINE`**: The component interface has undergone complete mathematical consistency verification, clearance checks, and engineering freeze review. Any modification requires an explicit entry in `hardware_decision_log.md` and a version bump.
- **`Q3 DESIGN FROZEN / PHYSICAL VALIDATION PENDING`**: Q3 CAD geometry is frozen; its physical performance claims still require prototype tests.
- **`SYSTEM CONCEPT BASELINE`**: Architectural concepts and structural layouts established at the system level. Specific numerical dimensions and performance ratings are design targets awaiting detailed modeling.
- **`PROPOSED / TBD`**: Engineering values, component selections, or test thresholds that serve as starting points but require formal vendor datasheet verification or bench testing.

---

## 4. Documentation Revision Rules

1. **Relative Links Only**: All intra-documentation cross-references must use clean relative Markdown links (e.g., `[Tool Changer Spec](02_tool_changer_spec.md)`). No absolute file system paths.
2. **Interface Preservation**: Subsystems marked `FROZEN DESIGN BASELINE` (specifically Tool Changer V1.1 and Receiver Plate V1) cannot have their feature coordinates, datum references, or mating clearances altered without formal change approval.
3. **Traceability**: Every major engineering choice, geometry correction, and interface adjustment must be documented in `hardware_decision_log.md`.
4. **Empirical Honesty**: Unmeasured performance claims (e.g., repeatability, retention force, runout) must be labeled `DESIGN TARGET / TO BE EXPERIMENTALLY VALIDATED`.
