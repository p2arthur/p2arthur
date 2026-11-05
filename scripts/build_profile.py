#!/usr/bin/env python3
"""Build self-contained GitHub profile SVGs from Arthur's public avatar.

Requires Python 3 and Pillow. Run from any directory. No network calls.
"""

from html import escape
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
PALETTES = {
    "dark": {
        "bg": "#0d1117", "surface": "#151b23", "line": "#303946",
        "text": "#d9e2ed", "muted": "#98a6b8", "label": "#e4b08a",
        "accent": "#9bcea9", "portrait": "#acbfd1",
    },
    "light": {
        "bg": "#ffffff", "surface": "#f6f8fa", "line": "#c9d1d9",
        "text": "#263545", "muted": "#576777", "label": "#8c4c2b",
        "accent": "#28633c", "portrait": "#415b70",
    },
}


def ascii_portrait():
    image = Image.open(ASSETS / "avatar-source.png").convert("RGB")
    # Trace the hood and shoulders, dropping the snow and trees from the ASCII.
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).polygon([
        (195, 89), (220, 91), (245, 101), (263, 120), (271, 149),
        (270, 174), (257, 203), (249, 221), (258, 241), (274, 264),
        (266, 277), (152, 277), (141, 258), (152, 231), (159, 213),
        (151, 191), (146, 165), (147, 139), (156, 116), (170, 102),
    ], fill=255)
    image = Image.composite(image, Image.new("RGB", image.size, "white"), mask)
    image = ImageOps.grayscale(image.crop((138, 83, 278, 278)))
    image = ImageEnhance.Contrast(ImageOps.autocontrast(image)).enhance(1.15)
    image = image.resize((56, 43), Image.Resampling.LANCZOS)
    ramp = "@%#*+=-:. "
    return [
        "".join(ramp[min(9, int(image.getpixel((x, y)) * 10 / 256))] for x in range(56))
        for y in range(43)
    ]


def build(theme, mobile=False):
    c = PALETTES[theme]
    w, h = (640, 1345) if mobile else (1200, 786)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
        '<title id="title">Arthur Rabelo | p2arthur</title>',
        '<desc id="desc">ASCII portrait of Arthur Rabelo. Product and full-stack engineer in Vancouver, Canada. Five years in software and ten years in UX/UI. Co-founder and primary builder of DevLoot. Works with React, TypeScript, React Native, Node.js, NestJS, PostgreSQL, RAG and MCP. Previously at Let’s Roam, Algorand Foundation and CompX Labs. Portfolio: arthurrabelo.com.</desc>',
        f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="8" fill="{c["bg"]}" stroke="{c["line"]}"/>',
        f'<path d="M8 .5 H{w-8} Q{w-.5} .5 {w-.5} 8 V64 H.5 V8 Q.5 .5 8 .5" fill="{c["surface"]}"/>',
        f'<path d="M1 64.5H{w-1}" stroke="{c["line"]}"/>',
        '<g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    ]

    def text(x, y, value, color="text", size=17, weight=400, **attributes):
        attrs = " ".join(f'{"xml:space" if k == "xml_space" else k.replace("_", "-")}="{v}"' for k, v in attributes.items())
        parts.append(f'<text x="{x}" y="{y}" fill="{c[color]}" font-size="{size}" font-weight="{weight}" {attrs}>{escape(value)}</text>')

    def line(x1, y, x2):
        parts.append(f'<path d="M{x1} {y}H{x2}" stroke="{c["line"]}"/>')

    text(28, 40, "p2arthur", "text", 18, 600)
    text(132, 40, "/ README.md", "muted", 17)
    if not mobile:
        text(1170, 40, "~/", "muted", 17, text_anchor="end")

    if mobile:
        text(30, 108, "$ whoami", "accent", 18)
        text(30, 150, "Arthur Rabelo", "text", 30, 600)
        text(30, 183, "Product & full-stack engineer", "muted", 19)
        for i, row in enumerate(ascii_portrait()):
            text(151, 215 + i * 8.25, row, "portrait", 8.5, xml_space="preserve", textLength="338", lengthAdjust="spacingAndGlyphs")
        text(320, 603, "Vancouver, Canada", "muted", 17, text_anchor="middle")
        line(30, 628, 610)
        x, y, label_width = 30, 670, 165
        row_gap, size = 31, 18
    else:
        text(36, 112, "$ whoami", "accent", 17)
        for i, row in enumerate(ascii_portrait()):
            text(35, 166 + i * 11.65, row, "portrait", 11.5, xml_space="preserve", textLength="366", lengthAdjust="spacingAndGlyphs")
        text(218, 705, "Vancouver, Canada", "muted", 16, text_anchor="middle")
        parts.append(f'<path d="M425 100V735" stroke="{c["line"]}"/>')
        text(461, 120, "arthur@p2arthur", "text", 25, 600)
        line(461, 139, 1164)
        x, y, label_width = 461, 176, 154
        row_gap, size = 30, 17

    def row(label, value):
        nonlocal y
        text(x, y, label, "label", size)
        # Dot leaders mirror terminal system-information tools.
        dot_start = x + len(label) * size * .61 + 9
        dot_end = x + label_width - 16
        if dot_end > dot_start:
            parts.append(f'<path d="M{dot_start} {y-4}H{dot_end}" stroke="{c["line"]}" stroke-dasharray="2 6"/>')
        text(x + label_width, y, value, "text", size)
        y += row_gap

    def section(label):
        nonlocal y
        y += 15
        text(x, y, label, "accent", size, 600)
        line(x + len(label) * size * .61 + 18, y - 5, w - (30 if mobile else 36))
        y += row_gap + 6

    row("Role", "Product / Full-stack Engineer" if not mobile else "Product / Full-stack")
    row("Building", "DevLoot · Co-founder")
    row("Experience", "5 years software · 10 years UX/UI" if not mobile else "5 years software / 10 UX/UI")
    section("Stack")
    row("Languages", "TypeScript, JavaScript")
    row("Frontend", "React, React Native, Next.js")
    row("Backend", "Node.js, NestJS, PostgreSQL")
    row("AI / agents", "RAG, MCP, adaptive retrieval")
    section("Selected work")
    row("DevLoot", "Open-source discovery & bounties" if not mobile else "Discovery & bounties")
    row("QuickPick", "AI search for people & projects" if not mobile else "AI-powered discovery")
    row("Agent Bond", "AI twins for event networking" if not mobile else "AI event networking")
    section("Previously")
    if mobile:
        text(x, y, "Let’s Roam · Algorand Foundation", "text", size)
        y += row_gap
        text(x, y, "CompX Labs", "muted", size)
    else:
        text(x, y, "Let’s Roam · Algorand Foundation · CompX Labs", "text", size)
    y += row_gap
    section("Connect")
    row("Web", "arthurrabelo.com")
    row("DevLoot", "devloot.xyz/profile/p2arthur")
    # Guard against text silently spilling out when content changes.
    assert y < h - 15, (mobile, y, h)
    parts.append("</g></svg>\n")
    suffix = "-mobile" if mobile else ""
    (ASSETS / f"profile-{theme}{suffix}.svg").write_text("\n".join(parts))


if __name__ == "__main__":
    for theme in PALETTES:
        for mobile in (False, True):
            build(theme, mobile)
    print("Built four self-contained profile SVGs.")
