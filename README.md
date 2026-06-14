# ttfPreviewExporter

A lightweight desktop tool that renders every keyboard character from a `.ttf` icon font — or a raw C header font array — into a clean exportable PNG sheet. Built for developers who use embedded icon fonts and need a fast way to see what glyph maps to what character.

<img width="1002" height="792" alt="App interface" src="https://github.com/user-attachments/assets/c6109e2a-8189-41e0-bfff-2447ce2412dc" />

---

## Features

- Load `.ttf` / `.otf` font files directly
- Load C header font data (`unsigned char icon[] = { 0x00, ... };`) — no need to extract the `.ttf` first
- Live preview that updates as you adjust icon size, label size, and column count
- Exports a PNG next to the source file, named after it (`icon.ttf` → `icon.png`)
- Discord dark theme UI
- Header bar on the exported PNG shows the font name, glyph count, and exact export timestamp
- `sleepyfish` watermark tiled across the export at 25% opacity

---

## Export

Each cell in the exported sheet pairs the icon glyph on top with its corresponding ASCII character on the bottom, separated by a divider line.

<img width="828" height="657" alt="Exported PNG preview" src="https://github.com/user-attachments/assets/934e1f94-036b-42e3-985c-1a1c6c0e19be" />

Characters covered: `a–z`, `A–Z`, `0–9`, and all standard keyboard symbols.

---

## Requirements

- Python 3.10+
- Pillow

```bash
pip install Pillow
```

---

## Usage

```bash
python font_preview.py
```

Or pass a file directly to load it on startup:

```bash
python font_preview.py icon.ttf
python font_preview.py fontdata.h
```

### Supported header format

```c
#pragma once
unsigned char icon[18572] = {
    0x00, 0x01, 0x00, 0x00, ...
};
```

Both `unsigned char` and `uint8_t` array declarations are supported. The array name is used as the display name in the exported PNG header.

---

## Interface

| Control | Description |
|---|---|
| 📂 Load .ttf Font | Open a `.ttf` or `.otf` font file |
| 📄 Load .h Header | Open a C header containing embedded font data |
| Icon px slider | Resize the glyph preview (16–64px) |
| Label px slider | Resize the ASCII label below each glyph (8–28px) |
| Cols slider | Change the number of columns in the grid (4–26) |
| 💾 Save to PNG | Export the current preview as a PNG next to the source file |

<img width="1002" height="792" alt="App with font loaded" src="https://github.com/user-attachments/assets/8b9a4b26-56f7-4724-b23f-2f77923dcdee" />

---

## License

MIT
