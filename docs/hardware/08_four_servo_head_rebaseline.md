<!-- scope-migration-20261002 -->
> **Phạm vi ngày 02/10/2026:** Tài liệu hardware hỗ trợ. Nội dung thiết kế/đo/review bên dưới giữ đúng phạm vi và ngày của nó; không đồng nghĩa đã mua máy, đã hiệu chuẩn hoặc đã nghiệm thu hướng nghiên cứu mới. Nghiên cứu dùng máy vẽ phẳng hai trục khi sẵn sàng, ghi cơ cấu/bộ điều khiển/bút/giấy theo run. Concept A4 một bút là phương án tham khảo hiện tại, không yêu cầu AxiDraw/CoreXY hay nhiều màu.
> Kế hoạch hiện hành: [Docs 30](../30_research_development_plan.md); đặc tả [Docs 31](../31_joint_solver_contract.md) và [Docs 32](../32_research_api_and_artifact_contract.md). Thông báo GVHD đồng ý hướng không thay sign-off kỹ thuật hoặc duyệt tham số.

# Q4D four-pen / four-servo moving head — architecture rebaseline

**Status:** USER-DIRECTED ARCHITECTURE / PARAMETRIC REFERENCE ONLY / **NO FABRICATION RELEASE**  
**Date:** 2026-09-27  
**Units:** mm

## 1. Intended operating principle

All four pens travel with the X/Y carriage. Each pen has its own servo and
slider. Selecting a color means first raising every pen, then lowering only
the selected pen; the three other pens remain parked. The drawing controller
applies that pen's calibrated XY nib offset to the commanded path. There is no
rear tool pickup/drop-off in this architecture.

This is a change from the stationary passive four-slot dock and one-servo Q3
head documented in the historical Q1–Q4C records. Those files and STEP exports
are retained as historical evidence, **not** accepted as the Q4D machine head.
The Q4C.4 passive dock prototype is likewise retired from the intended Q4D
integration path, not deleted.

## 2. Evidence extracted from the only surviving legacy CAD

The archived `hardware_3d/omnidraw_quad_pen_assembly_full.stl` is a mesh, not
parametric manufacturing source. The original editable CAD is no longer
available, so Q4D must be reconstructed from measured mesh geometry and
actual purchased parts. Connected triangle components give:

| Feature | Measured mesh evidence | Design status |
| --- | --- | --- |
| Whole assembly envelope | X −55..55, Y −55..55, Z −18..27 | STL bounding box only |
| Four pen/slider X axes | −36, −12, +12, +36; 24 pitch | Measured reference |
| Moving sliders | 4 distinct bodies, each 17 wide × 48 long | Measured reference |
| Sample pose | First slider Y center 0; other three Y center +10 | One-active, 10 travel reference |
| Servo bodies | 4 distinct housing meshes aligned with the four X axes | Packaging evidence, not torque proof |
| Pen tubes | 4 separate tube meshes | Nib tips/ink contact not specified |

The 10 mm sample-pose difference is in **local STL Y**. Under the candidate
head orientation used in the frame concept, local Y becomes machine Z, so it
represents a raised/lowered slider state, **not** a permanent machine-Y offset
between pens. The crown/slider X axes are likewise provisional proxies for
the nib X axes, not four measured nib-contact positions.

`cad/q4d_four_pen_reference.py` rebuilds those envelopes and the sample pose
as editable STEP solids. Its plate holes, cylindrical bores and servo shaft
caps are **simplified proxies**, not a copied printable base. The model does
not establish servo-horn geometry, actual pen tip height, fasteners, material,
motor torque, print tolerances, or four-color calibration.
For example, its deliberately simple servo-cap and pen-tube proxy solids
intersect by about 89 mm³ in one bay. This is a proxy-model conflict requiring
actual servo, linkage and pen geometry; it is **not** a cleared part interface.

`cad/q4d_frame_head_concept.py` additionally places that head at the nominal
Q4 gantry position in a separate view-only frame STEP. It proposes moving
the two Y rails 28 mm forward, trimming 5.5 mm from the right bracket's inner
plate edge, and moving the straight cable corridors behind the head. These
candidate parts clear all four one-active simplified head states at nine
sampled XY poses; the schematic cable corridors also avoid the modeled fixed
frame, motors and front idler mounts at those poses. However, the
model includes only a Q4D head-mount **space claim**, not a qualified joint;
real chain links/bend, endstops, belts and a real nib remain absent. It is not the
old `Q4C_FULL_ASSEMBLY.step` and must not be presented as a working machine.

### Head-to-X-block mounting audit (2026-09-27)

`cad/q4d_mount_interface_audit.py` measures the largest connected legacy-STL
plate component rather than copying the simplified STEP proxy. Its bottom
surface contains 13 visible circular edge loops (three at local Y=−11,
two at Y=+31, and eight near the four pen axes). A circular edge in a mesh
does not by itself certify a through-hole, thread, load rating or print
tolerance. None of their measured X-column pairs has the nominal **20 mm**
transverse pitch of the MGN12H four-hole pattern. The old head therefore
cannot be represented as directly bolting to that block.

At the earlier Y+50 placement, the X-block front face was 17 mm from the
original STL plate's rear face and **21 mm** from the thinner STEP proxy. A
6-mm backplate there collided with the head's slider proxies. The revised
Y+58 placement gives **25 mm** to the STL plate and **29 mm** to the proxy.
Both require a newly designed, load-bearing Q4D adapter; the proxy STEP is unsuitable as an
adapter drilling template. The nominal MGN12H 20 × 20 mm four-M3 hole pattern
comes from the [HIWIN MGN series catalog](https://www.hiwin.com/wp-content/uploads/Linear_Guideway-E-2.pdf),
not from the legacy mesh. A generic catalog STEP has the nominal pitch but an
apparently offset pattern datum, so its raw coordinate origin is not a
manufacturing datum. The head-side mounting points, fastener access,
cantilever stiffness and crash clearance must be determined in the new
parametric base before an adapter can be released.

`cad/q4d_xblock_head_mount_concept.py` now defines a separate, one-solid
layout bracket. Its rear face starts at the nominal X-block front (Y+23),
with four Ø3.4 clearance bores on the MGN12H 20 × 20 pattern. Two 4-mm-wide
struts use the narrow nominal inter-slider corridors at X±24. The forward
U-frame touches the simplified base at Y+52, with four **proposed new-base**
holes at X±50, Z35/95; these holes do **not** exist as a verified pattern in
the legacy STL. The **1.5-mm nominal lateral gap** from strut to each idealized
slider is a proxy result, not a verified manufacturing tolerance. FDM tolerance, flex, fastener
head/tool access, vibration and a measured load path are open design gates.
The STEP is a fit-study part, **not an STL to print**.

## 3. Frame fit and coordinate budget

For the existing Q4C active X range 15..435, the ±36 pen offsets require the
carriage center to travel **−21..471**. The existing 670-long X rail supports
its MGN12H block over this range with nominal 66.3 rail-end margin on each
side; this is a necessary packaging check, not proof of belt/endstop safety.
The legacy purchasing-list suggestion of a 550 mm X rail would leave only
**6.3 mm per end**, if precisely centered on the required block sweep. This is
below the Q4D **provisional 20 mm end-reserve design target** and is rejected
for the present layout. The 670 mm rail and associated 760 mm outer-X frame
from the current parametric Q4C candidate remain the Q4D packaging baseline;
neither is a cut-list or purchase release yet. The older 640 mm frame/580 mm
gantry/550 mm X-rail combination is not mixed into this CAD revision.

For a calibrated nib offset `(dx_i, dy_i)` relative to the carriage datum,
the geometric command is `(X_carriage, Y_carriage) =
(X_drawing - dx_i, Y_drawing - dy_i)`. Only the four X offsets
`(-36, -12, +12, +36)` have a mesh-based center reference. Each real nib's
X/Y offset and its raised/contact Z positions still require calibration. The
arithmetic is checked in `cad/q4d_kinematic_budget.py`; it does **not** issue
firmware commands.

A provisional head placement maps local +Y upward, local +Z toward machine
front, and places the head datum at gantry Y+58. It makes the full head
envelope just clear the X rail, belt lane and X block in nine sampled poses.
Using the pen-tube center at local Z=14.5 as a **surrogate** for the nib Y datum
gives nib Y = gantry Y +43.5 and requires gantry Y **−28.5..268.5** for the
existing 15..312 active Y range. The front Y blocks then overrun their current
rails by **21.2**. The actual nib datum remains unmeasured; this placement must
be recalculated after fitting real pens.

At the same nine sampled poses, the **old** straight X cable-chain corridor
intersects the simplified four-pen head by **1020 mm³**. At X=471, the
old right gantry bracket can intersect the outer slider in the earlier Y+50
placement. The left
bracket only intersects the conservative enclosing cuboid, not the simplified
individual solids. A Q4D candidate 28 mm frontward rail shift leaves **6.8 mm**
front block margin; the separate 5.5 mm right-bracket edge relief and rearward
straight cable corridors eliminate positive-volume head collisions in the
same nine simplified XY poses with all four one-active states. A further
25 × 9 = **225-pose** XY grid also reports no positive-volume reference-proxy
intersection with the proposed right bracket, mount space claim or straight cable corridors in
any of the four one-active states. These are packaging **candidates**, not claims
that the original STL meshes were collision-tested. Bracket strength,
fastener access, articulated chain reach/bend and endstop relocation remain
unproven.

## 3.1 Controls and mass: provisional, not frozen

> **2026-09-28 integration correction:** The newer modular head uses a gantry-to-head
> datum of +68 mm, not the earlier +58 mm layout discussed above. Its proxy
> nib axis is therefore at gantry Y+53.5 mm. To cover the nominal drawing
> Y=15..312 mm, the gantry would need Y=−38.5..258.5 mm. With the current
> 450 mm Y rail at −30..420 mm, the front MGN12H block edge overruns the rail
> by 31.2 mm; the earlier proposed 28 mm forward shift still overruns it by
> 3.2 mm. A 52 mm forward shift would leave a provisional 20.8 mm front
> reserve, but **is not approved** until front idler/bracket, endstop, frame
> fastening, cable and belt clearances are audited at the whole active range.
> These values describe the mock nib datum only; a purchased pen may change it.
>
> **Layout candidate, not release:** Keep the nominal 15..312 mm drawing
> coordinates but place the physical A3 work area 22 mm farther rearward
> (machine Y=37..334 mm), moving the 330 mm-deep bed reference by the same
> amount. The candidate coordinate rule is
> `Y_machine = Y_drawing + 22 − Y_nib_calibrated`; the 22 mm is **not** a
> measured nib offset or an installed firmware setting. Move both 450 mm Y
> rails 30 mm forward to Y=−60..390 mm. The mock
> nib then needs gantry Y=−16.5..280.5 mm, giving calculated MGN12H
> front/rear rail-edge reserves of 20.8/86.8 mm. A B-Rep spot-check at the
> frontmost gantry pose found zero overlap with the front-left idler bracket
> for the left gantry bracket and Y block; the earlier unshifted work area at
> gantry Y=−38.5 mm overlapped them by 1267/125.4 mm³. This is a packaging
> candidate only: dense XY sweep, belt anchors, homing switch locations,
> cable chain and actual pen nib calibration are not yet closed.
>
> The outboard X-block yoke now includes **provisional A/B belt landing
> solids** at X=carriage±20 mm, A at Y=gantry+15/Z=50 mm and B at
> Y=gantry−15/Z=40 mm. The B landing wraps above the 2040 beam with only
> 1 mm nominal clearance to both the beam top and gantry end-bracket plate.
> In the nominal CAD pose both Q4C belt references contact the yoke, while
> other head components remain clear; the yoke stays one solid and clears the
> beam/end brackets at three sampled X positions. These are **not belt
> clamps**: tooth engagement, actual 6 mm belt capture, fastener access,
> 7 mm tensioner stroke, load capacity and moving-belt path are unverified.
>
> A candidate Y homing switch/mount relocation places the trip at gantry
> Y=−18.5 mm, 2 mm before the proposed active front edge. The Q4C switch
> lever proxy has 17.6 mm³ intentional overlap with the moving trigger at
> home and zero overlap at the active front edge; the home gantry bracket
> clears the front-left idler mount. Switch actuation force, overtravel,
> electrical NC wiring and actual stopping distance are not verified. The
> Q4D X trigger remains **absent**, so neither axis has a released homing
> system.

The legacy one-servo/dock mass estimate of 333 g is **not** a Q4D moving-mass
measurement. The proposed 120 g printed head + four 13.4 g servos + four 12 g
pens sum to 221.6 g before X block/rail adapter, sliders, fasteners and cable
load. Therefore neither a 380–430 g Q4D total nor a 2000–2500 mm/s² safe
acceleration can be established from the current files. We will weigh the
assembled carriage and tune acceleration with step-loss and vibration tests.

Tool selection is a controller-level state transition, not a bare `T0`–`T3`
or `G10 L2 P1` line. `G10 L2 P1` edits a work-coordinate offset and repeated
use of `P1` overwrites that same system; it does not raise or lower servos.
The required sequence is: stop XY motion; raise all four pens; confirm an
up/settling interval; apply the calibrated selected-nib XY transform; move
the carriage to the new compensated position while all pens are up; lower
exactly one pen. On reset or loss of command, the controller must enter an
all-up/inhibited-drawing state. Whether the selected firmware and controller
can drive four independent servo channels, directly or through an I²C driver,
remains an integration test; no pinout or working G-code macro is claimed.
`cad/q4d_color_change_contract.py` expresses this order as pure actions so it
can be checked before firmware integration; the action list is not a working
machine driver and cannot by itself confirm servo position.

## 3.2 Procurement-design baseline for the next CAD iteration

- **Four identical genuine TowerPro MG90S digital servos (design selection).** The manufacturer's
  [product specification](https://towerpro.com.tw/product/mg90s-3/) lists
  22.8 × 12.2 × 28.5 mm body dimensions and 13.4 g mass. Specify the
  manufacturer's branded product from an authorized seller; an unbranded
  "MG90S compatible" unit is not an interchangeable purchasing item. The current legacy
  SG90 mesh cannot be substituted as a dimensionally verified MG90S model;
  the published body envelope alone does not locate the shaft, mounting ears,
  horn sweep or cable exit. These interfaces must remain adjustable or be
  confirmed from a dimensioned manufacturer drawing and delivered units.
- **Four Zebra Sarasa Clip 0.5 pens, JJ15 family (design selection).** The manufacturer's
  [product information](https://www.zebra.co.jp/pro/detail/sarasa-clip/)
  lists nominal barrel diameter 11.0 mm, overall length 141.0 mm and mass
  10.9 g for the 0.5 mm version; `JJ15-10C-N` is the published black-ink
  variant, while other ink colors need their own verified suffix. A diameter does not locate the actual nib
  relative to the clamp, and the pen clip/retracting button may need a
  clearance pocket. Keep pen retention adjustable until sample fit is tested.
- **One genuine HIWIN MGN12H standard (not MGN12H-0) carriage on a matching
  MGN12 rail, 670 mm long, for the X axis (design selection).** The
  [HIWIN dimension table](https://www.hiwin.com/wp-content/uploads/Linear_Guideway-E-2.pdf)
  gives a 20 × 20 mm four-M3 top-hole pattern, 27 mm block width,
  approximately 45.4 mm overall block length, 13 mm assembly height, and
  M3 × 3.5 mm tapped depth. Order the *carriage and rail together* with the
  rail's hole layout/end distances shown on the supplier drawing; do not
  substitute an MGN12C, MGN12H-0 or no-name clone by label alone. The
  670 mm length is the current Q4D X-rail packaging decision, not the older
  550 mm list. Y-axis rail lengths and end-hole positions remain separate
  frame procurement decisions.

These are **fixed target models for CAD and purchase inquiries**, but not a
guarantee of drop-in assembly and not a manufacturing release. Obtain seller
photos/dimensioned drawings before a full order; buying one servo, one pen
and the specified X rail/block as a fit lot before buying four servos/pens
avoids paying for unverified substitutions. In particular, the 24 mm pen pitch must be checked
against the MG90S mounting ears, horn sweep and four cable exits, not just
the nominal servo body boxes in the old STL. The 2026-09-27
`q4d_mg90s_packaging_study.py` instead orients the published 12.2 mm
body dimension along X, the 22.8 mm dimension along local Y, and 28.5 mm
along Z. This leaves 11.8 mm *body-only* gap at 24 mm pen pitch, versus
only 1.2 mm if the 22.8 mm body dimension were along X. This corrects the
earlier worst-case warning: four **bodies** can fit coplanar under that
orientation. It does not prove the actual ears, shafts, horns, cables or
mounting fasteners fit; TowerPro's unlabeled 32.5 mm table dimension must
not be guessed to be the ear span. The head remains unaccepted until a
dimensioned servo drawing resolves these features.

### 3.3 Four-MG90S body packaging study

`cad/export_q4d_candidate/q4d_mg90s_packaging_STUDY.step` contains four
published-size rectangular MG90S **body envelopes** plus the four legacy
slider/pen proxies. Its local body centers are X = −36/−12/+12/+36 mm,
Y = −35 mm, Z = −16 mm. At the saved one-active pose and all four choices
of active slider, B-Rep intersection volume is zero between each body and
every slider/pen proxy, and between all pairs of bodies. The STEP contains
12 valid solids and bounds 89 × 103 × 57.25 mm. It intentionally omits the
base plate, servo tabs, shaft, horn, linkage, cable and nib. The apparent
empty space between motor and slider is *not* a completed lifting mechanism.
The selected body orientation and Z datum are design assumptions to test,
not a manufacturer mounting drawing or final assembly placement.

### 3.4 Head chassis and four servo pockets (concept)

`cad/q4d_head_chassis_concept.py` now models the **missing support geometry**
that the body-envelope study intentionally left out. The separate
`q4d_head_with_chassis_study.py` assembly shows one open-top, connected
chassis; five longitudinal guide ribs with lower capture ledges around four
17 mm-wide slider proxies; four MG90S body pockets; and four separately
removable rear retainer bars. The top is an open lattice so the four bays
remain visible and serviceable. The nominal side clearance to a slider is
1.5 mm, ledge/slider underside gap 0.3 mm, body-pocket side allowance
0.4 mm per side, and retainer/body top gap 0.25 mm. B-Rep tests found no
positive-volume overlap between chassis and any slider/pen at 11 sampled
positions across each 0..10 mm stroke, or between chassis, body boxes and
retainer bars. This is **CAD fit only**, not a guarantee that PETG print
shrinkage will preserve those gaps.

The bars have provisional M2 holes and matching pilot holes, but screw
engagement, insert type, torque, horn clearance, actual MG90S ear shape,
shaft datum, cable exit and pen-actuation linkage are still unspecified.
The guide frame now has four integral side mounting ears. The separate
`q4d_integrated_carriage_mount.py` is an outboard yoke from the nominal
20 x 20 mm X-block pattern to those ears; its arms stay outside the slider
envelope. At the revised head datum Y=gantry+68 mm, the saved three-body
`q4d_integrated_carriage_fit.step` has four coaxial M3 clearance paths and
zero positive-volume B-Rep overlap between frame, yoke and X-block proxy.
The 110 mm guide lattice is now 132 mm overall with its side ears. This
resolves the previously missing *nominal geometric connection*, but does not
qualify PETG strength, real MGN12H hole depths, bolt stack (provisionally
M3 x 50 plus washers/nuts at the ears), servo actuation or the full-machine
dynamic envelope. None of these STEPs is an approved STL/print file. See
`cad/export_q4d_candidate/q4d_head_chassis_CONCEPT.step`
for the chassis alone and `q4d_head_with_chassis_STUDY.step` for the visible
17-part packaging assembly.

`q4d_complete_head_motion_review.step` and its animated GLB assemble the
X-block proxy, revised yoke, four-bay guide frame, four MG90S body proxies,
four crank/slot proxies, sliders and coloured pen proxies. The 12-second clip
lowers one pen at a time through the assumed 10 mm stroke, then parks it;
this is a visual motion review, **not** evidence of measured servo geometry
or a working electrical control sequence.

Service-access revision: the four provisional pen-clamp bosses now face the
machine rear, above the servo cradles. A straight Ø3 mm driver gauge reaches
all four screw mouths at both slider extremes without touching the fixed
frame, yoke or X-block proxy. The upper tie was lowered, leaving 17.5 mm of
the parked Ø11 mm pen proxy above the highest fixed frame feature; a Ø17 mm
top-grip gauge clears the frame over its upper 15 mm. These are nominal CAD
tool-envelope checks, not validation of fingers, pen clips, screw heads or
actual M2 inserts. The low cross-tie and its posts were raised: the lowest
fixed head feature is now the servo-cradle floor at machine Z=5.7 mm, rather
than the former lower tie at Z=0 mm. With the proxy barrel bottom at Z=7 mm
when down, a real nib would need at least 6.3 mm protrusion below that barrel
for 5 mm paper clearance at the chosen contact plane. This is a **purchase
and adjustment condition, not a clearance pass**; the physical nib length,
barrel insertion depth, paper plane and FDM tolerance are not yet measured.

### 3.5 Pin-in-slot actuation study (not a servo-horn release)

`cad/q4d_pin_slot_actuation_study.py` adds a follower tongue to each slider
proxy and an assumed shaft/crank/pin to each servo-body envelope. With a
7.071 mm pin radius and an assumed usable −45°..+45° sweep, the analytical
slider displacement is `5 + 7.071 sin(angle)` mm: 0 mm down, 10 mm parked,
strictly monotonic between. The pin travels along local Y and its changing
local X position is absorbed by a 2.4-mm-wide transverse capsule slot around
a proposed Ø2 mm steel pin, leaving 0.2 mm nominal radial clearance. This
is a kinematic construction, not evidence that a supplied MG90S horn has a
7.071 mm usable radius, the assumed shaft datum, or sufficient torque.

The exported `cad/export_q4d_candidate/q4d_pin_slot_actuation_STUDY.step`
shows one selected pen and three parked pens. Nominal B-Rep tests cover four
bays at seven sampled angles; they check the driven slider, crank, chassis,
body boxes and retainers for positive-volume overlap. The model still omits
actual servo ears/shaft spline/horn, pin bearing and retention, hard stops,
pen clamp, wiring, nib and verified force path. The follower tongue is a
study shape, not a PETG print release. In particular, no servo-angle or force
claim is valid until one genuine sample has been measured and cycled under
load. This study does not change the frozen Q1–Q3 geometry.

The STEP sidecar provides a 4-second looping `pen_1_lift` viewer clip: pen 1
starts down, rises 10 mm as its proxy crank rotates 90°, then returns. The
other three pens remain parked so the follower slot is easy to inspect. This
is visual kinematics, not a servo-control sequence or physical cycle test.

### 3.6 One-bay PETG fit-test draft (not a complete machine head)

The separate `q4d_single_bay_frame_TEST_ONLY`, `slider_TEST_ONLY` and
`retainer_TEST_ONLY` STEP/STL files make a replaceable one-pen trial set; the
`q4d_single_bay_fit_ASSEMBLY.step` shows those parts with a servo **body** box,
proxy crank and Ø11 pen tube. The frame includes two-sided stops: at nominal
travel 0..10 mm, the slider has 0.5 mm axial gap to each stop; at −1 or +11 mm
overtravel it intersects the stop pads. The slider has a top Ø1.7 mm pilot
for a proposed flush M2 pen set screw; its actual threads, retention force
and contact on the Sarasa barrel are not certified. The retainer uses a
proposed pair of M2 holes. No screws, inserts, horn or steel pin are modeled
as purchased hardware.

FDM/PETG DfAM measurements at a 45° self-support rule on the saved STL files:

| Trial part | Watertight | Sampled min / p05 wall | Current-orientation support estimate |
| --- | --- | --- | --- |
| One-bay frame | yes | 1.752 / 2.5 mm | 254% of part volume, coarse upper bound |
| Driven slider | yes | 1.6 / 1.6 mm | 97.2% of part volume, coarse upper bound |
| Servo retainer | yes | 1.654 / 2.0 mm | 0% |

These meet the default 1.2 mm *supported* wall threshold and just meet the
1.6 mm *unsupported* threshold at the slider tongue, but support demand is
not economical in the native orientation. An axis-only orientation sweep
suggests rotating the slider −90° about X reduces down-facing support area
from 17.6% to approximately 2.2%, at 64 mm build height. The frame remains
support-intensive; split-frame redesign or a slicer-specific support plan is
still needed before printing it. These metrics are geometry screening, not
PETG shrinkage, strength or successful slicing evidence.

The one-bay test does **not** resolve real MG90S ears/shaft/horn/cable exit,
the pen's actual cylindrical clamp zone and nib contact, servo torque,
thread engagement, the Q4D head-to-X-block adapter or four-bay wiring. A fit
lot of one genuine MG90S and one specified Sarasa pen remains the next
physical gate, not a full machine purchase.

## 4. Required release gates

1. Reconstruct the base, four linear guides, servo mounts and horn/linkages as
   manufacturable parametric solids from the STL and chosen purchased parts.
   Check all four 0..10 mm slider sweeps, hard stops, and no simultaneous nib
   contact. Verify pen clamping and replaceability.
2. Define the actual nib contact datum and each pen's X/Y/Z calibration. Check
   the full drawing rectangle for all four colors and every parking/active pose.
3. Extend/relocate the front Y guide and both X/Y endstops as needed; repair
   the right-bracket collision; replace the mount space claim with a validated
   carriage bracket/new head-base interface; reroute
   four servo cables with a real drag-chain supplier bend envelope. Run dense
   XY and continuous (or conservatively bounded) slider collision tests.
4. Specify four independently addressed servo outputs, a suitable power rail,
   a default all-up state, interlock preventing two pens down, and motion
   sequencing that raises the old pen before lowering the new one. Verify
   firmware/controller behavior and power-loss recovery on hardware.
5. Print and measure the head; prove stroke, nib clearance, repeatability,
   stiffness, servo torque/temperature, wiring endurance and ≥100 color-change
   cycles. STL and STEP geometry alone cannot satisfy these physical gates.

Until all gates pass, `Q4C_FULL_ASSEMBLY.step` and the new Q4D reference STEP
must **not** be called a stable whole-machine assembly.

### PETG fit-test gate (2026-09-27)

The printer, purchased servo/pen samples and actual print settings are not yet
known. PETG is the provisional FDM material, not a validated fit. The revised
one-piece mount STEP is one watertight body; a diagnostic mesh measured a
2.317 mm minimum local wall and 3.0 mm fifth-percentile wall. Its estimated
support volume is still substantial (about 103% of part volume in Z-up, or
82% after a 180-degree X rotation). Those estimates are coarse screening
metrics, not a slicer result or a strength certificate. **Do not print the
mount as a final machine part yet.**

`cad/export_q4d_candidate/q4d_pen_fit_coupon_TEST_ONLY.stl` is a small,
non-load-bearing calibration piece that may be printed first. It has three
nominal through-bores, 11.2 / 11.4 / 11.6 mm, chosen around Zebra's nominal
11.0 mm barrel. Print it using the intended PETG printer/profile, measure
the resulting holes and the actual pen's clamping zone, and record fit without
forcing the pen. The coupon does not validate nib location, servo clearance,
pen retention or the head's stiffness. Regenerate it from
`cad/q4d_pen_fit_coupon.py` if the geometry changes.

Before releasing a head design, obtain the exact four servos, four pens,
MGN12H carriage and fasteners. Measure the servo ears/shaft/horn sweep,
pen-barrel/clip/nib datums, rail-block holes and physical stroke; then revise
the head and rerun collision, slicer, assembly and ≥100-cycle tests. No
nominal vendor dimension substitutes for those measurements.

## 5. Reproducible checks

- `backend/venv/bin/python3 cad/q4d_four_pen_feasibility.py` measures the
  legacy STL and X travel. Exit 2 deliberately means machine release blocked.
- `backend/venv/bin/python3 -m pytest -q tests/test_q4d_kinematic_budget.py`
  checks four-pen corner reach, offset signs, rail margins and invalid inputs.
- `backend/venv/bin/python3 -m pytest -q tests/test_q4d_color_change_contract.py`
  checks all-up acknowledgement before compensated travel and exactly one
  lower-one action for every selected color.
- `backend/venv/bin/python3 cad/q4d_head_fit_verification.py` tests nine sampled
  XY poses against old Q4 parts and a 225-pose candidate grid with all four
  one-active states. Exit 2 deliberately means the
  remaining Y rail, bracket, chain and actuator gates are open.
- `backend/venv/bin/python3 cad/q4d_mount_interface_audit.py` checks the
  legacy base circular loops and both old 17/21 mm and revised 25/29 mm gaps.
- `cad/q4d_xblock_head_mount_concept.py` regenerates the provisional one-solid
  bracket STEP; `q4d_head_fit_verification.py` includes its proxy collision
  check at sampled and dense XY poses. It does not test loads or fasteners.
- `CADGEN_CACHE_DIR=/private/tmp/omnidraw-q4d-cadgen-cache backend/venv/bin/python3 cad/q4d_four_pen_reference.py`
  regenerates the Q4D reference STEP without changing frozen Q1–Q3 exports.
- Run `cad/q4d_frame_head_concept.py` with the same Python/cache setup to
  regenerate the view-only frame/head STEP.

# Q4D X endstop contact study (candidate, not fabrication release)

`cad/q4d_x_endstop_study.py` moves the X switch proxy to the left of the
Q4D outboard yoke. The old Q4C switch at gantry Y+15 did not meet the Q4D
moving arm. At carriage X=-23 mm the new lever proxy overlaps that arm by
2.4 mm³; at the candidate active limit X=-21 mm there is no overlap.
The switch body and carrier do not intersect the arm in either pose, and the
three fixed proxies do not penetrate the left gantry bracket. This proves a
geometric contact opportunity only. Actual switch lever travel, repeatability,
electrical wiring, overtravel stop, mounting holes and fastener access remain
open. The carrier only touches the bracket face in this study and is **not**
ready to print or install.

The initial Q4D belt landings were not clamps or tensioners. The provisional
pull-through clamp below supersedes those bare landings, but its holding force
and loaded adjustment range must be checked before belt routing can be
released for fabrication.

## Q4D pull-through belt clamp study — 2026-09-28

`cad/q4d_belt_clamp_concept.py` is a **provisional candidate** now shown in
the Q4D head and full-machine layout exports. It adds four 20 mm-long open slots on the Q4D yoke,
four removable pressure-shoe proxies, and one M3 pilot bore per slot. The
intent is to pull each open GT2 belt tail manually through its slot and then
clamp it. This avoids carrying four Q4C-style screw tensioner sliders on the
already crowded four-pen carriage. The old sliders demonstrably overlap the
current yoke by about 100–129 mm³ each and cannot simply be reused.

CAD checks at X=-21, 225, and 471 mm find no positive-volume intersection
between the *open* candidate clamp, nominal belt solids, X beam, X rail, or
gantry end brackets. A 7 mm continuation of each belt tail also fits through
the open slot. This is **7 mm of geometric pull-through space**, not a proven
7 mm loaded tensioner stroke. The saved STEP has one yoke and four separate
shoe occurrences; neither belt-tooth engagement nor clamp force is modeled.
The candidate yoke also clears selected fixed frame, rail, motor and front
idler-mount solids on a 3×3 sample of X=-21/225/471 mm and the candidate
front/middle/rear Y poses. This is a sampled collision check, not a swept or
structural qualification.

The former outer screw axes at X=±25 mm intersected the four-pen guide ribs.
The current concept uses one inner screw per clamp at X=±15 mm and a shorter
shoe centered at X=±16 mm. A straight Ø5 mm driver now clears the guide
**frame** at both belt planes. With all four pens installed, however, that
driver meets the sliders/pens in bays 2 and 3. After removing only those two
modular cartridges, the driver path clears the retained frame, servo pockets,
and other head parts in the nominal CAD pose. This is the proposed belt-service
sequence; it must be checked on a physical assembly for finger access and
repeatable pen replacement.

The upper-belt pilot bore was lengthened through the existing X-block
backplate; a Ø3.2 mm gauge now traverses each of the four candidate bores
from its service side into the slot. The `q4d_modular_head_full_machine_motion`
animation also translates the four open-position shoes with the carriage.
The Q4C belt paths in the static layout remain reference geometry; the motion
animation intentionally omits belts until closed-clamp grip and preload are
validated.

**Fabrication blockers remain:** the single-screw shoe has no validated
pressure distribution or belt-grip force; the actual 6 mm GT2 belt, shoe
material, screw/insert fit, PETG wall strength, slip under load, and achievable
tension still need physical verification. Do not treat this STEP as a print
file or interpret the 7 mm free-tail fit as a loaded tensioner stroke.

## Pulley/axle assembly gate — 2026-09-29

The full-machine STEP shows all ten CoreXY pulley/idler *locations*, but the
pulley bodies in `build_q4c_corexy_assembly.py` are solid reference cylinders:
they have no shaft/bearing bore, bearing races, spacers, bolt, washer, nut or
retention hardware. The nominal front 28T flange OD 22 mm, height 8.5–9 mm,
M5 axle and Ø7 support boss are still provisional; no exact purchasable 28T
part and its axial stack have been qualified.

`cad/q4d_pulley_axle_audit.py` measures B-Rep intersection volumes (mm³) in
the current nominal pose. Front left/right idler proxies each penetrate
their brackets by 42.412; rear left/right motor pulleys each penetrate their
motor-shaft proxies by 103.084; rear left/right idlers penetrate their motor
mounts by 208.349/203.723. The four gantry idlers have zero positive-volume
intersection with the gantry brackets, but still lack axle fasteners and
bearing/inner-race contact proof. These numbers diagnose intentionally solid
proxies; they must **not** be interpreted as corrected bearing bores.

Before modeling a released wheel-on-shaft assembly, choose exact GT2 pulleys
and 28T/20T idlers, obtain supplier drawings or STEP, and verify the tooth
count, flange OD/height, belt width, bearing ID/OD, hub protrusion, shaft
length, motor pulley bore/set-screw access, M5 bolt grip length, washer and
locknut clearances. Then replace the reference bodies in a Q4D-specific
assembly, verify zero forbidden penetration and positive axial retention at
all ten sites, and check belt tracking in both Z planes. Until then the
wheel positions are visual/layout references, not a buildable BOM or a
fabrication release.

### Sourcing shortlist and dimensional decision — 2026-09-29

**Do not order the complete pulley kit yet.** The following are identifiable
commercial candidates, not a released BOM. Prices/stock/shipping are omitted
because they change and were not used to decide geometry.

| Site / quantity | Candidate | Supplier-stated dimensions | CAD decision |
| --- | --- | --- | --- |
| Motor A-4/B-4, 2 | Runice `RLA20-2GT-6-C-P5-H16`, [product](https://dfh.fm/products/20t-pulley-bore-5mm-width-6mm-by-runice) | 20T 2GT, 6 mm belt, Ø5 bore, 16 mm overall, two M4 set screws | Correct tooth count/bore class; **hold** until exact motor shaft length and tooth-band/hub datum are drawn. The current 8.5 mm-high cylinder is not this part. |
| Toothed 20T return idlers A-5/B-5/A-6/B-6, 4 | LDO `LDO-2GT-20TI-ID5-H10`, [drawing](https://ooznest.co.uk/wp-content/uploads/2020/02/2GT-Toothed-Idler-20-Tooth-5mm-Bore-6mm-Belt-Drawing.pdf) | 20T 2GT, 6 mm belt, Ø5 bore, Ø15 flange, 10 mm overall, 7 mm tooth land | Suitable *type*; **hold** until axle shoulder/shim/washer stack and both rear-mount interfaces are redesigned and checked. |
| Smooth 20T-equivalent lead-in idlers A-2/B-2, 2 | LDO `LDO-2GT-20I-ID5-H10`, [drawing](https://ooznest.co.uk/wp-content/uploads/2020/02/2GT-Toothed-Idler-5mm-Bore-6mm-Belt-Drawing.pdf) | Ø5 bore, Ø12 running body, Ø15 flange, 10 mm overall, 7 mm land | Correct backside-contact type; its running radius is **not** the 20T pitch radius used by the existing pulley proxy. Recompute the affected tangencies and belt length before ordering. |
| Front 28T turnaround idlers A-3/B-3, 2 | 3DPW 28T 2GT 6 mm [seller specification](https://www.3dprow.com/products/%E6%83%B0%E8%BC%AA28%E9%BD%92-%E7%9A%AE%E5%B8%B6%E5%AF%AC%E5%BA%A66mm-%E5%A4%96%E5%BE%9111mm-gt2-%E9%9B%99%E9%82%8A%E5%A4%96%E8%BB%B8%E6%89%BF%E5%A2%AE%E8%BC%AA) | 28T, Ø17.2 tooth crest, Ø20 overall, two 5×11×5 bearings; seller describes a Ø5×21 mm central axle | Closest identifiable 28T assembly, but **not approved**: its integrated axle/bearing stack and Ø20 flange differ from the modeled M5-bolt/Ø7-boss/Ø22-flange stack. Request an axial-section drawing or sample, then redesign front brackets. |

The [step.parts](https://www.step.parts/) GT2 Ø5/6 mm idler records specify
profile, belt width and bore but **not tooth count**, so they cannot establish
an exact 20T or 28T purchase SKU. No catalog STEP was imported into the
machine on this evidence. Supplier pages/drawings above are specification
sources, not proof of stock or local Vietnamese availability.

**Next CAD work after dimensions are confirmed:** select the actual motor
model/shaft; establish each pulley tooth-band center and hub direction;
redesign M5 idler bosses to contact only the bearing inner race via measured
spacers; calculate bolt grip/washer/locknut and driver access; update the
smooth-idler tangency; replace the ten solid proxies; rerun B-Rep collision,
belt-plane and travel checks. A 28T sample or complete axial-section drawing
is the first procurement/design gate, not a full-machine print order.

### Small-sample decision (not a full-kit purchase)

Use the 3DPW 28T/2GT/6 mm idler above as the **selected front-idler
measurement sample** for the Q4D redesign. This selects a supplier specimen,
not the final mounting hardware or a released bracket. Order **one** specimen
first if it can be delivered; the complete machine ultimately needs two
matched front idlers, but do not buy the pair until the specimen's axial stack
has been measured and its vendor/model identity can be reproduced.

The independent four-pen gate needs **one** genuine TowerPro MG90S (including
its supplied horn and screws) and **one** Zebra Sarasa Clip 0.5/JJ15 pen. A
digital caliper with 0.1 mm or better readable resolution is useful if none
is available. Do not buy four servos, four pens, rails, the remaining pulleys,
or a full fastener kit for this first measurement round.

Record the sample seller link, package/model markings, and photos of all
three orthogonal views with a ruler/caliper. For the 28T idler, measure flange
OD, tooth-land width, total flange-to-flange height, assembled end-to-end
height, shaft/bearing protrusion on **each** side, and whether the Ø5×21 mm
shaft is supplied loose or captive. Confirm by photograph that it rotates on
bearings and identify any included spacer/retaining clip; do not disassemble
or pry out the press-fit bearings just to measure them. The seller-stated
5×11×5 mm bearings remain nominal until verified by a drawing or safe
non-destructive measurement.

For the MG90S, measure body and ear envelope, mounting-hole center spacing,
output-axis offset from the body/ear datum, supplied horn radius/thickness,
and cable exit; photograph the horn at both commanded end positions after a
safe low-load test. For the pen, measure barrel diameter at the proposed clamp
zone, length from that zone to the extended nib, and clip/button projection.
These measurements control the next CAD iteration; do not claim a PETG final
fit or servo stroke from catalog envelopes alone.
