"""Generate OG image 1200x630 for social sharing"""
from PIL import Image, ImageDraw, ImageFont
import math

W, H = 1200, 630
BG = (10, 14, 11)
ACCENT = (0, 255, 136)
ACCENT_DIM = (0, 160, 85)
STOP = (255, 51, 102)
THINK = (255, 184, 0)
GO = (0, 255, 136)
MUTED = (90, 110, 95)
TEXT = (232, 255, 232)

def lerp(c1, c2, t):
    return tuple(int(c1[i]*(1-t) + c2[i]*t) for i in range(3))

def arc_color(t):
    if t < 0.4: return lerp(STOP, THINK, t/0.4)
    return lerp(THINK, GO, (t-0.4)/0.6)

img = Image.new("RGBA", (W, H), BG+(255,))

# Subtle gradient
px = img.load()
for y in range(H):
    for x in range(W):
        d = math.sqrt((x-200)**2 + (y-H//2)**2)
        t = min(d / 500, 1.0) ** 1.5
        px[x,y] = lerp((20, 28, 22), BG, t) + (255,)

draw = ImageDraw.Draw(img)

# Mini gauge on left side
gcx, gcy = 200, H//2 - 20
gr = 140
arc_s, arc_e = 210, 330

# Arc gradient
steps = int(abs(arc_e - arc_s) * 3)
for i in range(steps):
    t = i / max(steps-1, 1)
    deg = arc_s + (arc_e - arc_s) * t
    color = arc_color(t)
    rad = math.radians(deg)
    for w in range(-3, 4):
        r = gr + w
        x = gcx + r * math.cos(rad)
        y = gcy + r * math.sin(rad)
        draw.ellipse((x-1, y-1, x+1, y+1), fill=color)

# Ticks
for deg in range(arc_s, arc_e+1, 15):
    rad = math.radians(deg)
    ir = gr - 16
    orr = gr + 4
    t = (deg - arc_s) / (arc_e - arc_s)
    tc = arc_color(t)
    draw.line([(gcx+ir*math.cos(rad), gcy+ir*math.sin(rad)),
               (gcx+orr*math.cos(rad), gcy+orr*math.sin(rad))], fill=tc, width=2)

# Needle
na = math.radians(318)
nl = gr - 30
nx, ny = gcx+nl*math.cos(na), gcy+nl*math.sin(na)
pa = na + math.pi/2
pts = [(gcx+6*math.cos(pa), gcy+6*math.sin(pa)),
       (gcx-6*math.cos(pa), gcy-6*math.sin(pa)),
       (nx-1.5*math.cos(pa), ny-1.5*math.sin(pa)),
       (nx+1.5*math.cos(pa), ny+1.5*math.sin(pa))]
draw.polygon(pts, fill=GO)

# Hub
draw.ellipse((gcx-8, gcy-8, gcx+8, gcy+8), fill=(140,150,142))
draw.ellipse((gcx-3, gcy-3, gcx+3, gcy+3), fill=(40,45,42))

# V below gauge
try:
    fv = ImageFont.truetype("segoeuib.ttf", 90)
except:
    fv = ImageFont.load_default()
vbb = draw.textbbox((0,0), "V", font=fv)
vw, vh = vbb[2]-vbb[0], vbb[3]-vbb[1]
vx = gcx - vw//2
vy = gcy + gr - 30

# V glow
for off in range(12, 0, -2):
    a = int(16 * off / 12)
    gl = Image.new("RGBA", (W,H), (0,0,0,0))
    ImageDraw.Draw(gl).text((vx,vy), "V", font=fv, fill=GO+(a,),
                            stroke_width=off, stroke_fill=GO+(a,))
    img = Image.alpha_composite(img, gl)
draw = ImageDraw.Draw(img)
draw.text((vx, vy), "V", font=fv, fill=ACCENT)

# Right side - text
tx = 420

try:
    f_title = ImageFont.truetype("segoeuib.ttf", 52)
    f_sub = ImageFont.truetype("segoeui.ttf", 22)
    f_tag = ImageFont.truetype("segoeuib.ttf", 16)
except:
    f_title = f_sub = f_tag = ImageFont.load_default()

draw.text((tx, 140), "VETRON", font=f_title, fill=ACCENT)

# Subtitle lines
lines = [
    "Singura aplicatie care iti spune",
    "instant daca o cursa Bolt merita."
]
for i, line in enumerate(lines):
    draw.text((tx, 210 + i*32), line, font=f_sub, fill=TEXT)

# Feature pills
pill_y = 310
pills = [
    ("STOP", STOP),
    ("THINK", THINK),
    ("GO", GO),
]
px_offset = tx
for label, color in pills:
    bb = draw.textbbox((0,0), label, font=f_tag)
    pw = bb[2]-bb[0] + 24
    ph = bb[3]-bb[1] + 12
    # Pill bg
    draw.rounded_rectangle((px_offset, pill_y, px_offset+pw, pill_y+ph), radius=6, fill=color)
    draw.text((px_offset+12, pill_y+4), label, font=f_tag, fill=(0,0,0))
    px_offset += pw + 12

# Bottom features
features = ["Overlay live", "Calculator profit/km", "6 filtre inteligente", "100% offline"]
fx = tx
fy = 400
try:
    f_feat = ImageFont.truetype("segoeui.ttf", 15)
except:
    f_feat = ImageFont.load_default()

for feat in features:
    draw.text((fx, fy), feat, font=f_feat, fill=ACCENT_DIM)
    bb = draw.textbbox((0,0), feat, font=f_feat)
    fw = bb[2]-bb[0]
    fx += fw + 30

# URL bottom right
try:
    f_url = ImageFont.truetype("segoeui.ttf", 14)
except:
    f_url = ImageFont.load_default()
url = "vetron.ro"
ubb = draw.textbbox((0,0), url, font=f_url)
draw.text((W - (ubb[2]-ubb[0]) - 30, H - 40), url, font=f_url, fill=MUTED)

# Three dots bottom left
dy = H - 35
dr = 5
dg = 18
for i, c in enumerate([STOP, THINK, GO]):
    dx = 30 + i*dg
    draw.ellipse((dx-dr, dy-dr, dx+dr, dy+dr), fill=c)

out = r"D:\Exercitiu instalare\Vetron\og-image.png"
img.save(out, "PNG")
print(f"OG image saved: {out}")
