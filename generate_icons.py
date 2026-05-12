"""
VETRON Icon Generator — clean, premium app icon set
V shape with speedometer arc + gradient glow
"""
from PIL import Image, ImageDraw, ImageFont
import math, shutil, datetime, pathlib

ASSETS = pathlib.Path(r"D:\Exercitiu instalare\DriverPower\DriverPowerRO\assets")
BACKUP = pathlib.Path(r"D:\Exercitiu instalare\backups")
BACKUP.mkdir(parents=True, exist_ok=True)

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
for f in ["icon.png", "adaptive-icon.png", "splash-icon.png"]:
    src = ASSETS / f
    if src.exists():
        shutil.copy(src, BACKUP / f"{f}.{ts}.bak")
        print(f"Backup: {f}")

# Brand colors
BG = (10, 14, 11)          # #0A0E0B
SURFACE = (20, 26, 21)     # #141A15
ACCENT = (0, 255, 136)     # #00FF88
ACCENT_DIM = (0, 180, 96)
ACCENT_GLOW = (0, 255, 136, 60)
WHITE = (232, 255, 232)    # #E8FFE8
BORDER = (30, 42, 31)      # #1E2A1F


def draw_thick_arc(draw, bbox, start, end, fill, width):
    for w in range(width):
        b = (bbox[0]+w, bbox[1]+w, bbox[2]-w, bbox[3]-w)
        if b[2] > b[0] and b[3] > b[1]:
            draw.arc(b, start, end, fill=fill, width=1)


def radial_gradient_bg(img, center, radius, color_center, color_edge):
    px = img.load()
    w, h = img.size
    cx, cy = center
    for y in range(h):
        for x in range(w):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            t = min(dist / radius, 1.0)
            t = t * t  # quadratic falloff
            r = int(color_center[0] * (1-t) + color_edge[0] * t)
            g = int(color_center[1] * (1-t) + color_edge[1] * t)
            b = int(color_center[2] * (1-t) + color_edge[2] * t)
            px[x, y] = (r, g, b, 255)


def create_icon(size=1024):
    img = Image.new("RGBA", (size, size), BG + (255,))

    # Subtle radial gradient from center
    radial_gradient_bg(img, (size//2, size//2 - 40), size * 0.7, (18, 28, 20), BG)

    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    # Outer speedometer arc (subtle)
    arc_r = int(size * 0.38)
    arc_bbox = (cx - arc_r, cy - arc_r - 40, cx + arc_r, cy + arc_r - 40)
    draw_thick_arc(draw, arc_bbox, 200, 340, BORDER, 6)

    # Accent speedometer arc (partial, showing "performance")
    draw_thick_arc(draw, arc_bbox, 200, 310, ACCENT_DIM, 4)
    draw_thick_arc(draw, arc_bbox, 260, 310, ACCENT, 6)

    # Tick marks on arc
    arc_center = (cx, cy - 40)
    for angle_deg in range(200, 345, 20):
        angle = math.radians(angle_deg)
        inner_r = arc_r - 18
        outer_r = arc_r + 12
        x1 = arc_center[0] + inner_r * math.cos(angle)
        y1 = arc_center[1] + inner_r * math.sin(angle)
        x2 = arc_center[0] + outer_r * math.cos(angle)
        y2 = arc_center[1] + outer_r * math.sin(angle)
        tick_color = ACCENT if angle_deg >= 260 else BORDER
        draw.line([(x1, y1), (x2, y2)], fill=tick_color, width=4)

    # Needle pointing to "GO" zone (~300 degrees)
    needle_angle = math.radians(300)
    needle_len = arc_r - 50
    nx = arc_center[0] + needle_len * math.cos(needle_angle)
    ny = arc_center[1] + needle_len * math.sin(needle_angle)
    # Needle body
    draw.line([arc_center, (nx, ny)], fill=ACCENT, width=8)
    # Needle tip glow
    for r in range(16, 0, -2):
        alpha = int(40 * (r / 16))
        glow_layer = Image.new("RGBA", (size, size), (0,0,0,0))
        gd = ImageDraw.Draw(glow_layer)
        gd.ellipse((nx-r, ny-r, nx+r, ny+r), fill=(0, 255, 136, alpha))
        img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img)
    # Needle center dot
    draw.ellipse((arc_center[0]-14, arc_center[1]-14, arc_center[0]+14, arc_center[1]+14), fill=ACCENT)
    draw.ellipse((arc_center[0]-6, arc_center[1]-6, arc_center[0]+6, arc_center[1]+6), fill=BG + (255,))

    # Big bold "V" letter
    try:
        font_v = ImageFont.truetype("segoeuib.ttf", int(size * 0.42))
    except:
        font_v = ImageFont.load_default()

    v_bbox = draw.textbbox((0, 0), "V", font=font_v)
    v_w = v_bbox[2] - v_bbox[0]
    v_h = v_bbox[3] - v_bbox[1]
    v_x = cx - v_w // 2
    v_y = cy + 20 - v_h // 2

    # V glow effect
    for offset in range(20, 0, -2):
        alpha = int(15 * (offset / 20))
        glow_layer = Image.new("RGBA", (size, size), (0,0,0,0))
        gd = ImageDraw.Draw(glow_layer)
        gd.text((v_x, v_y), "V", font=font_v, fill=(0, 255, 136, alpha),
                stroke_width=offset, stroke_fill=(0, 255, 136, alpha))
        img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img)

    # V letter solid
    draw.text((v_x, v_y), "V", font=font_v, fill=ACCENT)

    # Small "ETRON" text below V, subtle
    try:
        font_sub = ImageFont.truetype("segoeuib.ttf", int(size * 0.065))
    except:
        font_sub = ImageFont.load_default()

    sub_bbox = draw.textbbox((0, 0), "ETRON", font=font_sub)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_x = cx - sub_w // 2
    sub_y = v_y + v_h + 10

    # Letter spacing for ETRON
    draw.text((sub_x, sub_y), "E T R O N", font=font_sub, fill=ACCENT_DIM)

    # Three small verdict dots at the bottom (stop/think/go)
    dot_y = sub_y + int(size * 0.09)
    dot_r = int(size * 0.018)
    dot_gap = int(size * 0.06)
    colors_dots = [(255, 51, 102), (255, 184, 0), (0, 255, 136)]  # red, orange, green
    for i, color in enumerate(colors_dots):
        dx = cx - dot_gap + i * dot_gap
        draw.ellipse((dx - dot_r, dot_y - dot_r, dx + dot_r, dot_y + dot_r), fill=color)

    return img


def create_adaptive_icon(size=1024):
    """Adaptive icon foreground — just the V + arc on transparent bg"""
    # Android adaptive icons need safe zone (66% center), so we design within that
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    # Speedometer arc
    arc_r = int(size * 0.28)
    arc_bbox = (cx - arc_r, cy - arc_r - 30, cx + arc_r, cy + arc_r - 30)
    draw_thick_arc(draw, arc_bbox, 200, 340, (30, 42, 31, 180), 5)
    draw_thick_arc(draw, arc_bbox, 260, 310, ACCENT + (255,), 5)

    # Tick marks
    arc_center = (cx, cy - 30)
    for angle_deg in range(200, 345, 20):
        angle = math.radians(angle_deg)
        inner_r = arc_r - 14
        outer_r = arc_r + 10
        x1 = arc_center[0] + inner_r * math.cos(angle)
        y1 = arc_center[1] + inner_r * math.sin(angle)
        x2 = arc_center[0] + outer_r * math.cos(angle)
        y2 = arc_center[1] + outer_r * math.sin(angle)
        tc = ACCENT + (255,) if angle_deg >= 260 else (30, 42, 31, 180)
        draw.line([(x1, y1), (x2, y2)], fill=tc, width=3)

    # Needle
    needle_angle = math.radians(300)
    needle_len = arc_r - 40
    nx = arc_center[0] + needle_len * math.cos(needle_angle)
    ny = arc_center[1] + needle_len * math.sin(needle_angle)
    draw.line([arc_center, (nx, ny)], fill=ACCENT + (255,), width=6)
    draw.ellipse((arc_center[0]-10, arc_center[1]-10, arc_center[0]+10, arc_center[1]+10), fill=ACCENT + (255,))
    draw.ellipse((arc_center[0]-4, arc_center[1]-4, arc_center[0]+4, arc_center[1]+4), fill=BG + (255,))

    # V
    try:
        font_v = ImageFont.truetype("segoeuib.ttf", int(size * 0.32))
    except:
        font_v = ImageFont.load_default()

    v_bbox = draw.textbbox((0, 0), "V", font=font_v)
    v_w = v_bbox[2] - v_bbox[0]
    v_h = v_bbox[3] - v_bbox[1]
    v_x = cx - v_w // 2
    v_y = cy + 15 - v_h // 2
    draw.text((v_x, v_y), "V", font=font_v, fill=ACCENT + (255,))

    # Three dots
    dot_y = v_y + v_h + 15
    dot_r = int(size * 0.014)
    dot_gap = int(size * 0.045)
    colors_dots = [(255, 51, 102, 255), (255, 184, 0, 255), (0, 255, 136, 255)]
    for i, color in enumerate(colors_dots):
        dx = cx - dot_gap + i * dot_gap
        draw.ellipse((dx - dot_r, dot_y - dot_r, dx + dot_r, dot_y + dot_r), fill=color)

    return img


def create_splash(size=1284):
    """Splash screen icon — larger canvas, centered VETRON branding"""
    img = Image.new("RGBA", (size, size), BG + (255,))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    # Subtle radial gradient
    radial_gradient_bg(img, (cx, cy), size * 0.6, (16, 24, 18), BG)
    draw = ImageDraw.Draw(img)

    # V letter
    try:
        font_v = ImageFont.truetype("segoeuib.ttf", int(size * 0.3))
    except:
        font_v = ImageFont.load_default()

    v_bbox = draw.textbbox((0, 0), "V", font=font_v)
    v_w = v_bbox[2] - v_bbox[0]
    v_h = v_bbox[3] - v_bbox[1]
    v_x = cx - v_w // 2
    v_y = cy - v_h // 2 - 40

    # Glow
    for offset in range(24, 0, -3):
        alpha = int(12 * (offset / 24))
        glow = Image.new("RGBA", (size, size), (0,0,0,0))
        gd = ImageDraw.Draw(glow)
        gd.text((v_x, v_y), "V", font=font_v, fill=(0, 255, 136, alpha),
                stroke_width=offset, stroke_fill=(0, 255, 136, alpha))
        img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    draw.text((v_x, v_y), "V", font=font_v, fill=ACCENT)

    # "ETRON" spaced out
    try:
        font_name = ImageFont.truetype("segoeuib.ttf", int(size * 0.055))
    except:
        font_name = ImageFont.load_default()

    name_text = "E T R O N"
    n_bbox = draw.textbbox((0, 0), name_text, font=font_name)
    n_w = n_bbox[2] - n_bbox[0]
    n_x = cx - n_w // 2
    n_y = v_y + v_h + 16
    draw.text((n_x, n_y), name_text, font=font_name, fill=ACCENT_DIM)

    # Tagline
    try:
        font_tag = ImageFont.truetype("segoeui.ttf", int(size * 0.028))
    except:
        font_tag = ImageFont.load_default()

    tag = "Performance Intelligence"
    t_bbox = draw.textbbox((0, 0), tag, font=font_tag)
    t_w = t_bbox[2] - t_bbox[0]
    draw.text((cx - t_w // 2, n_y + int(size * 0.07)), tag, font=font_tag, fill=(122, 138, 124))

    # Three verdict dots
    dot_y_pos = n_y + int(size * 0.13)
    dot_r = int(size * 0.012)
    dot_gap = int(size * 0.04)
    colors_dots = [(255, 51, 102), (255, 184, 0), (0, 255, 136)]
    for i, color in enumerate(colors_dots):
        dx = cx - dot_gap + i * dot_gap
        draw.ellipse((dx - dot_r, dot_y_pos - dot_r, dx + dot_r, dot_y_pos + dot_r), fill=color)

    return img


print("Generating icon.png (1024x1024)...")
icon = create_icon(1024)
icon.save(ASSETS / "icon.png", "PNG")
print("OK")

print("Generating adaptive-icon.png (1024x1024)...")
adaptive = create_adaptive_icon(1024)
adaptive.save(ASSETS / "adaptive-icon.png", "PNG")
print("OK")

print("Generating splash-icon.png (1284x1284)...")
splash = create_splash(1284)
splash.save(ASSETS / "splash-icon.png", "PNG")
print("OK")

print("\nAll icons generated!")
