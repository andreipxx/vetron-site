"""
VETRON Icon V2 — inspired by Gemini gauge concept
Premium instrument gauge with red→orange→green gradient arc
Clean, dark, professional
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, shutil, datetime, pathlib

VETRON = pathlib.Path(r"D:\Exercitiu instalare\Vetron")
ASSETS = VETRON / "assets"
APP_ASSETS = pathlib.Path(r"D:\Exercitiu instalare\DriverPower\DriverPowerRO\assets")
BACKUP = VETRON / "backups"

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
for f in ["icon.png", "adaptive-icon.png", "splash-icon.png"]:
    src = ASSETS / f
    if src.exists():
        shutil.copy(src, BACKUP / f"{f}.{ts}.bak")

# Colors
BG = (10, 14, 11)
SURFACE = (18, 22, 19)
DARK_RING = (25, 32, 27)
ACCENT = (0, 255, 136)
ACCENT_DIM = (0, 180, 96)
STOP_RED = (255, 51, 102)
THINK_ORANGE = (255, 184, 0)
GO_GREEN = (0, 255, 136)
MUTED = (100, 120, 105)
CHROME = (160, 175, 165)


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] * (1-t) + c2[i] * t) for i in range(3))


def draw_gradient_arc(img, center, radius, start_deg, end_deg, width, colors_stops):
    """Draw arc with color gradient along its length"""
    draw = ImageDraw.Draw(img)
    steps = int(abs(end_deg - start_deg) * 2)
    for i in range(steps):
        t = i / max(steps - 1, 1)
        angle_deg = start_deg + (end_deg - start_deg) * t

        # Find color from stops
        if len(colors_stops) == 3:
            if t < 0.5:
                color = lerp_color(colors_stops[0], colors_stops[1], t * 2)
            else:
                color = lerp_color(colors_stops[1], colors_stops[2], (t - 0.5) * 2)
        else:
            color = colors_stops[0]

        angle = math.radians(angle_deg)
        for w in range(-width//2, width//2 + 1):
            r = radius + w
            x = center[0] + r * math.cos(angle)
            y = center[1] + r * math.sin(angle)
            if 0 <= int(x) < img.size[0] and 0 <= int(y) < img.size[1]:
                draw.ellipse((x-1, y-1, x+1, y+1), fill=color)


def draw_glow_circle(img, center, radius, color, intensity=40):
    """Draw a soft glow circle"""
    for r in range(radius, 0, -1):
        alpha = int(intensity * (r / radius))
        layer = Image.new("RGBA", img.size, (0,0,0,0))
        d = ImageDraw.Draw(layer)
        c = color + (alpha,)
        d.ellipse((center[0]-r, center[1]-r, center[0]+r, center[1]+r), fill=c)
        img = Image.alpha_composite(img, layer)
    return img


def radial_gradient(img, center, r1_color, r2_color, radius):
    px = img.load()
    cx, cy = center
    w, h = img.size
    for y in range(h):
        for x in range(w):
            dist = math.sqrt((x-cx)**2 + (y-cy)**2)
            t = min(dist / radius, 1.0)
            t = t ** 1.5
            r = int(r1_color[0]*(1-t) + r2_color[0]*t)
            g = int(r1_color[1]*(1-t) + r2_color[1]*t)
            b = int(r1_color[2]*(1-t) + r2_color[2]*t)
            px[x,y] = (r, g, b, 255)


def create_icon(size=1024):
    img = Image.new("RGBA", (size, size), BG + (255,))
    cx, cy = size//2, size//2

    # Subtle radial gradient
    radial_gradient(img, (cx, cy - 20), (22, 30, 24), BG, size * 0.65)
    draw = ImageDraw.Draw(img)

    gauge_cy = cy - int(size * 0.05)
    gauge_r = int(size * 0.34)

    # Outer dark ring (bezel effect)
    for w in range(18):
        ring_r = gauge_r + 30 + w
        brightness = max(20, 40 - w * 2)
        ring_color = (brightness, brightness + 5, brightness + 2)
        draw.arc((cx-ring_r, gauge_cy-ring_r, cx+ring_r, gauge_cy+ring_r),
                 195, 345, fill=ring_color, width=1)

    # Tick marks (fine instrument ticks)
    for angle_deg in range(200, 341, 10):
        angle = math.radians(angle_deg)
        is_major = (angle_deg % 20 == 0)

        inner_r = gauge_r - (25 if is_major else 15)
        outer_r = gauge_r + 5
        x1 = cx + inner_r * math.cos(angle)
        y1 = gauge_cy + inner_r * math.sin(angle)
        x2 = cx + outer_r * math.cos(angle)
        y2 = gauge_cy + outer_r * math.sin(angle)

        # Color based on position
        t = (angle_deg - 200) / 140
        if t < 0.35:
            tc = lerp_color(STOP_RED, THINK_ORANGE, t / 0.35)
        elif t < 0.6:
            tc = lerp_color(THINK_ORANGE, GO_GREEN, (t - 0.35) / 0.25)
        else:
            tc = GO_GREEN

        w = 4 if is_major else 2
        draw.line([(x1, y1), (x2, y2)], fill=tc, width=w)

    # Gradient arc (RED → ORANGE → GREEN)
    draw_gradient_arc(img, (cx, gauge_cy), gauge_r, 200, 340, 6,
                      [STOP_RED, THINK_ORANGE, GO_GREEN])
    draw = ImageDraw.Draw(img)

    # Small labels on arc: STOP / THINK / GO
    try:
        font_label = ImageFont.truetype("segoeuib.ttf", int(size * 0.028))
    except:
        font_label = ImageFont.load_default()

    labels = [("STOP", 215, STOP_RED), ("THINK", 270, THINK_ORANGE), ("GO", 325, GO_GREEN)]
    for text, angle_deg, color in labels:
        angle = math.radians(angle_deg)
        label_r = gauge_r + 45
        lx = cx + label_r * math.cos(angle)
        ly = gauge_cy + label_r * math.sin(angle)
        bb = draw.textbbox((0,0), text, font=font_label)
        tw, th = bb[2]-bb[0], bb[3]-bb[1]
        draw.text((lx - tw//2, ly - th//2), text, font=font_label, fill=color)

    # Needle pointing to GO zone (~310 degrees)
    needle_angle = math.radians(315)
    needle_len = gauge_r - 35

    # Needle shadow
    shadow_offset = 4
    nx_s = cx + needle_len * math.cos(needle_angle) + shadow_offset
    ny_s = gauge_cy + needle_len * math.sin(needle_angle) + shadow_offset
    draw.line([(cx + shadow_offset, gauge_cy + shadow_offset), (nx_s, ny_s)],
              fill=(0, 0, 0, 80), width=6)

    # Needle body
    nx = cx + needle_len * math.cos(needle_angle)
    ny = gauge_cy + needle_len * math.sin(needle_angle)

    # Tapered needle using polygon
    perp_angle = needle_angle + math.pi/2
    base_w = 10
    tip_w = 2
    points = [
        (cx + base_w * math.cos(perp_angle), gauge_cy + base_w * math.sin(perp_angle)),
        (cx - base_w * math.cos(perp_angle), gauge_cy - base_w * math.sin(perp_angle)),
        (nx - tip_w * math.cos(perp_angle), ny - tip_w * math.sin(perp_angle)),
        (nx + tip_w * math.cos(perp_angle), ny + tip_w * math.sin(perp_angle)),
    ]
    draw.polygon(points, fill=GO_GREEN)

    # Needle tip glow
    img = draw_glow_circle(img, (int(nx), int(ny)), 20, GO_GREEN, 50)
    draw = ImageDraw.Draw(img)

    # Center hub
    hub_r = 18
    draw.ellipse((cx-hub_r-4, gauge_cy-hub_r-4, cx+hub_r+4, gauge_cy+hub_r+4),
                 fill=(40, 50, 42))
    draw.ellipse((cx-hub_r, gauge_cy-hub_r, cx+hub_r, gauge_cy+hub_r),
                 fill=CHROME)
    draw.ellipse((cx-hub_r+5, gauge_cy-hub_r+5, cx+hub_r-5, gauge_cy+hub_r-5),
                 fill=(60, 70, 62))

    # "V" letter - big, bold, below gauge
    try:
        font_v = ImageFont.truetype("segoeuib.ttf", int(size * 0.28))
    except:
        font_v = ImageFont.load_default()

    v_bb = draw.textbbox((0,0), "V", font=font_v)
    v_w, v_h = v_bb[2]-v_bb[0], v_bb[3]-v_bb[1]
    v_x = cx - v_w // 2
    v_y = gauge_cy + gauge_r - int(size * 0.06)

    # V glow
    for offset in range(16, 0, -2):
        alpha = int(18 * (offset / 16))
        glow = Image.new("RGBA", (size, size), (0,0,0,0))
        gd = ImageDraw.Draw(glow)
        gd.text((v_x, v_y), "V", font=font_v, fill=(0, 255, 136, alpha),
                stroke_width=offset, stroke_fill=(0, 255, 136, alpha))
        img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)
    draw.text((v_x, v_y), "V", font=font_v, fill=ACCENT)

    # "ETRON" spaced
    try:
        font_sub = ImageFont.truetype("segoeuib.ttf", int(size * 0.058))
    except:
        font_sub = ImageFont.load_default()

    etron = "E T R O N"
    e_bb = draw.textbbox((0,0), etron, font=font_sub)
    e_w = e_bb[2] - e_bb[0]
    e_x = cx - e_w // 2
    e_y = v_y + v_h + 4
    draw.text((e_x, e_y), etron, font=font_sub, fill=ACCENT_DIM)

    # Three verdict dots
    dot_y = e_y + int(size * 0.075)
    dot_r = int(size * 0.015)
    dot_gap = int(size * 0.05)
    for i, (color, glow_c) in enumerate([(STOP_RED, STOP_RED), (THINK_ORANGE, THINK_ORANGE), (GO_GREEN, GO_GREEN)]):
        dx = cx - dot_gap + i * dot_gap
        # Dot glow
        for r in range(dot_r + 6, dot_r, -1):
            alpha = int(30 * ((r - dot_r) / 6))
            glow = Image.new("RGBA", (size, size), (0,0,0,0))
            gd = ImageDraw.Draw(glow)
            gd.ellipse((dx-r, dot_y-r, dx+r, dot_y+r), fill=glow_c + (alpha,))
            img = Image.alpha_composite(img, glow)
        draw = ImageDraw.Draw(img)
        draw.ellipse((dx-dot_r, dot_y-dot_r, dx+dot_r, dot_y+dot_r), fill=color)

    return img


def create_adaptive_icon(size=1024):
    """Adaptive foreground — gauge + V on transparent"""
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    cx, cy = size//2, size//2

    gauge_cy = cy - int(size * 0.04)
    gauge_r = int(size * 0.25)

    # Gradient arc
    draw_gradient_arc(img, (cx, gauge_cy), gauge_r, 200, 340, 5,
                      [STOP_RED, THINK_ORANGE, GO_GREEN])
    draw = ImageDraw.Draw(img)

    # Ticks
    for angle_deg in range(200, 341, 20):
        angle = math.radians(angle_deg)
        inner_r = gauge_r - 16
        outer_r = gauge_r + 4
        x1 = cx + inner_r * math.cos(angle)
        y1 = gauge_cy + inner_r * math.sin(angle)
        x2 = cx + outer_r * math.cos(angle)
        y2 = gauge_cy + outer_r * math.sin(angle)
        t = (angle_deg - 200) / 140
        if t < 0.35:
            tc = lerp_color(STOP_RED, THINK_ORANGE, t / 0.35)
        elif t < 0.6:
            tc = lerp_color(THINK_ORANGE, GO_GREEN, (t - 0.35) / 0.25)
        else:
            tc = GO_GREEN
        draw.line([(x1,y1),(x2,y2)], fill=tc + (255,), width=3)

    # Needle
    needle_angle = math.radians(315)
    needle_len = gauge_r - 30
    nx = cx + needle_len * math.cos(needle_angle)
    ny = gauge_cy + needle_len * math.sin(needle_angle)
    perp = needle_angle + math.pi/2
    pts = [
        (cx + 7*math.cos(perp), gauge_cy + 7*math.sin(perp)),
        (cx - 7*math.cos(perp), gauge_cy - 7*math.sin(perp)),
        (nx - 2*math.cos(perp), ny - 2*math.sin(perp)),
        (nx + 2*math.cos(perp), ny + 2*math.sin(perp)),
    ]
    draw.polygon(pts, fill=GO_GREEN + (255,))
    draw.ellipse((cx-12, gauge_cy-12, cx+12, gauge_cy+12), fill=CHROME + (255,))
    draw.ellipse((cx-5, gauge_cy-5, cx+5, gauge_cy+5), fill=(50,60,52,255))

    # V
    try:
        font_v = ImageFont.truetype("segoeuib.ttf", int(size * 0.22))
    except:
        font_v = ImageFont.load_default()
    v_bb = draw.textbbox((0,0), "V", font=font_v)
    v_w, v_h = v_bb[2]-v_bb[0], v_bb[3]-v_bb[1]
    v_x = cx - v_w//2
    v_y = gauge_cy + gauge_r - int(size * 0.04)
    draw.text((v_x, v_y), "V", font=font_v, fill=ACCENT + (255,))

    # Dots
    dot_y = v_y + v_h + 10
    dot_r = int(size * 0.012)
    dot_gap = int(size * 0.04)
    for i, c in enumerate([STOP_RED, THINK_ORANGE, GO_GREEN]):
        dx = cx - dot_gap + i * dot_gap
        draw.ellipse((dx-dot_r, dot_y-dot_r, dx+dot_r, dot_y+dot_r), fill=c + (255,))

    return img


def create_splash(size=1284):
    img = Image.new("RGBA", (size, size), BG + (255,))
    cx, cy = size//2, size//2

    radial_gradient(img, (cx, cy), (20, 28, 22), BG, size * 0.5)
    draw = ImageDraw.Draw(img)

    gauge_cy = cy - int(size * 0.06)
    gauge_r = int(size * 0.18)

    # Gradient arc
    draw_gradient_arc(img, (cx, gauge_cy), gauge_r, 200, 340, 4,
                      [STOP_RED, THINK_ORANGE, GO_GREEN])
    draw = ImageDraw.Draw(img)

    # Ticks
    for angle_deg in range(200, 341, 20):
        angle = math.radians(angle_deg)
        inner_r = gauge_r - 12
        outer_r = gauge_r + 3
        x1 = cx + inner_r * math.cos(angle)
        y1 = gauge_cy + inner_r * math.sin(angle)
        x2 = cx + outer_r * math.cos(angle)
        y2 = gauge_cy + outer_r * math.sin(angle)
        t = (angle_deg - 200) / 140
        if t < 0.35:
            tc = lerp_color(STOP_RED, THINK_ORANGE, t / 0.35)
        elif t < 0.6:
            tc = lerp_color(THINK_ORANGE, GO_GREEN, (t-0.35)/0.25)
        else:
            tc = GO_GREEN
        draw.line([(x1,y1),(x2,y2)], fill=tc, width=2)

    # Needle
    needle_angle = math.radians(315)
    needle_len = gauge_r - 20
    nx = cx + needle_len * math.cos(needle_angle)
    ny = gauge_cy + needle_len * math.sin(needle_angle)
    draw.line([(cx, gauge_cy), (nx, ny)], fill=GO_GREEN, width=4)
    draw.ellipse((cx-8, gauge_cy-8, cx+8, gauge_cy+8), fill=CHROME)

    # V
    try:
        font_v = ImageFont.truetype("segoeuib.ttf", int(size * 0.24))
    except:
        font_v = ImageFont.load_default()
    v_bb = draw.textbbox((0,0), "V", font=font_v)
    v_w, v_h = v_bb[2]-v_bb[0], v_bb[3]-v_bb[1]
    v_x = cx - v_w//2
    v_y = gauge_cy + gauge_r + 10

    # V glow
    for offset in range(20, 0, -2):
        alpha = int(14 * (offset / 20))
        glow = Image.new("RGBA", (size, size), (0,0,0,0))
        gd = ImageDraw.Draw(glow)
        gd.text((v_x, v_y), "V", font=font_v, fill=(0,255,136,alpha),
                stroke_width=offset, stroke_fill=(0,255,136,alpha))
        img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)
    draw.text((v_x, v_y), "V", font=font_v, fill=ACCENT)

    # ETRON
    try:
        font_sub = ImageFont.truetype("segoeuib.ttf", int(size * 0.045))
    except:
        font_sub = ImageFont.load_default()
    etron = "E T R O N"
    e_bb = draw.textbbox((0,0), etron, font=font_sub)
    e_w = e_bb[2] - e_bb[0]
    draw.text((cx - e_w//2, v_y + v_h + 4), etron, font=font_sub, fill=ACCENT_DIM)

    # Tagline
    try:
        font_tag = ImageFont.truetype("segoeui.ttf", int(size * 0.025))
    except:
        font_tag = ImageFont.load_default()
    tag = "Performance Intelligence"
    t_bb = draw.textbbox((0,0), tag, font=font_tag)
    t_w = t_bb[2] - t_bb[0]
    tag_y = v_y + v_h + int(size * 0.065)
    draw.text((cx - t_w//2, tag_y), tag, font=font_tag, fill=MUTED)

    # Three dots
    dot_y = tag_y + int(size * 0.055)
    dot_r = int(size * 0.01)
    dot_gap = int(size * 0.035)
    for i, color in enumerate([STOP_RED, THINK_ORANGE, GO_GREEN]):
        dx = cx - dot_gap + i * dot_gap
        draw.ellipse((dx-dot_r, dot_y-dot_r, dx+dot_r, dot_y+dot_r), fill=color)

    return img


# Generate all
print("Icon 1024x1024...")
icon = create_icon(1024)
icon.save(ASSETS / "icon.png", "PNG")
print("OK")

print("Adaptive icon 1024x1024...")
adaptive = create_adaptive_icon(1024)
adaptive.save(ASSETS / "adaptive-icon.png", "PNG")
print("OK")

print("Splash 1284x1284...")
splash = create_splash(1284)
splash.save(ASSETS / "splash-icon.png", "PNG")
print("OK")

# Copy to app project for builds
for f in ["icon.png", "adaptive-icon.png", "splash-icon.png"]:
    shutil.copy(ASSETS / f, APP_ASSETS / f)
    print(f"Copied {f} → DriverPowerRO/assets/")

print("\nDone! All V2 icons generated.")
