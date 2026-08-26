/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Bảng màu OmniDraw đã chốt — dùng trực tiếp bằng arbitrary value [#hex] trong code,
        // nhưng khai báo ở đây để có thể dùng dạng bg-omni-bg, text-omni-ink v.v. nếu muốn.
        "omni-bg": "#EDEBDF",
        "omni-ink": "#1A1A1A",
        "omni-accent": "#C0392B",
        "omni-paper": "#FEFDF9",
      },
      fontFamily: {
        kalam: ["Kalam", "cursive"],
      },
    },
  },
  plugins: [],
};
