import sys, os, re, io, threading, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

CHARS = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "`-=[]\\;',./"
    "~!@#$%^&*()_+{}|:\"<>?"
)

C_BG             = "#313338"
C_HEADER         = "#1e1f22"
C_CELL_BG        = "#2b2d31"
C_BORDER         = "#1e1f22"
C_ACCENT         = "#5865f2"
C_ICON           = "#5865f2"
C_LABEL          = "#b5bac1"
C_WHITE          = "#f2f3f5"
C_BTN_SAVE       = "#248046"
C_BTN_LOAD       = "#5865f2"
C_BTN_HEADER     = "#4752c4"
C_BTN_HOVER_SAVE = "#1a6334"
C_BTN_HOVER_LOAD = "#4752c4"
C_BTN_HOVER_HDR  = "#3c45a5"
C_STATUS_OK      = "#23a55a"
C_STATUS_ERR     = "#f23f43"
C_STATUS_INF     = "#b5bac1"

PADDING  = 6
CELL_GAP = 3
IMG_HDR  = 48

def find_system_font() -> str | None:
    for p in [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        if os.path.exists(p):
            return p
    return None

def parse_header(h_path: str) -> tuple[bytes, str]:
    text = open(h_path, "r", errors="replace").read()

    m = re.search(
        r'(?:unsigned\s+char|uint8_t)\s+(\w+)\s*\[.*?\]\s*=\s*\{([^}]*)\}',
        text, re.DOTALL
    )
    if not m:
        raise ValueError(
            "No  unsigned char name[] = { ... };  found in the header.\n"
            "Make sure the file matches the expected format."
        )

    name   = m.group(1)
    body   = m.group(2)
    hexvals = re.findall(r'0[xX][0-9A-Fa-f]{1,2}', body)
    if not hexvals:
        raise ValueError(f"Array '{name}' found but contains no hex values.")

    data = bytes(int(h, 16) for h in hexvals)
    return data, name

def draw_centered(draw, font, text, cx, cy, color):
    bb = draw.textbbox((0, 0), text, font=font)
    x  = cx - (bb[2] - bb[0]) // 2 - bb[0]
    y  = cy - (bb[3] - bb[1]) // 2 - bb[1]
    draw.text((x, y), text, font=font, fill=color)

def build_image(font_source, display_name: str, icon_size: int,
                label_size: int, cols: int) -> Image.Image:
    """
    font_source  – str path to .ttf/.otf  OR  bytes of raw font data
    display_name – shown in the header stripe
    """
    if isinstance(font_source, (bytes, bytearray)):
        icon_font = ImageFont.truetype(io.BytesIO(font_source), icon_size)
    else:
        icon_font = ImageFont.truetype(font_source, icon_size)

    sys_path   = find_system_font()
    label_font = ImageFont.truetype(sys_path, label_size) if sys_path else ImageFont.load_default()
    title_font = ImageFont.truetype(sys_path, 15)         if sys_path else ImageFont.load_default()

    cell_w = icon_size + 24
    cell_h = icon_size + label_size + 22
    rows   = (len(CHARS) + cols - 1) // cols

    img_w = PADDING * 2 + cols * cell_w + (cols - 1) * CELL_GAP
    img_h = IMG_HDR + PADDING + rows * cell_h + (rows - 1) * CELL_GAP + PADDING

    img  = Image.new("RGBA", (img_w, img_h), C_BG)
    draw = ImageDraw.Draw(img)

    import datetime
    small_font = ImageFont.truetype(sys_path, 11) if sys_path else ImageFont.load_default()

    draw.rectangle([(0, 0), (img_w, IMG_HDR)], fill=C_HEADER)

    title = f"{display_name}  ·  {len(CHARS)} glyphs  ·  {icon_size}px"
    draw_centered(draw, title_font, title, img_w // 2, IMG_HDR // 2, C_WHITE)

    gh = "github.com/SleepyFish_YT/ttfPreviewExporter"
    bb_gh = draw.textbbox((0, 0), gh, font=small_font)
    draw.text((10, IMG_HDR // 2 - (bb_gh[3] - bb_gh[1]) // 2 - bb_gh[1]), gh, font=small_font, fill=C_LABEL)

    ts = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    bb_ts = draw.textbbox((0, 0), ts, font=small_font)
    ts_w  = bb_ts[2] - bb_ts[0]
    draw.text((img_w - ts_w - 10, IMG_HDR // 2 - (bb_ts[3] - bb_ts[1]) // 2 - bb_ts[1]), ts, font=small_font, fill=C_LABEL)

    draw.rectangle([(0, IMG_HDR - 2), (img_w, IMG_HDR)], fill=C_ACCENT)

    for idx, ch in enumerate(CHARS):
        col = idx % cols
        row = idx // cols
        x0  = PADDING + col * (cell_w + CELL_GAP)
        y0  = IMG_HDR + PADDING + row * (cell_h + CELL_GAP)
        x1, y1 = x0 + cell_w, y0 + cell_h
        cx  = (x0 + x1) // 2

        draw.rectangle([(x0, y0), (x1, y1)], fill=C_CELL_BG, outline=C_BORDER, width=1)

        icon_cy   = y0 + (cell_h - label_size - 14) // 2
        divider_y = y1 - label_size - 10

        draw_centered(draw, icon_font,  ch, cx, icon_cy,                  C_ICON)
        draw.line([(x0 + 4, divider_y), (x1 - 4, divider_y)], fill=C_BORDER, width=1)
        draw_centered(draw, label_font, ch, cx, y1 - label_size // 2 - 5, C_LABEL)

    wm_text    = "sleepyfish"
    wm_cols    = 5
    wm_font_sz = max(16, img_w // (wm_cols * 5))
    try:
        wm_font = ImageFont.truetype(sys_path, wm_font_sz) if sys_path else ImageFont.load_default()
    except Exception:
        wm_font = ImageFont.load_default()

    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb    = dummy.textbbox((0, 0), wm_text, font=wm_font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]

    tile_w  = img_w // wm_cols
    wm_rows = max(1, round(img_h / tile_w * (tile_w / max(tw, 1)) * 0.55))

    overlay = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)

    for wr in range(wm_rows + 1):
        for wc in range(wm_cols + 1):
            cx_wm = wc * tile_w + tile_w // 2
            cy_wm = wr * (img_h // wm_rows) + (img_h // wm_rows) // 2
            ov_draw.text(
                (cx_wm - tw // 2 - bb[0], cy_wm - th // 2 - bb[1]),
                wm_text, font=wm_font, fill=(255, 255, 255, 64)
            )

    return Image.alpha_composite(img, overlay)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Font Icon Preview")
        self.configure(bg=C_BG)
        self.geometry("1000x760")
        self.minsize(700, 500)

        self.ttf_path:    str | None   = None
        self.font_bytes:  bytes | None = None
        self.font_name:   str          = ""
        self.source_path: str | None   = None

        self.preview_img: Image.Image | None      = None
        self._tk_images:  list                    = []

        self.icon_size_var  = tk.IntVar(value=36)
        self.label_size_var = tk.IntVar(value=14)
        self.cols_var       = tk.IntVar(value=13)

        self._build_toolbar()
        self._build_canvas()
        self._build_statusbar()

    def _build_toolbar(self):
        bar = tk.Frame(self, bg=C_HEADER, pady=8)
        bar.pack(fill="x")

        tk.Label(bar, text="Font Icon Preview", bg=C_HEADER,
                 fg=C_WHITE, font=("Segoe UI", 13, "bold")).pack(side="left", padx=14)

        self.save_btn = self._make_btn(bar, "💾  Save to PNG", C_BTN_SAVE,
                                       C_BTN_HOVER_SAVE, self._save_png, side="right")
        self.save_btn.configure(state="disabled")

        self._make_btn(bar, "📄  Load .h Header", C_BTN_HEADER,
                       C_BTN_HOVER_HDR, self._pick_header, side="right")

        self._make_btn(bar, "📂  Load .ttf Font", C_BTN_LOAD,
                       C_BTN_HOVER_LOAD, self._pick_ttf, side="right")

        self._slider(bar, "Icon px",  self.icon_size_var,  16, 64, side="right")
        self._slider(bar, "Label px", self.label_size_var,  8, 28, side="right")
        self._slider(bar, "Cols",     self.cols_var,         4, 26, side="right")

        self.font_label = tk.Label(bar, text="No font loaded", bg=C_HEADER,
                                   fg=C_LABEL, font=("Segoe UI", 9))
        self.font_label.pack(side="left", padx=10)

    def _make_btn(self, parent, text, color, hover, cmd, side="left"):
        btn = tk.Label(parent, text=text, bg=color, fg=C_WHITE,
                       font=("Segoe UI", 10, "bold"),
                       padx=14, pady=6, cursor="hand2", relief="flat")
        btn.pack(side=side, padx=6)
        btn.bind("<Button-1>", lambda e: cmd() if str(btn["state"]) != "disabled" else None)
        btn.bind("<Enter>",    lambda e: btn.configure(bg=hover))
        btn.bind("<Leave>",    lambda e: btn.configure(bg=color))
        return btn

    def _slider(self, parent, label, var, lo, hi, side="right"):
        f = tk.Frame(parent, bg=C_HEADER)
        f.pack(side=side, padx=4)
        tk.Label(f, text=label, bg=C_HEADER, fg=C_WHITE,
                 font=("Segoe UI", 8)).pack()
        tk.Scale(f, from_=lo, to=hi, orient="horizontal", variable=var,
                 bg=C_HEADER, fg=C_WHITE, highlightthickness=0,
                 troughcolor=C_BORDER, length=90,
                 command=lambda _: self._refresh()).pack()

    def _build_canvas(self):
        outer = tk.Frame(self, bg=C_BG)
        outer.pack(fill="both", expand=True, padx=6, pady=6)

        self.canvas = tk.Canvas(outer, bg=C_BG, highlightthickness=0)
        vbar = ttk.Scrollbar(outer, orient="vertical",   command=self.canvas.yview)
        hbar = ttk.Scrollbar(outer, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)

        hbar.pack(side="bottom", fill="x")
        vbar.pack(side="right",  fill="y")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<MouseWheel>", self._scroll_y)
        self.canvas.bind("<Button-4>",   self._scroll_y)
        self.canvas.bind("<Button-5>",   self._scroll_y)

        self._show_placeholder()

    def _show_placeholder(self):
        self.canvas.delete("all")
        self.canvas.create_text(
            500, 260,
            text="📂  Load a .ttf font  or  📄  a fontdata.h header to preview",
            fill=C_LABEL, font=("Segoe UI", 13), anchor="center"
        )

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value="Ready")
        bar = tk.Frame(self, bg=C_HEADER, pady=3)
        bar.pack(fill="x", side="bottom")
        self.status_lbl = tk.Label(bar, textvariable=self.status_var,
                                   bg=C_HEADER, fg=C_STATUS_INF,
                                   font=("Segoe UI", 9), anchor="w")
        self.status_lbl.pack(side="left", padx=10)

    def _set_status(self, msg, kind="info"):
        color = {"info": C_STATUS_INF, "ok": C_STATUS_OK, "err": C_STATUS_ERR}.get(kind, C_STATUS_INF)
        self.status_var.set(msg)
        self.status_lbl.configure(fg=color)

    def _pick_ttf(self):
        path = filedialog.askopenfilename(
            title="Select icon font",
            filetypes=[("Font files", "*.ttf *.otf"), ("All files", "*.*")]
        )
        if path:
            self.ttf_path   = path
            self.font_bytes = None
            self.font_name  = os.path.splitext(os.path.basename(path))[0]
            self.source_path = path
            self.font_label.configure(text=os.path.basename(path))
            self._set_status(f"Loaded TTF: {os.path.basename(path)}", "info")
            self._refresh()

    def _pick_header(self):
        path = filedialog.askopenfilename(
            title="Select C header font file",
            filetypes=[("C Headers", "*.h *.hpp"), ("All files", "*.*")]
        )
        if path:
            self._load_header(path)

    def _load_header(self, path: str):
        try:
            data, array_name = parse_header(path)
        except ValueError as e:
            messagebox.showerror("Parse error", str(e))
            self._set_status(f"Failed to parse header: {os.path.basename(path)}", "err")
            return

        self.ttf_path   = None
        self.font_bytes = data
        self.font_name  = array_name
        self.source_path = path
        self.font_label.configure(text=f"{os.path.basename(path)}  [{array_name}, {len(data):,} bytes]")
        self._set_status(f"Parsed header: {array_name}  ({len(data):,} bytes)", "info")
        self._refresh()

    def _refresh(self):
        if not self.ttf_path and not self.font_bytes:
            return
        self._set_status("Rendering…", "info")
        threading.Thread(target=self._render_thread, daemon=True).start()

    def _render_thread(self):
        try:
            source = self.font_bytes if self.font_bytes else self.ttf_path
            img = build_image(
                source,
                self.font_name,
                self.icon_size_var.get(),
                self.label_size_var.get(),
                self.cols_var.get(),
            )
            self.preview_img = img
            self.after(0, self._blit_preview)
        except Exception as e:
            self.after(0, lambda: self._set_status(f"Error: {e}", "err"))

    def _blit_preview(self):
        if not self.preview_img:
            return
        self._tk_images.clear()
        tk_img = ImageTk.PhotoImage(self.preview_img)
        self._tk_images.append(tk_img)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=tk_img, anchor="nw")
        w, h = self.preview_img.size
        self.canvas.configure(scrollregion=(0, 0, w, h))

        self.save_btn.configure(state="normal")
        self._set_status(f"Preview ready — {w}×{h}px  ·  {len(CHARS)} glyphs", "ok")

    def _save_png(self):
        if not self.preview_img or not self.source_path:
            return
        out = os.path.splitext(self.source_path)[0] + ".png"
        try:
            self.preview_img.save(out, "PNG")
            self._set_status(f"Saved → {out}", "ok")
            messagebox.showinfo("Saved", f"PNG saved to:\n{out}")
        except Exception as e:
            self._set_status(f"Save failed: {e}", "err")
            messagebox.showerror("Error", str(e))

    def _scroll_y(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

if __name__ == "__main__":
    try:
        from PIL import Image
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "--quiet"])
        from PIL import Image, ImageDraw, ImageFont, ImageTk

    app = App()

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if os.path.exists(arg):
            if arg.lower().endswith(".h") or arg.lower().endswith(".hpp"):
                app.after(100, lambda: app._load_header(arg))
            else:
                app.after(100, lambda: app._pick_ttf.__func__(app) or app.__dict__.update(
                    ttf_path=arg, font_bytes=None,
                    font_name=os.path.splitext(os.path.basename(arg))[0],
                    source_path=arg
                ) or app._refresh())

    app.mainloop()