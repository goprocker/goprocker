"""Generate the Tech Stack and GSSoC section cards for the README."""
import base64
import io
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "readme"
BADGES = ROOT / "assets" / "gssoc-badges"
SANS = "'Segoe UI',Inter,-apple-system,Helvetica,Arial,sans-serif"
MONO = "Consolas,'SF Mono',Menlo,monospace"

DEFS = """<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1430"/><stop offset="1" stop-color="#080c1a"/></linearGradient>
    <style>.in{animation:in .6s ease-out backwards}@keyframes in{from{opacity:0;transform:translateY(8px)}}</style>"""

STACK = [
    ("Languages", "#70a5fd", [("C++", "#00599C"), ("C", "#A8B9CC"), ("JavaScript", "#F7DF1E"), ("TypeScript", "#3178C6"),
                             ("Python", "#3776AB"), ("Java", "#ED8B00"), ("HTML", "#E34F26"), ("CSS", "#1572B6")]),
    ("Frontend", "#a78bfa", [("React", "#61DAFB"), ("Next.js", "#ffffff"), ("Astro", "#FF5D01"), ("Vue", "#4FC08D"),
                            ("Vite", "#646CFF"), ("Tailwind", "#06B6D4"), ("Vuetify", "#1867C0"), ("WordPress", "#21759B")]),
    ("Backend & Data", "#34d399", [("Node.js", "#5FA04E"), ("Express", "#ffffff"), ("MongoDB", "#47A248"), ("MySQL", "#4479A1"),
                                  ("PostgreSQL", "#4169E1"), ("SQLite", "#5ea9d6"), ("Supabase", "#3FCF8E"), ("Firebase", "#FFCA28")]),
    ("AI & ML", "#f472b6", [("TensorFlow", "#FF6F00"), ("PyTorch", "#EE4C2C"), ("OpenCV", "#5C3EE8"), ("Pandas", "#9b8cff"),
                           ("NumPy", "#4DABCF"), ("Matplotlib", "#11a0c0"), ("Streamlit", "#FF4B4B")]),
    ("Infra & Tools", "#fbbf24", [("Git", "#F05032"), ("GitHub", "#ffffff"), ("GitLab", "#FC6D26"), ("Actions", "#2088FF"),
                                 ("Docker", "#2496ED"), ("Vercel", "#ffffff"), ("Netlify", "#00C7B7"), ("Cloudflare", "#F38020"),
                                 ("Render", "#46E3B7")]),
    ("Design", "#22d3ee", [("Figma", "#F24E1E"), ("Photoshop", "#31A8FF"), ("Illustrator", "#FF9A00"), ("Premiere", "#9999FF"),
                          ("After Effects", "#9999FF"), ("Lightroom", "#31A8FF"), ("Framer", "#0099ff"), ("Canva", "#00C4CC")]),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def text_w(s, size):
    return sum(size * (0.33 if c in "il.I" else 0.62 if c.isupper() else 0.55) for c in s)


def stack():
    W, cols, gap, cw = 1200, 3, 24, 384
    pad, chip_h, chip_gap = 22, 30, 8
    cards, row_h = [], []
    for i, (name, accent, items) in enumerate(STACK):
        # lay out chips into rows that fit the card width
        x, y, chips = pad, 78, []
        for label, color in items:
            w = text_w(label, 13) + 34
            if x + w > cw - pad:
                x, y = pad, y + chip_h + chip_gap
            chips.append((x, y, w, label, color))
            x += w + chip_gap
        cards.append((name, accent, items, chips))
        row_h.append(y + chip_h + pad)
    ch = max(row_h)
    H = ch * 2 + gap
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Tech stack by category">',
           f"  <defs>\n    {DEFS}\n  </defs>", f'  <g font-family="{SANS}">']
    for i, (name, accent, items, chips) in enumerate(cards):
        cx, cy = (i % cols) * (cw + gap), (i // cols) * (ch + gap)
        out.append(f'  <g class="in" style="animation-delay:{i * .08:.2f}s" transform="translate({cx} {cy})">')
        out.append(f'    <rect x=".5" y=".5" width="{cw - 1}" height="{ch - 1}" rx="16" fill="url(#g)" stroke="#ffffff" stroke-opacity=".09"/>')
        out.append(f'    <rect x="{pad}" y=".5" width="28" height="3" rx="1.5" fill="{accent}"/>')
        out.append(f'    <text x="{pad}" y="38" font-family="{MONO}" font-size="12" font-weight="700" fill="{accent}">0{i + 1}</text>')
        out.append(f'    <text x="{pad + 26}" y="39" font-size="18" font-weight="800" fill="#e6edf3" letter-spacing="-.2">{esc(name)}</text>')
        out.append(f'    <text x="{cw - pad}" y="38" text-anchor="end" font-size="11.5" font-weight="600" fill="#6b7896" letter-spacing=".6">{len(items)} TOOLS</text>')
        out.append(f'    <rect x="{pad}" y="54" width="{cw - 2 * pad}" height="1" fill="#ffffff" fill-opacity=".07"/>')
        for x, y, w, label, color in chips:
            out.append(f'    <rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{chip_h}" rx="15" fill="#ffffff" fill-opacity=".04" stroke="#ffffff" stroke-opacity=".09"/>'
                       f'<circle cx="{x + 15:.1f}" cy="{y + 15}" r="4" fill="{color}"/>'
                       f'<text x="{x + 25:.1f}" y="{y + 19.5}" font-size="13" font-weight="600" fill="#c9d3ea">{esc(label)}</text>')
        out.append("  </g>")
    out += ["  </g>", "</svg>", ""]
    (OUT / "stack.svg").write_text("\n".join(out), encoding="utf-8")


def badge_uri(name, px):
    im = Image.open(BADGES / f"{name}.png").convert("RGBA")
    im = im.crop(im.getbbox()).resize((px, px), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def gssoc():
    W, H = 1200, 380
    small = [("first-steps", "First Steps"), ("discord-verified", "Discord Verified"), ("profile-complete", "Profile Complete"),
             ("point-scorer", "Point Scorer"), ("bounty-hunter", "Bounty Hunter"), ("contributor", "Contributor")]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GSSoC 2026: Ambassador plus six contributor badges earned">',
           f"""  <defs>
    {DEFS}
    <radialGradient id="o" cx=".2" cy=".5" r=".55"><stop offset="0" stop-color="#f59e0b" stop-opacity=".18"/><stop offset="1" stop-color="#f59e0b" stop-opacity="0"/></radialGradient>
    <radialGradient id="halo"><stop offset="0" stop-color="#fbbf24" stop-opacity=".35"/><stop offset=".7" stop-color="#fbbf24" stop-opacity="0"/></radialGradient>
    <linearGradient id="hl" x1="0" x2="1"><stop offset="0" stop-color="#fcd34d"/><stop offset="1" stop-color="#f472b6"/></linearGradient>
    <style>.pulse{{animation:p 3s ease-in-out infinite;transform-origin:170px 175px}}@keyframes p{{50%{{opacity:.55;transform:scale(1.08)}}}}</style>
  </defs>""",
           f'  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="url(#g)" stroke="#ffffff" stroke-opacity=".09"/>',
           f'  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="url(#o)"/>',
           f'  <g font-family="{SANS}">',
           '    <circle class="pulse" cx="170" cy="175" r="130" fill="url(#halo)"/>',
           f'    <image class="in" x="80" y="85" width="180" height="180" href="{badge_uri("ambassador", 360)}"/>',
           '    <rect x="105" y="290" width="130" height="26" rx="13" fill="#fbbf24" fill-opacity=".14" stroke="#fbbf24" stroke-opacity=".5"/>',
           '    <text x="170" y="308" text-anchor="middle" font-size="12" font-weight="800" fill="#fcd34d" letter-spacing="1.4">★ RARE BADGE</text>',
           '    <rect x="330" y="40" width="1" height="300" fill="#ffffff" fill-opacity=".08"/>',
           f'    <text x="370" y="66" font-family="{MONO}" font-size="14" fill="#fbbf24">GirlScript Summer of Code · 2026</text>',
           '    <text x="370" y="110" font-size="32" font-weight="800" fill="#e6edf3" letter-spacing="-.6"><tspan fill="url(#hl)">Ambassador</tspan> &amp; Contributor</text>',
           '    <text x="370" y="140" font-size="15.5" fill="#97a3c2">Every badge earned during the program, from first PR to ambassador.</text>',
           '    <text x="1160" y="66" text-anchor="end" font-size="11.5" font-weight="600" fill="#6b7896" letter-spacing=".6">7 BADGES EARNED</text>']
    for i, (key, label) in enumerate(small):
        x = 370 + i * 132
        out.append(f'    <g class="in" style="animation-delay:{.15 + i * .08:.2f}s">'
                   f'<rect x="{x}" y="172" width="120" height="150" rx="14" fill="#ffffff" fill-opacity=".035" stroke="#ffffff" stroke-opacity=".08"/>'
                   f'<image x="{x + 22}" y="186" width="76" height="76" href="{badge_uri(key, 152)}"/>'
                   f'<text x="{x + 60}" y="292" text-anchor="middle" font-size="12.5" font-weight="700" fill="#e6edf3">{label}</text>'
                   f'<circle cx="{x + 60}" cy="308" r="3" fill="#34d399"/></g>')
    out += ["  </g>", "</svg>", ""]
    (OUT / "gssoc.svg").write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    stack()
    gssoc()
