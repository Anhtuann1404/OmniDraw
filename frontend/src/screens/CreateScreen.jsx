import React, { useState, useRef } from "react";
import { Image, Pencil, UploadCloud, ArrowRight, Minus, LineChart, Grid2x2, X } from "lucide-react";
import { ScreenShell, ComicButton, StarBadge, Logo } from "../components/ComicPrimitives";

const STYLES = [
  { id: "sketch", label: "Ký hoạ", icon: Minus },
  { id: "line_art", label: "Line art", icon: LineChart },
  { id: "stipple", label: "Chấm bi", icon: Grid2x2 },
  { id: "hatching", label: "Hatching", icon: Grid2x2 },
];

export default function CreateScreen({ onSubmit }) {
  const [inputType, setInputType] = useState("image"); // "image" | "text"
  const [style, setStyle] = useState("sketch");
  
  // Thêm state để lưu ảnh xem trước
  const [previewUrl, setPreviewUrl] = useState(null);
  
  // Dùng ref để liên kết với thẻ input file bị ẩn
  const fileInputRef = useRef(null);

  // Xử lý khi người dùng chọn file qua nút click
  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setPreviewUrl(URL.createObjectURL(file)); // Tạo URL ảo để hiển thị ảnh ngay lập tức
    }
  };

  // Xử lý khi người dùng kéo thả file vào khung
  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) {
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  // Ngăn chặn hành vi mở ảnh ở tab mới mặc định của trình duyệt
  const handleDragOver = (e) => {
    e.preventDefault();
  };

  // Xóa ảnh đã chọn
  const clearImage = (e) => {
    e.stopPropagation(); // Ngăn sự kiện click lan ra khung ngoài
    setPreviewUrl(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

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
        // Khung Dropzone có thêm sự kiện onDrop và onDragOver
        <div 
          className="relative border-[3px] border-dashed border-[#1A1A1A] rounded-xl py-9 px-4 text-center mb-5 bg-[#FEFDF9] cursor-pointer hover:bg-[#F5F3EA] transition-colors"
          onClick={() => fileInputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        >
          {/* Thẻ input thực sự xử lý file, nhưng bị ẩn đi */}
          <input 
            type="file" 
            ref={fileInputRef} 
            className="hidden" 
            accept="image/png, image/jpeg" 
            onChange={handleFileChange}
          />
          
          {previewUrl ? (
            <div className="relative inline-block">
              <img src={previewUrl} alt="Xem trước" className="mx-auto max-h-32 object-contain border-2 border-[#1A1A1A] rounded-lg shadow-[4px_4px_0px_0px_rgba(26,26,26,1)]" />
              <button 
                onClick={clearImage}
                className="absolute -top-3 -right-3 bg-[#C0392B] text-white p-1 rounded-full border-2 border-[#1A1A1A] hover:scale-110 transition-transform"
              >
                <X size={16} />
              </button>
            </div>
          ) : (
            <>
              <UploadCloud size={30} className="mx-auto text-[#1A1A1A]" />
              <p className="text-sm font-bold text-[#1A1A1A] mt-2">KÉO THẢ ẢNH VÀO ĐÂY NÀO!</p>
              <p className="text-xs text-[#6B6B66] mt-1">JPG, PNG — tối đa 10MB</p>
            </>
          )}
        </div>
      ) : (
        <textarea
          className="w-full border-[3px] border-[#1A1A1A] rounded-xl p-4 mb-5 bg-[#FEFDF9] text-sm h-32 resize-none focus:outline-none"
          placeholder="Mô tả bức tranh bạn muốn vẽ, ví dụ: một chú mèo đang ngủ trên bậu cửa sổ..."
        />
      )}

      <p className="text-xs font-bold text-[#1A1A1A] uppercase mb-2.5">Chọn phong cách vẽ</p>
      <div className="grid grid-cols-4 gap-2.5 mb-6">
        {STYLES.map(({ id, label, icon: Icon }) => {
          const active = style === id;
          return (
            <button
              key={id}
              onClick={() => setStyle(id)}
              className={`relative min-w-0 h-[64px] flex flex-col items-center justify-center border-[2.5px] rounded-lg px-1.5 text-center overflow-hidden transition-all ${
                active ? "border-[#C0392B] bg-[#FBEAF0] -rotate-2 scale-105" : "border-[#1A1A1A] bg-white hover:-translate-y-1"
              }`}
            >
              <Icon size={18} className={active ? "text-[#C0392B] shrink-0" : "text-[#1A1A1A] shrink-0"} />
              <p className={`w-full text-xs mt-1 truncate ${active ? "font-bold text-[#1A1A1A]" : "font-medium text-[#1A1A1A]"}`}>
                {label}
              </p>
            </button>
          );
        })}
      </div>

      <div className="flex items-center justify-between border-t-[3px] border-[#1A1A1A] pt-5">
        <span className="text-xs font-bold text-[#1A1A1A]">KHỔ GIẤY: A4</span>
        <ComicButton variant="primary" onClick={() => onSubmit?.({ inputType, style, image: previewUrl })}>
          <span className="flex items-center gap-1.5">
            TẠO TRANH! <ArrowRight size={18} />
          </span>
        </ComicButton>
      </div>
    </ScreenShell>
  );
}