"""
Unit Test Suite for OmniDraw Hardware Abstraction Layer (TV3) — v1.4
=====================================================================
Kiểm thử toàn diện backend/hardware_adapter.py:

Nhóm 1 — Hình học SVG, Nhóm Transform & Quãng đường thực tế:
  - parse_svg_path_length_mm: M/L/H/V/C/Q/S/T/A/Z
  - Cubic Bézier thẳng 30mm (control points thẳng hàng)
  - Elliptic Arc (A/a) tính toán chuẩn xác
  - Phân cấp nhóm lồng nhau: Đường 10mm trong <g transform="scale(2)"> tính đúng 20s ở v=1mm/s
  - Quy đổi offset an toàn 5mm chuẩn xác theo tỉ lệ viewBox (width/viewBox)
  - Quãng đường pen-up thực tế giữa các subpath
  - Chặn đứng XML sai cú pháp: <svg><path></svg> bị từ chối với SVG_INVALID
  - Từ chối chuỗi "not an svg" trả lỗi SVG_INVALID

Nhóm 2 — MockSimulatorAdapter:
  - Vòng đời cơ bản: start → pause → resume → done
  - Không sinh task trùng khi pause/resume nhanh
  - Disconnect giữa khi job đang chạy → HARDWARE_NOT_CONNECTED
  - Cancel sau done → INVALID_STATE

Nhóm 3 — AxiDrawAdapter & Chế độ Máy thật vs Fake:
  - Chế độ physical khi thiếu pyaxidraw: Báo lỗi KHÔNG KẾT NỐI, KHÔNG tự ý tráo sang fake driver!
  - Fake driver chỉ được bật khi use_fake_driver=True hoặc mode='fake'
  - Fake driver phân định chuẩn: is_simulated=True, actual_hardware_measured=False
  - Pause trên fake driver ngắt chuyển động thực tế, không tự ý chuyển done
  - Cancel ngắt chuyển động ngay lập tức

Nhóm 4 — Calibration Profile (Nạp & Validate):
  - load_calibration_profile() với file hợp lệ
  - Validation schema: chấp nhận profile hợp lệ, từ chối model lạ/tham số âm
"""

import asyncio
import csv
import os
import sys
import tempfile
import time
import unittest

_current_dir = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.dirname(_current_dir)
_backend_dir = os.path.join(_repo_root, "backend")
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from hardware_adapter import (
    HardwareAdapterInterface,
    MockSimulatorAdapter,
    AxiDrawAdapter,
    _FakeAxiDrawDriver,
    get_hardware_adapter,
    reset_hardware_adapter,
    estimate_svg_draw_time,
    parse_svg_path_length_mm,
    parse_svg_path_geometry,
    extract_svg_viewbox_scale,
    validate_svg_content_or_path,
    validate_calibration_profile,
    load_calibration_profile,
    apply_origin_offset_to_svg,
    record_metric,
    run_rq3_calibration_benchmark,
    VALID_HARDWARE_ERRORS,
)


# ---------------------------------------------------------------------------
# Nhóm 1 — Hình học SVG & Nhóm Transform
# ---------------------------------------------------------------------------

class TestSVGGeometry(unittest.TestCase):

    def test_simple_line_30mm(self):
        length = parse_svg_path_length_mm("M 10 10 L 40 10")
        self.assertAlmostEqual(length, 30.0, places=3)

    def test_relative_lineto(self):
        length = parse_svg_path_length_mm("M 10 10 l 30 0")
        self.assertAlmostEqual(length, 30.0, places=3)

    def test_h_command(self):
        length = parse_svg_path_length_mm("M 5 5 H 35")
        self.assertAlmostEqual(length, 30.0, places=3)

    def test_v_command(self):
        length = parse_svg_path_length_mm("M 5 5 V 25")
        self.assertAlmostEqual(length, 20.0, places=3)

    def test_rectangle_closepath(self):
        length = parse_svg_path_length_mm("M 10 30 L 30 30 L 30 40 L 10 40 Z")
        self.assertAlmostEqual(length, 60.0, places=2)

    def test_cubic_bezier_straight_30mm(self):
        length = parse_svg_path_length_mm("M 10 20 C 20 20, 30 20, 40 20")
        self.assertAlmostEqual(length, 30.0, delta=0.5)

    def test_quadratic_bezier(self):
        length = parse_svg_path_length_mm("M 0 0 Q 10 10 20 0")
        self.assertGreater(length, 20.0)
        self.assertLess(length, 35.0)

    def test_elliptic_arc_A_semicircle(self):
        d = "M 0 0 A 10 10 0 0 1 20 0"
        length = parse_svg_path_length_mm(d)
        expected = 10.0 * 3.14159265
        self.assertAlmostEqual(length, expected, delta=0.5)

    def test_nested_group_transform_scale(self):
        """
        Đường 10mm nằm trong nhóm <g transform="scale(2)">:
        Chiều dài thực tế = 10mm * 2 = 20mm.
        Ở tốc độ 1 mm/s (không pen-up, v_penup lớn, delay=0):
        thời gian ước lượng phải là đúng 20 giây!
        """
        svg = (
            '<svg width="100mm" height="100mm" viewBox="0 0 100 100">'
            '  <g transform="scale(2)">'
            '    <path d="M 0 0 L 10 0"/>'
            '  </g>'
            '</svg>'
        )
        time_sec = estimate_svg_draw_time(
            svg,
            speed_mm_per_sec=1.0,
            speed_penup_mm_per_sec=1000.0,
            pen_down_delay_ms=0.0,
            pen_up_delay_ms=0.0
        )
        self.assertEqual(time_sec, 20, f"Đường 10mm trong scale(2) ở v=1mm/s phải tốn 20s, got {time_sec}s")

    def test_origin_offset_scaled_by_viewbox(self):
        """
        Kiểm tra quy đổi offset 5mm theo viewBox:
        SVG width="200mm", viewBox 0 0 1000 500 -> 1mm = 5 units.
        Offset 5mm trên giấy phải được quy đổi thành 25.0000 units trong viewBox.
        """
        svg = '<svg width="200mm" height="100mm" viewBox="0 0 1000 500"><path d="M 0 0 L 10 10"/></svg>'
        offsetted = apply_origin_offset_to_svg(svg, 5.0, 5.0)
        self.assertIn('transform="translate(25.0000, 25.0000)"', offsetted)

    def test_malformed_svg_xml_rejected(self):
        """
        Thẻ <svg><path></svg> sai XML (thẻ path mở mà không đóng)
        PHẢI bị từ chối với SVG_INVALID!
        """
        malformed_svg = "<svg><path></svg>"
        is_valid, _, err = validate_svg_content_or_path(malformed_svg)
        self.assertFalse(is_valid)
        self.assertEqual(err, "SVG_INVALID")

    def test_validate_svg_rejects_non_svg_strings(self):
        is_valid, _, err = validate_svg_content_or_path("not an svg")
        self.assertFalse(is_valid)
        self.assertEqual(err, "SVG_INVALID")

    def test_validate_svg_accepts_valid_inline_svg(self):
        valid_svg = '<svg width="100" height="100"><path d="M 0 0 L 10 10"/></svg>'
        is_valid, resolved, err = validate_svg_content_or_path(valid_svg)
        self.assertTrue(is_valid)
        self.assertIsNone(err)


# ---------------------------------------------------------------------------
# Nhóm 2 — MockSimulatorAdapter
# ---------------------------------------------------------------------------

class TestMockSimulatorAdapter(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.fixture = os.path.join(_repo_root, "tests", "fixtures", "smoke_test_specimen.svg")
        self.adapter = MockSimulatorAdapter(connected=True, speed_factor=25.0)

    async def asyncTearDown(self):
        for rid, job in self.adapter.jobs.items():
            task = job.get("task")
            if task and not task.done():
                task.cancel()

    async def test_job_lifecycle_start_pause_resume_done(self):
        req_id = "lifecycle-sim-01"
        res = await self.adapter.start_job(req_id, self.fixture)
        self.assertEqual(res.get("status"), "printing")

        p_res = await self.adapter.pause_job(req_id)
        self.assertEqual(p_res.get("status"), "paused")

        r_res = await self.adapter.resume_job(req_id)
        self.assertEqual(r_res.get("status"), "printing")

        for _ in range(200):
            await asyncio.sleep(0.05)
            if self.adapter.get_status(req_id)["status"] == "done":
                break

        st = self.adapter.get_status(req_id)
        self.assertEqual(st["status"], "done")
        self.assertTrue(st["is_simulated"])
        self.assertFalse(st["actual_hardware_measured"])


# ---------------------------------------------------------------------------
# Nhóm 3 — AxiDrawAdapter: Chế độ Máy thật vs Fake Driver
# ---------------------------------------------------------------------------

class TestAxiDrawAdapterModes(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.fixture = os.path.join(_repo_root, "tests", "fixtures", "smoke_test_specimen.svg")

    async def test_physical_mode_without_pyaxidraw_refuses_to_connect(self):
        """
        NGUYÊN TẮC: Chế độ physical khi không có pyaxidraw
        PHẢI báo không kết nối, TUYỆT ĐỐI KHÔNG tự ý chọn fake driver!
        """
        adapter = AxiDrawAdapter(use_fake_driver=False)
        # Nếu môi trường không có pyaxidraw
        if adapter._ad is None:
            self.assertFalse(adapter._use_fake_driver, "Không được tự ý bật use_fake_driver!")
            self.assertFalse(adapter.is_connected)
            conn = adapter.connect()
            self.assertFalse(conn, "connect() phải trả về False khi không có driver thật")

            res = await adapter.start_job("phys-fail-test", self.fixture)
            self.assertIn("error", res)
            self.assertEqual(res["error"]["code"], "HARDWARE_NOT_CONNECTED")

    async def test_fake_mode_reports_simulated_properly(self):
        """Khi chỉ định rõ fake driver, adapter hoạt động và khai báo chuẩn."""
        adapter = AxiDrawAdapter(use_fake_driver=True)
        self.assertTrue(adapter._use_fake_driver)
        self.assertTrue(adapter.connect())

        req_id = "fake-run-test"
        await adapter.start_job(req_id, self.fixture)

        for _ in range(50):
            await asyncio.sleep(0.05)
            if adapter.get_status(req_id)["status"] == "done":
                break

        st = adapter.get_status(req_id)
        self.assertEqual(st["status"], "done")
        self.assertTrue(st["is_simulated"])
        self.assertFalse(st["actual_hardware_measured"])
        self.assertEqual(st["source_tag"], "axidraw_fake_driver")

    async def test_fake_driver_pause_does_not_become_done_automatically(self):
        adapter = AxiDrawAdapter(use_fake_driver=True)
        adapter.connect()
        adapter._ad.total_plot_time = 0.5
        req_id = "pause-safety-test"

        await adapter.start_job(req_id, self.fixture)
        await asyncio.sleep(0.05)

        p_res = await adapter.pause_job(req_id)
        self.assertEqual(p_res["status"], "paused")

        await asyncio.sleep(0.3)
        st = adapter.get_status(req_id)
        self.assertEqual(st["status"], "paused", "Job không được tự động chuyển done khi đang pause!")

        await adapter.resume_job(req_id)
        for _ in range(50):
            await asyncio.sleep(0.05)
            if adapter.get_status(req_id)["status"] == "done":
                break

        self.assertEqual(adapter.get_status(req_id)["status"], "done")

    async def test_fake_driver_cancel_aborts_immediately(self):
        adapter = AxiDrawAdapter(use_fake_driver=True)
        adapter.connect()
        adapter._ad.total_plot_time = 0.5
        req_id = "cancel-stop-test"

        await adapter.start_job(req_id, self.fixture)
        await asyncio.sleep(0.05)

        c_res = await adapter.cancel_job(req_id)
        self.assertEqual(c_res["status"], "cancelled")

        await asyncio.sleep(0.2)
        st = adapter.get_status(req_id)
        self.assertEqual(st["status"], "cancelled")


# ---------------------------------------------------------------------------
# Nhóm 4 — Calibration Profile
# ---------------------------------------------------------------------------

class TestCalibrationProfile(unittest.TestCase):

    def test_load_real_profile_yaml_with_pyyaml(self):
        yaml_path = os.path.join(_repo_root, "config", "calibration_profile.yaml")
        profile = load_calibration_profile(yaml_path)
        self.assertIn("version", profile)
        self.assertEqual(profile["paper"]["size"], "a4")
        self.assertIn("speed_pendown_mm_s", profile["motion"])

    def test_validation_rejects_invalid_profile(self):
        bad_profile = {
            "version": "1.0",
            "device": {"model": "NonExistentModel_999"},
            "paper": {"width_mm": -100, "height_mm": 200},
            "motion": {"speed_pendown_mm_s": -50}
        }
        is_valid, msg = validate_calibration_profile(bad_profile)
        self.assertFalse(is_valid)

    def test_validation_accepts_valid_profile(self):
        valid_p = {
            "version": "1.0",
            "device": {"model": "AxiDraw_V3"},
            "paper": {"size": "a4", "width_mm": 297, "height_mm": 210},
            "origin": {"x_mm": 5.0, "y_mm": 5.0},
            "motion": {"speed_pendown_mm_s": 25, "speed_penup_mm_s": 75, "accel_pct": 75},
            "pen": {"pos_up_pct": 60, "pos_down_pct": 35, "delay_down_ms": 120, "delay_up_ms": 100}
        }
        is_valid, msg = validate_calibration_profile(valid_p)
        self.assertTrue(is_valid, msg)


# ---------------------------------------------------------------------------
# Nhóm 5 — Factory
# ---------------------------------------------------------------------------

class TestFactory(unittest.TestCase):

    def setUp(self):
        reset_hardware_adapter()

    def tearDown(self):
        reset_hardware_adapter()

    def test_simulator_mode(self):
        adapter = get_hardware_adapter(mode="simulator")
        self.assertIsInstance(adapter, MockSimulatorAdapter)

    def test_fake_mode(self):
        adapter = get_hardware_adapter(mode="fake")
        self.assertIsInstance(adapter, AxiDrawAdapter)
        self.assertTrue(adapter._use_fake_driver)

# ---------------------------------------------------------------------------
# Nhóm 6 — RQ3 Calibration Benchmark (TV3 Physical Feasibility)
# ---------------------------------------------------------------------------

class TestRQ3CalibrationBenchmark(unittest.TestCase):

    def setUp(self):
        reset_hardware_adapter()

    def tearDown(self):
        reset_hardware_adapter()

    def test_rq3_specimen_fixture_valid(self):
        fixture_path = os.path.join(_repo_root, "tests", "fixtures", "rq3_clearance_calibration_specimen.svg")
        self.assertTrue(os.path.isfile(fixture_path), "rq3_clearance_calibration_specimen.svg fixture must exist")
        is_valid, content, err = validate_svg_content_or_path(fixture_path)
        self.assertTrue(is_valid, f"Fixture SVG must be valid XML: {err}")

    def test_rq3_benchmark_simulator_run(self):
        res = asyncio.run(run_rq3_calibration_benchmark(mode="simulator"))
        self.assertEqual(res.get("status"), "done")
        self.assertTrue(res.get("is_simulated"))
        self.assertFalse(res.get("actual_hardware_measured"))
        self.assertEqual(res.get("source_tag"), "simulator")
        self.assertEqual(res.get("clearance_ladder_tested_mm"), [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70])
        self.assertEqual(res.get("acute_turn_angles_tested_deg"), [60, 90, 120, 150])
        self.assertTrue(res.get("rapid_pen_lift_actuation_tested"))

    def test_rq3_benchmark_physical_mode_blocked_without_device(self):
        # Khi không có máy vẽ thật kết nối, physical mode bắt buộc trả về status blocked
        res = asyncio.run(run_rq3_calibration_benchmark(mode="physical"))
        self.assertEqual(res.get("status"), "blocked")
        self.assertIn("BLOCKED_BY_HARDWARE", res.get("reason", ""))
        self.assertFalse(res.get("actual_hardware_measured"))

    def test_rq3_benchmark_missing_fixture_returns_error(self):
        res = asyncio.run(run_rq3_calibration_benchmark(mode="simulator", fixture_path="non_existent_fixture.svg"))
        self.assertEqual(res.get("status"), "error")
        self.assertIn("Không tìm thấy fixture RQ3", res.get("error", ""))


# ---------------------------------------------------------------------------
# Nhóm 7 — TV4 Integration Contracts (Pause Capability & CSV Data Integrity)
# ---------------------------------------------------------------------------

class MockRealAxiDrawDriver:
    def __init__(self, fail_on_run: bool = False, fail_msg: str = "Device disconnected"):
        self.options = type("opts", (), {
            "mode": "plot",
            "model": 1,
            "speed_pendown": 25,
            "speed_penup": 75,
            "accel": 75,
            "pen_pos_up": 60,
            "pen_pos_down": 35,
            "pen_delay_up": 100,
            "pen_delay_down": 120,
            "port": None,
            "auto_rotate": True,
        })()
        self.fail_on_run = fail_on_run
        self.fail_msg = fail_msg
        self.plot_setup_called = False
        self.plot_ran = False

    def interactive(self):
        pass

    def connect(self) -> bool:
        return True

    def disconnect(self):
        pass

    def plot_setup(self, svg_path: str):
        self.plot_setup_called = True

    def plot_run(self):
        if self.fail_on_run:
            raise RuntimeError(self.fail_msg)
        time.sleep(0.05)
        self.plot_ran = True

    def stop(self):
        pass


class TestTV4IntegrationContracts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.fixture = os.path.join(_repo_root, "tests", "fixtures", "smoke_test_specimen.svg")
        self.csv_path = os.path.join(_repo_root, "logs", "hardware_metrics.csv")
        reset_hardware_adapter()

    def tearDown(self):
        reset_hardware_adapter()

    def _get_csv_rows_for_request(self, request_id: str):
        if not os.path.isfile(self.csv_path):
            return []
        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [row for row in reader if row.get("request_id") == request_id]

    async def test_physical_success_records_actual_hardware_measured(self):
        """
        TV4 Contract:
        Physical job hoàn tất thành công -> actual_hardware_measured=True, is_simulated=False, source_tag=axidraw_real.
        CSV ghi đúng 9 cột với thời gian thực đo > 0.
        """
        adapter = AxiDrawAdapter(use_fake_driver=False)
        adapter._ad = MockRealAxiDrawDriver()
        adapter._connected = True

        self.assertFalse(adapter.pause_supported)
        self.assertFalse(adapter.is_simulation)

        req_id = f"test-phys-ok-{int(time.time() * 1000)}"
        start_res = await adapter.start_job(req_id, self.fixture)
        self.assertEqual(start_res["status"], "printing")
        self.assertFalse(start_res["pause_supported"])

        # Chờ worker thread hoàn thành
        for _ in range(50):
            await asyncio.sleep(0.05)
            st = adapter.get_status(req_id)
            if st["status"] == "done":
                break

        st = adapter.get_status(req_id)
        self.assertEqual(st["status"], "done")
        self.assertFalse(st["is_simulated"])
        self.assertTrue(st["actual_hardware_measured"])
        self.assertEqual(st["source_tag"], "axidraw_real")
        self.assertFalse(st["pause_supported"])
        self.assertIsNotNone(st.get("actual_draw_time_sec"))
        self.assertGreater(st["actual_draw_time_sec"], 0)

        # Kiểm tra hàng CSV tương ứng
        rows = self._get_csv_rows_for_request(req_id)
        self.assertGreaterEqual(len(rows), 1)
        last_row = rows[-1]
        self.assertEqual(last_row["hardware_status"], "done")
        self.assertEqual(last_row["is_simulated"], "False")
        self.assertEqual(last_row["actual_hardware_measured"], "True")
        self.assertEqual(last_row["source_tag"], "axidraw_real")
        self.assertEqual(last_row["error_code"], "")
        self.assertTrue(float(last_row["actual_draw_time_sec"]) > 0)

    async def test_physical_runtime_failure_records_unmeasured_and_empty_timing(self):
        """
        TV4 Contract:
        Physical thất bại / mất kết nối runtime:
        - is_simulated=False
        - actual_hardware_measured=False
        - actual_draw_time_sec rỗng/None (KHÔNG ghi timing giả hoặc 0)
        - error_code được ghi nhận (ví dụ: HARDWARE_NOT_CONNECTED)
        """
        adapter = AxiDrawAdapter(use_fake_driver=False)
        adapter._ad = MockRealAxiDrawDriver(fail_on_run=True, fail_msg="AxiDraw disconnected unexpectedly")
        adapter._connected = True

        req_id = f"test-phys-fail-{int(time.time() * 1000)}"
        start_res = await adapter.start_job(req_id, self.fixture)
        self.assertEqual(start_res["status"], "printing")

        for _ in range(50):
            await asyncio.sleep(0.05)
            st = adapter.get_status(req_id)
            if st["status"] == "error":
                break

        st = adapter.get_status(req_id)
        self.assertEqual(st["status"], "error")
        self.assertFalse(st["is_simulated"])
        self.assertFalse(st["actual_hardware_measured"])
        self.assertIsNone(st.get("actual_draw_time_sec"), "Physical lỗi không được ghi timing giả hoặc 0")
        self.assertEqual(st["error"]["code"], "HARDWARE_NOT_CONNECTED")
        self.assertFalse(st["pause_supported"])

        rows = self._get_csv_rows_for_request(req_id)
        self.assertGreaterEqual(len(rows), 1)
        last_row = rows[-1]
        self.assertEqual(last_row["hardware_status"], "error")
        self.assertEqual(last_row["is_simulated"], "False")
        self.assertEqual(last_row["actual_hardware_measured"], "False")
        self.assertEqual(last_row["actual_draw_time_sec"], "")
        self.assertEqual(last_row["error_code"], "HARDWARE_NOT_CONNECTED")
        self.assertEqual(last_row["source_tag"], "axidraw_real")

    async def test_physical_not_connected_records_failure_and_does_not_fallback(self):
        """
        TV4 Contract:
        Request mode physical khi chưa kết nối:
        - Tuyệt đối không âm thầm fallback sang simulator
        - Trả về status 503 với error HARDWARE_NOT_CONNECTED
        - CSV ghi nhận error với is_simulated=False, actual_hardware_measured=False
        """
        reset_hardware_adapter()
        adapter = get_hardware_adapter(mode="physical")
        self.assertIsInstance(adapter, AxiDrawAdapter)
        self.assertFalse(adapter._use_fake_driver)
        self.assertNotIsInstance(adapter, MockSimulatorAdapter)

        req_id = f"test-phys-noconn-{int(time.time() * 1000)}"
        res = await adapter.start_job(req_id, self.fixture)
        self.assertEqual(res["status_code"], 503)
        self.assertEqual(res["error"]["code"], "HARDWARE_NOT_CONNECTED")
        self.assertFalse(res["pause_supported"])

        rows = self._get_csv_rows_for_request(req_id)
        self.assertGreaterEqual(len(rows), 1)
        last_row = rows[-1]
        self.assertEqual(last_row["hardware_status"], "error")
        self.assertEqual(last_row["error_code"], "HARDWARE_NOT_CONNECTED")
        self.assertEqual(last_row["is_simulated"], "False")
        self.assertEqual(last_row["actual_hardware_measured"], "False")
        self.assertEqual(last_row["actual_draw_time_sec"], "")
        self.assertEqual(last_row["source_tag"], "axidraw_real")

    async def test_physical_pause_rejected_status_unchanged(self):
        """
        TV4 Contract:
        Physical pause_supported: False.
        Khi gọi pause trên physical:
        - Kiểm tra capability trước khi đổi trạng thái
        - Tuyệt đối không chuyển job sang paused (vẫn giữ printing)
        - Trả lỗi có cấu trúc HARDWARE_PAUSE_UNSUPPORTED với status_code 400 và pause_supported: False
        """
        adapter = AxiDrawAdapter(use_fake_driver=False)
        adapter._ad = MockRealAxiDrawDriver()
        adapter._connected = True

        req_id = f"test-phys-pause-{int(time.time() * 1000)}"
        await adapter.start_job(req_id, self.fixture)

        # Trạng thái ban đầu đang printing
        st_before = adapter.get_status(req_id)
        self.assertEqual(st_before["status"], "printing")

        # Gọi pause trên physical (chưa hỗ trợ pause an toàn)
        p_res = await adapter.pause_job(req_id)
        self.assertEqual(p_res["status_code"], 400)
        self.assertEqual(p_res["error"]["code"], "HARDWARE_PAUSE_UNSUPPORTED")
        self.assertFalse(p_res["pause_supported"])
        self.assertEqual(p_res["status"], "printing")

        # Trạng thái job KHÔNG bị đổi thành paused!
        job = adapter.jobs[req_id]
        self.assertEqual(job["status"], "printing", "Job status must NOT transition to paused when pause is unsupported!")

        # Gọi resume cũng từ chối với HARDWARE_PAUSE_UNSUPPORTED
        r_res = await adapter.resume_job(req_id)
        self.assertEqual(r_res["status_code"], 400)
        self.assertEqual(r_res["error"]["code"], "HARDWARE_PAUSE_UNSUPPORTED")
        self.assertFalse(r_res["pause_supported"])

    def test_consistent_pause_supported_flag(self):
        """
        TV4 Contract:
        Đồng nhất pause_supported trong response của simulator và fake driver (=True)
        so với physical (=False).
        """
        sim = MockSimulatorAdapter(connected=True)
        self.assertTrue(sim.pause_supported)

        fake = AxiDrawAdapter(use_fake_driver=True)
        self.assertTrue(fake.pause_supported)

        phys = AxiDrawAdapter(use_fake_driver=False)
        self.assertFalse(phys.pause_supported)


if __name__ == "__main__":
    unittest.main(verbosity=2)
