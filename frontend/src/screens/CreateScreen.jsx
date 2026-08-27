import React, { useRef, useState } from "react";
import { Image, Pencil, UploadCloud, ArrowRight, Minus, LineChart, Grid2x2, Loader2 } from "lucide-react";
import { ScreenShell, ComicButton, StarBadge, Logo } from "../components/ComicPrimitives";

const STYLES = [
  { id: "sketch", label: "Ký hoạ", icon: Minus },
  { id: "line_art", label: "Line art", icon: LineChart },
  { id: "stipple", label: "Chấm bi", icon: Grid2x2 },
  { id: "hatching", label: "Hatching", icon: Grid2x2 },
];

const MAX_FILE_MB = 10;

/**
 * Màn 1 — Trang tạo tranh
 * Props:
 *  - onSubmit({ inputType, style, imageBase64?, prompt? }) : gọi khi bấm "Tạo tranh"
 *  - loading?: boolean — disable nút + hiện spinner khi đang gọi API
 */
export default function CreateScreen({ onSubmit, loading = false }) {
  const [inputType, setInputType] = useState("image"); // "image" | "text"
  const [style, setStyle] = useState("sketch");
  const [imageBase64, setImageBase64] = useState(null);
  const [imagePreviewName, setImagePreviewName] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [fileError, setFileError] = useState(null);
  const fileInputRef = useRef(null);

  // Chuẩn hoá đầu vào ngay tại tầng giao diện theo đúng mục 1 của API Spec:
  // chỉ nhận jpg/jpeg/png, tối đa 10MB. Việc resize về 1024px cạnh dài nhất
  // nên làm ở backend hoặc bổ sung canvas-resize riêng khi cần — ở đây chặn sớm
  // các input rõ ràng sai định dạng/kích thước để không gửi rác lên API.
  function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileError(null);

    const validTypes = ["image/jpeg", "image/jpg", "image/png"];
    if (!validTypes.includes(file.type)) {
      setFileError("Chỉ nhận file JPG hoặc PNG.");
      return;
    }
    if (file.size > MAX_FILE_MB * 1024 * 1024) {
      setFileError(`File vượt quá ${MAX_FILE_MB}MB.`);
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      setImageBase64(reader.result); // đã ở dạng "data:image/...;base64,...." đúng chuẩn mục 1
      setImagePreviewName(file.name);
    };
    reader.onerror = () => setFileError("Không đọc được file, thử lại nhé.");
    reader.readAsDataURL(file);
  }

  function handleSubmit() {
    if (inputType === "image" && !imageBase64) {
      setFileError("Chọn một ảnh trước đã nhé.");
      return;
    }
    if (inputType === "text" && !prompt.trim()) {
      setFileError("Nhập mô tả trước đã nhé.");
      return;
    }
    onSubmit?.({
      inputType,
      style,
      imageBase64: inputType === "image" ? imageBase64 : undefined,
      prompt: inputType === "text" ? prompt.trim() : undefined,
    });
  }

  return (
    <ScreenShell patternId="pattern-create">
      <div className="flex items-start justify-between mb-6">
        <Logo subtitle="Trang tạo tranh" size="text-3xl" />
        <StarBadge topLabel="MỚI" bottomLabel="AI" />
      </div>

      <div className="flex gap-2.5 mb-5">
        <button
          onClick={() => setInputType("image")}
          className={`flex-1 flex items-center justify-center gap-2 border-[2.5px] border-[#1A1A1A] rounded-lg py-2.5 text-sm font-bold ${
            inputType === "image" ? "bg-[#1A1A1A] text-[#FAFAF8]" : "bg-white text-[#1A1A1A]"
          }`}
        >
          <Image size={17} /> TẢI ẢNH LÊN
        </button>
        <button
          onClick={() => setInputType("text")}
          className={`flex-1 flex items-center justify-center gap-2 border-[2.5px] border-[#1A1A1A] rounded-lg py-2.5 text-sm font-bold ${
            inputType === "text" ? "bg-[#1A1A1A] text-[#FAFAF8]" : "bg-white text-[#1A1A1A]"
          }`}
        >
          <Pencil size={17} /> NHẬP MÔ TẢ
        </button>
      </div>

      {inputType === "image" ? (
        <div
          onClick={() => fileInputRef.current?.click()}
          className="border-[3px] border-dashed border-[#1A1A1A] rounded-xl py-9 px-4 text-center mb-2 bg-[#FEFDF9] cursor-pointer"
        >
          <input ref={fileInputRef} type="file" accept="image/jpeg,image/png" className="hidden" onChange={handleFileChange} />
          {imageBase64 ? (
            <img src={imageBase64} alt="preview" className="max-h-32 mx-auto rounded-lg object-contain" />
          ) : (
            <>
              <UploadCloud size={30} className="mx-auto text-[#1A1A1A]" />
              <p className="text-sm font-bold text-[#1A1A1A] mt-2">KÉO THẢ ẢNH VÀO ĐÂY NÀO!</p>
            </>
          )}
          <p className="text-xs text-[#6B6B66] mt-1">
            {imagePreviewName || `JPG, PNG — tối đa ${MAX_FILE_MB}MB`}
          </p>
        </div>
      ) : (
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="w-full border-[3px] border-[#1A1A1A] rounded-xl p-4 mb-2 bg-[#FEFDF9] text-sm h-32 resize-none focus:outline-none"
          placeholder="Mô tả bức tranh bạn muốn vẽ, ví dụ: một chú mèo đang ngủ trên bậu cửa sổ..."
        />
      )}

      {fileError && <p className="text-xs font-bold text-[#C0392B] mb-3">{fileError}</p>}
      {!fileError && <div className="mb-3" />}

      <p className="text-xs font-bold text-[#1A1A1A] uppercase mb-2.5">Chọn phong cách vẽ</p>
      <div className="grid grid-cols-4 gap-2.5 mb-6">
        {STYLES.map(({ id, label, icon: Icon }) => {
          const active = style === id;
          return (
            <button
              key={id}
              onClick={() => setStyle(id)}
              className={`relative min-w-0 h-[64px] flex flex-col items-center justify-center border-[2.5px] rounded-lg px-1.5 text-center overflow-hidden ${
                active ? "border-[#C0392B] bg-[#FBEAF0] -rotate-2" : "border-[#1A1A1A] bg-white"
              }`}
            >
              <Icon size={18} className={active ? "text-[#C0392B] shrink-0" : "text-[#1A1A1A] shrink-0"} />
              <p
                className={`w-full text-xs mt-1 truncate ${
                  active ? "font-bold text-[#1A1A1A]" : "font-medium text-[#1A1A1A]"
                }`}
              >
                {label}
              </p>
            </button>
          );
        })}
      </div>

      <div className="flex items-center justify-between border-t-[3px] border-[#1A1A1A] pt-5">
        <span className="text-xs font-bold text-[#1A1A1A]">KHỔ GIẤY: A4</span>
        <ComicButton variant="primary" onClick={handleSubmit} className={loading ? "opacity-70 pointer-events-none" : ""}>
          <span className="flex items-center gap-1.5">
            {loading ? (
              <>
                <Loader2 size={18} className="animate-spin" /> ĐANG TẠO...
              </>
            ) : (
              <>
                TẠO TRANH! <ArrowRight size={18} />
              </>
            )}
          </span>
        </ComicButton>
      </div>
    </ScreenShell>
  );
}
