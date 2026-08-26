import React from "react";
import { Plus, Image as ImageIcon } from "lucide-react";
import { ScreenShell, ComicButton, Logo, HardShadowBox } from "../components/ComicPrimitives";

/**
 * Màn 5 — Thư viện (lịch sử tranh đã vẽ)
 * Props:
 *  - items: [{ id, title, style, timeAgo, thumbnailUrl? }]
 *  - onCreateNew() / onOpenItem(item)
 */
export default function HistoryScreen({ items = DEFAULT_ITEMS, onCreateNew, onOpenItem }) {
  const totalMinutes = items.reduce((sum, i) => sum + (i.minutes || 0), 0);

  return (
    <ScreenShell patternId="pattern-history">
      <div className="flex items-start justify-between mb-5">
        <Logo subtitle="Thư viện" size="text-[28px]" />
        <ComicButton variant="primary" onClick={onCreateNew} className="!py-2 !px-4 !text-xs">
          <span className="flex items-center gap-1">
            <Plus size={14} /> TẠO MỚI
          </span>
        </ComicButton>
      </div>

      <div className="grid grid-cols-3 gap-3.5">
        {items.map((item) => (
          <button key={item.id} onClick={() => onOpenItem?.(item)} className="text-left">
            <HardShadowBox shadowOffset={4}>
              <div className="rounded-lg overflow-hidden">
                <div className="h-[90px] bg-[#FEFDF9] flex items-center justify-center border-b-[2.5px] border-[#1A1A1A]">
                  {item.thumbnailUrl ? (
                    <img src={item.thumbnailUrl} alt={item.title} className="w-full h-full object-cover" />
                  ) : (
                    <ImageIcon size={28} className="text-[#C0392B]" />
                  )}
                </div>
                <div className="px-2.5 py-2">
                  <p className="text-xs font-bold text-[#1A1A1A] truncate">{item.title}</p>
                  <p className="text-[10px] text-[#6B6B66] mt-0.5">
                    {item.style} · {item.timeAgo}
                  </p>
                </div>
              </div>
            </HardShadowBox>
          </button>
        ))}
      </div>

      <div className="text-center mt-5 pt-4 border-t-[2.5px] border-[#1A1A1A]">
        <span className="text-xs text-[#6B6B66] font-semibold">
          Đã vẽ {items.length} / {items.length} tranh · Tổng thời gian: {totalMinutes} phút
        </span>
      </div>
    </ScreenShell>
  );
}

const DEFAULT_ITEMS = [
  { id: "1", title: "Mèo ngủ", style: "Ký hoạ", timeAgo: "2 ngày trước", minutes: 12 },
  { id: "2", title: "Phong cảnh núi", style: "Line art", timeAgo: "5 ngày trước", minutes: 10 },
  { id: "3", title: "Chân dung", style: "Chấm bi", timeAgo: "1 tuần trước", minutes: 12 },
];
