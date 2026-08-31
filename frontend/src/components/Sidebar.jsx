import React from "react";
import { Plus, Image as ImageIcon, User, X } from "lucide-react";
import { Logo, ComicButton } from "./ComicPrimitives";

/**
 * Sidebar — danh sách lịch sử / thư viện bản vẽ
 * Cấu trúc kiểu ChatGPT/Gemini nhưng giữ 100% theme comic OmniDraw
 *
 * Props:
 *  - items: [{ id, title, style, timeAgo, thumbnailUrl? }]
 *  - activeItemId?: string
 *  - onCreateNew()
 *  - onOpenItem(item)
 *  - onDeleteItem(item)
 */
export default function Sidebar({ items = [], activeItemId, onCreateNew, onOpenItem, onDeleteItem }) {
  return (
    <aside className="w-[220px] shrink-0 h-screen flex flex-col bg-[#EDEBDF] border-r-[3px] border-[#1A1A1A]">
      {/* ── Header: Logo ── */}
      <div className="px-4 pt-5 pb-3">
        <Logo size="text-2xl" />
      </div>

      {/* ── Nút Tạo tranh mới ── */}
      <div className="px-3 pb-3">
        <button
          onClick={onCreateNew}
          className="w-full flex items-center gap-2 border-[2.5px] border-[#1A1A1A] rounded-lg px-3 py-2.5 bg-white text-[#1A1A1A] text-sm font-bold hover:bg-[#F5F1E0] transition-colors"
        >
          <Plus size={16} />
          Tạo tranh mới
        </button>
      </div>

      {/* ── Divider ── */}
      <div className="mx-3 border-t-[2px] border-[#1A1A1A] opacity-20 mb-2" />

      {/* ── Label ── */}
      <p className="px-4 text-[10px] font-bold text-[#6B6B66] uppercase tracking-widest mb-2">
        Lịch sử
      </p>

      {/* ── Danh sách items ── */}
      <div className="flex-1 overflow-y-auto px-3 pt-3 pb-3 flex flex-col gap-2.5">
        {items.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 text-center px-2">
            <ImageIcon size={24} className="text-[#C0392B] mb-2 opacity-50" />
            <p className="text-xs text-[#6B6B66] font-medium">
              Chưa có bản vẽ nào
            </p>
          </div>
        ) : (
          items.map((item) => {
            const isActive = item.id === activeItemId;
            return (
              <button
                key={item.id}
                onClick={() => onOpenItem?.(item)}
                className={`w-full text-left rounded-lg px-2.5 py-2 transition-all relative ${
                  isActive
                    ? "border-[2.5px] border-[#1A1A1A] bg-white shadow-[3px_3px_0px_0px_#1A1A1A] -translate-y-[2px] -translate-x-[2px]"
                    : "border-[2.5px] border-[#1A1A1A] bg-white hover:bg-[#F5F1E0]"
                }`}
              >
                <div className="flex items-center gap-2 min-w-0">
                  {item.thumbnailUrl ? (
                    <img
                      src={item.thumbnailUrl}
                      alt={item.title}
                      className="w-8 h-8 rounded object-cover border border-[#1A1A1A] shrink-0"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded bg-[#EDEBDF] border border-[#1A1A1A] flex items-center justify-center shrink-0">
                      <ImageIcon size={14} className="text-[#C0392B]" />
                    </div>
                  )}
                  <div className="min-w-0">
                    <p className="text-xs font-bold text-[#1A1A1A] truncate">
                      {item.title}
                    </p>
                    <p className="text-[10px] text-[#6B6B66] truncate">
                      {item.style} · {item.timeAgo}
                    </p>
                  </div>
                </div>

                {isActive && (
                  <div 
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteItem?.(item);
                    }}
                    className="absolute -top-2 -right-2 w-5 h-5 rounded-full bg-[#C0392B] border-[1.5px] border-[#1A1A1A] flex items-center justify-center shrink-0 hover:scale-110 transition-transform cursor-pointer shadow-[1px_1px_0px_0px_#1A1A1A]"
                    title="Xoá lịch sử"
                  >
                    <X size={10} className="text-white" strokeWidth={4} />
                  </div>
                )}
              </button>
            );
          })
        )}
      </div>

      {/* ── Divider ── */}
      <div className="mx-3 border-t-[2px] border-[#1A1A1A] opacity-20 mt-2" />

      {/* ── Footer: User ── */}
      <div className="px-3 py-3 flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-full bg-[#C0392B] border-[2px] border-[#1A1A1A] flex items-center justify-center shrink-0">
          <User size={14} className="text-white" />
        </div>
        <div className="min-w-0">
          <p className="text-xs font-bold text-[#1A1A1A] font-['Kalam'] truncate">
            Guest
          </p>
          <p className="text-[10px] text-[#6B6B66]">OmniDraw</p>
        </div>
      </div>
    </aside>
  );
}
