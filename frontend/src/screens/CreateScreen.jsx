import React, { useRef, useState } from "react";
import { Image, Pencil, UploadCloud, ArrowRight, Minus, LineChart, Grip, Hash, Loader2, FileText, Type, Feather, PenTool, Palette, PenLine, ChevronDown } from "lucide-react";
import { ScreenShell, ComicButton, ScreenTitle, Logo } from "../components/ComicPrimitives";

const ART_STYLES = [
  { id: "sketch", label: "Ký hoạ", icon: Pencil },
  { id: "line_art", label: "Line art", icon: Minus },
  { id: "stipple", label: "Chấm bi", icon: Grip },
  { id: "hatching", label: "Hatching", icon: Hash },
];

const HAND_FONTS = [
  { id: "oly", name: "Tiểu Học Nét Đều" },
  { id: "omni_casual", name: "Omni Casual (thân thiện)" },
  { id: "thanhdam", name: "Bút Máy Thanh Đậm" },
  { id: "thuphap", name: "Thư Pháp Thủy Mặc" },
  { id: "cursive", name: "Chữ Thảo Cursive" },
];

const HAND_STYLES = [
  { id: "hand_hocsinh", label: "Học sinh", desc: "Nắn nót, nét đứng", icon: Pencil },
  { id: "hand_nguoilon", label: "Thảo nghiêng", desc: "Tự nhiên, mềm mại", icon: PenTool },
  { id: "hand_thuphap", label: "Thư pháp", desc: "Uốn lượn, nghệ thuật", icon: Feather },
  { id: "hand_chukinhanh", label: "Ký tên", desc: "Phóng khoáng, bay", icon: PenLine },
];

const SAMPLES = {
  tho: `Nam quốc sơn hà Nam đế cư,\nTuyệt nhiên định phận tại thiên thư.\nNhư hà nghịch lỗ lai xâm phạm,\nNhữ đẳng hành khan thủ bại hư!`,
  thiep: `Kính gửi thầy cô kính yêu,\nNhân ngày Nhà giáo Việt Nam 20/11, em xin kính chúc thầy cô luôn dồi dào sức khỏe, ngập tràn hạnh phúc và thành công trên con đường trồng người cao quý!`,
  bangken: `HIỆU TRƯỞNG TRƯỜNG ĐẠI HỌC BÁCH KHOA\nChứng nhận sinh viên đã đạt Giải Nhất\nCuộc thi Nghiên Cứu Khoa Học 2026-2027\nĐề tài: Máy vẽ & viết thư tay tự động OmniDraw.`
};

const MAX_FILE_MB = 10;

/**
 * Màn 1 — Trang tạo tranh / Viết thư tay
 * Hỗ trợ 2 chế độ:
 *  - "art": Vẽ tranh nghệ thuật (tải ảnh hoặc prompt AI, 4 style tranh)
 *  - "letter": Viết thư tay (tải file văn bản hoặc gõ chữ, chọn font + style viết tay)
 */
export default function CreateScreen({ onSubmit, loading = false }) {
  const [mode, setMode] = useState("art"); // "art" | "letter"

  // State cho chế độ Vẽ tranh
  const [inputType, setInputType] = useState("image"); // "image" | "text"
  const [style, setStyle] = useState("sketch");
  const [imageBase64, setImageBase64] = useState(null);
  const [imagePreviewName, setImagePreviewName] = useState(null);
  const [prompt, setPrompt] = useState("");

  // State cho chế độ Viết thư tay
  const [letterInputType, setLetterInputType] = useState("text"); // "file" | "text"
  const [handFont, setHandFont] = useState("oly");
  const [isFontDropdownOpen, setIsFontDropdownOpen] = useState(false);
  const [handStyle, setHandStyle] = useState("hand_hocsinh");
  const [letterPrompt, setLetterPrompt] = useState("");
  const [docFileName, setDocFileName] = useState(null);
  const [docBase64, setDocBase64] = useState(null);

  // Cấu hình chung
  const [paperSize, setPaperSize] = useState("a4"); // "a3" | "a4" | "a5"
  const [fileError, setFileError] = useState(null);
  const fileInputRef = useRef(null);
  const docInputRef = useRef(null);
  const docReadTokenRef = useRef(0);

  function handleSwitchToText() {
    docReadTokenRef.current += 1;
    setLetterInputType("text");
    setDocBase64(null);
    setDocFileName(null);
    if (docInputRef.current) {
      docInputRef.current.value = "";
    }
    setFileError(null);
  }

  function handleSwitchToFile() {
    setLetterInputType("file");
    setFileError(null);
  }

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
      setImageBase64(reader.result);
      setImagePreviewName(file.name);
    };
    reader.onerror = () => setFileError("Không đọc được file, thử lại nhé.");
    reader.readAsDataURL(file);
  }

  function handleDocFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    // 1. Tăng token và lưu token của lượt mới
    const readToken = ++docReadTokenRef.current;

    // 2. Xóa toàn bộ state thuộc file trước
    setDocBase64(null);
    setDocFileName(null);
    setLetterPrompt("");
    setFileError(null);

    // 3. Validation
    const name = file.name.toLowerCase();
    if (!name.endsWith(".txt") && !name.endsWith(".docx")) {
      setFileError("Chỉ nhận file .TXT hoặc .DOCX.");
      e.target.value = "";
      return;
    }
    if (file.size > MAX_FILE_MB * 1024 * 1024) {
      setFileError(`File vượt quá ${MAX_FILE_MB}MB.`);
      e.target.value = "";
      return;
    }

    if (name.endsWith(".txt")) {
      const reader = new FileReader();
      reader.onload = () => {
        if (readToken !== docReadTokenRef.current) return;
        setLetterPrompt(reader.result || "");
        setDocBase64(null);
        setDocFileName(file.name);
      };
      reader.onerror = () => {
        if (readToken !== docReadTokenRef.current) return;
        setFileError("Không đọc được file TXT, thử lại nhé.");
        e.target.value = "";
      };
      reader.readAsText(file);
    } else {
      const reader = new FileReader();
      reader.onload = () => {
        if (readToken !== docReadTokenRef.current) return;
        setDocBase64(reader.result);
        setLetterPrompt("");
        setDocFileName(file.name);
      };
      reader.onerror = () => {
        if (readToken !== docReadTokenRef.current) return;
        setFileError("Không đọc được file DOCX, thử lại nhé.");
        e.target.value = "";
      };
      reader.readAsDataURL(file);
    }
  }

  const selectedFont = HAND_FONTS.find((f) => f.id === handFont) || HAND_FONTS[0];

  function handleSubmit() {
    if (mode === "art") {
      if (inputType === "image" && !imageBase64) {
        setFileError("Chọn một ảnh trước đã nhé.");
        return;
      }
      if (inputType === "text" && !prompt.trim()) {
        setFileError("Nhập mô tả trước đã nhé.");
        return;
      }
      onSubmit?.({
        mode: "art",
        inputType,
        style,
        paperSize,
        imageBase64: inputType === "image" ? imageBase64 : undefined,
        prompt: inputType === "text" ? prompt.trim() : undefined,
        fileName: inputType === "image" ? imagePreviewName : undefined,
      });
    } else {
      // Chế độ viết thư tay
      let submitImageBase64 = undefined;
      let submitPrompt = undefined;
      let submitFileName = undefined;

      if (letterInputType === "text") {
        if (!letterPrompt.trim()) {
          setFileError("Vui lòng nhập nội dung thư tay trước nhé.");
          return;
        }
        submitPrompt = letterPrompt.trim();
      } else {
        // letterInputType === "file"
        if (!docFileName) {
          setFileError("Vui lòng tải lên một file văn bản trước.");
          return;
        }
        submitFileName = docFileName;
        if (docFileName.toLowerCase().endsWith(".docx")) {
          if (!docBase64) {
            setFileError("Đang đọc file DOCX hoặc file rỗng, vui lòng thử lại.");
            return;
          }
          submitImageBase64 = docBase64;
          submitPrompt = undefined;
        } else {
          // TXT: gửi qua prompt, không gửi Base64
          if (!letterPrompt.trim()) {
            setFileError("File TXT không có nội dung văn bản.");
            return;
          }
          submitPrompt = letterPrompt.trim();
          submitImageBase64 = undefined;
        }
      }

      onSubmit?.({
        mode: "letter",
        inputType: "handwriting",
        style: handStyle,
        font: handFont,
        paperSize,
        imageBase64: submitImageBase64,
        prompt: submitPrompt,
        fileName: submitFileName,
      });
    }
  }

  return (
    <ScreenShell patternId="pattern-create">
      {/* ── Header: Logo + Công tắc chuyển đổi Vẽ tranh / Viết thư tay ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
        <Logo subtitle={mode === "art" ? "Trang tạo tranh" : "Trang tạo thư tay"} size="text-3xl" />

        {/* Công tắc nút tròn bật/tắt chuyển đổi Vẽ tranh (Palette) / Viết thư tay (PenLine) */}
        <button
          type="button"
          role="switch"
          aria-checked={mode === "letter"}
          onClick={() => {
            setMode(mode === "art" ? "letter" : "art");
            setFileError(null);
          }}
          title={mode === "art" ? "Bấm để chuyển sang viết thư tay" : "Bấm để chuyển sang vẽ tranh"}
          className="relative w-[76px] h-[38px] bg-[#EFECE6] border-[2.5px] border-[#1A1A1A] rounded-full p-[3px] cursor-pointer shadow-[2.5px_2.5px_0px_#1A1A1A] transition-all self-start sm:self-auto hover:shadow-[3px_3px_0px_#1A1A1A] active:translate-x-0.5 active:translate-y-0.5 select-none"
        >
          {/* 2 icon nền nằm ở 2 vị trí cố định */}
          <div className="absolute inset-0 flex items-center justify-between px-2.5 pointer-events-none">
            <Palette
              size={17}
              className={`transition-opacity duration-200 ${
                mode === "art" ? "opacity-0" : "text-[#888882] opacity-70"
              }`}
            />
            <PenLine
              size={17}
              className={`transition-opacity duration-200 ${
                mode === "letter" ? "opacity-0" : "text-[#888882] opacity-70"
              }`}
            />
          </div>

          {/* Nút tròn trượt (Sliding Circular Knob) */}
          <div
            className={`relative w-[28px] h-[28px] rounded-full border-[2px] border-[#1A1A1A] flex items-center justify-center shadow-[1px_1px_0px_#1A1A1A] transition-all duration-200 ease-in-out ${
              mode === "letter"
                ? "translate-x-[38px] bg-[#C0392B] text-white"
                : "translate-x-0 bg-[#1A1A1A] text-[#FFEAA7]"
            }`}
          >
            {mode === "art" ? (
              <Palette size={15} strokeWidth={2.5} />
            ) : (
              <PenLine size={15} strokeWidth={2.5} />
            )}
          </div>
        </button>
      </div>

      {/* ==================== CHẾ ĐỘ 1: VẼ TRANH NGHỆ THUẬT ==================== */}
      {mode === "art" ? (
        <>
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
              className="border-[3px] border-dashed border-[#1A1A1A] rounded-xl py-9 px-4 text-center mb-2 bg-[#FEFDF9] cursor-pointer hover:bg-[#FDF9EE] transition-colors"
            >
              <input ref={fileInputRef} type="file" accept="image/jpeg,image/png" className="hidden" onChange={handleFileChange} />
              {imageBase64 ? (
                <img src={imageBase64} alt="preview" className="max-h-64 mx-auto rounded-lg object-contain" />
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
            {ART_STYLES.map(({ id, label, icon: Icon }) => {
              const active = style === id;
              return (
                <button
                  key={id}
                  type="button"
                  onClick={() => setStyle(id)}
                  className={`relative min-w-0 h-[64px] flex flex-col items-center justify-center border-[2.5px] rounded-lg px-1.5 text-center overflow-hidden transition-colors duration-150 shadow-[2px_2px_0px_#1A1A1A] cursor-pointer ${
                    active ? "border-[#C0392B] bg-[#FBEAF0] text-[#C0392B]" : "border-[#1A1A1A] bg-white text-[#1A1A1A] hover:bg-[#FDF9EE]"
                  }`}
                >
                  <Icon size={18} className={`shrink-0 ${active ? "text-[#C0392B]" : "text-[#1A1A1A]"}`} />
                  <p className="w-full text-xs mt-1 truncate font-bold">
                    {label}
                  </p>
                </button>
              );
            })}
          </div>
        </>
      ) : (
        /* ==================== CHẾ ĐỘ 2: VIẾT THƯ TAY ==================== */
        <>
          <div className="flex gap-2.5 mb-5">
            <button
              type="button"
              onClick={handleSwitchToFile}
              className={`flex-1 flex items-center justify-center gap-2 border-[2.5px] border-[#1A1A1A] rounded-lg py-2.5 text-sm font-bold shadow-[2px_2px_0px_#1A1A1A] transition-colors duration-150 cursor-pointer ${
                letterInputType === "file" ? "bg-[#1A1A1A] text-[#FAFAF8]" : "bg-white text-[#1A1A1A] hover:bg-[#F5F1E0]"
              }`}
            >
              <FileText size={17} /> TẢI VĂN BẢN LÊN
            </button>
            <button
              type="button"
              onClick={handleSwitchToText}
              className={`flex-1 flex items-center justify-center gap-2 border-[2.5px] border-[#1A1A1A] rounded-lg py-2.5 text-sm font-bold shadow-[2px_2px_0px_#1A1A1A] transition-colors duration-150 cursor-pointer ${
                letterInputType === "text" ? "bg-[#1A1A1A] text-[#FAFAF8]" : "bg-white text-[#1A1A1A] hover:bg-[#F5F1E0]"
              }`}
            >
              <Type size={17} /> NHẬP CHỮ (TEXT)
            </button>
          </div>

          {letterInputType === "file" ? (
            <div
              onClick={() => docInputRef.current?.click()}
              className="border-[3px] border-dashed border-[#1A1A1A] rounded-xl py-9 px-4 text-center mb-2 bg-[#FEFDF9] cursor-pointer hover:bg-[#FDF9EE] transition-colors"
            >
              <input ref={docInputRef} type="file" accept=".txt,.docx" className="hidden" onChange={handleDocFileChange} />
              <FileText size={32} className="mx-auto text-[#1A1A1A]" />
              <p className="text-sm font-bold text-[#1A1A1A] mt-2">
                {docFileName ? docFileName.toUpperCase() : "KÉO THẢ TẬP TIN VĂN BẢN VÀO ĐÂY!"}
              </p>
              <p className="text-xs text-[#6B6B66] mt-1">
                {docFileName ? "Đã sẵn sàng tạo nét thư tay" : `Hỗ trợ TXT, DOCX — tối đa ${MAX_FILE_MB}MB`}
              </p>
            </div>
          ) : (
            <div className="relative mb-2">
              <textarea
                value={letterPrompt}
                onChange={(e) => setLetterPrompt(e.target.value)}
                className="w-full border-[3px] border-[#1A1A1A] rounded-xl p-3.5 bg-[#FEFDF9] text-sm h-32 resize-none focus:outline-none leading-relaxed"
                placeholder="Nhập nội dung thư tay, bài thơ, hoặc lời chúc mừng của bạn..."
              />
              <div className="flex flex-wrap items-center gap-1.5 mt-1.5 mb-1 text-xs font-bold">
                <span className="text-[#6B6B66] mr-1 text-[11px]">Chèn nhanh mẫu:</span>
                <button
                  type="button"
                  onClick={() => setLetterPrompt(SAMPLES.tho)}
                  className="bg-[#F0EEE6] hover:bg-[#FFEAA7] border border-[#1A1A1A] px-2 py-0.5 rounded text-[11px] transition-colors"
                >
                  📜 Bài thơ
                </button>
                <button
                  type="button"
                  onClick={() => setLetterPrompt(SAMPLES.thiep)}
                  className="bg-[#F0EEE6] hover:bg-[#FFEAA7] border border-[#1A1A1A] px-2 py-0.5 rounded text-[11px] transition-colors"
                >
                  💌 Thiệp 20/11
                </button>
                <button
                  type="button"
                  onClick={() => setLetterPrompt(SAMPLES.bangken)}
                  className="bg-[#F0EEE6] hover:bg-[#FFEAA7] border border-[#1A1A1A] px-2 py-0.5 rounded text-[11px] transition-colors"
                >
                  🎖️ Giấy khen
                </button>
              </div>
            </div>
          )}

          {fileError && <p className="text-xs font-bold text-[#C0392B] mb-3">{fileError}</p>}
          {!fileError && <div className="mb-2" />}

          {/* ── BẢNG ĐIỀU KHIỂN: 1. KIỂU NÉT ROBOT (THANH TRÒN DROPDOWN) ── */}
          <div className="mb-4 relative">
            <div className="flex items-center justify-between mb-1.5">
              <p className="text-xs font-bold text-[#1A1A1A] uppercase tracking-wide flex items-center gap-1.5">
                <span>🔤</span> 1. Kiểu nét robot
              </p>
              <span className="text-[10px] font-bold text-[#6B6B66]">Bấm thanh để mở rộng</span>
            </div>

            {/* Thanh selector: Tên kiểu nét bên trái, Mũi tên bên phải */}
            <button
              type="button"
              onClick={() => setIsFontDropdownOpen((prev) => !prev)}
              className="w-full flex items-center justify-between px-4 py-2.5 bg-white border-[2.5px] border-[#1A1A1A] rounded-full shadow-[2px_2px_0px_#1A1A1A] hover:bg-[#FDF9EE] transition-colors duration-150 cursor-pointer select-none"
            >
              <span className="text-xs font-bold text-[#1A1A1A] truncate">
                {selectedFont.name}
              </span>
              <ChevronDown
                size={16}
                className={`text-[#1A1A1A] transition-transform duration-200 shrink-0 ml-2 ${
                  isFontDropdownOpen ? "rotate-180" : ""
                }`}
              />
            </button>

            {/* Menu thả nổi đè lên trên (Overlay Popover) */}
            {isFontDropdownOpen && (
              <>
                {/* Lớp nền trong suốt bắt sự kiện click ra ngoài để đóng menu */}
                <div
                  className="fixed inset-0 z-40"
                  onClick={() => setIsFontDropdownOpen(false)}
                />

                <div className="absolute top-full left-0 right-0 mt-1.5 bg-[#FFFDF7] border-[2.5px] border-[#1A1A1A] rounded-2xl p-2.5 shadow-[4px_4px_0px_#1A1A1A] z-50">
                  <div className="flex flex-col gap-1 max-h-[175px] overflow-y-auto pr-1">
                    {HAND_FONTS.map((f) => {
                      const isSelected = handFont === f.id;
                      return (
                        <button
                          key={f.id}
                          type="button"
                          onClick={() => {
                            setHandFont(f.id);
                            setIsFontDropdownOpen(false);
                          }}
                          className={`w-full flex items-center justify-between px-3 py-2 rounded-xl border transition-colors duration-150 text-left cursor-pointer ${
                            isSelected
                              ? "border-[#1A1A1A] bg-[#FFEAA7] shadow-[1px_1px_0px_#1A1A1A]"
                              : "border-transparent hover:border-[#1A1A1A] hover:bg-[#FDF9EE]"
                          }`}
                        >
                          <span className="text-xs font-bold text-[#1A1A1A] truncate">
                            {f.name}
                          </span>
                          {isSelected && (
                            <span className="text-xs font-black text-[#1A1A1A] shrink-0 ml-2">✓</span>
                          )}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </>
            )}
          </div>

          {/* ── BẢNG ĐIỀU KHIỂN: 2. ĐẶC TÍNH NÉT BÚT (PHONG CÁCH VIẾT) ── */}
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-bold text-[#1A1A1A] uppercase tracking-wide flex items-center gap-1.5">
              <span>✍️</span> 2. Đặc tính nét bút (Phong cách)
            </p>
            <span className="text-[10px] font-bold bg-[#E8F5E9] text-[#2E7D32] border border-[#2E7D32] px-1.5 py-0.5 rounded shadow-[1px_1px_0px_#2E7D32]">
              Động học ngòi bút
            </span>
          </div>
          <div className="grid grid-cols-4 gap-2.5 mb-6">
            {HAND_STYLES.map(({ id, label, desc, icon: Icon }) => {
              const active = handStyle === id;
              return (
                <button
                  key={id}
                  type="button"
                  onClick={() => setHandStyle(id)}
                  className={`relative min-w-0 h-[64px] flex flex-col items-center justify-center border-[2.5px] rounded-lg px-1.5 text-center overflow-hidden transition-colors duration-150 shadow-[2px_2px_0px_#1A1A1A] cursor-pointer ${
                    active
                      ? "border-[#C0392B] bg-[#FBEAF0] text-[#C0392B]"
                      : "border-[#1A1A1A] bg-white text-[#1A1A1A] hover:bg-[#FDF9EE]"
                  }`}
                >
                  <Icon
                    size={18}
                    className={`shrink-0 ${active ? "text-[#C0392B]" : "text-[#1A1A1A]"}`}
                  />
                  <p className="w-full text-xs mt-1 truncate font-bold">
                    {label}
                  </p>
                </button>
              );
            })}
          </div>
        </>
      )}

      {/* ── Footer: Khổ giấy + Nút hành động chính ── */}
      <div className="flex items-end justify-between border-t-[3px] border-[#1A1A1A] pt-5">
        <div className="min-w-[140px] pb-1">
          <p className="text-[10px] text-[#6B6B66] font-bold mb-1.5 uppercase">Khổ giấy</p>
          <select 
            value={paperSize} 
            onChange={e => setPaperSize(e.target.value)}
            className="w-full border-[2.5px] border-[#1A1A1A] rounded-md font-bold text-[13px] px-2 py-1.5 bg-white outline-none cursor-pointer hover:bg-[#F5F1E0] transition-colors"
          >
            <option value="a4">A4 (210x297mm)</option>
            <option value="a3">A3 (297x420mm)</option>
            <option value="a5">A5 (148x210mm)</option>
          </select>
        </div>

        <ComicButton variant="primary" onClick={handleSubmit} className={loading ? "opacity-70 pointer-events-none" : ""}>
          <span className="flex items-center gap-1.5">
            {loading ? (
              <>
                <Loader2 size={18} className="animate-spin" /> ĐANG TẠO...
              </>
            ) : (
              <>
                {mode === "letter" ? "TẠO THƯ TAY!" : "TẠO TRANH!"} <ArrowRight size={18} />
              </>
            )}
          </span>
        </ComicButton>
      </div>
    </ScreenShell>
  );
}
