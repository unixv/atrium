from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parents[1] / "frontend" / "public" / "assets" / "items"
OUT.mkdir(parents=True, exist_ok=True)
S = 4

OUTLINE = "#20242a"
OUTLINE_2 = "#3a4147"
WOOD = "#7b4f31"
WOOD_DARK = "#4a2f20"
WOOD_LIGHT = "#b47b4b"
CREAM = "#ded0b8"
CREAM_LIGHT = "#fbefd9"
CREAM_DARK = "#a58f70"
METAL = "#8d9aa1"
METAL_LIGHT = "#cbd4d6"
METAL_DARK = "#536168"
GLASS = "#aee5ef"
GLASS_DARK = "#5aa5b8"
BLUE = "#2e6f8f"
BLUE_DARK = "#174155"
GOLD = "#d9aa3e"
GOLD_DARK = "#8f641c"
GREEN = "#31965d"
GREEN_LIGHT = "#55c27c"
GREEN_DARK = "#1b5736"
RED = "#b55150"
RED_DARK = "#733333"
SLATE = "#4e6475"
SLATE_DARK = "#263642"
TEAL = "#2c8492"
TEAL_DARK = "#17515b"
INK_ALPHA = (0, 0, 0, 0)


def hx(color: str, a: int = 255):
    color = color.lstrip("#")
    if len(color) == 3:
        color = "".join(ch * 2 for ch in color)
    return tuple(int(color[i:i+2], 16) for i in (0, 2, 4)) + (a,)


def shade(color: str, amt: int):
    color = color.lstrip("#")
    if len(color) == 3:
        color = "".join(ch * 2 for ch in color)
    vals = [max(0, min(255, int(color[i:i+2], 16) + amt)) for i in (0, 2, 4)]
    return tuple(vals) + (255,)


def canvas(w: int, h: int):
    return Image.new("RGBA", (w * S, h * S), INK_ALPHA)


def d(im):
    return ImageDraw.Draw(im)


def box(rect):
    return tuple(round(v * S) for v in rect)


def pts(points):
    return [(round(x * S), round(y * S)) for x, y in points]


def save(name: str, im: Image.Image):
    # Keep sprites crisp but not jagged. Final files are 2x the design size.
    out = im.resize((im.width // 2, im.height // 2), Image.Resampling.LANCZOS)
    out.save(OUT / f"{name}.png")


def line(draw, points, fill, width=1):
    draw.line(pts(points), fill=fill if isinstance(fill, tuple) else hx(fill), width=max(1, round(width*S)), joint="curve")


def poly(draw, points, fill, outline=OUTLINE, width=1):
    draw.polygon(pts(points), fill=fill if isinstance(fill, tuple) else hx(fill))
    if outline:
        line(draw, points + [points[0]], outline, width)


def rect(draw, rect_, fill, outline=OUTLINE, width=1, radius=0):
    if radius:
        draw.rounded_rectangle(box(rect_), radius=round(radius*S), fill=fill if isinstance(fill, tuple) else hx(fill), outline=hx(outline) if outline else None, width=max(1, round(width*S)))
    else:
        draw.rectangle(box(rect_), fill=fill if isinstance(fill, tuple) else hx(fill), outline=hx(outline) if outline else None, width=max(1, round(width*S)))


def ellipse(draw, rect_, fill, outline=OUTLINE, width=1):
    draw.ellipse(box(rect_), fill=fill if isinstance(fill, tuple) else hx(fill), outline=hx(outline) if outline else None, width=max(1, round(width*S)))


def soft_shadow(im, cx, cy, w, h, alpha=55, blur=5):
    # Do not bake floating blob shadows into the art. The room renderer draws
    # tile-contact shadows so props stay grounded consistently.
    return


def diamond(cx, cy, w, h):
    return [(cx, cy-h/2), (cx+w/2, cy), (cx, cy+h/2), (cx-w/2, cy)]


def cuboid(draw, cx, cy, w, depth, h, top, left, right, outline=OUTLINE, width=1.15):
    # cy is center of top diamond.
    top_pts = diamond(cx, cy, w, depth)
    l_top, r_top, b_top, back_top = top_pts[3], top_pts[1], top_pts[2], top_pts[0]
    left_pts = [l_top, b_top, (b_top[0], b_top[1]+h), (l_top[0], l_top[1]+h)]
    right_pts = [r_top, b_top, (b_top[0], b_top[1]+h), (r_top[0], r_top[1]+h)]
    poly(draw, left_pts, left, outline, width)
    poly(draw, right_pts, right, outline, width)
    poly(draw, top_pts, top, outline, width)


def base_plate(draw, cx, cy, w, depth, color="#d7d0c4"):
    cuboid(draw, cx, cy, w, depth, 8, color, shade(color, -42), shade(color, -28), OUTLINE, 1.0)


def panel(draw, x, y, w, h, fill, outline=OUTLINE, radius=0):
    rect(draw, (x, y, x+w, y+h), fill, outline, 1.15, radius)
    rect(draw, (x+4, y+4, x+w-4, y+h-4), (255,255,255,35), None, 0, max(0, radius-2))


def glint(draw, x1, y1, x2, y2, alpha=95, width=.7):
    line(draw, [(x1,y1),(x2,y2)], (255,255,255,alpha), width)


# ------- Floor pieces -------

def rug_ocean():
    im = canvas(210, 120); dd = d(im)
    poly(dd, diamond(105, 67, 150, 66), hx(TEAL_DARK), "#0f4048", 1.1)
    poly(dd, diamond(105, 67, 126, 52), hx("#2aa7b5"), "#6ce8ef", .75)
    poly(dd, diamond(105, 67, 98, 38), hx("#1b5664"), "#a5f8ff", .65)
    for off in [0, 9, -9]:
        line(dd, [(64,67+off),(105,49+off/2),(146,67+off)], (255,255,255,36), .65)
    save("rug_ocean", im)


def runner_sky():
    im = canvas(260, 90); dd = d(im)
    poly(dd, diamond(130, 45, 212, 44), hx("#456f80"), "#223d4a", 1)
    poly(dd, diamond(130, 45, 190, 34), hx("#9ec6d0"), "#e9ffff", .7)
    for i in range(4):
        x1 = 72 + i*28
        line(dd, [(x1, 46), (130, 22), (188-i*28, 46)], (255,255,255,45), .55)
    save("runner_sky", im)


def floor_marker():
    im = canvas(120, 82); dd = d(im)
    poly(dd, diamond(60, 42, 78, 35), (105,221,240,105), "#56d8e8", 1)
    poly(dd, diamond(60, 42, 50, 21), (28,88,102,150), "#a8ffff", .8)
    save("floor_marker", im)


# ------- Seating and low furniture -------

def velvet_ottoman(name="pouf_coral", color=RED):
    im = canvas(132, 112); dd = d(im)
    soft_shadow(im, 66, 91, 66, 18, 36, 3)
    cuboid(dd, 66, 45, 62, 32, 34, shade(color, 18), shade(color, -30), shade(color, -14), "#462c2c", 1.0)
    # inset top cushion
    poly(dd, diamond(66, 43, 42, 21), shade(color, 36), None)
    glint(dd, 45, 50, 66, 39, 50, .6)
    save(name, im)


def cube_seat():
    im = canvas(132, 116); dd = d(im)
    soft_shadow(im, 66, 96, 66, 20, 35, 3)
    cuboid(dd, 66, 42, 62, 34, 42, "#5e4d38", "#39301f", "#4f3e2b", OUTLINE, 1.0)
    poly(dd, diamond(66, 38, 32, 16), (255,255,255,55), None)
    save("cube_seat", im)


def lounge_seat():
    im = canvas(188, 132); dd = d(im)
    soft_shadow(im, 94, 106, 118, 26, 38, 3)
    cuboid(dd, 94, 64, 112, 52, 30, "#6d8da0", "#3a586a", "#4d7082", OUTLINE, 1.0)
    cuboid(dd, 88, 47, 102, 38, 18, "#7fa7bc", "#476a7c", "#5b8295", OUTLINE, 1.0)
    line(dd, [(52,69),(94,89),(136,69)], "#2e4d5e", 1.2)
    save("lounge_seat", im)


def office_chair():
    im = canvas(138, 164); dd = d(im)
    soft_shadow(im, 69, 145, 66, 20, 32, 3)
    # base star
    for x in [44, 94, 55, 83]: line(dd, [(69,127),(x,145)], "#2e3439", 2.2)
    line(dd, [(69,94),(69,130)], "#333b40", 3)
    cuboid(dd, 69, 90, 56, 30, 18, "#385b72", "#203d4e", "#2b4d61", OUTLINE, .9)
    rect(dd, (47, 39, 91, 86), "#406a82", "#172b36", 1.1, 7)
    rect(dd, (52, 45, 86, 80), (255,255,255,28), None, 0, 5)
    save("office_chair", im)


# ------- Office / reference-style pieces -------

def executive_desk():
    im = canvas(268, 180); dd = d(im)
    soft_shadow(im, 134, 144, 178, 35, 34, 4)
    cuboid(dd, 134, 76, 184, 58, 48, "#8d5c37", "#51311f", "#6b4027", "#271a13", 1.1)
    # front panels
    panel(dd, 72, 96, 50, 22, "#d6c4a4", "#32241a", 2)
    panel(dd, 146, 93, 52, 22, "#d6c4a4", "#32241a", 2)
    # phone, papers, lamp
    rect(dd, (94, 55, 116, 68), "#20282f", "#0f151a", .8, 2)
    line(dd, [(105,68),(91,78)], "#222", 1.5)
    poly(dd, diamond(159, 58, 38, 16), hx(CREAM_LIGHT), "#8a7a61", .7)
    glint(dd, 70, 77, 132, 51, 58, .7)
    save("executive_desk", im)


def reception_desk():
    im = canvas(286, 184); dd = d(im)
    soft_shadow(im, 143, 148, 190, 36, 34, 4)
    cuboid(dd, 143, 82, 200, 60, 48, "#805532", "#4d2f1d", "#684026", "#271a13", 1.1)
    # raised side returns
    cuboid(dd, 88, 72, 70, 34, 24, "#a47a4e", "#65432b", "#805332", OUTLINE, .9)
    cuboid(dd, 199, 70, 70, 34, 24, "#a47a4e", "#65432b", "#805332", OUTLINE, .9)
    panel(dd, 84, 105, 44, 20, "#e2d1ad", "#33261b", 1)
    panel(dd, 154, 102, 50, 20, "#e2d1ad", "#33261b", 1)
    rect(dd, (176, 59, 204, 74), "#22313c", "#11191f", .8, 2)
    rect(dd, (101, 64, 121, 76), "#b13b36", "#5c2220", .8, 2)
    glint(dd, 51, 86, 142, 50, 52, .7)
    save("reception_desk", im)


def work_terminal():
    im = canvas(198, 170); dd = d(im)
    soft_shadow(im, 99, 140, 112, 26, 34, 3)
    cuboid(dd, 99, 93, 122, 42, 36, "#855532", "#51321f", "#684026", OUTLINE, 1)
    rect(dd, (103, 45, 145, 76), "#213746", "#101820", 1.1, 2)
    rect(dd, (109, 51, 139, 70), GLASS, None, 0, 1)
    line(dd, [(124,77),(124,95)], "#26333c", 3)
    poly(dd, diamond(68, 90, 38, 18), hx(CREAM), "#6d5f4c", .7)
    cuboid(dd, 70, 74, 34, 20, 20, "#b39b79", "#69583f", "#867052", OUTLINE, .8)
    save("work_terminal", im)


def info_kiosk():
    im = canvas(138, 190); dd = d(im)
    soft_shadow(im, 69, 165, 58, 18, 30, 3)
    base_plate(dd, 69, 154, 54, 25, "#d4cab7")
    rect(dd, (45, 40, 93, 142), CREAM, "#655947", 1.0, 8)
    rect(dd, (53, 50, 85, 82), "#213946", "#1b2a31", .9, 3)
    rect(dd, (59, 56, 79, 74), GLASS, None, 0, 2)
    rect(dd, (57, 98, 81, 106), GOLD, GOLD_DARK, .7, 2)
    rect(dd, (61, 114, 77, 119), "#6f786d", None, 0, 1)
    save("info_kiosk", im)


def drink_counter():
    im = canvas(230, 180); dd = d(im)
    soft_shadow(im, 115, 145, 146, 34, 32, 4)
    cuboid(dd, 115, 95, 148, 54, 40, "#6f4a30", "#3f281a", "#583822", OUTLINE, 1)
    cuboid(dd, 115, 58, 138, 48, 28, "#e4d2ad", "#967b57", "#c6a87d", OUTLINE, 1)
    # glass front
    rect(dd, (74, 92, 156, 122), (170,225,235,115), "#405663", .8, 2)
    for x, col in [(90, "#4da0d1"), (111, GOLD), (132, GREEN_LIGHT)]:
        rect(dd, (x-4, 72, x+4, 92), col, "#2a2e26", .65, 2)
        ellipse(dd, (x-5, 68, x+5, 77), col, "#2a2e26", .65)
    save("drink_counter", im)


def filing_cabinet():
    im = canvas(138, 158); dd = d(im)
    soft_shadow(im, 69, 135, 70, 22, 30, 3)
    cuboid(dd, 69, 55, 70, 34, 68, "#a8b2b8", "#68777f", "#83929a", "#334047", 1)
    for y in [72, 94, 116]:
        rect(dd, (49, y, 89, y+14), "#c2ccd1", "#58676e", .55, 1)
        rect(dd, (63, y+5, 75, y+8), "#59666c", None, 0, 0)
    save("filing_cabinet", im)


# ------- Display -------

def map_board():
    im = canvas(230, 178); dd = d(im)
    soft_shadow(im, 115, 150, 138, 24, 28, 3)
    rect(dd, (42, 36, 188, 112), "#5a3827", "#231815", 1.3, 2)
    rect(dd, (50, 45, 180, 103), "#5babc4", "#1e3e4c", 1.0, 1)
    # map shapes
    for shape in [[(72,66),(90,55),(104,65),(96,78),(78,78)],[(123,58),(152,66),(147,83),(119,81)],[(90,86),(117,83),(124,95),(101,99)]]:
        poly(dd, shape, hx("#d6b84c"), None)
    line(dd, [(50, 45), (180, 103)], (255,255,255,50), .7)
    for x in [60,172]: line(dd, [(x,112),(x,148)], "#30221a", 3)
    save("map_board", im)


def display_case():
    im = canvas(156, 174); dd = d(im)
    soft_shadow(im, 78, 148, 78, 24, 32, 3)
    base_plate(dd, 78, 132, 82, 36, "#d6cdbf")
    # glass prism
    poly(dd, [(45,70),(78,52),(112,70),(112,112),(78,132),(45,112)], (205,241,248,116), "#49636d", 1.0)
    line(dd, [(78,52),(78,132)], (255,255,255,70), .8)
    cuboid(dd, 78, 100, 42, 20, 12, GOLD, GOLD_DARK, shade(GOLD, -25), "#604719", .8)
    save("display_case", im)


def trophy_case():
    im = canvas(184, 176); dd = d(im)
    soft_shadow(im, 92, 148, 104, 26, 32, 3)
    cuboid(dd, 92, 110, 110, 46, 28, "#7b5638", "#4d311f", "#614026", OUTLINE, 1)
    rect(dd, (52, 49, 132, 113), (195,235,241,112), "#435760", 1.0, 3)
    for x in [74, 92, 110]:
        ellipse(dd, (x-7, 65, x+7, 80), GOLD, GOLD_DARK, .7)
        rect(dd, (x-4, 80, x+4, 96), GOLD_DARK, None, 0, 0)
    save("trophy_case", im)


def world_globe():
    im = canvas(154, 172); dd = d(im)
    soft_shadow(im, 77, 148, 72, 22, 30, 3)
    ellipse(dd, (43, 29, 111, 97), "#6ab8d5", "#234655", 1.15)
    # meridians
    for x in [58, 77, 96]: line(dd, [(x,35),(x-10 if x<77 else x+10,92)], (255,255,255,35), .65)
    for shape in [[(55,51),(70,42),(83,53),(73,69),(58,65)],[(86,40),(100,52),(93,68),(79,59)],[(65,76),(94,74),(99,86),(73,90)]]:
        poly(dd, shape, hx("#d6b84c"), None)
    line(dd, [(77,98),(77,130)], GOLD_DARK, 3)
    cuboid(dd, 77, 137, 68, 30, 12, "#6e4c32", "#3e2a1e", "#563921", OUTLINE, 1)
    save("world_globe", im)


def bubble_sculpture():
    im = canvas(160, 194); dd = d(im)
    soft_shadow(im, 80, 166, 76, 22, 30, 3)
    line(dd, [(80, 77), (80, 150)], "#4d5a60", 3)
    for x,y,r,a in [(78,47,12,190),(95,62,11,175),(64,67,11,170),(82,82,13,176),(105,94,11,155),(66,102,12,160),(89,116,11,155)]:
        ellipse(dd, (x-r,y-r,x+r,y+r), (225,238,240,a), "#7d8c92", .75)
    base_plate(dd, 80, 158, 66, 30, "#d4cbbd")
    save("bubble_sculpture", im)


def marble_plinth():
    im = canvas(134, 160); dd = d(im)
    soft_shadow(im, 67, 140, 66, 20, 28, 3)
    cuboid(dd, 67, 62, 64, 32, 64, "#f0eee5", "#b2b2aa", "#d0d0c7", "#44443e", 1)
    for x in [51, 63, 75]: line(dd, [(x,68),(x+12,92),(x+5,121)], (130,130,124,60), .65)
    save("marble_plinth", im)


def wall_monitor():
    im = canvas(150, 162); dd = d(im)
    soft_shadow(im, 75, 139, 70, 20, 28, 3)
    rect(dd, (45, 45, 105, 84), "#1a2f3a", "#11191f", 1.2, 3)
    rect(dd, (53, 53, 97, 77), GLASS, None, 0, 1)
    line(dd, [(75,84),(75,119)], "#26343c", 4)
    poly(dd, diamond(75, 132, 68, 30), hx("#26343c"), "#11191f", 1.0)
    save("wall_monitor", im)


# ------- Decor -------

def plant_stand():
    im = canvas(150, 190); dd = d(im)
    soft_shadow(im, 75, 163, 64, 20, 30, 3)
    for leaf in [[(75,31),(61,99),(75,82)],[(80,32),(92,102),(77,84)],[(67,57),(39,113),(68,95)],[(88,58),(120,115),(86,96)],[(71,83),(54,146),(74,104)],[(86,83),(101,146),(79,104)]]:
        poly(dd, leaf, GREEN_LIGHT if leaf[0][0] % 2 else GREEN, GREEN_DARK, .8)
        glint(dd, leaf[0][0], leaf[0][1]+4, leaf[2][0], leaf[2][1]-4, 52, .5)
    cuboid(dd, 75, 139, 54, 28, 26, "#9b633d", "#5a3624", "#77482d", OUTLINE, 1)
    save("plant_stand", im)


def floor_planter():
    im = canvas(190, 180); dd = d(im)
    soft_shadow(im, 95, 152, 104, 24, 30, 3)
    cuboid(dd, 95, 123, 92, 38, 26, "#516542", "#313f2c", "#415438", OUTLINE, 1)
    for x in [56,70,84,101,116,131]:
        poly(dd, [(x,55),(x-16,115),(x+5,103)], GREEN, GREEN_DARK, .7)
        poly(dd, [(x+5,53),(x+22,116),(x-1,103)], GREEN_LIGHT, GREEN_DARK, .7)
    save("floor_planter", im)


def lamp_glow():
    im = canvas(130, 204); dd = d(im)
    # glow, drawn first and very soft
    layer = Image.new("RGBA", im.size, INK_ALPHA)
    ld = d(layer)
    ld.ellipse(box((26, 28, 104, 105)), fill=(255,212,93,50))
    im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(10*S)))
    soft_shadow(im, 65, 180, 56, 18, 28, 3)
    line(dd, [(65,80),(65,166)], "#40505a", 3)
    poly(dd, [(36,62),(65,41),(95,62),(65,84)], GOLD, GOLD_DARK, 1)
    poly(dd, [(36,62),(65,84),(65,94),(36,73)], shade(GOLD, -30), GOLD_DARK, 1)
    poly(dd, [(95,62),(65,84),(65,94),(95,73)], shade(GOLD, -15), GOLD_DARK, 1)
    base_plate(dd, 65, 178, 58, 26, "#43505a")
    save("lamp_glow", im)


def signal_mast():
    im = canvas(120, 222); dd = d(im)
    soft_shadow(im, 60, 194, 54, 18, 26, 3)
    line(dd, [(60, 26), (60, 177)], "#4d5a61", 2.2)
    line(dd, [(51, 46), (69, 46)], "#a1b1b9", 1.8)
    line(dd, [(54, 67), (66, 67)], "#a1b1b9", 1.8)
    ellipse(dd, (55, 20, 65, 30), "#f7fafb", "#6e7e86", .7)
    base_plate(dd, 60, 190, 54, 25, "#d5d2c7")
    save("signal_mast", im)


def crate_walnut():
    im = canvas(140, 132); dd = d(im)
    soft_shadow(im, 70, 106, 66, 20, 30, 3)
    cuboid(dd, 70, 55, 72, 38, 40, "#96613b", "#58331f", "#764629", "#2f2118", 1)
    for p1, p2 in [((52, 48),(70, 58)), ((70,48),(88,58)), ((52,68),(70,78)), ((88,68),(70,78))]: line(dd, [p1,p2], (255,220,160,65), .75)
    save("crate_walnut", im)


def glass_table():
    im = canvas(190, 128); dd = d(im)
    soft_shadow(im, 95, 108, 120, 22, 26, 3)
    for x,y in [(56,74),(134,74),(76,84),(114,84)]: line(dd, [(x,y),(x,y+28)], "#384b52", 2.5)
    poly(dd, diamond(95, 64, 132, 56), (190,237,244,128), "#34636e", 1.05)
    poly(dd, diamond(95, 64, 100, 38), (255,255,255,42), "#b8eef5", .6)
    save("glass_table", im)


def coffee_table():
    im = canvas(190, 122); dd = d(im)
    soft_shadow(im, 95, 98, 118, 22, 28, 3)
    cuboid(dd, 95, 58, 128, 44, 16, "#9b704d", "#593821", "#74482d", OUTLINE, 1)
    for x,y in [(56,69),(134,69),(76,79),(114,79)]: line(dd, [(x,y),(x,y+20)], "#3f281b", 2.4)
    save("coffee_table", im)


def divider_panel():
    im = canvas(210, 176); dd = d(im)
    soft_shadow(im, 105, 149, 122, 22, 28, 3)
    for i, x in enumerate([55,85,115]):
        rect(dd, (x, 44, x+36, 134), CREAM if i%2==0 else "#c7b596", "#4b4034", 1, 2)
        rect(dd, (x+6, 55, x+30, 123), (255,255,255,58), None, 0, 1)
    line(dd, [(54,137),(158,137)], "#4b4034", 2)
    save("divider_panel", im)


def book_stack():
    im = canvas(124, 98); dd = d(im)
    soft_shadow(im, 62, 84, 60, 16, 22, 3)
    for i, col in enumerate(["#6c8aa0", "#c5a14a", "#8e5e45", "#596f4e"]):
        cuboid(dd, 62+i*2, 59-i*8, 62-i*3, 22, 6, col, shade(col,-42), shade(col,-26), "#342b25", .7)
    save("book_stack", im)


MAKERS = [
    rug_ocean, runner_sky, floor_marker,
    velvet_ottoman, cube_seat, lounge_seat, office_chair,
    reception_desk, executive_desk, work_terminal, info_kiosk, drink_counter, filing_cabinet,
    map_board, display_case, trophy_case, world_globe, bubble_sculpture, marble_plinth, wall_monitor,
    plant_stand, floor_planter, lamp_glow, signal_mast, crate_walnut, glass_table, coffee_table, divider_panel, book_stack,
]

if __name__ == "__main__":
    for maker in MAKERS:
        maker()
    print(f"generated {len(MAKERS)} item sprites in {OUT}")
