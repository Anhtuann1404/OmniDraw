import csv
import os
from typing import Dict, Any

CSV_COLUMNS = [
    "request_id", "timestamp", "dataset_item_id", "method_tag", "input_type",
    "style", "model_used", "ai_processing_time_ms", "svg_metrics.total_path_length_mm",
    "svg_metrics.pen_lift_distance_mm", "svg_metrics.pen_lift_count",
    "svg_metrics.optimize_time_ms", "actual_draw_time_sec", "final_status", "error_code"
]


def log_experiment_csv(payload_dict: Dict[str, Any], log_file_path: str):
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    file_exists = os.path.isfile(log_file_path)

    with open(log_file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()

        row = {col: payload_dict.get(col, "") for col in CSV_COLUMNS}
        writer.writerow(row)