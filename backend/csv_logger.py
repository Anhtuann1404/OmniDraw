import csv
import os
from typing import Any, Dict, Optional, Sequence

CSV_COLUMNS = [
    "request_id", "timestamp", "dataset_item_id", "method_tag", "input_type",
    "style", "model_used", "ai_processing_time_ms", "svg_metrics.total_path_length_mm",
    "svg_metrics.pen_lift_distance_mm", "svg_metrics.pen_lift_count",
    "svg_metrics.optimize_time_ms", "actual_draw_time_sec", "final_status", "error_code"
]


def log_experiment_csv(
    payload_dict: Dict[str, Any],
    log_file_path: str,
    columns: Optional[Sequence[str]] = None,
):
    fieldnames = list(columns or CSV_COLUMNS)
    log_dir = os.path.dirname(log_file_path)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    file_exists = os.path.isfile(log_file_path)
    has_content = file_exists and os.path.getsize(log_file_path) > 0

    if has_content:
        with open(log_file_path, newline="", encoding="utf-8") as existing_file:
            existing_header = next(csv.reader(existing_file), [])
        if existing_header != fieldnames:
            raise ValueError(
                f"CSV schema mismatch for '{log_file_path}': "
                f"expected {fieldnames}, found {existing_header}"
            )

    with open(log_file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not has_content:
            writer.writeheader()

        row = {col: payload_dict.get(col, "") for col in fieldnames}
        writer.writerow(row)
