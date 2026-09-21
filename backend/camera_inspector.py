"""
OmniDraw - Module Thị giác Máy tính: Giám sát Giấy & Camera (Closed-Loop Vision)
=============================================================================
Kiểm tra tình trạng giấy trước khi vẽ:
- Phát hiện có giấy trắng trên bàn hay không (Pre-flight check).
- Đo góc nghiêng (skew angle) để tự động nắn thẳng/bù trừ tọa độ.
- Đo độ sạch của giấy (Cleanliness ratio) để cảnh báo giấy đã dùng.
- Trả về ảnh preview base64 có vẽ bounding box 4 góc để hiển thị lên Web UI.
"""

import base64
import math
import cv2
import numpy as np


def _normalize_paper_rect(rect):
    """Chuẩn hóa góc nghiêng [-45, 45] độ và cạnh dài/cạnh ngắn."""
    (cx, cy), (w, h), angle = rect
    if w < h:
        w, h = h, w
        angle += 90.0
    while angle > 45.0:
        angle -= 90.0
    while angle < -45.0:
        angle += 90.0
    return (float(cx), float(cy)), (float(w), float(h)), float(angle)


def inspect_paper(frame=None, camera_index=0, min_paper_area=30000):
    """
    Kiểm tra tình trạng giấy từ frame ảnh hoặc webcam.
    # ponytail: dùng Otsu threshold + minAreaRect sẵn có của OpenCV, không cần model AI nặng.
    """
    is_live = False
    if frame is None:
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            is_live = ret and (frame is not None)

    if frame is None:
        # Fallback khi chưa cắm webcam: trả trạng thái mô phỏng an toàn
        return {
            "status": "camera_unavailable",
            "has_paper": True,
            "is_live_camera": False,
            "skew_angle_deg": 0.0,
            "cleanliness_percent": 100.0,
            "paper_type": "A4 (Gia lap)",
            "recommendation": "ready",
            "preview_base64": None,
            "message": "Khong ket noi duoc camera vat ly, su dung vi tri giay mac dinh."
        }

    h_img, w_img = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Otsu threshold tách vùng sáng (giấy trắng) trên nền tối
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return {
            "status": "no_paper",
            "has_paper": False,
            "is_live_camera": is_live,
            "skew_angle_deg": 0.0,
            "cleanliness_percent": 0.0,
            "paper_type": "None",
            "recommendation": "insert_paper",
            "preview_base64": _encode_jpeg(frame),
            "message": "Khong tim thay giay tren ban ve. Vui long dat giay vao."
        }

    largest_contour = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest_contour)

    if area < min_paper_area:
        return {
            "status": "paper_too_small",
            "has_paper": False,
            "is_live_camera": is_live,
            "skew_angle_deg": 0.0,
            "cleanliness_percent": 0.0,
            "paper_type": "Unknown",
            "recommendation": "insert_paper",
            "preview_base64": _encode_jpeg(frame),
            "message": "Dien tich giay qua nho hoac bi che khuat mot phan."
        }

    # Bóc tách hình chữ nhật xoay góc
    rect = cv2.minAreaRect(largest_contour)
    (cx, cy), (w, h), angle = _normalize_paper_rect(rect)

    # Đánh giá tỷ lệ khổ giấy (A4 ~ 1.414)
    aspect_ratio = w / max(1.0, h)
    if 1.25 <= aspect_ratio <= 1.6:
        paper_type = "A4" if w > 350 else "A5"
    else:
        paper_type = "Custom"

    # Đo độ sạch (tỷ lệ điểm ảnh trắng bên trong vùng giấy)
    mask = np.zeros((h_img, w_img), dtype=np.uint8)
    box_pts = cv2.boxPoints(((cx, cy), (w, h), angle)).astype(np.int32)
    cv2.fillPoly(mask, [box_pts], 255)
    
    paper_pixels = gray[mask == 255]
    if len(paper_pixels) > 0:
        dark_pixels = np.count_nonzero(paper_pixels < 140)
        soiled_ratio = dark_pixels / len(paper_pixels)
        cleanliness = max(0.0, min(100.0, round((1.0 - soiled_ratio) * 100.0, 1)))
    else:
        cleanliness = 100.0

    # Khuyến nghị
    if abs(angle) > 5.0:
        recommendation = "realign_paper"
        msg = f"Phat hien giay {paper_type} nhung bi lech {angle:+.1f} do. He thong se tu dong bu tru goc xoay."
    elif cleanliness < 75.0:
        recommendation = "warn_soiled"
        msg = f"Phat hien giay {paper_type} co muc cu (do sach {cleanliness}%). Khuyen nghi doi giay moi."
    else:
        recommendation = "ready"
        msg = f"Giay {paper_type} hop le, san sang ve (goc lech: {angle:+.1f} do, do sach: {cleanliness}%)."

    # Vẽ bounding box overlay màu xanh lá lên ảnh preview
    preview_frame = frame.copy()
    cv2.drawContours(preview_frame, [box_pts], 0, (0, 255, 0), 2)
    cv2.circle(preview_frame, (int(cx), int(cy)), 5, (0, 0, 255), -1)
    cv2.putText(preview_frame, f"{paper_type} | {angle:+.1f} deg | Clean: {cleanliness}%",
                (max(10, int(cx - w / 2)), max(30, int(cy - h / 2 - 10))),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    return {
        "status": "success",
        "has_paper": True,
        "is_live_camera": is_live,
        "skew_angle_deg": round(angle, 2),
        "center_px": [round(cx, 1), round(cy, 1)],
        "dimensions_px": [round(w, 1), round(h, 1)],
        "aspect_ratio": round(aspect_ratio, 2),
        "cleanliness_percent": cleanliness,
        "paper_type": paper_type,
        "recommendation": recommendation,
        "preview_base64": _encode_jpeg(preview_frame),
        "message": msg
    }


def _encode_jpeg(img_bgr):
    """Chuyển ảnh OpenCV BGR thành chuỗi Base64 Data URL để UI render trực tiếp."""
    success, buffer = cv2.imencode(".jpg", img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 80])
    if not success:
        return None
    b64_str = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_str}"


def _run_self_check():
    """Ponytail runnable check: assert synthetic paper detection precision."""
    img = np.zeros((600, 800, 3), dtype=np.uint8) + 40
    center = (400, 300)
    size = (420, 297)
    angle_gt = 3.5

    box = cv2.boxPoints((center, size, angle_gt)).astype(np.int32)
    cv2.fillPoly(img, [box], (245, 245, 245))

    res = inspect_paper(frame=img)
    assert res["has_paper"] is True, "Phai phat hien co giay"
    assert abs(res["skew_angle_deg"] - angle_gt) < 0.5, f"Goc do lech: {res['skew_angle_deg']} vs {angle_gt}"
    assert res["cleanliness_percent"] >= 95.0, f"Giay tong hop phai sach: {res['cleanliness_percent']}"
    assert res["preview_base64"].startswith("data:image/jpeg;base64,"), "Preview phai la base64 hop le"
    print(f"[CAMERA SELF-CHECK PASS] Paper: {res['paper_type']}, Angle: {res['skew_angle_deg']} deg (GT: {angle_gt}), Clean: {res['cleanliness_percent']}%")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OmniDraw Camera Paper Inspector")
    parser.add_argument("--self-check", action="store_true", help="Chay kiem tra tu dong")
    parser.add_argument("--device", type=int, default=0, help="Camera device index (mac dinh: 0)")
    args = parser.parse_args()

    if args.self_check:
        _run_self_check()
    else:
        result = inspect_paper(camera_index=args.device)
        preview = result.pop("preview_base64")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"Preview image base64 length: {len(preview) if preview else 0}")
