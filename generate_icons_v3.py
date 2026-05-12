"""
VETRON Icon V3 — V integrated inside gauge
Compact, centered, nothing cut off
"""
from PIL import Image, ImageDraw, ImageFont
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

BG = (10, 14, 11)
ACCENT = (0, 255, 136)
ACCENT_DIM = (0, 160, 85)
STOP = (255, 51, 102)
THINK = (255, 184, 0)
GO = (0, 255, 136)
CHROME = (160, 175, 165)
MUTED = (90, 110, 95)


def lerp(c1, c2, t):
    return tuple(int(c1[i]*(1-t) + c2[i]*t) for i in range(3))


def arc_color(t):
    if t < 0.4:
        return lerp(STOP, THINK, t / 0.4)
    else:
        return lerp(THINK, GO, (t - 0.4) / 0.6)


def draw_gradient_arc(draw, center, radius, start, end, width):
    cx, cy = center
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
            draw.ellipse((x-1.2, y-1.2, x+1.2, y+1.2), fill=color)


def radial_bg(img, cx, cy, radius, c_in, c_out):
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            d = math.sqrt((x-cx)**2 + (y-cy)**2)
            t = min(d / radius, 1.0) ** 1.8
            px[x,y] = lerp(c_in, c_out, t) + (255,)


def create_icon(size=1024):
    img = Image.new("RGBA", (size, size), BG+(255,))
    cx, cy = size//2, size//2
    radial_bg(img, cx, cy, size*0.6, (20, 28, 22), BG)
    draw = ImageDraw.Draw(img)

    gauge_r = int(size * 0.35)
    arc_start, arc_end = 210, 330

    # Bezel ring
    for w in range(20):
        br = gauge_r + 22 + w
        brt = max(18, 35 - w*2)
        c = (brt, brt+3, brt+1)
        draw.arc((cx-br, cy-br, cx+br, cy+br), arc_start-5, arc_end+5, fill=c, width=1)

    # Gradient arc
    draw_gradient_arc(draw, (cx, cy), gauge_r, arc_start, arc_end, 8)

    # Ticks
    for deg in range(arc_start, arc_end+1, 10):
        rad = math.radians(deg)
        major = (deg % 30 == 0)
        ir = gauge_r - (28 if major else 16)
        orr = gauge_r + 8
        x1 = cx + ir * math.cos(rad)
        y1 = cy + ir * math.sin(rad)
        x2 = cx + orr * math.cos(rad)
        y2 = cy + orr * math.sin(rad)
        t = (deg - arc_start) / (arc_end - arc_start)
        tc = arc_color(t)
        draw.line([(x1,y1),(x2,y2)], fill=tc, width=(4 if major else 2))

    # STOP / THINK / GO labels outside arc
    try:
        fl = ImageFont.truetype("segoeuib.ttf", int(size * 0.03))
    except:
        fl = ImageFont.load_default()

    for text, deg, color in [("STOP", 218, STOP), ("THINK", 270, THINK), ("GO", 322, GO)]:
        rad = math.radians(deg)
        lr = gauge_r + 50
        lx = cx + lr * math.cos(rad)
        ly = cy + lr * math.sin(rad)
        bb = draw.textbbox((0,0), text, font=fl)
        tw, th = bb[2]-bb[0], bb[3]-bb[1]
        draw.text((lx-tw//2, ly-th//2), text, font=fl, fill=color)

    # Needle to GO zone (315 deg)
    na = math.radians(318)
    nl = gauge_r - 45
    nx = cx + nl * math.cos(na)
    ny = cy + nl * math.sin(na)

    # Tapered needle
    pa = na + math.pi/2
    bw, tw = 10, 2
    pts = [
        (cx + bw*math.cos(pa), cy + bw*math.sin(pa)),
        (cx - bw*math.cos(pa), cy - bw*math.sin(pa)),
        (nx - tw*math.cos(pa), ny - tw*math.sin(pa)),
        (nx + tw*math.cos(pa), ny + tw*math.sin(pa)),
    ]
    draw.polygon(pts, fill=GO)

    # Needle tip glow
    for r in range(18, 0, -2):
        a = int(40 * r / 18)
        gl = Image.new("RGBA", (size,size), (0,0,0,0))
        ImageDraw.Draw(gl).ellipse((nx-r, ny-r, nx+r, ny+r), fill=GO+(a,))
        img = Image.alpha_composite(img, gl)
    draw = ImageDraw.Draw(img)

    # Center hub
    draw.ellipse((cx-16, cy-16, cx+16, cy+16), fill=(40,48,42))
    draw.ellipse((cx-13, cy-13, cx+13, cy+13), fill=CHROME)
    draw.ellipse((cx-5, cy-5, cx+5, cy+5), fill=(50,58,52))

    # V inside gauge — centered, big
    try:
        fv = ImageFont.truetype("segoeuib.ttf", int(size * 0.32))
    except:
        fv = ImageFont.load_default()

    vbb = draw.textbbox((0,0), "V", font=fv)
    vw, vh = vbb[2]-vbb[0], vbb[3]-vbb[1]
    vx = cx - vw//2
    vy = cy + int(size * 0.02)

    # V glow
    for off in range(18, 0, -2):
        a = int(16 * off / 18)
        gl = Image.new("RGBA", (size,size), (0,0,0,0))
        gd = ImageDraw.Draw(gl)
        gd.text((vx, vy), "V", font=fv, fill=GO+(a,),
                stroke_width=off, stroke_fill=GO+(a,))
        img = Image.alpha_composite(img, gl)
    draw = ImageDraw.Draw(img)
    draw.text((vx, vy), "V", font=fv, fill=ACCENT)

    # Three dots below V
    dy = vy + vh + 12
    dr = int(size * 0.016)
    dg = int(size * 0.055)
    for i, c in enumerate([STOP, THINK, GO]):
        dx = cx - dg + i * dg
        for r in range(dr+5, dr, -1):
            a = int(25 * (r-dr) / 5)
            gl = Image.new("RGBA", (size,size), (0,0,0,0))
            ImageDraw.Draw(gl).ellipse((dx-r, dy-r, dx+r, dy+r), fill=c+(a,))
            img = Image.alpha_composite(img, gl)
        draw = ImageDraw.Draw(img)
        draw.ellipse((dx-dr, dy-dr, dx+dr, dy+dr), fill=c)

    return img


def create_adaptive(size=1024):
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    cx, cy = size//2, size//2

    gauge_r = int(size * 0.24)
    arc_s, arc_e = 210, 330

    draw_gradient_arc(draw, (cx,cy), gauge_r, arc_s, arc_e, 6)

    for deg in range(arc_s, arc_e+1, 15):
        rad = math.radians(deg)
        ir = gauge_r - 14
        orr = gauge_r + 5
        t = (deg - arc_s) / (arc_e - arc_s)
        tc = arc_color(t) + (255,)
        draw.line([(cx+ir*math.cos(rad), cy+ir*math.sin(rad)),
                   (cx+orr*math.cos(rad), cy+orr*math.sin(rad))], fill=tc, width=3)

    # Needle
    na = math.radians(318)
    nl = gauge_r - 30
    nx, ny = cx+nl*math.cos(na), cy+nl*math.sin(na)
    pa = na + math.pi/2
    pts = [(cx+7*math.cos(pa), cy+7*math.sin(pa)),
           (cx-7*math.cos(pa), cy-7*math.sin(pa)),
           (nx-2*math.cos(pa), ny-2*math.sin(pa)),
           (nx+2*math.cos(pa), ny+2*math.sin(pa))]
    draw.polygon(pts, fill=GO+(255,))
    draw.ellipse((cx-10, cy-10, cx+10, cy+10), fill=CHROME+(255,))
    draw.ellipse((cx-4, cy-4, cx+4, cy+4), fill=(50,58,52,255))

    # V
    try:
        fv = ImageFont.truetype("segoeuib.ttf", int(size * 0.24))
    except:
        fv = ImageFont.load_default()
    vbb = draw.textbbox((0,0), "V", font=fv)
    vw, vh = vbb[2]-vbb[0], vbb[3]-vbb[1]
    draw.text((cx-vw//2, cy + int(size*0.02)), "V", font=fv, fill=ACCENT+(255,))

    # Dots
    dy = cy + int(size*0.02) + vh + 8
    dr = int(size*0.011)
    dg = int(size*0.04)
    for i, c in enumerate([STOP, THINK, GO]):
        dx = cx - dg + i*dg
        draw.ellipse((dx-dr, dy-dr, dx+dr, dy+dr), fill=c+(255,))

    return img


def create_splash(size=1284):
    img = Image.new("RGBA", (size, size), BG+(255,))
    cx, cy = size//2, size//2 - 30
    radial_bg(img, cx, cy+30, size*0.5, (20, 28, 22), BG)
    draw = ImageDraw.Draw(img)

    gauge_r = int(size * 0.2)

    draw_gradient_arc(draw, (cx,cy), gauge_r, 210, 330, 5)

    for deg in range(210, 331, 15):
        rad = math.radians(deg)
        ir, orr = gauge_r - 12, gauge_r + 4
        t = (deg - 210) / 120
        tc = arc_color(t)
        draw.line([(cx+ir*math.cos(rad), cy+ir*math.sin(rad)),
                   (cx+orr*math.cos(rad), cy+orr*math.sin(rad))], fill=tc, width=2)

    na = math.radians(318)
    nl = gauge_r - 22
    nx, ny = cx+nl*math.cos(na), cy+nl*math.sin(na)
    draw.line([(cx,cy),(nx,ny)], fill=GO, width=3)
    draw.ellipse((cx-7, cy-7, cx+7, cy+7), fill=CHROME)

    # V
    try:
        fv = ImageFont.truetype("segoeuib.ttf", int(size * 0.22))
    except:
        fv = ImageFont.load_default()
    vbb = draw.textbbox((0,0), "V", font=fv)
    vw, vh = vbb[2]-vbb[0], vbb[3]-vbb[1]
    vx, vy = cx - vw//2, cy + int(size*0.02)

    for off in range(20, 0, -2):
        a = int(14 * off / 20)
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
    ty = ey + int(size*0.055)
    draw.text((cx-tw//2, ty), tag, font=ft, fill=MUTED)

    # Dots
    dy = ty + int(size*0.05)
    dr = int(size*0.009)
    dg = int(size*0.03)
    for i, c in enumerate([STOP, THINK, GO]):
        dx = cx - dg + i*dg
        draw.ellipse((dx-dr, dy-dr, dx+dr, dy+dr), fill=c)

    return img


print("Icon...")
create_icon(1024).save(ASSETS / "icon.png", "PNG")
print("Adaptive...")
create_adaptive(1024).save(ASSETS / "adaptive-icon.png", "PNG")
print("Splash...")
create_splash(1284).save(ASSETS / "splash-icon.png", "PNG")

for f in ["icon.png", "adaptive-icon.png", "splash-icon.png"]:
    shutil.copy(ASSETS / f, APP_ASSETS / f)

print("Done - V3 icons saved to Vetron/assets/ and copied to app")
