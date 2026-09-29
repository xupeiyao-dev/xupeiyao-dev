"""Generate the light/dark SVG graphics for the GitHub profile README.

Run:  python3 assets/build_assets.py   -> rewrites the SVGs next to this file
Every figure is drawn twice (light + dark) from the same geometry so the
README can swap them with <picture> + prefers-color-scheme.
"""
import math
import random
from pathlib import Path
from xml.sax.saxutils import escape as esc

OUT = Path(__file__).parent  # run from inside assets/
OUT.mkdir(exist_ok=True)

THEMES = {
    "light": dict(
        text="#1f2328", text2="#59636e", muted="#818b98", hair="#d1d9e0",
        line="#9aa4af", accent="#2a78d6", accent_tint="#eaf2fc",
        hl="#eb6834", hl_tint="#fdefe8", on_accent="#ffffff", surface="#ffffff",
    ),
    "dark": dict(
        text="#f0f6fc", text2="#9198a1", muted="#6e7681", hair="#3d444d",
        line="#656c76", accent="#3987e5", accent_tint="#132339",
        hl="#d95926", hl_tint="#2b1911", on_accent="#ffffff", surface="#0d1117",
    ),
}

FONTS = """
  .sans{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif}
  .serif{font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif}
  .mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace}
"""


def svg(w, h, body, label, t):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{label}">\n<title>{label}</title>\n'
        f"<style>{FONTS}</style>\n"
        f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        f'orient="auto-start-reverse"><path d="M1 1 L9 5 L1 9" fill="none" stroke="{t["line"]}" '
        f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>\n'
        f"{body}\n</svg>\n"
    )


def write(name, w, h, draw, label):
    for mode, t in THEMES.items():
        (OUT / f"{name}-{mode}.svg").write_text(svg(w, h, draw(t), label, t), encoding="utf-8")


# --------------------------------------------------------------------------- header
def header(t):
    W = 900
    parts = []
    # left: identity
    parts.append(
        f'<text x="4" y="50" class="sans" font-size="12.5" font-weight="600" letter-spacing="2.2" '
        f'fill="{t["accent"]}">UNDERGRADUATE RESEARCHER · SHOW LAB @ NUS</text>'
    )
    parts.append(
        f'<text x="0" y="114" class="serif" font-size="62" fill="{t["text"]}">Peiyao Xu</text>'
    )
    parts.append(
        f'<text x="3" y="150" class="sans" font-size="17" fill="{t["text2"]}">'
        f"Computer Engineering · National University of Singapore</text>"
    )
    x = 4
    for i, kw in enumerate(["Embodied agents", "Real-to-sim", "Robot evaluation"]):
        parts.append(f'<rect x="{x}" y="176" width="7" height="7" rx="1.5" fill="{t["accent"]}"/>')
        parts.append(
            f'<text x="{x + 14}" y="184" class="sans" font-size="14.5" fill="{t["text"]}">{kw}</text>'
        )
        x += 14 + len(kw) * 8.2 + 26

    # right: real -> sim motif (point cloud cube becomes a wireframe cube on a grid)
    s = 33
    c1, c2, cy = (648, 110), (812, 110), 110

    def iso(cx, x, y, z, k=s):
        return cx + (x - z) * k * 0.866, cy + (x + z) * k * 0.5 - y * k

    rnd = random.Random(7)
    pts = []
    for _ in range(150):  # top face  (lightest)
        pts.append(((rnd.uniform(-1, 1), 1, rnd.uniform(-1, 1)), 0.45))
    for _ in range(115):  # right face x=1 (darkest)
        pts.append(((1, rnd.uniform(-1, 1), rnd.uniform(-1, 1)), 0.9))
    for _ in range(115):  # left face z=1
        pts.append(((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 1), 0.68))
    for _ in range(16):  # sparse ground returns
        pts.append(((rnd.uniform(-1.45, 1.45), -1, rnd.uniform(-1.45, 1.45)), 0.3))
    for (x, y, z), op in pts:
        j = 0.035
        X, Y = iso(c1[0], x + rnd.gauss(0, j), y + rnd.gauss(0, j), z + rnd.gauss(0, j))
        col = t["accent"] if rnd.random() < 0.14 else t["text2"]
        o = max(0.2, min(1, op + rnd.uniform(-0.12, 0.12)))
        parts.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="1.45" fill="{col}" fill-opacity="{o:.2f}"/>')

    # arrow between the two cubes
    parts.append(
        f'<path d="M 712 110 L 744 110" stroke="{t["line"]}" stroke-width="1.6" fill="none" '
        f'marker-end="url(#ah)"/>'
    )

    # ground grid for the sim cube
    g = 1.35
    for k in range(-3, 4):
        v = k * g / 3
        a1, b1 = iso(c2[0], v, -1, -g), iso(c2[0], v, -1, g)
        a2, b2 = iso(c2[0], -g, -1, v), iso(c2[0], g, -1, v)
        for (p, q) in ((a1, b1), (a2, b2)):
            parts.append(
                f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" '
                f'stroke="{t["hair"]}" stroke-width="1"/>'
            )
    # wireframe cube
    V = {
        (x, y, z): iso(c2[0], x, y, z)
        for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)
    }
    top = [V[(-1, 1, -1)], V[(1, 1, -1)], V[(1, 1, 1)], V[(-1, 1, 1)]]
    parts.append(
        '<polygon points="' + " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in top)
        + f'" fill="{t["accent"]}" fill-opacity="0.12" stroke="none"/>'
    )
    edges = []
    for a in V:
        for b in V:
            if a < b and sum(1 for i in range(3) if a[i] != b[i]) == 1:
                edges.append((a, b))
    hidden_corner = (-1, -1, -1)
    for a, b in edges:
        hidden = hidden_corner in (a, b)
        p, q = V[a], V[b]
        if hidden:
            parts.append(
                f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" '
                f'stroke="{t["accent"]}" stroke-opacity="0.45" stroke-width="1.2" stroke-dasharray="3 3"/>'
            )
        else:
            parts.append(
                f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" '
                f'stroke="{t["accent"]}" stroke-width="1.7" stroke-linecap="round"/>'
            )
    for key, p in V.items():
        if key != hidden_corner:
            parts.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="2.6" fill="{t["accent"]}"/>')

    for cx, lab in ((c1[0], "real"), (c2[0], "sim")):
        parts.append(
            f'<text x="{cx}" y="206" text-anchor="middle" class="mono" font-size="11.5" '
            f'fill="{t["muted"]}">{lab}</text>'
        )
    parts.append(f'<line x1="0" y1="228" x2="{W}" y2="228" stroke="{t["hair"]}" stroke-width="1"/>')
    return "\n".join(parts)


# --------------------------------------------------------------------------- PAPAV teaser
def rect_exit(cx, cy, hw, hh, dx, dy):
    """Distance from a rect centre along (dx,dy) to its edge."""
    tx = hw / abs(dx) if dx else math.inf
    ty = hh / abs(dy) if dy else math.inf
    return min(tx, ty)


def papav(t):
    W, H = 520, 340
    cx, cy, RX, RY = 260, 160, 176, 118
    names = ["Perceive", "Anticipate", "Plan", "Act", "Verify"]
    sub = {"Anticipate": "5 of 64 benchmarks", "Verify": "3 of 64 benchmarks", "Act": "most evaluated"}
    nodes = []
    for i, n in enumerate(names):
        a = math.radians(-90 + 72 * i)
        x, y = cx + RX * math.cos(a), cy + RY * math.sin(a)
        w = 132 if n in sub else 104
        h = 50 if n in sub else 36
        nodes.append((n, x, y, w, h))
    parts = []
    # arrows around the loop
    for i in range(5):
        n1, x1, y1, w1, h1 = nodes[i]
        n2, x2, y2, w2, h2 = nodes[(i + 1) % 5]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        d1 = rect_exit(x1, y1, w1 / 2 + 6, h1 / 2 + 6, ux, uy)
        d2 = rect_exit(x2, y2, w2 / 2 + 7, h2 / 2 + 7, ux, uy)
        sx, sy = x1 + ux * d1, y1 + uy * d1
        ex, ey = x2 - ux * d2, y2 - uy * d2
        # slight outward bow so the loop reads as a cycle
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        ox, oy = mx - cx, my - cy
        oL = math.hypot(ox, oy)
        bx, by = mx + ox / oL * 10, my + oy / oL * 10
        parts.append(
            f'<path d="M {sx:.1f} {sy:.1f} Q {bx:.1f} {by:.1f} {ex:.1f} {ey:.1f}" fill="none" '
            f'stroke="{t["line"]}" stroke-width="1.6" marker-end="url(#ah)"/>'
        )
    for n, x, y, w, h in nodes:
        if n == "Act":
            fill, stroke, dash, tc, sc = t["accent"], t["accent"], "", t["on_accent"], t["on_accent"]
        elif n in ("Anticipate", "Verify"):
            fill, stroke, dash, tc, sc = t["hl_tint"], t["hl"], ' stroke-dasharray="5 4"', t["text"], t["text2"]
        else:
            fill, stroke, dash, tc, sc = t["accent_tint"], t["accent"], "", t["text"], t["text2"]
        parts.append(
            f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w}" height="{h}" rx="10" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.6"{dash}/>'
        )
        if n in sub:
            parts.append(
                f'<text x="{x:.1f}" y="{y - 3:.1f}" text-anchor="middle" class="sans" font-size="15" '
                f'font-weight="600" fill="{tc}">{n}</text>'
            )
            parts.append(
                f'<text x="{x:.1f}" y="{y + 15:.1f}" text-anchor="middle" class="sans" font-size="11.5" '
                f'fill="{sc}" fill-opacity="{0.9 if n == "Act" else 1}">{sub[n]}</text>'
            )
        else:
            parts.append(
                f'<text x="{x:.1f}" y="{y + 5:.1f}" text-anchor="middle" class="sans" font-size="15" '
                f'font-weight="600" fill="{tc}">{n}</text>'
            )
    parts.append(
        f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" class="sans" font-size="23" font-weight="700" '
        f'letter-spacing="3" fill="{t["text"]}">PAPAV</text>'
    )
    parts.append(
        f'<text x="{cx}" y="{cy + 24}" text-anchor="middle" class="sans" font-size="11.5" '
        f'fill="{t["muted"]}">computer-use → robot-use</text>'
    )
    # legend
    ly = 318
    parts.append(
        f'<rect x="96" y="{ly - 10}" width="22" height="13" rx="4" fill="{t["hl_tint"]}" '
        f'stroke="{t["hl"]}" stroke-width="1.4" stroke-dasharray="4 3"/>'
    )
    parts.append(
        f'<text x="126" y="{ly + 1}" class="sans" font-size="12" fill="{t["text2"]}">'
        f"rarely measured by current benchmarks (n = 64)</text>"
    )
    return "\n".join(parts)


# --------------------------------------------------------------------------- ShibaSteps system teaser
def shiba(t):
    parts = []
    parts.append(
        f'<text x="20" y="30" class="sans" font-size="11.5" font-weight="600" letter-spacing="1.8" '
        f'fill="{t["accent"]}">ONE TASK STATE · FOUR RUNTIMES</text>'
    )
    W_, H_ = 140, 58
    boxes = {
        "web": (20, 58, "React + Vite", "web planner", "mine"),
        "api": (190, 58, "Express", "REST API · 17 routes", "team"),
        "db": (360, 58, "Supabase", "auth + storage", "team"),
        "esp": (190, 190, "ESP32", "desk assistant", "mine"),
        "io": (360, 190, "Peripherals", "OLED · IR · stepper", "mine"),
        "study": (20, 190, "User study", "20 users × 9 tasks", "eval"),
    }

    def c(k):
        x, y, *_ = boxes[k]
        return x + W_ / 2, y + H_ / 2

    def arrow(p, q, both=False, dashed=False):
        d = ' stroke-dasharray="4 4"' if dashed else ""
        ms = ' marker-start="url(#ah)"' if both else ""
        parts.append(
            f'<path d="M {p[0]} {p[1]} L {q[0]} {q[1]}" stroke="{t["line"]}" stroke-width="1.6" '
            f'fill="none"{d}{ms} marker-end="url(#ah)"/>'
        )

    def label(x, y, s, anchor="middle"):
        parts.append(
            f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="mono" font-size="10.5" '
            f'fill="{t["muted"]}">{s}</text>'
        )

    ymid = 58 + H_ / 2
    arrow((164, ymid), (186, ymid), both=True)
    label(175, ymid - 12, "JWT")
    arrow((334, ymid), (356, ymid), both=True)
    arrow((260, 120), (260, 186), both=True)
    label(268, 157, "device token", anchor="start")
    ymid2 = 190 + H_ / 2
    arrow((334, ymid2), (356, ymid2), both=True)
    arrow((90, 186), (90, 120), dashed=True)
    label(98, 157, "evaluates", anchor="start")

    for k, (x, y, a, b, kind) in boxes.items():
        if kind == "mine":
            fill, stroke, dash = t["accent_tint"], t["accent"], ""
        elif kind == "eval":
            fill, stroke, dash = t["hl_tint"], t["hl"], ' stroke-dasharray="5 4"'
        else:
            fill, stroke, dash = "none", t["line"], ""
        parts.append(
            f'<rect x="{x}" y="{y}" width="{W_}" height="{H_}" rx="10" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="1.6"{dash}/>'
        )
        parts.append(
            f'<text x="{x + W_ / 2}" y="{y + 25}" text-anchor="middle" class="sans" font-size="14.5" '
            f'font-weight="600" fill="{t["text"]}">{a}</text>'
        )
        parts.append(
            f'<text x="{x + W_ / 2}" y="{y + 43}" text-anchor="middle" class="sans" font-size="11.5" '
            f'fill="{t["text2"]}">{b}</text>'
        )
    # legend
    ly = 296
    parts.append(
        f'<rect x="20" y="{ly - 10}" width="22" height="13" rx="4" fill="{t["accent_tint"]}" '
        f'stroke="{t["accent"]}" stroke-width="1.4"/>'
    )
    parts.append(f'<text x="50" y="{ly + 1}" class="sans" font-size="12" fill="{t["text2"]}">my part</text>')
    parts.append(
        f'<rect x="120" y="{ly - 10}" width="22" height="13" rx="4" fill="none" '
        f'stroke="{t["line"]}" stroke-width="1.4"/>'
    )
    parts.append(
        f'<text x="150" y="{ly + 1}" class="sans" font-size="12" fill="{t["text2"]}">teammate-led</text>'
    )
    parts.append(
        f'<rect x="258" y="{ly - 10}" width="22" height="13" rx="4" fill="{t["hl_tint"]}" '
        f'stroke="{t["hl"]}" stroke-width="1.4" stroke-dasharray="4 3"/>'
    )
    parts.append(
        f'<text x="288" y="{ly + 1}" class="sans" font-size="12" fill="{t["text2"]}">evaluation</text>'
    )
    return "\n".join(parts)


# --------------------------------------------------------------------------- user-study chart
TASKS = [
    ("Create a goal", 90, 8.20, False),
    ("Add three tasks", 80, 7.95, False),
    ("Complete one task", 100, 8.40, False),
    ("Move a task to tomorrow", 80, 6.20, False),
    ("View the moved task", 80, 6.95, False),
    ("Daily check-in", 70, 5.45, True),
    ("Streak & Bone Points", 60, 5.20, True),
    ("Browse Dog Circle", 90, 7.35, False),
    ("Switch to another goal", 80, 7.30, False),
]


def bar(x0, yc, length, thick, color):
    """Horizontal bar: square at the baseline, 4px rounded data end."""
    r = min(4, length / 2)
    y0, y1 = yc - thick / 2, yc + thick / 2
    x1 = x0 + length
    return (
        f'<path d="M {x0:.1f} {y0:.1f} L {x1 - r:.1f} {y0:.1f} Q {x1:.1f} {y0:.1f} {x1:.1f} {y0 + r:.1f} '
        f'L {x1:.1f} {y1 - r:.1f} Q {x1:.1f} {y1:.1f} {x1 - r:.1f} {y1:.1f} L {x0:.1f} {y1:.1f} Z" '
        f'fill="{color}"/>'
    )


def study(t):
    parts = []
    parts.append(
        f'<text x="0" y="24" class="sans" font-size="16" font-weight="600" fill="{t["text"]}">'
        f"Task-level results · 20 participants × 9 tasks = 180 attempts</text>"
    )
    parts.append(f'<rect x="0" y="38" width="10" height="10" rx="2" fill="{t["hl"]}"/>')
    parts.append(
        f'<text x="17" y="47.5" class="sans" font-size="13" fill="{t["text2"]}">'
        f"Rule- and reward-related tasks: 14 of the 34 failed attempts</text>"
    )
    lab_x = 196
    panels = [
        ("Completion rate", 216, 250, 100, [0, 50, 100], lambda v: f"{v}%", 1),
        ("Average score (1–10)", 540, 250, 10, [0, 5, 10], lambda v: f"{v:.2f}", 2),
    ]
    top, row = 96, 28
    bottom = top + row * len(TASKS)
    for title, x0, pw, vmax, ticks, fmt, idx in panels:
        parts.append(
            f'<text x="{x0}" y="84" class="sans" font-size="13" font-weight="600" fill="{t["text"]}">{title}</text>'
        )
        for tk in ticks:
            gx = x0 + pw * tk / vmax
            parts.append(
                f'<line x1="{gx:.1f}" y1="{top - 4}" x2="{gx:.1f}" y2="{bottom}" stroke="{t["hair"]}" stroke-width="1"/>'
            )
            tl = f"{tk}%" if idx == 1 else f"{tk}"
            parts.append(
                f'<text x="{gx:.1f}" y="{bottom + 16}" text-anchor="middle" class="sans" font-size="11" '
                f'fill="{t["muted"]}">{tl}</text>'
            )
        for i, (name, comp, score, hl) in enumerate(TASKS):
            yc = top + row * i + row / 2
            v = comp if idx == 1 else score
            L = pw * v / vmax
            parts.append(bar(x0, yc, L, 14, t["hl"] if hl else t["accent"]))
            parts.append(
                f'<text x="{x0 + L + 6:.1f}" y="{yc + 4:.1f}" class="sans" font-size="11.5" '
                f'fill="{t["text2"]}" stroke="{t["surface"]}" stroke-width="4" paint-order="stroke" '
                f'style="font-variant-numeric:tabular-nums">{fmt(v)}</text>'
            )
    for i, (name, comp, score, hl) in enumerate(TASKS):
        yc = top + row * i + row / 2
        w = "600" if hl else "400"
        col = t["text"] if hl else t["text2"]
        parts.append(
            f'<text x="{lab_x}" y="{yc + 4.5:.1f}" text-anchor="end" class="sans" font-size="13" '
            f'font-weight="{w}" fill="{col}">{esc(name)}</text>'
        )
    return "\n".join(parts)


if __name__ == "__main__":
    write("header", 900, 232, header,
          "Peiyao Xu — Computer Engineering, National University of Singapore. "
          "Undergraduate researcher at Show Lab. Embodied agents, real-to-sim, robot evaluation.")
    write("papav", 520, 336, papav,
          "PAPAV capability loop: Perceive, Anticipate, Plan, Act, Verify. Most benchmarks evaluate Act; "
          "only 5 of 64 assess Anticipate and 3 of 64 assess Verify.")
    write("shibasteps", 520, 312, shiba,
          "ShibaSteps system: React web planner, Express REST API, Supabase, and an ESP32 desk assistant "
          "with OLED, IR remote, button and stepper motor, evaluated in a 20-participant user study.")
    write("shibasteps-study", 830, 396, study,
          "ShibaSteps user study: completion rate and average score for each of nine tasks. Daily check-in "
          "(70%, 5.45) and Streak and Bone Points (60%, 5.20) were weakest; Complete one task was strongest (100%, 8.40).")
    print(sorted(p.name for p in OUT.iterdir()))
