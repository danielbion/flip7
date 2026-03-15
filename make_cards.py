import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from io import BytesIO
import time
from tqdm import tqdm

def get_font(name, size, fallback="arialbd.ttf"):
    try:
        return ImageFont.truetype(name, size)
    except:
        try:
            return ImageFont.truetype(fallback, size)
        except:
            return ImageFont.load_default()

def create_card_image(card, settings):
    width_px = int(settings["width_mm"] * settings["dpi"] / 25.4)
    height_px = int(settings["height_mm"] * settings["dpi"] / 25.4)
    bg_color = settings.get("bg_color", "#FFFFFF")
    
    img = Image.new("RGBA", (width_px, height_px), bg_color)
    draw = ImageDraw.Draw(img)
    color = card["color"]
    label = card["label"]
    
    font_name = settings.get("font", "arialbd.ttf")
    
    # 1. Draw oval in the center
    tilt = settings.get("tilt_oval", 30)
    thickness = settings.get("oval_thickness", 8)
    
    oval_w = width_px * 0.70
    oval_h = height_px * 0.75
    
    # We draw the oval on a larger transparent canvas to rotate it safely
    # multiplying by 2
    canvas_size = max(width_px, height_px) * 2
    oval_canvas = Image.new("RGBA", (canvas_size, canvas_size), (0,0,0,0))
    oval_draw = ImageDraw.Draw(oval_canvas)
    
    x0 = (canvas_size - oval_w) / 2
    y0 = (canvas_size - oval_h) / 2
    x1 = (canvas_size + oval_w) / 2
    y1 = (canvas_size + oval_h) / 2
    
    oval_draw.ellipse([x0, y0, x1, y1], outline=color, width=thickness)
    
    oval_rotated = oval_canvas.rotate(tilt, resample=Image.BICUBIC)
    
    # Paste centered
    offset_x = (width_px - canvas_size) // 2
    offset_y = (height_px - canvas_size) // 2
    img.paste(oval_rotated, (offset_x, offset_y), oval_rotated)
    
    # 2. Draw Center Text
    font_size_center = card.get("font_size_center", settings.get("font_size_center", 200))
    lines = label.split("\n")
    
    if "font_size_center" not in card and (len(lines) > 1 or len(label) > 3):
        font_size_center = int(font_size_center * 0.5)
        
    font_main = get_font(font_name, font_size_center)
    
    bbox = draw.multiline_textbbox((0,0), label, font=font_main, align="center")
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    # Center text vertically and horizontally
    cx = (width_px - tw) / 2
    cy = (height_px - th) / 2 - bbox[1] # Adjusts for font baseline offset
    
    draw.multiline_text((cx, cy), label, fill=color, font=font_main, align="center")
    
    # 3. Draw Corner Text (Top-Left) or Asset
    font_size_corner = card.get("font_size_corner", settings.get("font_size_corner", 60))
    corner_font = get_font(font_name, font_size_corner)
    
    margin_x = 40
    margin_y = 40
    
    corner_asset = card.get("corner_asset")
    asset_img = None
    if corner_asset and Path(corner_asset).exists():
        asset_img = Image.open(corner_asset).convert("RGBA")
        # Scale asset height closely to corner font size
        w, h = asset_img.size
        new_h = font_size_corner + 10  # adding arbitrary padding so it's visible
        new_w = int(w * (new_h / h))
        asset_img = asset_img.resize((new_w, new_h), Image.LANCZOS)
        
    if asset_img:
        # User defined an asset image
        img.paste(asset_img, (margin_x, margin_y), asset_img)
    else:
        draw.multiline_text((margin_x, margin_y), label, fill=color, font=corner_font, align="center")
    
    # 4. Draw Corner Text/Asset (Bottom-Right, rotated 180 degrees)
    corner_canvas = Image.new("RGBA", (width_px, height_px), (0,0,0,0))
    corner_draw = ImageDraw.Draw(corner_canvas)
    
    if asset_img:
        corner_canvas.paste(asset_img, (margin_x, margin_y), asset_img)
    else:
        corner_draw.multiline_text((margin_x, margin_y), label, fill=color, font=corner_font, align="center")
    
    corner_canvas_rot = corner_canvas.rotate(180)
    img.paste(corner_canvas_rot, (0,0), corner_canvas_rot)
    
    return img.convert("RGB")

def save_cards_to_pdf(images, settings, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    page_width, page_height = A4
    
    width_pt = settings["width_mm"] * 72 / 25.4
    height_pt = settings["height_mm"] * 72 / 25.4
    
    cards_per_row = 3
    cards_per_col = 3
    spacing = 0
    
    margin_x_pt = (page_width - (cards_per_row * width_pt + (cards_per_row - 1) * spacing)) / 2
    margin_y_pt = (page_height - (cards_per_col * height_pt + (cards_per_col - 1) * spacing)) / 2
    
    CROP_MARK_LEN = 8
    CROP_MARK_GAP = 3
    
    def draw_crop_marks(x, y, w, h):
        c.saveState()
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(0.3)
        corners = [
            (x, y), (x + w, y), (x, y + h), (x + w, y + h)
        ]
        for cx, cy in corners:
            dx = -1 if cx == x else 1
            c.line(cx + dx * CROP_MARK_GAP, cy, cx + dx * (CROP_MARK_GAP + CROP_MARK_LEN), cy)
            dy = -1 if cy == y else 1
            c.line(cx, cy + dy * CROP_MARK_GAP, cx, cy + dy * (CROP_MARK_GAP + CROP_MARK_LEN))
        c.restoreState()

    def draw_page(start_index):
        idx = start_index
        for row in range(cards_per_col):
            for col in range(cards_per_row):
                if idx >= len(images):
                    return idx
                img = images[idx]
                img_buf = BytesIO()
                img.save(img_buf, format="PNG", dpi=(settings["dpi"], settings["dpi"]))
                img_buf.seek(0)
                img_reader = ImageReader(img_buf)
                
                x = margin_x_pt + col * (width_pt + spacing)
                y = page_height - margin_y_pt - (row + 1) * height_pt - row * spacing
                
                c.drawImage(img_reader, x, y, width=width_pt, height=height_pt)
                draw_crop_marks(x, y, width_pt, height_pt)
                idx += 1
        return idx
    
    pbar = tqdm(total=len(images), desc="Processando PDF")
    idx = 0
    while idx < len(images):
        old_idx = idx
        idx = draw_page(idx)
        pbar.update(idx - old_idx)
        c.showPage()
        
    pbar.close()
    c.save()

if __name__ == "__main__":
    start_time = time.time()
    
    with open("cards.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    settings = data.get("settings", {})
    cards_def = data.get("cards", [])
    
    # Expand based on count
    deck = []
    for c in cards_def:
        count = c.get("count", 1)
        for _ in range(count):
            deck.append(c)
            
    print(f"Total de cartas a gerar: {len(deck)}")
    
    images = []
    for card in tqdm(deck, desc="Renderizando imagens"):
        img = create_card_image(card, settings)
        images.append(img)
        
    output_pdf = "print_flip7_v2.pdf"
    print(f"Salvando em {output_pdf}...")
    save_cards_to_pdf(images, settings, output_pdf)
    
    print(f"Sucesso! Tempo total: {time.time() - start_time:.2f} s")
