import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from handwriting import text_to_strokes
from api_generator import APIResponse

client = TestClient(app)

SAMPLE_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAIAAACRXR/mAAABTElEQVRYCc3BAYpaWQBFwXv2v"
    "+gaCAgvJJ2xW79aFfZ5wj5P2OcJ+zxhh2ob9lZhN9VusPcJu6l2wN4k7FDtgL1D2O+qHbCX"
    "C/tDtQP2WmF/U+2AvVDYF6odsFcJ+1q1A/YSYf9U7YBdL+z/VDtgFwu7Q7UDdqWw+1Q7YJc"
    "Ju1u1A3aNsO+odsAuEPZN1Q7Ys4V9X7UD9lRhP1LtgD1P2E9VO2BPEvaAagfsGcIeU+2APSz"
    "sYdUO2GPCnqHaAXtA2JNUO2A/FfY81Q7Yj4Q9VbUD9n1hz1btgH1T2AWqHbDvCLtGtQN2t7D"
    "LVDtg9wm7UrUDdoewi1U7YP8n7HrVDtg/hb1EtQP2tbBXqXbAvhD2QtUO2N+EvVa1A/aHsJe"
    "rdsB+F/YO1Q7YIexNqh2wm7D3qXbAfgl7q2o32C9h71Ztw27CPk/Y5wn7PP8BPpoWrPdqkjQ"
    "AAAAASUVORK5CYII="
)

BASE_PAYLOAD = {
    "request_id": "test_req_valid_001",
    "input_type": "handwriting",
    "prompt": "Xin chào OmniDraw, đây là bài kiểm tra.",
    "style": "hand_hocsinh",
    "options": {
        "font": "oly",
        "letter_type": "general",
        "seed": 42,
        "target_paper_size_mm": [210.0, 297.0],
    },
}


def test_valid_handwriting_request():
    """Request hợp lệ với đầy đủ tham số chuẩn phải trả về status success, svg_ready=True, và metrics."""
    res = client.post("/api/ai/generate", json=BASE_PAYLOAD)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["request_id"] == BASE_PAYLOAD["request_id"]
    assert data["svg_ready"] is True
    assert "svg_metrics" in data
    assert data["svg_metrics"]["pen_lift_count"] > 0
    assert data["meta"]["seed"] == 42
    assert data["meta"]["letter_type"] == "general"


def test_seed_determinism():
    """Cùng text và cùng seed phải cho metrics giống nhau hoàn toàn."""
    payload1 = {**BASE_PAYLOAD, "request_id": "test_det_1", "options": {**BASE_PAYLOAD["options"], "seed": 9999}}
    payload2 = {**BASE_PAYLOAD, "request_id": "test_det_2", "options": {**BASE_PAYLOAD["options"], "seed": 9999}}
    res1 = client.post("/api/ai/generate", json=payload1).json()
    res2 = client.post("/api/ai/generate", json=payload2).json()
    assert res1["status"] == "success"
    assert res2["status"] == "success"
    assert res1["svg_metrics"]["total_path_length_mm"] == res2["svg_metrics"]["total_path_length_mm"]
    assert res1["svg_metrics"]["pen_lift_distance_mm"] == res2["svg_metrics"]["pen_lift_distance_mm"]
    assert res1["svg_metrics"]["pen_lift_count"] == res2["svg_metrics"]["pen_lift_count"]


def test_invalid_style_rejected_without_silent_fallback():
    """Style không tồn tại trong STYLE_CONFIGS phải bị từ chối với lỗi INPUT_INVALID_FORMAT."""
    invalid_styles = ["hand_fake", "abc_xyz", "sketch", "", "invalid_style"]
    for idx, invalid_style in enumerate(invalid_styles):
        payload = {
            **BASE_PAYLOAD,
            "request_id": f"test_req_invalid_style_{idx}",
            "style": invalid_style,
        }
        res = client.post("/api/ai/generate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "error", f"Style {invalid_style} không được phép fallback ngầm thành công"
        assert data["error"]["code"] == "INPUT_INVALID_FORMAT"
        assert "Phong cách" in data["error"]["message"]


def test_valid_styles_all_succeed():
    """Tất cả 4 style chuẩn trong STYLE_CONFIGS đều phải render thành công."""
    valid_styles = ["hand_hocsinh", "hand_nguoilon", "hand_thuphap", "hand_chukinhanh"]
    for idx, style in enumerate(valid_styles):
        payload = {
            **BASE_PAYLOAD,
            "request_id": f"test_req_valid_style_{idx}",
            "style": style,
        }
        res = client.post("/api/ai/generate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success", f"Style {style} phải render thành công"


def test_valid_fonts_succeed():
    """Tất cả các font trong RENDER_PROFILES với letter_type=general đều phải render thành công."""
    valid_fonts = ["oly", "omni_casual", "thanhdam", "thuphap", "cursive"]
    for idx, font in enumerate(valid_fonts):
        payload = {
            **BASE_PAYLOAD,
            "request_id": f"test_req_valid_font_{idx}",
            "options": {
                **BASE_PAYLOAD["options"],
                "font": font,
                "letter_type": "general",
            },
        }
        res = client.post("/api/ai/generate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success", f"Font {font} phải thành công"


def test_invalid_font_rejected():
    """Font không nằm trong RENDER_PROFILES phải trả lỗi UNSUPPORTED_FONT."""
    for idx, font in enumerate(["comic_sans", "custom", "times_new_roman", "xyz"]):
        payload = {
            **BASE_PAYLOAD,
            "request_id": f"test_req_invalid_font_{idx}",
            "options": {
                **BASE_PAYLOAD["options"],
                "font": font,
            },
        }
        res = client.post("/api/ai/generate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "UNSUPPORTED_FONT"


def test_font_omitted_defaults_to_oly():
    """Nếu không truyền font trong options, hệ thống dùng default 'oly' và chạy thành công."""
    payload = {
        "request_id": "test_req_font_omitted",
        "input_type": "handwriting",
        "prompt": "Kiểm tra font mặc định.",
        "style": "hand_hocsinh",
        "options": {
            "seed": 100,
        },
    }
    res = client.post("/api/ai/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"


def test_formal_letter_type_compatibility():
    """letter_type='formal' hợp lệ với font pack legacy ('oly'), nhưng không tương thích với 'omni_casual'."""
    # 1. Với oly (legacy) -> Phải thành công
    payload_formal_oly = {
        **BASE_PAYLOAD,
        "request_id": "test_formal_oly",
        "options": {
            **BASE_PAYLOAD["options"],
            "font": "oly",
            "letter_type": "formal",
        },
    }
    res = client.post("/api/ai/generate", json=payload_formal_oly)
    assert res.status_code == 200
    assert res.json()["status"] == "success"

    # 2. Với omni_casual -> Phải trả UNSUPPORTED_LETTER_TYPE
    payload_formal_casual = {
        **BASE_PAYLOAD,
        "request_id": "test_formal_casual",
        "options": {
            **BASE_PAYLOAD["options"],
            "font": "omni_casual",
            "letter_type": "formal",
        },
    }
    res = client.post("/api/ai/generate", json=payload_formal_casual)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "UNSUPPORTED_LETTER_TYPE"


def test_invalid_letter_type_rejected():
    """letter_type không nằm trong LETTER_TYPES phải trả lỗi UNSUPPORTED_LETTER_TYPE."""
    for idx, lt in enumerate(["business", "informal", "casual", ""]):
        payload = {
            **BASE_PAYLOAD,
            "request_id": f"test_invalid_lt_{idx}",
            "options": {
                **BASE_PAYLOAD["options"],
                "letter_type": lt,
            },
        }
        res = client.post("/api/ai/generate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "UNSUPPORTED_LETTER_TYPE"


def test_seed_boundary_and_type_validation():
    """Seed phải là số nguyên không âm trong khoảng [0, 4294967295], không chấp nhận float, string, boolean."""
    # 1. Hợp lệ: biên 0 và 4294967295
    for seed in [0, 4294967295]:
        payload = {
            **BASE_PAYLOAD,
            "request_id": f"test_seed_valid_{seed}",
            "options": {**BASE_PAYLOAD["options"], "seed": seed},
        }
        res = client.post("/api/ai/generate", json=payload)
        assert res.status_code == 200
        assert res.json()["status"] == "success"

    # 2. Không hợp lệ: ngoài biên, kiểu dữ liệu sai
    invalid_seeds = [-1, 4294967296, True, False, "42", 3.14]
    for idx, invalid_seed in enumerate(invalid_seeds):
        payload = {
            **BASE_PAYLOAD,
            "request_id": f"test_seed_invalid_{idx}",
            "options": {**BASE_PAYLOAD["options"], "seed": invalid_seed},
        }
        res = client.post("/api/ai/generate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "error", f"Seed {invalid_seed} phải bị từ chối"
        assert data["error"]["code"] == "INVALID_SEED"


def test_empty_handwriting_text_rejected():
    """Nội dung prompt rỗng hoặc chỉ có khoảng trắng phải trả lỗi EMPTY_TEXT."""
    for idx, empty_prompt in enumerate(["", "   ", "\n\t  "]):
        payload = {
            **BASE_PAYLOAD,
            "request_id": f"test_empty_{idx}",
            "prompt": empty_prompt,
            "image_base64": None,
        }
        res = client.post("/api/ai/generate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "EMPTY_TEXT"


def test_invalid_target_paper_size():
    """target_paper_size_mm sai định dạng (null, len != 2, âm, 0, string, bool, NaN, Inf) phải trả lỗi INPUT_INVALID_FORMAT."""
    invalid_sizes = [
        None,
        "A4",
        [-210.0, 297.0],
        [0, 297.0],
        [210.0],
        [210.0, 297.0, 50.0],
        ["210", 297.0],
        [True, False],
        "210x297",
    ]
    for idx, paper_size in enumerate(invalid_sizes):
        payload = {
            **BASE_PAYLOAD,
            "request_id": f"test_paper_{idx}",
            "options": {**BASE_PAYLOAD["options"], "target_paper_size_mm": paper_size},
        }
        res = client.post("/api/ai/generate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "error", f"Paper size {paper_size} phải bị từ chối"
        assert data["error"]["code"] == "INPUT_INVALID_FORMAT"

    # Kiểm tra thêm trường hợp raw JSON chứa NaN và Infinity
    res_nan = client.post(
        "/api/ai/generate",
        content=b'{"request_id": "test_paper_nan", "input_type": "handwriting", "prompt": "Hi", "style": "hand_hocsinh", "options": {"target_paper_size_mm": [NaN, 297.0]}}',
        headers={"Content-Type": "application/json"},
    )
    assert res_nan.status_code == 200
    assert res_nan.json()["status"] == "error"
    assert res_nan.json()["error"]["code"] == "INPUT_INVALID_FORMAT"

    res_inf = client.post(
        "/api/ai/generate",
        content=b'{"request_id": "test_paper_inf", "input_type": "handwriting", "prompt": "Hi", "style": "hand_hocsinh", "options": {"target_paper_size_mm": [210.0, Infinity]}}',
        headers={"Content-Type": "application/json"},
    )
    assert res_inf.status_code == 200
    assert res_inf.json()["status"] == "error"
    assert res_inf.json()["error"]["code"] == "INPUT_INVALID_FORMAT"


def test_direct_engine_style_strict_validation():
    """Kiểm tra gọi trực tiếp hàm text_to_strokes ở tầng handwriting/engine.py cũng từ chối style sai."""
    with pytest.raises(ValueError, match="Phong cách chữ"):
        text_to_strokes("Xin chào", font="oly", style="hand_not_exist")


def test_explicit_font_null_or_invalid_type_rejected():
    """Truyền key 'font' nhưng value là null hoặc sai kiểu dữ liệu phải trả lỗi UNSUPPORTED_FONT."""
    for idx, invalid_val in enumerate([None, 123, False, []]):
        payload = {
            **BASE_PAYLOAD,
            "request_id": f"test_font_null_{idx}",
            "options": {
                **BASE_PAYLOAD["options"],
                "font": invalid_val,
            },
        }
        res = client.post("/api/ai/generate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "error", f"font={invalid_val!r} không được phép bỏ qua hoặc fallback ngầm"
        assert data["error"]["code"] == "UNSUPPORTED_FONT"


def test_letter_type_omitted_defaults_to_general():
    """Nếu không truyền letter_type trong options, hệ thống dùng default 'general' và chạy thành công."""
    payload = {
        "request_id": "test_req_lt_omitted",
        "input_type": "handwriting",
        "prompt": "Kiểm tra letter_type mặc định.",
        "style": "hand_hocsinh",
        "options": {
            "font": "oly",
            "seed": 100,
        },
    }
    res = client.post("/api/ai/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["meta"]["letter_type"] == "general"


def test_explicit_letter_type_null_or_invalid_type_rejected():
    """Truyền key 'letter_type' nhưng value là null hoặc sai kiểu dữ liệu phải trả lỗi UNSUPPORTED_LETTER_TYPE."""
    for idx, invalid_val in enumerate([None, 123, False, []]):
        payload = {
            **BASE_PAYLOAD,
            "request_id": f"test_lt_null_{idx}",
            "options": {
                **BASE_PAYLOAD["options"],
                "letter_type": invalid_val,
            },
        }
        res = client.post("/api/ai/generate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "error", f"letter_type={invalid_val!r} không được phép bỏ qua hoặc fallback ngầm"
        assert data["error"]["code"] == "UNSUPPORTED_LETTER_TYPE"


def test_missing_style_structured_error():
    """Thiếu trường 'style' trong request handwriting phải trả structured error INPUT_INVALID_FORMAT (không phải HTTP 422)."""
    payload = {
        "request_id": "test_missing_style_001",
        "input_type": "handwriting",
        "prompt": "Kiểm tra thiếu style.",
        "options": {"font": "oly"},
    }
    res = client.post("/api/ai/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "INPUT_INVALID_FORMAT"
    assert "bắt buộc" in data["error"]["message"] or "Phong cách" in data["error"]["message"]


def test_style_null_or_invalid_type_structured_error():
    """style = null hoặc sai datatype trong request handwriting phải trả structured error INPUT_INVALID_FORMAT."""
    for idx, invalid_style in enumerate([None, 123, False, []]):
        payload = {
            "request_id": f"test_style_invalid_type_{idx}",
            "input_type": "handwriting",
            "prompt": "Kiểm tra style null/sai kiểu.",
            "style": invalid_style,
            "options": {"font": "oly"},
        }
        res = client.post("/api/ai/generate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "INPUT_INVALID_FORMAT"


def test_target_paper_size_omitted_defaults_to_a4():
    """Nếu không truyền key target_paper_size_mm trong options, backend dùng mặc định A4 [210, 297] và render thành công."""
    payload = {
        "request_id": "test_paper_omitted",
        "input_type": "handwriting",
        "prompt": "Kiểm tra khổ giấy mặc định A4.",
        "style": "hand_hocsinh",
        "options": {
            "font": "oly",
            "letter_type": "general",
            "seed": 42,
        },
    }
    res = client.post("/api/ai/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["svg_ready"] is True


def test_target_paper_size_valid_explicit():
    """Truyền target_paper_size_mm hợp lệ ([210.0, 297.0] hoặc [148.0, 210.0]) phải render thành công."""
    for idx, valid_size in enumerate([[210.0, 297.0], [148.0, 210.0], [297, 420]]):
        payload = {
            **BASE_PAYLOAD,
            "request_id": f"test_paper_valid_{idx}",
            "options": {
                **BASE_PAYLOAD["options"],
                "target_paper_size_mm": valid_size,
            },
        }
        res = client.post("/api/ai/generate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success", f"Paper size {valid_size} phải thành công"
        assert data["svg_ready"] is True


def test_art_mode_text_sketch_regression():
    """Art Mode text-to-drawing với style='sketch' không bị handwriting validation chặn nhầm và trả status success."""
    mock_resp = APIResponse(
        request_id="test_art_sketch",
        status="success",
        result_image_base64=SAMPLE_PNG_B64,
        model_used="mock-ai-dalle3",
        processing_time_ms=150,
    )
    payload = {
        "request_id": "test_art_sketch",
        "input_type": "text",
        "prompt": "A scenic landscape sketch with mountains and pine trees",
        "style": "sketch",
        "options": {
            "target_paper_size_mm": [210.0, 297.0],
        },
    }
    with patch("main.call_openai_image_api", return_value=mock_resp):
        res = client.post("/api/ai/generate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["svg_ready"] is True
        assert data["svg_metrics"] is not None
        assert "error" not in data or data["error"] is None


def test_art_mode_text_line_art_regression():
    """Art Mode text-to-drawing với style='line_art' không bị handwriting validation chặn nhầm và trả status success."""
    mock_resp = APIResponse(
        request_id="test_art_lineart",
        status="success",
        result_image_base64=SAMPLE_PNG_B64,
        model_used="mock-ai-dalle3",
        processing_time_ms=150,
    )
    payload = {
        "request_id": "test_art_lineart",
        "input_type": "text",
        "prompt": "Minimalist continuous line art of a rose flower",
        "style": "line_art",
        "options": {
            "target_paper_size_mm": [210.0, 297.0],
        },
    }
    with patch("main.call_openai_image_api", return_value=mock_resp):
        res = client.post("/api/ai/generate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["svg_ready"] is True
        assert data["svg_metrics"] is not None
        assert "error" not in data or data["error"] is None


def test_art_mode_image_upload_regression():
    """Art Mode image input với style='sketch' chuyển đổi ảnh sang SVG thành công."""
    payload = {
        "request_id": "test_art_img_upload",
        "input_type": "image",
        "image_base64": SAMPLE_PNG_B64,
        "style": "sketch",
        "options": {
            "target_paper_size_mm": [210.0, 297.0],
        },
    }
    res = client.post("/api/ai/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["svg_ready"] is True
    assert data["svg_metrics"] is not None
    assert "error" not in data or data["error"] is None


def test_art_mode_optional_style_handling():
    """Art Mode khi style là None hoặc thiếu không bị crash ngoài kiểm soát (tự động fallback về 'sketch' theo contract Art Mode)."""
    # 1. Image upload với style=None
    payload_img = {
        "request_id": "test_art_img_none_style",
        "input_type": "image",
        "image_base64": SAMPLE_PNG_B64,
        "style": None,
    }
    res_img = client.post("/api/ai/generate", json=payload_img)
    assert res_img.status_code == 200
    data_img = res_img.json()
    assert data_img["status"] == "success"
    assert data_img["svg_ready"] is True

    # 2. Text input với style=None (mock AI)
    mock_resp = APIResponse(
        request_id="test_art_text_none_style",
        status="success",
        result_image_base64=SAMPLE_PNG_B64,
        model_used="mock-ai-dalle3",
        processing_time_ms=100,
    )
    payload_text = {
        "request_id": "test_art_text_none_style",
        "input_type": "text",
        "prompt": "Abstract geometrical lines",
        "style": None,
    }
    with patch("main.call_openai_image_api", return_value=mock_resp):
        res_text = client.post("/api/ai/generate", json=payload_text)
        assert res_text.status_code == 200
        data_text = res_text.json()
        assert data_text["status"] == "success"
        assert data_text["svg_ready"] is True


def test_art_mode_invalid_input_graceful():
    """Art Mode thiếu prompt (text) hoặc thiếu image_base64 (image) trả lỗi có cấu trúc INPUT_INVALID_FORMAT, không crash."""
    # 1. input_type="text" nhưng prompt rỗng
    res_empty_prompt = client.post("/api/ai/generate", json={
        "request_id": "test_art_empty_prompt",
        "input_type": "text",
        "prompt": "",
        "style": "sketch",
    })
    assert res_empty_prompt.status_code == 200
    assert res_empty_prompt.json()["status"] == "error"
    assert res_empty_prompt.json()["error"]["code"] == "INPUT_INVALID_FORMAT"

    # 2. input_type="image" nhưng image_base64 rỗng
    res_empty_img = client.post("/api/ai/generate", json={
        "request_id": "test_art_empty_img",
        "input_type": "image",
        "image_base64": "",
        "style": "sketch",
    })
    assert res_empty_img.status_code == 200
    assert res_empty_img.json()["status"] == "error"
    assert res_empty_img.json()["error"]["code"] == "INPUT_INVALID_FORMAT"


def test_art_mode_style_defaults_downstream_verification():
    """Art Mode khi style omitted hoặc None phải tự động resolve thành 'sketch' và truyền xuống downstream."""
    mock_resp = APIResponse(
        request_id="test_art_style_default",
        status="success",
        result_image_base64=SAMPLE_PNG_B64,
        model_used="mock-ai-dalle3",
        processing_time_ms=100,
    )
    mock_svg_res = {
        "status": "success",
        "svg_metrics": {
            "pen_lift_count": 2,
            "pen_down_length_mm": 50.0,
            "pen_lift_distance_mm": 10.0,
            "total_path_length_mm": 60.0,
        },
    }

    # Case 1: Text mode, style omitted -> downstream nhận style="sketch"
    with patch("main.call_openai_image_api", return_value=mock_resp) as mock_api, \
         patch("main.svg_process", return_value=mock_svg_res) as mock_svg:
        res = client.post("/api/ai/generate", json={
            "request_id": "test_text_omitted_style",
            "input_type": "text",
            "prompt": "A modern building",
        })
        assert res.status_code == 200
        assert res.json()["status"] == "success"
        assert mock_api.call_args.kwargs.get("style") == "sketch"
        assert mock_svg.call_args.kwargs.get("style") == "sketch"

    # Case 2: Text mode, style=None -> downstream nhận style="sketch"
    with patch("main.call_openai_image_api", return_value=mock_resp) as mock_api, \
         patch("main.svg_process", return_value=mock_svg_res) as mock_svg:
        res = client.post("/api/ai/generate", json={
            "request_id": "test_text_null_style",
            "input_type": "text",
            "prompt": "A modern building",
            "style": None,
        })
        assert res.status_code == 200
        assert res.json()["status"] == "success"
        assert mock_api.call_args.kwargs.get("style") == "sketch"
        assert mock_svg.call_args.kwargs.get("style") == "sketch"

    # Case 3: Image mode, style omitted -> downstream nhận style="sketch"
    with patch("main.svg_process", return_value=mock_svg_res) as mock_svg:
        res = client.post("/api/ai/generate", json={
            "request_id": "test_img_omitted_style",
            "input_type": "image",
            "image_base64": SAMPLE_PNG_B64,
        })
        assert res.status_code == 200
        assert res.json()["status"] == "success"
        assert mock_svg.call_args.kwargs.get("style") == "sketch"

    # Case 4: Image mode, style=None -> downstream nhận style="sketch"
    with patch("main.svg_process", return_value=mock_svg_res) as mock_svg:
        res = client.post("/api/ai/generate", json={
            "request_id": "test_img_null_style",
            "input_type": "image",
            "image_base64": SAMPLE_PNG_B64,
            "style": None,
        })
        assert res.status_code == 200
        assert res.json()["status"] == "success"
        assert mock_svg.call_args.kwargs.get("style") == "sketch"


def test_art_mode_text_all_valid_styles_downstream_verification():
    """Text-to-Drawing với 4 style chuẩn (sketch, line_art, stipple, hatching) phải truyền chính xác style xuống API và SVG process."""
    valid_art_styles = ["sketch", "line_art", "stipple", "hatching"]
    mock_svg_res = {
        "status": "success",
        "svg_metrics": {
            "pen_lift_count": 2,
            "pen_down_length_mm": 50.0,
            "pen_lift_distance_mm": 10.0,
            "total_path_length_mm": 60.0,
        },
    }

    for style in valid_art_styles:
        mock_resp = APIResponse(
            request_id=f"test_text_style_{style}",
            status="success",
            result_image_base64=SAMPLE_PNG_B64,
            model_used="mock-ai-dalle3",
            processing_time_ms=100,
        )
        with patch("main.call_openai_image_api", return_value=mock_resp) as mock_api, \
             patch("main.svg_process", return_value=mock_svg_res) as mock_svg:
            res = client.post("/api/ai/generate", json={
                "request_id": f"test_text_style_{style}",
                "input_type": "text",
                "prompt": f"Artwork in style {style}",
                "style": style,
            })
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "success"
            assert mock_api.call_args.kwargs.get("style") == style
            assert mock_svg.call_args.kwargs.get("style") == style


def test_art_mode_image_all_valid_styles_downstream_verification():
    """Image-to-Drawing với 4 style chuẩn (sketch, line_art, stipple, hatching) phải truyền chính xác style xuống SVG process."""
    valid_art_styles = ["sketch", "line_art", "stipple", "hatching"]
    mock_svg_res = {
        "status": "success",
        "svg_metrics": {
            "pen_lift_count": 3,
            "pen_down_length_mm": 80.0,
            "pen_lift_distance_mm": 15.0,
            "total_path_length_mm": 95.0,
        },
    }

    for style in valid_art_styles:
        with patch("main.svg_process", return_value=mock_svg_res) as mock_svg:
            res = client.post("/api/ai/generate", json={
                "request_id": f"test_img_style_{style}",
                "input_type": "image",
                "image_base64": SAMPLE_PNG_B64,
                "style": style,
            })
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "success"
            assert mock_svg.call_args.kwargs.get("style") == style


def test_art_mode_invalid_style_rejected_without_side_effects():
    """Art Mode khi truyền style sai định dạng hoặc ngoài enum (kể cả style handwriting) phải reject ngay và không gọi downstream."""
    invalid_styles = ["abc", 123, "", "hand_hocsinh", ["sketch"], True]

    # Kiểm tra Text mode
    for idx, bad_style in enumerate(invalid_styles):
        with patch("main.call_openai_image_api") as mock_api, \
             patch("main.svg_process") as mock_svg:
            res = client.post("/api/ai/generate", json={
                "request_id": f"test_text_bad_style_{idx}",
                "input_type": "text",
                "prompt": "Draw a cat",
                "style": bad_style,
            })
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "error"
            assert data["error"]["code"] == "INPUT_INVALID_FORMAT"
            mock_api.assert_not_called()
            mock_svg.assert_not_called()

    # Kiểm tra Image mode
    for idx, bad_style in enumerate(invalid_styles):
        with patch("main.svg_process") as mock_svg:
            res = client.post("/api/ai/generate", json={
                "request_id": f"test_img_bad_style_{idx}",
                "input_type": "image",
                "image_base64": SAMPLE_PNG_B64,
                "style": bad_style,
            })
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "error"
            assert data["error"]["code"] == "INPUT_INVALID_FORMAT"
            mock_svg.assert_not_called()


def test_art_mode_empty_payload_rejected_without_side_effects():
    """Art Mode thiếu prompt (text) hoặc thiếu image_base64 (image) phải bị reject ngay trước khi gọi downstream."""
    # Text mode rỗng / whitespace / None
    for idx, empty_prompt in enumerate(["", "   ", None]):
        with patch("main.call_openai_image_api") as mock_api, \
             patch("main.svg_process") as mock_svg:
            res = client.post("/api/ai/generate", json={
                "request_id": f"test_empty_prompt_{idx}",
                "input_type": "text",
                "prompt": empty_prompt,
                "style": "sketch",
            })
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "error"
            assert data["error"]["code"] == "INPUT_INVALID_FORMAT"
            mock_api.assert_not_called()
            mock_svg.assert_not_called()

    # Image mode rỗng / whitespace / None
    for idx, empty_img in enumerate(["", "   ", None]):
        with patch("main.svg_process") as mock_svg:
            res = client.post("/api/ai/generate", json={
                "request_id": f"test_empty_img_{idx}",
                "input_type": "image",
                "image_base64": empty_img,
                "style": "sketch",
            })
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "error"
            assert data["error"]["code"] == "INPUT_INVALID_FORMAT"
            mock_svg.assert_not_called()


def test_invalid_input_type_rejected():
    """Bất kỳ input_type nào ngoài ('handwriting', 'letter', 'text', 'image') đều phải bị từ chối với INPUT_INVALID_FORMAT."""
    bad_types = ["unknown", "video", "audio", "", 123, None]
    for idx, bad_type in enumerate(bad_types):
        res = client.post("/api/ai/generate", json={
            "request_id": f"test_bad_type_{idx}",
            "input_type": bad_type,
            "prompt": "Hello world",
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "INPUT_INVALID_FORMAT"


def test_art_mode_target_paper_size_validation():
    """Art Mode cũng phải validate nghiêm ngặt target_paper_size_mm trước khi gọi downstream."""
    mock_resp = APIResponse(
        request_id="test_art_paper_size",
        status="success",
        result_image_base64=SAMPLE_PNG_B64,
        model_used="mock-ai-dalle3",
        processing_time_ms=100,
    )
    mock_svg_res = {
        "status": "success",
        "svg_metrics": {
            "pen_lift_count": 2,
            "pen_down_length_mm": 50.0,
            "pen_lift_distance_mm": 10.0,
            "total_path_length_mm": 60.0,
        },
    }

    # Invalid paper size rejected before downstream
    invalid_sizes = [None, [210.0], [210.0, 0], [0, 297], [-10, 200], "A4", [True, False], "210x297"]
    for idx, inv_size in enumerate(invalid_sizes):
        with patch("main.call_openai_image_api") as mock_api, \
             patch("main.svg_process") as mock_svg:
            res = client.post("/api/ai/generate", json={
                "request_id": f"test_art_bad_paper_{idx}",
                "input_type": "text",
                "prompt": "Draw a car",
                "options": {"target_paper_size_mm": inv_size},
            })
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "error"
            assert data["error"]["code"] == "INPUT_INVALID_FORMAT"
            mock_api.assert_not_called()
            mock_svg.assert_not_called()

    # Raw content for NaN and Inf
    with patch("main.call_openai_image_api") as mock_api:
        res_nan = client.post(
            "/api/ai/generate",
            content=b'{"request_id": "test_art_nan", "input_type": "text", "prompt": "Draw a car", "options": {"target_paper_size_mm": [NaN, 297.0]}}',
            headers={"Content-Type": "application/json"},
        )
        assert res_nan.status_code == 200
        assert res_nan.json()["status"] == "error"
        assert res_nan.json()["error"]["code"] == "INPUT_INVALID_FORMAT"
        mock_api.assert_not_called()

    # Valid custom paper size passed to svg_process
    with patch("main.call_openai_image_api", return_value=mock_resp), \
         patch("main.svg_process", return_value=mock_svg_res) as mock_svg:
        res = client.post("/api/ai/generate", json={
            "request_id": "test_art_custom_paper_ok",
            "input_type": "text",
            "prompt": "Draw a flower",
            "options": {"target_paper_size_mm": [148.0, 210.0]},
        })
        assert res.status_code == 200
        assert res.json()["status"] == "success"
        assert mock_svg.call_args.kwargs.get("target_paper_size_mm") == (148.0, 210.0)


def test_invalid_requests_do_not_trigger_cleanup_or_side_effects():
    """Tất cả các request bị từ chối ở tầng validation tuyệt đối không được gọi _clear_cached_svg_for_request hoặc tạo side effect."""
    invalid_cases = [
        # 1. Invalid handwriting style
        {
            "payload": {
                "request_id": "test_side_effect_hw_style",
                "input_type": "handwriting",
                "prompt": "Xin chào",
                "style": "invalid_style",
            },
            "expected_code": "INPUT_INVALID_FORMAT",
        },
        # 2. Invalid Art Mode style
        {
            "payload": {
                "request_id": "test_side_effect_art_style",
                "input_type": "text",
                "prompt": "Draw a tree",
                "style": "hand_hocsinh",
            },
            "expected_code": "INPUT_INVALID_FORMAT",
        },
        # 3. Invalid target_paper_size_mm (handwriting)
        {
            "payload": {
                "request_id": "test_side_effect_paper_hw",
                "input_type": "handwriting",
                "prompt": "Xin chào",
                "style": "hand_hocsinh",
                "options": {"target_paper_size_mm": None},
            },
            "expected_code": "INPUT_INVALID_FORMAT",
        },
        # 4. Invalid target_paper_size_mm (art mode)
        {
            "payload": {
                "request_id": "test_side_effect_paper_art",
                "input_type": "text",
                "prompt": "Draw a tree",
                "options": {"target_paper_size_mm": [210, 0]},
            },
            "expected_code": "INPUT_INVALID_FORMAT",
        },
        # 5. Invalid font
        {
            "payload": {
                "request_id": "test_side_effect_font",
                "input_type": "handwriting",
                "prompt": "Xin chào",
                "style": "hand_hocsinh",
                "options": {"font": "unknown_font"},
            },
            "expected_code": "UNSUPPORTED_FONT",
        },
        # 6. Invalid letter_type
        {
            "payload": {
                "request_id": "test_side_effect_letter_type",
                "input_type": "handwriting",
                "prompt": "Xin chào",
                "style": "hand_hocsinh",
                "options": {"letter_type": "invalid_type"},
            },
            "expected_code": "UNSUPPORTED_LETTER_TYPE",
        },
        # 7. Incompatible letter_type (formal + omni_casual)
        {
            "payload": {
                "request_id": "test_side_effect_formal_incompatible",
                "input_type": "handwriting",
                "prompt": "Xin chào",
                "style": "hand_hocsinh",
                "options": {"font": "omni_casual", "letter_type": "formal"},
            },
            "expected_code": "UNSUPPORTED_LETTER_TYPE",
        },
        # 8. Invalid seed
        {
            "payload": {
                "request_id": "test_side_effect_seed",
                "input_type": "handwriting",
                "prompt": "Xin chào",
                "style": "hand_hocsinh",
                "options": {"seed": -1},
            },
            "expected_code": "INVALID_SEED",
        },
        # 9. Invalid input_type
        {
            "payload": {
                "request_id": "test_side_effect_input_type",
                "input_type": "unknown_type",
                "prompt": "Xin chào",
            },
            "expected_code": "INPUT_INVALID_FORMAT",
        },
        # 10. Empty text (handwriting)
        {
            "payload": {
                "request_id": "test_side_effect_empty_hw",
                "input_type": "handwriting",
                "prompt": "   ",
                "style": "hand_hocsinh",
            },
            "expected_code": "EMPTY_TEXT",
        },
        # 11. Empty prompt (art text)
        {
            "payload": {
                "request_id": "test_side_effect_empty_art_text",
                "input_type": "text",
                "prompt": "",
                "style": "sketch",
            },
            "expected_code": "INPUT_INVALID_FORMAT",
        },
        # 12. Empty image_base64 (art image)
        {
            "payload": {
                "request_id": "test_side_effect_empty_art_img",
                "input_type": "image",
                "image_base64": "",
                "style": "sketch",
            },
            "expected_code": "INPUT_INVALID_FORMAT",
        },
    ]

    for case in invalid_cases:
        with patch("main._clear_cached_svg_for_request") as mock_clear, \
             patch("main.call_openai_image_api") as mock_api, \
             patch("main.svg_process") as mock_svg:
            res = client.post("/api/ai/generate", json=case["payload"])
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "error", f"Request {case['payload']['request_id']} phải trả error"
            assert data["error"]["code"] == case["expected_code"], f"Request {case['payload']['request_id']} mã lỗi phải là {case['expected_code']}"
            mock_clear.assert_not_called()
            mock_api.assert_not_called()
            mock_svg.assert_not_called()


def test_valid_requests_trigger_cleanup_exactly_once_before_pipeline():
    """Request hợp lệ phải gọi _clear_cached_svg_for_request đúng 1 lần trước khi pipeline chạy."""
    mock_resp = APIResponse(
        request_id="test_cleanup_art_text",
        status="success",
        result_image_base64=SAMPLE_PNG_B64,
        model_used="mock-ai-dalle3",
        processing_time_ms=100,
    )
    mock_svg_res = {
        "status": "success",
        "svg_metrics": {
            "pen_lift_count": 2,
            "pen_down_length_mm": 50.0,
            "pen_lift_distance_mm": 10.0,
            "total_path_length_mm": 60.0,
        },
    }

    # 1. Valid Handwriting Mode
    with patch("main._clear_cached_svg_for_request") as mock_clear:
        res = client.post("/api/ai/generate", json={
            "request_id": "test_valid_cleanup_hw",
            "input_type": "handwriting",
            "prompt": "Kiểm thử dọn dẹp cache một lần duy nhất.",
            "style": "hand_hocsinh",
        })
        assert res.status_code == 200
        assert res.json()["status"] == "success"
        mock_clear.assert_called_once_with("test_valid_cleanup_hw")

    # 2. Valid Art Mode (Text)
    with patch("main._clear_cached_svg_for_request") as mock_clear, \
         patch("main.call_openai_image_api", return_value=mock_resp), \
         patch("main.svg_process", return_value=mock_svg_res):
        res = client.post("/api/ai/generate", json={
            "request_id": "test_valid_cleanup_art_text",
            "input_type": "text",
            "prompt": "A beautiful landscape",
            "style": "sketch",
        })
        assert res.status_code == 200
        assert res.json()["status"] == "success"
        mock_clear.assert_called_once_with("test_valid_cleanup_art_text")

    # 3. Valid Art Mode (Image)
    with patch("main._clear_cached_svg_for_request") as mock_clear, \
         patch("main.svg_process", return_value=mock_svg_res):
        res = client.post("/api/ai/generate", json={
            "request_id": "test_valid_cleanup_art_img",
            "input_type": "image",
            "image_base64": SAMPLE_PNG_B64,
            "style": "line_art",
        })
        assert res.status_code == 200
        assert res.json()["status"] == "success"
        mock_clear.assert_called_once_with("test_valid_cleanup_art_img")





