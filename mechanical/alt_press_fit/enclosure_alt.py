#!/usr/bin/env python3
"""PressureTaps alternative enclosure: a sensor module glued to the PCB, pressed into a separate case.
Needs cadquery. Usage: enclosure_alt.py OUTPUT_DIR
Model origin = centre of the 4 x 4 sensor grid, board (128.5, 125). Z = 0 is the PCB top face.
Ampseal data from TE drawing 2489696 and application spec 114-160220.

Parts
  Cover:      glued on the IC side, 17 sealed chambers.
  Tube block: glued on the back, square glue grid and 17 barbs.
              Four M3 x 6 screws at H5-H8 hold cover and block together while the glue cures.
  Case:       top and bottom halves. The tube block spigot presses through the bottom-half window.

Seals
  Chambers:   glue on the cover walls and the tube block grid, clamped flat on the PCB by the screws.
  Window:     1.5 mm silicone cord in the spigot groove, a radial seal, so it needs no clamping.
  Cover:      a second 1.5 mm cord on the cover spigot seals into a blind socket under the lid.
              No opening goes through the lid, and the seal puts no load on the lid.
  Seam:       2 mm silicone cord in the bottom-half groove, ends butt on the Ampseal gasket.
  Connector:  the header's own silicone gasket on the 4.5 mm end wall."""
import sys
import cadquery as cq

CX, CY = 128.5, 125.0
def p(x, y):
    return (x - CX, CY - y)
def box(x1, x2, y1, y2, z1, z2):
    (a, b), (c, d) = p(x1, y1), p(x2, y2)
    return cq.Workplane("XY").workplane(offset=z1).center((a + c) / 2, (b + d) / 2).rect(abs(c - a), abs(d - b)).extrude(z2 - z1)
def rbox(x1, x2, y1, y2, z1, z2, r):
    return box(x1, x2, y1, y2, z1, z2).edges("|Z").fillet(r)
def cyl(x, y, d, z1, z2):
    return cq.Workplane("XY").workplane(offset=z1).center(*p(x, y)).circle(d / 2).extrude(z2 - z1)
def prism(pts, width=200):
    return cq.Workplane("XZ").polyline([(x - CX, z) for x, z in pts]).close().extrude(width / 2, both=True)
def interp(pts, x):
    for (a, za), (b, zb) in zip(pts, pts[1:]):
        if a <= x <= b and b > a:
            return za + (zb - za) * (x - a) / (b - a)
    return pts[-1][1]

# Board
BX1, BX2, BY1, BY2 = 105.9, 192.0, 100.0, 152.0
PCB_T = 1.6
# Ampseal 2489696-1 on the back of the right edge; numbers scaled from TE section A-A
JY = 129.0
JZ = -PCB_T - 10.3          # nose centre
FLANGE_REAR = BX2 + 0.3
FLANGE_T = 3.7              # flange plus uncompressed gasket
GASKET_SQUEEZE = 0.3
FLANGE_HIGH, FLANGE_LOW = JZ + 16.05, JZ - 16.05
# Enclosure
WALL = 4.5                  # also the TE panel thickness T (2-5 mm), screws M3 x 10
GAP = 0.5
R_OUT = 6.0
CAV_X1, CAV_Y1, CAV_Y2 = BX1 - GAP, BY1 - GAP, BY2 + GAP
CAV_X2 = FLANGE_REAR + FLANGE_T - GASKET_SQUEEZE
OUT_X1, OUT_X2, OUT_Y1, OUT_Y2 = CAV_X1 - WALL, CAV_X2 + WALL, CAV_Y1 - WALL, CAV_Y2 + WALL
TALL_X = 157.6
# Seam: high over the sensors, ramps down to the connector centreline
SEAM_HI = 4.0
SEAM_GAP = 0.1              # keeps the H5-H8 clamp in charge of the chamber seal
RAMP_X = 174.0
SEAM = [(OUT_X1 - 20, SEAM_HI), (RAMP_X, SEAM_HI), (RAMP_X + SEAM_HI - JZ, JZ), (OUT_X2 + 20, JZ)]
# Outer and inner profiles along X
LID_TOP = 8.0               # flat over the whole board. P2-P4 pin headers do not fit under it
CEIL = 5.5                  # clears the Ampseal tails, flange and J1
LID_OUT = [(OUT_X1 - 20, LID_TOP), (OUT_X2 + 20, LID_TOP)]
LID_IN = [(CAV_X1, CEIL), (CAV_X2, CEIL)]
BOT_OUT = [(OUT_X1 - 20, -5.7), (180.7, -5.7), (189.9, -14.9), (OUT_X2 + 20, -14.9)]
BOT_IN = [(CAV_X1, -3.2), (180.7, -3.2), (189.9, -12.4), (CAV_X2, -12.4)]
# Rounded hood around the header flange, below the board
HOOD_W_OUT, HOOD_W_IN = 46.8, 41.8
HOOD_R_OUT, HOOD_R_IN = 8.0, 5.5
HOOD_IN = FLANGE_LOW - 0.6
HOOD_OUT = HOOD_IN - 2.5
# Chambers
CELL = 8.0
CELL_R = 1.0
PLUG_R = 1.0
CAV_R = 3.0
ROOF_Z = 2.8
CELLS = [(115 + 9 * (i % 4), 111.5 + 9 * (i // 4), str(i + 1)) for i in range(16)] + [(151, 125, "REF")]
PLUG = [(111.1, 106.4), (147.1, 106.4), (147.1, 119.9), (156.1, 119.9), (156.1, 130.1),
        (147.1, 130.1), (147.1, 143.6), (109.9, 143.6), (109.9, 107.6)]
H = {"H1": (109.7, 103.8), "H2": (188.2, 103.8), "H3": (109.7, 148.2), "H4": (188.2, 148.2),
     "H5": (119.5, 103.4), "H6": (143.5, 103.4), "H7": (119.5, 146.6), "H8": (143.5, 146.6)}
# Tube barbs for 1.6 mm ID tube
BARB_LEN, BARB_D, STEM_D, BORE = 7.0, 2.3, 1.9, 1.0
FO = BOT_OUT[0][1]
# Seam screws: M4 x 10 from the top into M4 heat-set inserts (5.6 mm hole, 6 mm long) in the bottom half.
SEAM_CLEAR, SEAM_INSERT_D, SEAM_INSERT_L, SEAM_WELL_D = 4.5, 5.6, 6.5, 8.0
CLAMP = ("H5", "H6", "H7", "H8")
EARS = [(x, y, SEAM_HI) for x in (112, 138, 166) for y in (OUT_Y1 - 3, OUT_Y2 + 3)] + [(OUT_X1 - 3, 126.0, SEAM_HI)]
EARS += [(195, OUT_Y1 - 3, JZ), (195, OUT_Y2 + 3, JZ)]
EAR_R = 5.0
# Seam cord
CORD_W, CORD_D = 2.4, 1.5
RING = 18.0                 # Ampseal gasket centre line from the connector centre

def cutout():
    return (cq.Workplane("YZ", origin=(CAV_X2 - 1 - CX, 0, 0)).center(p(0, JY)[1], JZ).rect(24.25, 25.0)
            .extrude(WALL + 2).edges("|X").fillet(6.7))
def header_screws():
    out = None
    for z, half in ((JZ - 10.8, 13.7), (JZ + 7.3, 15.2)):
        for s in (-1, 1):
            c = (cq.Workplane("YZ", origin=(CAV_X2 - 1 - CX, 0, 0)).center(p(0, JY + s * half)[1], z)
                 .circle(1.65).extrude(WALL + 2))
            out = c if out is None else out.union(c)
    return out
def ear(x, y, z1, z2):
    e = cyl(x, y, 2 * EAR_R, z1, z2)
    f = 2.0                             # rounded root where the ear meets the wall
    if x < OUT_X1:
        e = e.union(box(x, OUT_X1 + 1, y - EAR_R, y + EAR_R, z1, z2))
        for s in (-1, 1):
            web = box(OUT_X1 - f, OUT_X1 + 0.1, min(y + s * EAR_R, y + s * (EAR_R + f)), max(y + s * EAR_R, y + s * (EAR_R + f)), z1, z2)
            e = e.union(web.cut(cyl(OUT_X1 - f, y + s * (EAR_R + f), 2 * f, z1 - 1, z2 + 1)))
        return e
    corner = x > 190                    # the end ears run into the rounded box corner
    depth = 4.4 if corner else 1
    y1, y2 = (y, OUT_Y1 + depth) if y < 125 else (OUT_Y2 - depth, y)
    e = e.union(box(x - EAR_R, x + EAR_R, y1, y2, z1, z2))
    wall, out = (OUT_Y1, -1) if y < 125 else (OUT_Y2, 1)
    for s in (() if corner else (-1, 1)):
        a, c = sorted((x + s * EAR_R, x + s * (EAR_R + f)))
        b1, b2 = sorted((wall - out * 0.1, wall + out * f))
        web = box(a, c, b1, b2, z1, z2)
        e = e.union(web.cut(cyl(x + s * (EAR_R + f), wall + out * f, 2 * f, z1 - 1, z2 + 1)))
    return e
def hood(top_pts, arc, z_bot, xend, w, r, zr):
    wp = cq.Workplane("XZ").moveTo(top_pts[0][0] - CX, zr).lineTo(top_pts[0][0] - CX, top_pts[0][1]).lineTo(top_pts[1][0] - CX, top_pts[1][1])
    wp = wp.threePointArc((arc[0] - CX, arc[1]), (arc[2] - CX, z_bot)).lineTo(xend - CX, z_bot).lineTo(xend - CX, zr).close()
    side = wp.extrude(100, both=True)
    sec = (cq.Workplane("YZ", origin=(100 - CX, 0, 0)).center(p(0, JY)[1], (zr + z_bot) / 2).rect(w, zr - z_bot)
           .extrude(120).edges("|X").edges("<Z").fillet(r))
    return side.intersect(sec)

# ---------- full shell ----------
plan_out = rbox(OUT_X1, OUT_X2, OUT_Y1, OUT_Y2, -60, 60, R_OUT)
body = prism(LID_OUT + BOT_OUT[::-1]).edges("|Y").fillet(1.5).intersect(plan_out)
body = body.union(hood([(168.5, -14.6), (180, -28.1)], (182.6, -30.2, 185), HOOD_OUT, OUT_X2, HOOD_W_OUT, HOOD_R_OUT, -4).intersect(plan_out))
cav_top = LID_IN
cav = prism(cav_top + BOT_IN[::-1]).intersect(rbox(CAV_X1, CAV_X2, CAV_Y1, CAV_Y2, -40, 40, CAV_R))
body = body.cut(cav)
body = body.cut(hood([(171, -13.3), (181.5, -25.5)], (183, -27.5, 185.2), HOOD_IN, CAV_X2, HOOD_W_IN, HOOD_R_IN, -3.0))
body = body.cut(cutout()).cut(header_screws())
below = prism([(SEAM[0][0], -80)] + SEAM + [(SEAM[-1][0], -80)])
bot = body.intersect(below)
top = body.cut(below.translate((0, 0, SEAM_GAP)))

# ---------- top half ----------
def round_top(w, r=1.0):
    try:
        out = w.faces(">Z").edges().fillet(r)
        return out if out.val().isValid() else w
    except Exception:
        return w
top = round_top(top)
for x, y, z in EARS:
    top = top.union(round_top(ear(x, y, z + SEAM_GAP, LID_TOP)))
def plug(z1, z2):
    return cq.Workplane("XY").workplane(offset=z1).polyline([p(*q) for q in PLUG]).close().extrude(z2 - z1).edges("|Z").fillet(PLUG_R)
def cells(w, z1, z2):
    for x, y, _ in CELLS:
        w = w.cut(cq.Workplane("XY").workplane(offset=z1).center(*p(x, y)).rect(CELL, CELL).extrude(z2 - z1).edges("|Z").fillet(CELL_R))
    return w
for k in ("H1", "H3"):
    top = top.union(cyl(*H[k], 5.0, 0, CEIL + 0.1))
for k in ("H2", "H4"):
    top = top.union(cyl(*H[k], 6.0, 0, CEIL + 0.1))
for x, y, t in CELLS:
    size = 3.0 if t == "REF" else 3.6
    top = top.cut(cq.Workplane("XY").workplane(offset=LID_TOP - 0.3).center(*p(x, y)).text(t, size, 0.4, combine=False, kind="bold"))
for x, y, z in EARS:
    top = top.cut(cyl(x, y, SEAM_CLEAR, z - 1, LID_TOP + 1))
    if z < 0:
        top = top.cut(cyl(x, y, SEAM_WELL_D, z + 4, LID_TOP + 1))     # screw head well, keeps the lid flush

# ---------- glued sensor module ----------
COVER_TOP = 5.0
WINDOW_CLEAR_LID = 0.1
GLUE_GAP = 0.0              # flat: cover and tube block clamp straight onto the PCB
GRID_DEPTH = 0.4
TAB_D = 6.8
SHOULDER = 3.6
COVER_SPIG_TOP = 6.4
LID_POCKET = 6.5            # leaves a 1.5 mm roof over the cover spigot
RIB_LOW = 3.8
RIB_T = 1.5
def cover_spigot(z1, z2, grow=0.0):
    x1, x2, y1, y2, xr, yr1, yr2 = 111.5 - grow, 145.5 + grow, 108.4 - grow, 141.6 + grow, 154.5 + grow, 121.5 - grow, 128.5 + grow
    pts = [(x1, y1), (x2, y1), (x2, yr1), (xr, yr1), (xr, yr2), (x2, yr2), (x2, y2), (x1, y2)]
    return cq.Workplane("XY").workplane(offset=z1).polyline([p(*q) for q in pts]).close().extrude(z2 - z1).edges("|Z").fillet(2.0 + grow)
cover = plug(GLUE_GAP, SHOULDER)
for k in CLAMP:
    x, y = H[k]
    y2 = 106.6 if y < 125 else 143.4
    cover = cover.union(cyl(x, y, TAB_D, 0, COVER_TOP)).union(box(x - TAB_D / 2, x + TAB_D / 2, min(y, y2), max(y, y2), GLUE_GAP, COVER_TOP))
cover = cover.union(cover_spigot(SHOULDER - 0.1, COVER_SPIG_TOP).faces(">Z").edges().chamfer(0.3))
cover = cover.cut(cover_spigot(4.1, 5.8).cut(cover_spigot(4.0, 5.9, -1.1)))
cover = cells(cover, 0, ROOF_Z)
for k in CLAMP:
    cover = cover.cut(cyl(*H[k], 3.4, -1, COVER_TOP + 1)).cut(cyl(*H[k], 5.8, COVER_TOP - 3.2, COVER_TOP + 1))

# blind socket in the lid
rib = cover_spigot(RIB_LOW, CEIL + 0.1, WINDOW_CLEAR_LID + RIB_T).cut(cover_spigot(RIB_LOW - 1, CEIL + 1, WINDOW_CLEAR_LID))
top = top.union(rib).cut(cover_spigot(CEIL - 0.01, LID_POCKET, WINDOW_CLEAR_LID))

grid_top = -PCB_T - GLUE_GAP
FLANGE_Z = BOT_IN[0][1]
SPIG = [(111.0, 108.5), (146.6, 108.5), (146.6, 123.8), (155.6, 123.8), (155.6, 129.8), (146.6, 129.8), (146.6, 142.6), (111.0, 142.6)]
SPIG_R = 2.0
WINDOW_CLEAR = 0.1
def spigot(z1, z2, grow=0.0):
    pts = [(111.0 - grow, 108.5 - grow), (146.6 + grow, 108.5 - grow), (146.6 + grow, 123.8 - grow), (155.6 + grow, 123.8 - grow),
           (155.6 + grow, 129.8 + grow), (146.6 + grow, 129.8 + grow), (146.6 + grow, 142.6 + grow), (111.0 - grow, 142.6 + grow)]
    return cq.Workplane("XY").workplane(offset=z1).polyline([p(*q) for q in pts]).close().extrude(z2 - z1).edges("|Z").fillet(SPIG_R + grow)
tube = plug(FLANGE_Z, grid_top)
tube = tube.union(rbox(146, 148.6, 105.0, 145.0, FLANGE_Z, grid_top, 1.0)).union(rbox(146, 157.3, 118.4, 131.6, FLANGE_Z, grid_top, 2.0))
for k in CLAMP:
    x, y = H[k]
    y2 = 106.6 if y < 125 else 143.4
    tube = tube.union(cyl(x, y, TAB_D, FLANGE_Z, -PCB_T)).union(box(x - TAB_D / 2, x + TAB_D / 2, min(y, y2), max(y, y2), FLANGE_Z, grid_top))
    tube = tube.union(cyl(x, y, 5.6, -5.0, FLANGE_Z + 0.1))
tube = cells(tube, grid_top - GRID_DEPTH, grid_top + 0.1)
sp = spigot(FO, FLANGE_Z + 0.1).faces("<Z").edges().chamfer(0.3)
tube = tube.union(sp)
ring = spigot(-5.2, -3.5).cut(spigot(-5.3, -3.4, -1.1))
tube = tube.cut(ring)
ports = [(x + 1.8, y + 1.8, t) for x, y, t in CELLS]
for x, y, t in ports:
    tube = tube.union(cyl(x, y, STEM_D, FO - BARB_LEN, FO + 0.1))
    for zc in (FO - BARB_LEN + 1.0, FO - BARB_LEN + 3.0):
        cone = cq.Solid.makeCone(BARB_D / 2, STEM_D / 2, 1.5, pnt=cq.Vector(*p(x, y), zc), dir=cq.Vector(0, 0, 1))
        tube = tube.union(cq.Workplane(obj=cone))
    tube = tube.cut(cyl(x, y, BORE, FO - BARB_LEN - 0.1, grid_top + 0.1))
    lab = "P" + t if t != "REF" else t
    lx, ly = (x - 3.9, y + 0.8) if t == "REF" else (x - 3.2, y - 2.6)
    tx = cq.Workplane("XY").workplane(offset=FO).center(*p(lx, ly)).text(lab, 2.2, 0.4, combine=False, kind="bold")
    tube = tube.cut(tx.mirror("YZ", basePointVector=(p(lx, 0)[0], 0, 0)))
for k in CLAMP:
    tube = tube.cut(cyl(*H[k], 4.0, -PCB_T - 3.1, -PCB_T + 0.1))

# ---------- bottom half ----------
x, y = H["H2"]                                          # none at H4: the Ampseal rear lobes sit there
bot = bot.union(cyl(x, y, 6.0, interp(BOT_IN, x) - 0.1, -PCB_T)).union(cyl(x, y, 2.8, -PCB_T, -0.2))
bot = bot.cut(spigot(FO - 1, FLANGE_Z + 0.1, WINDOW_CLEAR))
for k in CLAMP:                                        # blind pockets, the floor stays closed
    bot = bot.cut(cyl(*H[k], 6.4, -5.2, FLANGE_Z + 0.1))
for x, y, z in EARS:
    bot = bot.union(ear(x, y, max(z - 9, FO) if z > 0 else z - 9, z)).cut(cyl(x, y, SEAM_INSERT_D, z - SEAM_INSERT_L, z + 1))
# seam cord groove follows the stepped seam; the end-wall run stops on the Ampseal gasket
m = WALL / 2 - CORD_W / 2
loop = rbox(OUT_X1 + m, OUT_X2 - m, OUT_Y1 + m, OUT_Y2 - m, -60, 60, R_OUT - m)
loop = loop.cut(rbox(OUT_X1 + m + CORD_W, OUT_X2 - m - CORD_W, OUT_Y1 + m + CORD_W, OUT_Y2 - m - CORD_W, -61, 61, R_OUT - m - CORD_W))
loop = loop.cut(box(CAV_X2 + 0.1, OUT_X2, JY - RING + CORD_W / 2, JY + RING - CORD_W / 2, -60, 60))
for yy in (JY - RING, JY + RING):
    loop = loop.union(box(CAV_X2 - 0.1, OUT_X2 - m, yy - CORD_W / 2, yy + CORD_W / 2, -60, 60))
k = CORD_D * 0.414          # mitre of the groove floor at the 45 degree ramp
under = [(SEAM[0][0], SEAM_HI - CORD_D), (RAMP_X - k, SEAM_HI - CORD_D), (SEAM[2][0] - k, JZ - CORD_D), (SEAM[3][0], JZ - CORD_D)]
band = prism([(x, z + 1) for x, z in SEAM] + under[::-1])
bot = bot.cut(loop.intersect(band))

if __name__ == "__main__":
    out = sys.argv[1]
    for name, part in (("Case_Top", top), ("Case_Bottom", bot), ("Sensor_Cover", cover), ("Tube_Block", tube)):
        cq.exporters.export(part, f"{out}/PressureTaps_{name}.step")
        cq.exporters.export(part, f"{out}/PressureTaps_{name}.stl", tolerance=0.02, angularTolerance=0.1)
