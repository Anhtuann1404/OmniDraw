<!-- scope-migration-20261002 -->
> **Phạm vi ngày 02/10/2026:** Tài liệu hardware hỗ trợ. Nội dung thiết kế/đo/review bên dưới giữ đúng phạm vi và ngày của nó; không đồng nghĩa đã mua máy, đã hiệu chuẩn hoặc đã nghiệm thu hướng nghiên cứu mới. Nghiên cứu dùng máy vẽ phẳng hai trục khi sẵn sàng, ghi cơ cấu/bộ điều khiển/bút/giấy theo run. Concept A4 một bút là phương án tham khảo hiện tại, không yêu cầu AxiDraw/CoreXY hay nhiều màu.
> Kế hoạch hiện hành: [Docs 30](../30_research_development_plan.md); đặc tả [Docs 31](../31_joint_solver_contract.md) và [Docs 32](../32_research_api_and_artifact_contract.md). Thông báo GVHD đồng ý hướng không thay sign-off kỹ thuật hoặc duyệt tham số.

# Q4D modular pen adapter study — NOT print-ready

The aim is to let four independently lifted pens use replaceable barrel liners,
instead of freezing the entire head to the Zebra Sarasa Clip diameter. The
source of truth is `cad/q4d_modular_pen_adapter_study.py`; the exported STEP is
`cad/export_q4d_candidate/q4d_modular_pen_adapter_study.step`.

## Nominal interface

- Four illustrative straight barrels: Ø8, Ø9, Ø10 and Ø11 mm, one per bay in
  the review STEP. These are *diameter gauges*, not verified purchasable pens.
- Common moving slider bore: Ø14 mm. Each pen uses two removable longitudinal
  split liners, outer Ø13.6 mm, inner diameter = nominal barrel + 0.2 mm.
  The thinnest nominal liner wall is 1.2 mm for the Ø11 barrel.
- The removable rear jaw sits in an 8 mm-long pocket **inside** the moving
  slider, not above it. The old external upper collar study overlaps fixed
  frame ribs at certain poses and must not be used as a print source.
- The slider remains in the existing four bays on 24 mm X pitch. The sampled
  0, 2.5, 5, 7.5 and 10 mm travel poses have zero nominal B-Rep overlap between
  each moving assembly component and the fixed head chassis. The body stays
  one solid.
- Each straight pen proxy now carries a **7.1 mm illustrative tapered nib**.
  At the nominal 0 mm downstroke its point reaches the reference work-bed
  top at Z=−0.1 mm; at the 10 mm parked position it clears that plane by
  10 mm. This corrects the earlier visualization: 5.8 mm was the fixed
  chassis-to-bed gap, **not** a measured nib-to-paper gap. Paper thickness,
  pen compression, actual nib profile and servo end angles remain unknown.

## What remains open

The two displayed screw shapes are **placement gauges only**. Clearance
holes, counterbores, inserts/nuts, engagement length, clamp compliance, torque,
PETG strength and repeatability are not designed or verified. The 1.2 mm
liner wall and 1.5 mm minimum body wall near the Ø14 bore need print coupons
and handling tests before release. Printed dimensions will require the actual
printer/profile and purchased pen measurements, not just CAD nominal gaps.

The mock pens have a constant-diameter 93 mm cylindrical body and an
illustrative, unmeasured tapered tip, but no real clip, retract button or
qualified nib profile. Real pen qualification requires a straight
gripping zone through the guide and jaw, a nib-contact height range that fits
the 10 mm servo stroke, top removal access, no clip collision and individual
XY/Z calibration. A barrel diameter alone is **not** proof of compatibility.

Recommended next gate: purchase or obtain one ordinary candidate pen, measure
its actual barrel/clip/nib profile, print a short Ø14 guide and liner coupon
in PETG, then perform insertion, clamp-force, tilt and repeated-removal tests.
Only after that should the jaw fasteners and full printable parts be released.
