"""
VETRON Icon V4 — Premium with GPS/NET/API indicators
icon.png stays as V3 (approved)
Metallic bezel, chrome hub, rich gradients, status LEDs
"""
from PIL import Image, ImageDraw, ImageFont
import math, shutil, datetime, pathlib

VETRON = pathlib.Path(r"D:\Exercitiu instalare\Vetron")
ASSETS = VETRON / "assets"
APP_ASSETS = pathlib.Path(r"D:\Exercitiu instalare\DriverPower\DriverPowerRO\assets")
BACKUP = VETRON / "backups"

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
for f in ["adaptive-icon.png", "splash-icon.png"]:
    src = ASSETS / f
    if src.exists():
        shutil.copy(src, BACKUP / f"{f}.{ts}.bak")

BG = (10, 14, 11)
ACCENT = (0, 255, 136)
ACCENT_DIM = (0, 160, 85)
STOP = (255, 51, 102)
THINK = (255, 184, 0)
GO = (0, 255, 136)
MUTED = (90, 110, 95)
LED_GREEN = (0, 220, 100)
LED_BLUE = (50, 140, 255)
LED_OFF = (50, 55, 52)


def lerp(c1, c2, t):
    return tuple(int(c1[i]*(1-t) + c2[i]*t) for i in range(3))


def arc_color(t):
    if t < 0.4:
        return lerp(STOP, THINK, t / 0.4)
    else:
        return lerp(THINK, GO, (t - 0.4) / 0.6)


def radial_bg(img, cx, cy, radius, c_in, c_out):
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            d = math.sqrt((x-cx)**2 + (y-cy)**2)
            t = min(d / radius, 1.0) ** 1.8
            px[x,y] = lerp(c_in, c_out, t) + (255,)


def draw_metallic_ring(draw, cx, cy, r_inner, r_outer):
    for r in range(r_inner, r_outer):
        t = (r - r_inner) / max(r_outer - r_inner - 1, 1)
        edge_t = abs(t - 0.5) * 2
        base = 28 + int(edge_t * 30)
        for deg in range(0, 360):
            rad = math.radians(deg)
            highlight = math.cos(rad - math.radians(45))
            brightness = base + int(highlight * 18)
            brightness = max(15, min(brightness, 75))
            c = (brightness, brightness + 2, brightness + 1)
            x = cx + r * math.cos(rad)
            y = cy + r * math.sin(rad)
            if 0 <= int(x) < draw.im.size[0] and 0 <= int(y) < draw.im.size[1]:
                draw.point((int(x), int(y)), fill=c)


def draw_gradient_arc(draw, cx, cy, radius, start, end, width):
    steps = int(abs(end - start) * 3)
    for i in range(steps):
        t = i / max(steps-1, 1)
        deg = start + (end - start) * t
        color = arc_color(t)
        rad = math.radians(deg)
        for w in range(-width//2, width//2+1):
            r = radius + w
            x = cx + r * math.cos(rad)
            y = cy + r * math.sin(rad)
            draw.ellipse((x-1.3, y-1.3, x+1.3, y+1.3), fill=color)


def draw_chrome_hub(draw, cx, cy, r):
    draw.ellipse((cx-r-3, cy-r-3, cx+r+3, cy+r+3), fill=(25, 30, 27))
    for i in range(r, 0, -1):
        t = i / r
        if t > 0.7:
            b = int(60 + (1-t)/0.3 * 120)
        elif t > 0.3:
            b = int(180 - (0.7-t)/0.4 * 80)
        else:
            b = int(100 - t/0.3 * 50)
        ox = int((1-t) * 2)
        oy = int((1-t) * -2)
        draw.ellipse((cx-i+ox, cy-i+oy, cx+i+ox, cy+i+oy), fill=(b, b+3, b+1))
    draw.ellipse((cx-4, cy-4, cx+4, cy+4), fill=(30, 35, 32))


def draw_needle(draw, cx, cy, angle_deg, length, color, base_w=10, tip_w=2):
    na = math.radians(angle_deg)
    nx = cx + length * math.cos(na)
    ny = cy + length * math.sin(na)
    pa = na + math.pi/2

    # Shadow
    sx, sy = 3, 3
    s_pts = [(cx+base_w*math.cos(pa)+sx, cy+base_w*math.sin(pa)+sy),
             (cx-base_w*math.cos(pa)+sx, cy-base_w*math.sin(pa)+sy),
             (nx-tip_w*math.cos(pa)+sx, ny-tip_w*math.sin(pa)+sy),
             (nx+tip_w*math.cos(pa)+sx, ny+tip_w*math.sin(pa)+sy)]
    draw.polygon(s_pts, fill=(5, 5, 5))

    # Body
    pts = [(cx+base_w*math.cos(pa), cy+base_w*math.sin(pa)),
           (cx-base_w*math.cos(pa), cy-base_w*math.sin(pa)),
           (nx-tip_w*math.cos(pa), ny-tip_w*math.sin(pa)),
           (nx+tip_w*math.cos(pa), ny+tip_w*math.sin(pa))]
    draw.polygon(pts, fill=color)

    # Bright edge
    e_pts = [(cx+(base_w-2)*math.cos(pa), cy+(base_w-2)*math.sin(pa)),
             (cx+(base_w-4)*math.cos(pa), cy+(base_w-4)*math.sin(pa)),
             (nx+(tip_w-1)*math.cos(pa), ny+(tip_w-1)*math.sin(pa)),
             (nx+tip_w*math.cos(pa), ny+tip_w*math.sin(pa))]
    bright = tuple(min(255, c+60) for c in color)
    draw.polygon(e_pts, fill=bright)
    return nx, ny


def draw_led(img, draw, x, y, r, color, is_on=True):
    """Draw a small LED indicator with glow"""
    if is_on:
        # Glow
        for gr in range(r+8, r, -1):
            a = int(30 * (gr-r) / 8)
            gl = Image.new("RGBA", img.size, (0,0,0,0))
            ImageDraw.Draw(gl).ellipse((x-gr, y-gr, x+gr, y+gr), fill=color+(a,))
            img_ref = Image.alpha_composite(img, gl)
            img.paste(img_ref)
        # LED body
        draw.ellipse((x-r, y-r, x+r, y+r), fill=color)
        # Highlight spot
        draw.ellipse((x-r//3-1, y-r//3-1, x+r//3-1, y+r//3-1),
                     fill=tuple(min(255, c+80) for c in color))
    else:
        draw.ellipse((x-r, y-r, x+r, y+r), fill=LED_OFF)
    return img


def draw_status_indicators(img, draw, x, y, font_size, spacing):
    """Draw GPS/NET/API indicators like Gemini design"""
    try:
        fl = ImageFont.truetype("segoeuib.ttf", font_size)
    except:
        fl = ImageFont.load_default()

    led_r = max(4, font_size // 4)
    indicators = [
        ("GPS", LED_GREEN, True),
        ("NET", LED_BLUE, True),
        ("API", LED_GREEN, True),
    ]

    for i, (label, color, on) in enumerate(indicators):
        iy = y + i * spacing
        # Label
        draw.text((x, iy), label, font=fl, fill=MUTED)
        # LED dot
        lbb = draw.textbbox((0,0), label, font=fl)
        lw = lbb[2] - lbb[0]
        lh = lbb[3] - lbb[1]
        led_x = x + lw + led_r + 8
        led_y = iy + lh // 2
        img = draw_led(img, draw, led_x, led_y, led_r, color, on)
        draw = ImageDraw.Draw(img)

    return img, draw


def create_adaptive(size=1024):
    img = Image.new("RGBA", (size, size), BG + (255,))
    cx, cy = size//2, size//2
    radial_bg(img, cx, cy, size*0.55, (22, 28, 24), BG)
    draw = ImageDraw.Draw(img)

    gauge_r = int(size * 0.26)
    arc_s, arc_e = 210, 330

    # Metallic bezel
    draw_metallic_ring(draw, cx, cy, gauge_r + 10, gauge_r + 28)

    # Gradient arc
    draw_gradient_arc(draw, cx, cy, gauge_r, arc_s, arc_e, 7)

    # Ticks
    for deg in range(arc_s, arc_e+1, 10):
        rad = math.radians(deg)
        major = (deg % 30 == 0)
        ir = gauge_r - (24 if major else 14)
        orr = gauge_r + 6
        t = (deg - arc_s) / (arc_e - arc_s)
        tc = arc_color(t)
        draw.line([(cx+ir*math.cos(rad), cy+ir*math.sin(rad)),
                   (cx+orr*math.cos(rad), cy+orr*math.sin(rad))], fill=tc, width=(3 if major else 2))

    # Needle
    nx, ny = draw_needle(draw, cx, cy, 318, gauge_r - 38, GO, 8, 2)

    # Glow at tip
    for r in range(14, 0, -2):
        a = int(35 * r / 14)
        gl = Image.new("RGBA", (size,size), (0,0,0,0))
        ImageDraw.Draw(gl).ellipse((nx-r, ny-r, nx+r, ny+r), fill=GO+(a,))
        img = Image.alpha_composite(img, gl)
    draw = ImageDraw.Draw(img)

    # Chrome hub
    draw_chrome_hub(draw, cx, cy, 13)

    # V inside
    try:
        fv = ImageFont.truetype("segoeuib.ttf", int(size * 0.18))
    except:
        fv = ImageFont.load_default()
    vbb = draw.textbbox((0,0), "V", font=fv)
    vw, vh = vbb[2]-vbb[0], vbb[3]-vbb[1]
    vx = cx - vw//2
    vy = cy + int(size * 0.05)

    for off in range(12, 0, -2):
        a = int(18 * off / 12)
        gl = Image.new("RGBA", (size,size), (0,0,0,0))
        ImageDraw.Draw(gl).text((vx,vy), "V", font=fv, fill=GO+(a,),
                                stroke_width=off, stroke_fill=GO+(a,))
        img = Image.alpha_composite(img, gl)
    draw = ImageDraw.Draw(img)
    draw.text((vx, vy), "V", font=fv, fill=ACCENT)

    # GPS/NET/API indicators - right side
    ind_x = cx + gauge_r + 40
    ind_y = cy - int(size * 0.05)
    img, draw = draw_status_indicators(img, draw, ind_x, ind_y, int(size * 0.022), int(size * 0.035))

    return img


def create_splash(size=1284):
    img = Image.new("RGBA", (size, size), BG + (255,))
    cx, cy = size//2, size//2 - int(size * 0.06)
    radial_bg(img, cx, cy+int(size*0.06), size*0.55, (22, 30, 24), BG)
    draw = ImageDraw.Draw(img)

    gauge_r = int(size * 0.22)
    arc_s, arc_e = 210, 330

    # Metallic bezel
    draw_metallic_ring(draw, cx, cy, gauge_r + 8, gauge_r + 26)

    # Gradient arc
    draw_gradient_arc(draw, cx, cy, gauge_r, arc_s, arc_e, 6)

    # Ticks
    for deg in range(arc_s, arc_e+1, 10):
        rad = math.radians(deg)
        major = (deg % 30 == 0)
        ir = gauge_r - (20 if major else 12)
        orr = gauge_r + 5
        t = (deg - arc_s) / (arc_e - arc_s)
        tc = arc_color(t)
        draw.line([(cx+ir*math.cos(rad), cy+ir*math.sin(rad)),
                   (cx+orr*math.cos(rad), cy+orr*math.sin(rad))], fill=tc, width=(3 if major else 2))

    # Needle
    nx, ny = draw_needle(draw, cx, cy, 318, gauge_r - 32, GO, 7, 2)

    # Tip glow
    for r in range(12, 0, -2):
        a = int(35 * r / 12)
        gl = Image.new("RGBA", (size,size), (0,0,0,0))
        ImageDraw.Draw(gl).ellipse((nx-r, ny-r, nx+r, ny+r), fill=GO+(a,))
        img = Image.alpha_composite(img, gl)
    draw = ImageDraw.Draw(img)

    # Chrome hub
    draw_chrome_hub(draw, cx, cy, 11)

    # GPS/NET/API - right side of gauge
    ind_x = cx + gauge_r + 38
    ind_y = cy - int(size * 0.03)
    img, draw = draw_status_indicators(img, draw, ind_x, ind_y, int(size * 0.018), int(size * 0.03))

    # V below gauge
    try:
        fv = ImageFont.truetype("segoeuib.ttf", int(size * 0.2))
    except:
        fv = ImageFont.load_default()
    vbb = draw.textbbox((0,0), "V", font=fv)
    vw, vh = vbb[2]-vbb[0], vbb[3]-vbb[1]
    vx = cx - vw//2
    vy = cy + gauge_r + 20

    for off in range(18, 0, -2):
        a = int(14 * off / 18)
        gl = Image.new("RGBA", (size,size), (0,0,0,0))
        ImageDraw.Draw(gl).text((vx,vy), "V", font=fv, fill=GO+(a,),
                                stroke_width=off, stroke_fill=GO+(a,))
        img = Image.alpha_composite(img, gl)
    draw = ImageDraw.Draw(img)
    draw.text((vx, vy), "V", font=fv, fill=ACCENT)

    # ETRON
    try:
        fs = ImageFont.truetype("segoeuib.ttf", int(size * 0.04))
    except:
        fs = ImageFont.load_default()
    et = "E T R O N"
    ebb = draw.textbbox((0,0), et, font=fs)
    ew = ebb[2]-ebb[0]
    ey = vy + vh + 6
    draw.text((cx-ew//2, ey), et, font=fs, fill=ACCENT_DIM)

    # Tagline
    try:
        ft = ImageFont.truetype("segoeui.ttf", int(size * 0.022))
    except:
        ft = ImageFont.load_default()
    tag = "Performance Intelligence"
    tbb = draw.textbbox((0,0), tag, font=ft)
    tw = tbb[2]-tbb[0]
    ty = ey + int(size * 0.05)
    draw.text((cx-tw//2, ty), tag, font=ft, fill=MUTED)

    # Three verdict dots
    dy = ty + int(size * 0.045)
    dr = int(size * 0.008)
    dg = int(size * 0.03)
    for i, c in enumerate([STOP, THINK, GO]):
        dx = cx - dg + i*dg
        for r in range(dr+4, dr, -1):
            a = int(30 * (r-dr) / 4)
            gl = Image.new("RGBA", (size,size), (0,0,0,0))
            ImageDraw.Draw(gl).ellipse((dx-r, dy-r, dx+r, dy+r), fill=c+(a,))
            img = Image.alpha_composite(img, gl)
        draw = ImageDraw.Draw(img)
        draw.ellipse((dx-dr, dy-dr, dx+dr, dy+dr), fill=c)

    return img


print("Adaptive icon with GPS/NET/API...")
create_adaptive(1024).save(ASSETS / "adaptive-icon.png", "PNG")
print("OK")

print("Splash icon with GPS/NET/API...")
create_splash(1284).save(ASSETS / "splash-icon.png", "PNG")
print("OK")

for f in ["adaptive-icon.png", "splash-icon.png"]:
    shutil.copy(ASSETS / f, APP_ASSETS / f)

print("Done - V4 with status LEDs")
