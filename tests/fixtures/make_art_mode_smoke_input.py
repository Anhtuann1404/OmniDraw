"""Create the deterministic raster input for the TV2 Art Mode smoke specimen."""

from pathlib import Path

import cv2
import numpy as np


def main() -> None:
    image = np.full((420, 640, 3), 255, dtype=np.uint8)
    cv2.line(image, (85, 290), (185, 115), (0, 0, 0), 3)
    cv2.line(image, (185, 115), (285, 290), (0, 0, 0), 3)
    cv2.ellipse(image, (425, 195), (95, 75), 0, 20, 340, (0, 0, 0), 3)
    points = np.array([[95, 325], [190, 305], [285, 330], [380, 305], [475, 330], [555, 310]], dtype=np.int32)
    cv2.polylines(image, [points], False, (0, 0, 0), 2)
    target = Path(__file__).with_name("tv2_art_mode_smoke_input.png")
    if not cv2.imwrite(str(target), image):
        raise OSError(f"Could not write {target}")


if __name__ == "__main__":
    main()
