"""
OmniDraw Scan-Validation Pipeline — Master Orchestrator & CLI Runner.

Executes end-to-end validation on 600 DPI flatbed scans of P01..P04:
1. Fiducial Marker Detection
2. Perspective Rectification (Canonical A4 at 600 DPI)
3. Calibration Scale Check (50mm ruler & aspect ratio square)
4. Deterministic Auto-Cropping
5. Quality Control & Boundary Overflow Assessment
6. Report Generation & Artifact Persistence
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import cv2
import numpy as np

# Ensure repo root is on sys.path for direct script execution
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.scan_validator.specs import DEFAULT_DPI, get_form_specs
from backend.scan_validator.fiducial_detector import detect_fiducials, FiducialDetectionResult
from backend.scan_validator.rectifier import rectify_scan, RectificationResult
from backend.scan_validator.calibration_checker import check_calibration, CalibrationCheckResult
from backend.scan_validator.auto_cropper import crop_sheet, ExtractedCrop
from backend.scan_validator.qc_evaluator import CropQCResult


@dataclass
class ScanValidationReport:
    is_success: bool
    form_type: str
    input_file: str
    target_dpi: int
    overall_status: str  # "SHEET_PASS", "SHEET_WARNING", "SHEET_REJECTED"
    fiducials: Dict[str, Any]
    calibration: Dict[str, Any]
    summary: Dict[str, Any]
    crops_metadata: List[Dict[str, Any]]
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def save_json(self, output_path: Union[str, Path]) -> None:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


class ScanValidationPipeline:
    """Bộ điều phối toàn trình xử lý và kiểm định ảnh quét OmniDraw."""

    def __init__(self, dpi: int = DEFAULT_DPI):
        self.dpi = dpi

    def process(
        self,
        image_input: Union[str, Path, np.ndarray],
        form_type: str = "P01",
        output_dir: Optional[Union[str, Path]] = None,
        save_crops: bool = True,
        save_rectified: bool = True,
    ) -> ScanValidationReport:
        """
        Xử lý toàn bộ pipeline cho 1 ảnh quét.

        Args:
            image_input: Đường dẫn file ảnh hoặc mảng numpy ảnh.
            form_type: Tên biểu mẫu ("P01", "P02", "P03", "P04").
            output_dir: Thư mục lưu kết quả ảnh nắn, ảnh crop và báo cáo JSON.
            save_crops: Có lưu ảnh crop ra đĩa hay không.
            save_rectified: Có lưu ảnh canvas nắn thẳng ra đĩa hay không.

        Returns:
            ScanValidationReport chứa toàn bộ thông tin kiểm định.
        """
        input_filename = "in_memory_array"
        if isinstance(image_input, (str, Path)):
            input_path = Path(image_input)
            input_filename = input_path.name
            if not input_path.exists():
                return ScanValidationReport(
                    is_success=False,
                    form_type=form_type,
                    input_file=str(input_path),
                    target_dpi=self.dpi,
                    overall_status="SHEET_REJECTED",
                    fiducials={},
                    calibration={},
                    summary={},
                    crops_metadata=[],
                    error_message=f"Input file does not exist: {input_path}",
                )
            image = cv2.imread(str(input_path))
            if image is None:
                return ScanValidationReport(
                    is_success=False,
                    form_type=form_type,
                    input_file=str(input_path),
                    target_dpi=self.dpi,
                    overall_status="SHEET_REJECTED",
                    fiducials={},
                    calibration={},
                    summary={},
                    crops_metadata=[],
                    error_message=f"Failed to decode image: {input_path}",
                )
        else:
            image = image_input

        # 1. Phát hiện 4 mốc quang học Fiducials
        fid_res: FiducialDetectionResult = detect_fiducials(image, dpi=self.dpi)
        if not fid_res.is_success:
            return ScanValidationReport(
                is_success=False,
                form_type=form_type,
                input_file=input_filename,
                target_dpi=self.dpi,
                overall_status="SHEET_REJECTED",
                fiducials=asdict(fid_res),
                calibration={},
                summary={"reason": "Fiducial detection failed"},
                crops_metadata=[],
                error_message=f"Fiducial detection failed: {fid_res.error_message}",
            )

        # 2. Nắn chỉnh phối cảnh đưa về Canvas A4 chuẩn
        rect_res: RectificationResult = rectify_scan(
            image, fid_res.centers, target_dpi=self.dpi
        )
        if not rect_res.is_success or rect_res.rectified_image is None:
            return ScanValidationReport(
                is_success=False,
                form_type=form_type,
                input_file=input_filename,
                target_dpi=self.dpi,
                overall_status="SHEET_REJECTED",
                fiducials=asdict(fid_res),
                calibration={},
                summary={"reason": "Rectification failed"},
                crops_metadata=[],
                error_message=f"Rectification failed: {rect_res.error_message}",
            )

        rectified_img = rect_res.rectified_image

        # 3. Kiểm định dung sai khối kiểm chuẩn
        calib_res: CalibrationCheckResult = check_calibration(rectified_img, dpi=self.dpi)

        # 4. Tự động cắt tách các ô mẫu viết tay
        extracted_crops: List[ExtractedCrop] = crop_sheet(
            rectified_img, form_type=form_type, dpi=self.dpi, extract_full_cell=True
        )

        # 5. Đánh giá thống kê chất lượng QC toàn trang
        expected_specs = get_form_specs(form_type)
        pass_count = sum(1 for c in extracted_crops if c.qc_result.qc_status == "QC_PASS")
        flagged_count = sum(1 for c in extracted_crops if c.qc_result.qc_status == "QC_FLAGGED")
        empty_count = sum(1 for c in extracted_crops if c.qc_result.qc_status == "QC_EMPTY")
        rejected_count = sum(1 for c in extracted_crops if c.qc_result.qc_status == "QC_REJECTED")

        # Xác định trạng thái chung của trang phiếu
        if not calib_res.overall_pass:
            overall_status = "SHEET_WARNING"
        elif rejected_count > 0:
            overall_status = "SHEET_WARNING" if rejected_count <= 2 else "SHEET_REJECTED"
        elif flagged_count > 0 or empty_count > 0:
            overall_status = "SHEET_WARNING"
        else:
            overall_status = "SHEET_PASS"

        # 6. Chuẩn bị metadata và lưu trữ artifact nếu có output_dir
        crops_meta = []
        out_p = Path(output_dir) if output_dir else None

        if out_p:
            out_p.mkdir(parents=True, exist_ok=True)
            crops_dir = out_p / "crops"
            if save_crops:
                crops_dir.mkdir(parents=True, exist_ok=True)

            if save_rectified:
                rect_file = out_p / "rectified_canvas.png"
                cv2.imwrite(str(rect_file), rectified_img)

        for c in extracted_crops:
            crop_file_rel = None
            full_file_rel = None

            if out_p and save_crops:
                crop_filename = f"{c.sample_id}_crop.png"
                crop_filepath = out_p / "crops" / crop_filename
                cv2.imwrite(str(crop_filepath), c.crop_image)
                crop_file_rel = str(Path("crops") / crop_filename)

                if c.full_cell_image is not None:
                    full_filename = f"{c.sample_id}_full.png"
                    full_filepath = out_p / "crops" / full_filename
                    cv2.imwrite(str(full_filepath), c.full_cell_image)
                    full_file_rel = str(Path("crops") / full_filename)

            crops_meta.append({
                "sample_id": c.sample_id,
                "prompt": c.prompt,
                "context_tag": c.context_tag,
                "bbox_mm": list(c.bbox_mm),
                "writing_bbox_mm": list(c.writing_bbox_mm),
                "crop_file": crop_file_rel,
                "full_cell_file": full_file_rel,
                "qc_status": c.qc_result.qc_status,
                "has_ink": c.qc_result.has_ink,
                "ink_ratio_percent": c.qc_result.ink_ratio_percent,
                "background_mean": c.qc_result.background_mean,
                "overflow_detected": c.qc_result.overflow_detected,
                "overflow_details": c.qc_result.overflow_details,
                "warnings": c.qc_result.warnings,
                "is_valid_for_dataset": c.qc_result.is_valid_for_dataset,
            })

        summary = {
            "total_expected_samples": len(expected_specs),
            "total_extracted_samples": len(extracted_crops),
            "qc_pass_count": pass_count,
            "qc_flagged_count": flagged_count,
            "qc_empty_count": empty_count,
            "qc_rejected_count": rejected_count,
            "calibration_pass": calib_res.overall_pass,
        }

        report = ScanValidationReport(
            is_success=True,
            form_type=form_type,
            input_file=input_filename,
            target_dpi=self.dpi,
            overall_status=overall_status,
            fiducials=asdict(fid_res),
            calibration=asdict(calib_res),
            summary=summary,
            crops_metadata=crops_meta,
            error_message=None,
        )

        if out_p:
            report_file = out_p / "validation_report.json"
            report.save_json(report_file)

        return report


def main():
    parser = argparse.ArgumentParser(description="OmniDraw Scan-Validation Pipeline CLI")
    parser.add_argument("--input", "-i", required=True, help="Path to raw scanned PNG image")
    parser.add_argument("--form", "-f", default="P01", choices=["P01", "P02", "P03", "P04"], help="Form type")
    parser.add_argument("--output", "-o", default=None, help="Output directory to save rectified canvas and crops")
    parser.add_argument("--dpi", type=int, default=DEFAULT_DPI, help="Scan DPI (default 600)")
    args = parser.parse_args()

    pipeline = ScanValidationPipeline(dpi=args.dpi)
    report = pipeline.process(
        image_input=args.input,
        form_type=args.form,
        output_dir=args.output,
    )

    print(f"============================================================")
    print(f"OmniDraw Scan Validation: {args.input} (Form {args.form})")
    print(f"Status: {report.overall_status} (Success: {report.is_success})")
    if report.error_message:
        print(f"Error: {report.error_message}")
    else:
        print(f"Fiducials: 4/4 Detected (Skew: {report.fiducials.get('estimated_skew_deg')} deg)")
        print(f"Calibration: Overall Pass = {report.calibration.get('overall_pass')}")
        print(f"Samples Extracted: {report.summary.get('total_extracted_samples')}/{report.summary.get('total_expected_samples')}")
        print(f"QC Breakdown: Pass={report.summary.get('qc_pass_count')}, Flagged={report.summary.get('qc_flagged_count')}, Empty={report.summary.get('qc_empty_count')}")
    print(f"============================================================")


if __name__ == "__main__":
    main()
