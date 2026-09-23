"""
OmniDraw Scan-Validation Pipeline Package.

Provides automated fiducial detection, perspective rectification,
scale calibration checks, deterministic auto-cropping, and QC evaluation
for OmniDraw handwriting collection sheets (P01..P04).
"""

from backend.scan_validator.specs import (
    A4_WIDTH_MM,
    A4_HEIGHT_MM,
    DEFAULT_DPI,
    FIDUCIAL_SIZE_MM,
    FIDUCIAL_THEORETICAL_CENTERS_MM,
    mm_to_px,
    px_to_mm,
    get_form_specs,
    CropItemSpec,
)
from backend.scan_validator.fiducial_detector import (
    detect_fiducials,
    FiducialDetectionResult,
)
from backend.scan_validator.rectifier import (
    rectify_scan,
    RectificationResult,
)
from backend.scan_validator.calibration_checker import (
    check_calibration,
    CalibrationCheckResult,
)
from backend.scan_validator.qc_evaluator import (
    evaluate_crop_qc,
    CropQCResult,
)
from backend.scan_validator.auto_cropper import (
    crop_sheet,
    ExtractedCrop,
)
from backend.scan_validator.pipeline import (
    ScanValidationPipeline,
    ScanValidationReport,
)

__all__ = [
    "A4_WIDTH_MM",
    "A4_HEIGHT_MM",
    "DEFAULT_DPI",
    "FIDUCIAL_SIZE_MM",
    "FIDUCIAL_THEORETICAL_CENTERS_MM",
    "mm_to_px",
    "px_to_mm",
    "get_form_specs",
    "CropItemSpec",
    "detect_fiducials",
    "FiducialDetectionResult",
    "rectify_scan",
    "RectificationResult",
    "check_calibration",
    "CalibrationCheckResult",
    "evaluate_crop_qc",
    "CropQCResult",
    "crop_sheet",
    "ExtractedCrop",
    "ScanValidationPipeline",
    "ScanValidationReport",
]
