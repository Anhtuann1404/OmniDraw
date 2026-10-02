<!-- scope-migration-20261002 -->
> **Phạm vi ngày 02/10/2026:** Tài liệu hardware hỗ trợ. Nội dung thiết kế/đo/review bên dưới giữ đúng phạm vi và ngày của nó; không đồng nghĩa đã mua máy, đã hiệu chuẩn hoặc đã nghiệm thu hướng nghiên cứu mới. Nghiên cứu dùng máy vẽ phẳng hai trục khi sẵn sàng, ghi cơ cấu/bộ điều khiển/bút/giấy theo run. Concept A4 một bút là phương án tham khảo hiện tại, không yêu cầu AxiDraw/CoreXY hay nhiều màu.
> Kế hoạch hiện hành: [Docs 30](../30_research_development_plan.md); đặc tả [Docs 31](../31_joint_solver_contract.md) và [Docs 32](../32_research_api_and_artifact_contract.md). Thông báo GVHD đồng ý hướng không thay sign-off kỹ thuật hoặc duyệt tham số.

# A4 single-pen budget prototype — design rebaseline

**Status:** `CONCEPT / KIT SKU AND PHYSICAL FIT PENDING`  
**Decision date:** 2026-09-30  
**Priority:** research handwriting prototype, not a released print or purchase pack.

## Scope and authority

The budget-constrained first prototype is **A4 landscape, one pen, one lift
servo**. It is meant to validate Vietnamese handwriting paths, pen-up moves,
diacritic placement and physical calibration. Four-color Q4D, passive dock Q2,
tool-change cycles, A3 CoreXY and the old Q1–Q3 tool interface are not part of
this prototype. Their files remain historical/optional; do not scale them down
or order parts from their BOM. This is a new branch of hardware intent, not a
claim that Q1–Q3 frozen geometry has been changed.

The user's quoted `DIY A4 full kit` is **not yet an identified product/SKU**.
Therefore `cad/a4_single_pen_reference.py` and its STEP export depict a
provisional packaging envelope, not the purchased kit. No V-wheel pitch,
extrusion slot standard, motor shaft, servo horn, controller pin or mounting
hole pattern has been verified.

## Useful ideas retained from the earlier work

- Keep millimeters and an explicit paper-top Z=0 datum; machine +X right and
  +Y rear. Calibrate paper origin, steps/mm, X/Y squareness and pen contact.
- Use a single removable pen clamp/liner concept, but measure the selected
  ordinary pen's straight barrel, clip, tip-to-clamp distance and actual
  insertion force before cutting the clamp or printing a final part.
- Preserve mechanical endstops, software travel limits, an accessible power
  switch and safe pen-up homing. No sensorless homing or unmeasured clearance
  claim is carried over.
- Retain the existing software SVG/metrics and physical calibration protocol;
  only map the output into a qualified A4 reachable field.

## Provisional coordinate and geometry budget

| Datum | Candidate value | Meaning |
| --- | ---: | --- |
| Outer 2020 frame | 400 × 320 mm | Study envelope, not a vendor-kit size |
| Nominal extrusion cut list | 2 × 320 + 3 × 360 = 1,720 mm | Includes a 360 mm X gantry; cutting allowance extra |
| A4 paper | 297 × 210 mm | Landscape, centered in study model |
| Paper margin | 10 mm per edge | Target draw rectangle 277 × 190 mm |
| Drawing field | X=−138.5…+138.5, Y=−95…+95 mm | Paper-centered coordinates; transform to machine home after calibration |
| Head | 1 pen + 1 servo | Exact barrel, nib, horn and linkage are pending measurement |

The source model has named proxy occurrences for the frame, bed, paper,
gantry, carriage, servo, clamp and pen. Its pen is shown in a visual *down*
pose only. Its lift stroke, true nib contact, fastening, cable routing, wheel
geometry, belt path and endstop activation are **not verified by the STEP**.
The analytical test checks only that the nominal drawing rectangle fits the
proxy frame and leaves nominal head/gantry box-envelope margins. It cannot
qualify a purchasable kit.

`cad/a4_single_pen_detailed_review.py` is a separate **visual assembly study**
for easier whole-machine inspection. It adds visible slotted 2020 profiles,
V-wheel/bearing/axle proxies, two motor/shaft/pulley packages, front idler
proxies, A4 platen and clips, guide/slider/split-clamp/servo-horn components,
endstop bodies, and controller/power packaging. These are individually named
STEP occurrences, not sourced or dimensionally qualified purchased parts.
The belt route is intentionally absent: the kit drive topology and pulley
heights have not been identified. No appearance in this review STEP is proof
of actual wheel engagement, fastening, servo lift, travel, electrical wiring,
or collision-free motion. Do not print/order directly from this file.

## Target minimal electrical stack

- Two NEMA17 steppers, each with its own compatible driver; one lift servo.
- Arduino Uno + CNC Shield V3 + two A4988 are **budget candidates**, not a
  validated firmware/controller stack. Standard GRBL servo behavior and the
  chosen shield's available control pin must be proven on the bench before
  wiring or purchase freeze.
- A 12 V supply may feed the stepper board **only if** motor/driver current
  budgets pass. The servo needs a regulated 5 V rail with shared signal ground;
  do not power its stall current through an Arduino I/O pin or assume USB 5 V
  is sufficient. Add buck converter, fuse/switch, connectors and flexible
  cable to the quote; these were missing from the initial 1.35–1.45 m VND list.
- Two normally closed X/Y endstops are the minimum homing target. FSR402 and
  camera are optional research add-ons, not prerequisites for one-pen writing.

## Purchase and release gates

1. Obtain the **exact kit link, seller BOM and mechanical drawings/photos**:
   outer rail cuts, V-wheel spacing, X/Y usable travel, motor model/shaft,
   belt width and pulley bore, gantry/carriage mounting pattern, and supplied
   board/driver/PSU. Compare actual contents with the user's 14-line estimate;
   do not double-count an already-inclusive full kit.
2. Buy or borrow **one ordinary pen and one lift servo**. Measure barrel,
   clip, nib and servo body/ears/shaft/horn; choose one combination and create
   a small clamp test coupon before printing the final moving head.
3. Revise the STEP from measured kit interfaces; check the one-pen head at
   home and all four A4 drawing corners, wheel/belt/endstop clearance, cable
   flex, screw access and pen-up/down against actual paper thickness.
4. Bench-check driver current, 5 V servo rail under stall, servo control
   command, emergency stop and NC endstop behavior. Then run the existing
   [physical calibration protocol](07_physical_calibration_protocol.md).

**Release verdict:** `NEEDS KIT DIMENSIONS AND PHYSICAL FIT`. The reference
STEP is suitable for layout discussion only, not printing or buying a final
mechanical set.

## Cartesian belt-drive candidate (2026-09-30)

The user confirmed a fixed A4 sheet, moving Y crossbeam, X pen carriage,
independent X/Y steppers, and hand repositioning only with power off. The new
`cad/a4_cartesian_belt_study.py` and its STEP are an **alternative concept**
to the simple visual model; they are not an order list or a kit retrofit.

- One stationary Y stepper turns a rear cross-shaft on **two frame-mounted
  bearings**. Equal 20T pitch-reference pulleys on the same shaft drive one
  GT2 belt on each Y side. Each belt is clamped to its respective gantry end.
  The shaft and these pulleys rotate about **X**; the two Y belts run in
  **vertical YZ planes**, outside the ends of the X beam and above the Y end
  plates. This mechanically links left and right Y travel
  without a third stepper. An earlier sketch with horizontal XY Y-belts and
  a transverse shaft had mismatched axes and was rejected; do not use it as
  fabrication geometry.
- One X stepper rides on the **front/outboard left** of the gantry and drives
  a separate X belt; the belt is clamped to the pen carriage. This placement
  replaces an earlier rear-of-beam pose that would hit the fixed Y cross-shaft
  near the rear A4 writing limit. Green in the STEP is X, reddish is Y. Belts
  show pitch-centre ribbons and half-wraps, not actual teeth or stock width.
- Compared with the earlier 400 × 320 mm visual envelope, the candidate uses
  **400 × 360 mm** outer frame and places the A4 platen **40 mm forward**.
  This is necessary because the current pen tip is 54 mm ahead of the gantry:
  the intended 190 mm active Y field requires gantry centres from −81 to
  +109 mm. On the nominal 360 mm Y rails, a 40 mm deep end plate still has
  51 mm geometric rail-end margin at +109 mm. This does **not** prove wheel
  support, belt-clamp clearance, or real usable travel.
- At 2 mm nominal GT2 pitch, a 20T pulley has pitch radius 6.366 mm. The
  illustrated Y pulley-centre separation is 310 mm, X is 385 mm. Geometric
  loop-centre lengths are about 660 mm per Y side and 810 mm for X; these are
  **not cutting lengths** because clamp return, adjustment and stock
  selection are unknown. Three open-ended belts with independently adjustable
  idlers are the proposed sourcing form.
- X/Y switch and padded hard-stop bodies are illustrated separately. Their
  locations are nominal; actuator levers, elastic compression and braking
  distance need physical checks before claiming switch-first/stop-second.

In the latest candidate, the nominal X carriage-plate to Y end-plate side
gap at the ±138.5 mm writing limit is **4 mm**; the rear-most X motor body is
at least **58 mm** ahead of the fixed rear shaft's nominal envelope. The
saved-STEP checks also verify straight belt runs terminate at their pulley
pitch centres and that the Y pulley axes match the cross-shaft. These are
bounding-envelope checks, not proof of full 3D
collision clearance at every moving pose. The outboard X motor makes the
overall machine wider than its 400 mm extrusion frame; the outboard Y motor
extends the nominal envelope to roughly X=−261 mm, while the right idler
mount extends to about X=+204 mm. Leave desk and cable-loop space beyond
the frame.

### Supplied dimension images: provisional fit revision

The supplied dimension images have no traceable seller SKU, revision or
manufacturer source. They specify a
24.0 mm OD, 10.2 mm wide V-wheel with a 625ZZ 5 × 16 × 5 mm bearing, and a
6 mm-bore KP06 with a 55 × 13 mm mounting foot, 42 mm bolt pitch, 15 mm
base-to-shaft centre height and 29 mm total height. The visual wheel and
rear bearing envelopes now use these numbers. Their V-grooves, wheel-rail
contact, fastener heads and eccentric adjustment are **not** modeled or
qualified. The assembly currently shows eight wheels (four X, four Y), not
the proposed order quantity of twelve; four extras have no validated
mounting positions.
The wheel image labels its groove-root diameter as **22 mm**, whereas the
earlier supplied text said **19 mm**. Do not machine or freeze the V-contact
geometry from these conflicting values. The image also shows a 5 mm-thick
625ZZ bearing in a 10.2 mm-wide wheel but does not establish the final
bearing/spacer stack or whether one or two bearings are supplied per wheel.

The KP06 foot would intrude into the previous rear A4 gantry pose. To keep
the proposed 360 mm Y rails, the platen centre moved from Y=−20 to Y=−40 mm.
For the 190 mm active Y field, nominal gantry centres are now −81 to +109 mm.
At the rear active pose the Y end plate ends at Y=+129 mm; the bearing foot
starts at Y=+137.5 mm, giving 8.5 mm nominal separation. The rear hard stop
was moved to Y=+134 mm and the front stop/home switch were moved forward.
Switch lever compression and the actual stop-contact order remain unverified.

The Y shaft candidate is **400 mm long**, offset 4.5 mm left: X=−204.5 to
+195.5 mm. The supplied pulley drawing shows a 9 mm total axial width with
7 mm usable belt groove and 16 mm flange OD. The modeled shaft extends
10 mm before the left pulley face and only 1 mm beyond the right pulley
face. The supplied 25 mm coupler drawing shows 10 mm bores from each end
with a 5 mm central web. The model places both shaft ends 0.5 mm short of
that web, for 9.5 mm nominal insertion each; the coupler's right face is
only 0.5 mm from the left pulley face. These gaps are **too small to
release for purchase** without an actual tolerance stack, set-screw/hub
positions and axial-retention strategy. A 360 mm shaft is definitely too
short for pulley centres at X=±190 mm.

**Why this is still conditional:** the two-motor idea needs a straight
supported cross-shaft, two bearings, coupler, two identical Y drive pulleys,
two front idlers, and a moving X motor cable loop. These extra parts may make
it more expensive than a three-motor dual-Y kit. If the selected low-budget
kit already provides its own motion system, prefer its proven geometry over
fabricating this candidate. Measure the kit and quote the extra parts before
freezing the architecture. The servo/control issue from the previous section
remains open.

Operating rule: manually move with power off only gently and with the pen up;
home again before executing a drawing. GRBL's homing establishes machine
position after power-up, and its work offset should locate the paper corner.
Do not rely on a hand-set approximate corner as the machine coordinate origin.

Reference comparisons (not endorsement or dimensional inputs): Inventables'
[X-Carve belt assembly](https://x-carve-instructions.inventables.com/xcarve2015/step06/)
shows separate open-ended belt runs and mechanical clamps; its
[Y-motor assembly](https://x-carve-instructions.inventables.com/500mm/step2a/5motors/)
uses two Y motors rather than the single-motor cross-shaft proposed here.
[GRBL settings](https://github.com/gnea/grbl/blob/master/doc/markdown/settings.md)
explain homing and machine position after power-up. These examples support
the design trade-off, not a claim that the candidate has been built or tested.
