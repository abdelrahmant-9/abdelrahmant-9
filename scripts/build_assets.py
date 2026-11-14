"""Generate the animated SVGs in assets/.

Usage:
  npm pack simple-icons && tar xzf simple-icons-*.tgz
  python3 scripts/build_assets.py assets package

Edit the text and colours below, re-run, commit the SVGs.
"""
import json, os, re, sys
from xml.sax.saxutils import escape

OUT = sys.argv[1]
SI = sys.argv[2]  # simple-icons package dir

BG, PANEL, PANEL2, LINE, LINE2 = "#090d17", "#111a2c", "#152036", "#26334c", "#3b5278"
T1, T2, T3, T4 = "#f1f5fc", "#c1cce0", "#97a9c7", "#8a9ab4"
PASS, INFO, VIOLET, WARN, FAIL = "#75d7ca", "#6ba5ff", "#b0a6ef", "#dfbb8d", "#ff8d9a"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono','Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def svg(w, h, body, style="", label=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>'
            f'<style>{style}{REDUCED}</style>{body}</svg>\n')


def write(name, content):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(content)


def show(t, T, until=None, fade=0.25):
    """SMIL opacity: hidden until t, visible until `until`, loop of length T."""
    until = T - 0.6 if until is None else until
    a, b, c, d = t / T, min((t + fade) / T, 0.999), until / T, min((until + 0.3) / T, 1)
    return (f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{a:.4f};{b:.4f};{c:.4f};{d:.4f};1" '
            f'dur="{T}s" repeatCount="indefinite"/>')


def icon_path(slug):
    s = open(os.path.join(SI, "icons", slug + ".svg")).read()
    return re.search(r' d="([^"]+)"', s).group(1)


# ---------------------------------------------------------------- typing header
def typing():
    W, H, fs, cw = 860, 64, 24, 24 * 0.602
    phrases = [
        ("Software QA Engineer @ Lumofy", PASS),
        ("I break things so users don't.", T1),
        ("Building Spectara: locators in 3 seconds", INFO),
        ("Learning dbt · Airflow · Snowflake", VIOLET),
    ]
    per = []
    for p, _ in phrases:
        n = len(p)
        per.append(n * 0.06 + 1.8 + n * 0.025 + 0.4)  # type, hold, delete, gap
    T = round(sum(per), 2)
    body, t0 = [], 0.0
    body.append(f'<rect width="{W}" height="{H}" rx="12" fill="{BG}"/>')
    for i, ((p, col), dur) in enumerate(zip(phrases, per)):
        n = len(p)
        x0 = W / 2 - (n * cw) / 2
        # clip width keyframes (discrete per char)
        vals, keys = [], []
        times = []
        for k in range(n + 1):
            times.append((t0 + k * 0.06, k))
        hold_end = t0 + n * 0.06 + 1.8
        for k in range(n, -1, -1):
            times.append((hold_end + (n - k) * 0.025, k))
        del_end = hold_end + n * 0.025
        times = [(0, 0)] + times + [(del_end + 0.05, 0), (T, 0)]
        for tt, k in times:
            keys.append(f"{min(tt / T, 1):.5f}")
            vals.append(f"{k * cw + 0.5:.1f}")
        # keyTimes must be non-decreasing; ensure
        cid = f"c{i}"
        body.append(
            f'<clipPath id="{cid}"><rect x="{x0:.1f}" y="10" height="44" width="0">'
            f'<animate attributeName="width" values="{";".join(vals)}" keyTimes="{";".join(keys)}" '
            f'calcMode="discrete" dur="{T}s" repeatCount="indefinite"/></rect></clipPath>')
        body.append(
            f'<text x="{x0:.1f}" y="41" font-family="{MONO}" font-size="{fs}" fill="{col}" '
            f'clip-path="url(#{cid})" xml:space="preserve">{escape(p)}</text>')
        # cursor follows
        cvals = [f"{float(v) + x0:.1f}" for v in vals]
        vis = ["1" if (t0 - 0.001 <= tt <= del_end + 0.001) else "0" for tt, _ in times]
        body.append(
            f'<rect y="17" width="3" height="30" fill="{PASS}" opacity="0">'
            f'<animate attributeName="x" values="{";".join(cvals)}" keyTimes="{";".join(keys)}" '
            f'calcMode="discrete" dur="{T}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="{";".join(vis)}" keyTimes="{";".join(keys)}" '
            f'calcMode="discrete" dur="{T}s" repeatCount="indefinite"/></rect>')
        t0 += dur
    write("typing.svg", svg(W, H, "".join(body), label="Software QA Engineer at Lumofy. I break things so users don't."))


# ---------------------------------------------------------------- terminal
def terminal():
    W, H, T = 860, 340, 16
    lh, x0, y0 = 27, 28, 82
    css = f"text{{font-family:{MONO};font-size:15px}}"
    b = [f'<rect width="{W}" height="{H}" rx="14" fill="{BG}" stroke="{LINE}"/>',
         f'<path d="M0 14a14 14 0 0 1 14-14h{W-28}a14 14 0 0 1 14 14v26H0z" fill="{PANEL}"/>',
         f'<line x1="0" y1="40" x2="{W}" y2="40" stroke="{LINE}"/>']
    for i, c in enumerate([FAIL, WARN, PASS]):
        b.append(f'<circle cx="{24 + i * 20}" cy="20" r="6" fill="{c}" opacity=".85"/>')
    b.append(f'<text x="{W/2}" y="25" text-anchor="middle" fill="{T4}" style="font-size:13px">qa-run — abdelrahman-tarek</text>')
    # typed command
    cmd = "qa-run --profile abdelrahman-tarek"
    b.append(f'<text x="{x0}" y="{y0}" fill="{PASS}">$</text>')
    for i, ch in enumerate(cmd):
        if ch == " ":
            continue
        b.append(f'<text x="{x0 + 18 + i * 9.03:.2f}" y="{y0}" fill="{T1}">{escape(ch)}{show(0.4 + i * 0.045, T)}</text>')
    rows = [
        ("PASS", "role", "Software QA Engineer @ Lumofy", "intern → full-time"),
        ("PASS", "freelance", "Test IO · 10+ cycles", "20+ accepted bugs"),
        ("PASS", "leadership", "DEPI · led a 5-person QA team", "50+ test cases"),
        ("PASS", "building", "Spectara · click → Selenium + POM", "~3s"),
        ("RUN", "learning", "dbt · Airflow · Snowflake · DuckDB", ""),
    ]
    t = 2.4
    for i, (st, k, v, note) in enumerate(rows):
        y = y0 + lh * (i + 1.5)
        col = PASS if st == "PASS" else INFO
        g = [f'<rect x="{x0}" y="{y-16}" width="50" height="22" rx="4" fill="{col}"/>',
             f'<text x="{x0+25}" y="{y}" text-anchor="middle" fill="{BG}" font-weight="700" style="font-size:13px">{st}</text>',
             f'<text x="{x0+66}" y="{y}" fill="{T3}">{k}</text>',
             f'<text x="{x0+176}" y="{y}" fill="{T1}">{escape(v)}</text>']
        if note:
            g.append(f'<text x="{W-28}" y="{y}" text-anchor="end" fill="{T4}">{escape(note)}</text>')
        if st == "RUN":
            cx, cy = W - 40, y - 5
            g.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="none" stroke="{LINE2}" stroke-width="2.5"/>'
                     f'<path d="M{cx} {cy-7}a7 7 0 0 1 7 7" fill="none" stroke="{INFO}" stroke-width="2.5" stroke-linecap="round">'
                     f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="0.9s" repeatCount="indefinite"/></path>')
        b.append(f'<g>{"".join(g)}{show(t, T)}</g>')
        t += 0.7
    # summary + progress
    y = y0 + lh * 7.3
    b.append(f'<g><text x="{x0}" y="{y}" fill="{T2}">Tests:</text>'
             f'<text x="{x0+66}" y="{y}" fill="{PASS}">4 passed</text>'
             f'<text x="{x0+138}" y="{y}" fill="{T4}">,</text>'
             f'<text x="{x0+156}" y="{y}" fill="{INFO}">1 running</text>{show(t + 0.2, T)}</g>')
    bx, bw = x0 + 300, W - 28 - (x0 + 300)
    b.append(f'<g><rect x="{bx}" y="{y-12}" width="{bw}" height="10" rx="5" fill="{PANEL2}"/>'
             f'<rect x="{bx}" y="{y-12}" height="10" rx="5" fill="{PASS}" width="{bw*0.8:.0f}">'
             f'<animate attributeName="width" values="0;0;{bw*0.8:.0f};{bw*0.8:.0f}" keyTimes="0;{(t+0.2)/T:.3f};{(t+1.6)/T:.3f};1" dur="{T}s" repeatCount="indefinite"/></rect>'
             f'{show(t + 0.2, T)}</g>')
    y2 = y + lh * 1.2
    b.append(f'<g><text x="{x0}" y="{y2}" fill="{T4}">// quality is not about finding bugs, it\'s about preventing them.</text>{show(t + 1.4, T)}</g>')
    y3 = y2 + lh
    b.append(f'<text x="{x0}" y="{y3}" fill="{PASS}">$</text>'
             f'<rect x="{x0+18}" y="{y3-14}" width="9" height="18" fill="{PASS}">'
             f'<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/></rect>')
    write("terminal.svg", svg(W, H, "".join(b), css,
          "qa-run: PASS Software QA Engineer at Lumofy; PASS Test IO freelance; PASS DEPI team lead; PASS building Spectara; RUN learning dbt, Airflow, Snowflake"))


# ---------------------------------------------------------------- journey
def journey():
    W, H, T = 860, 250, 12
    ly, xs = 104, [110, 323, 537, 750]
    ms = [
        ("2025", "DEPI", ["Software Testing track", "Led a 5-person QA team"], PASS),
        ("OCT 2025", "Lumofy", ["QA intern", "→ full-time Apr 2026"], PASS),
        ("2026", "Builder", ["Test IO · Flutter apps", "Spectara · QA Reps"], WARN),
        ("NOW", "Data", ["dbt · Airflow", "Snowflake warehouses"], INFO),
    ]
    css = f".f{{font-family:{MONO}}}.s{{font-family:{SANS}}}"
    L = xs[-1] - xs[0]
    b = [f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>',
         f'<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{PASS}"/><stop offset=".66" stop-color="{WARN}"/><stop offset="1" stop-color="{INFO}"/></linearGradient></defs>',
         f'<line x1="{xs[0]}" y1="{ly}" x2="{xs[-1]}" y2="{ly}" stroke="{LINE}" stroke-width="4" stroke-linecap="round"/>',
         f'<line x1="{xs[0]}" y1="{ly}" x2="{xs[-1]}" y2="{ly}" stroke="url(#g)" stroke-width="4" stroke-linecap="round" stroke-dasharray="{L}" stroke-dashoffset="0">'
         f'<animate attributeName="stroke-dashoffset" values="{L};{L};0;0;{L}" keyTimes="0;.04;.5;.94;1" dur="{T}s" repeatCount="indefinite"/></line>']
    for i, (x, (yr, name, lines, col)) in enumerate(zip(xs, ms)):
        t = 0.5 + i * (0.46 * T / 3) if i else 0.5
        a = t / T
        b.append(f'<text x="{x}" y="{ly-44}" text-anchor="middle" class="f" font-size="12" fill="{T4}" letter-spacing="2">{yr}</text>')
        b.append(f'<text x="{x}" y="{ly-22}" text-anchor="middle" class="s" font-size="19" font-weight="700" fill="{T1}">{name}</text>')
        b.append(f'<circle cx="{x}" cy="{ly}" r="11" fill="{BG}" stroke="{LINE2}" stroke-width="3"/>')
        b.append(f'<circle cx="{x}" cy="{ly}" r="7" fill="{col}">'
                 f'<animate attributeName="r" values="0;0;9;7;7;0" keyTimes="0;{a:.3f};{a+0.03:.3f};{a+0.05:.3f};.94;1" dur="{T}s" repeatCount="indefinite"/></circle>')
        # pulse ring
        last = i == len(xs) - 1
        b.append(f'<circle cx="{x}" cy="{ly}" r="10" fill="none" stroke="{col}" stroke-width="2" opacity="0">'
                 f'<animate attributeName="r" values="10;26" dur="{1.6 if last else T}s" begin="{0 if last else t}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="{".8;0" if last else ".8;0;0"}" {"" if last else f"keyTimes=\"0;{1.4/T:.3f};1\""} dur="{1.6 if last else T}s" begin="{0 if last else t}s" repeatCount="indefinite"/></circle>')
        for j, ln in enumerate(lines):
            b.append(f'<text x="{x}" y="{ly+42+j*22}" text-anchor="middle" class="s" font-size="14" fill="{T2 if j==0 else T3}">{escape(ln)}{show(t+0.2+j*0.15, T, T-0.7)}</text>')
    b.append(f'<text x="{xs[-1]+2}" y="{ly+100}" text-anchor="middle" class="f" font-size="11" fill="{INFO}" letter-spacing="2">● IN PROGRESS'
             f'<animate attributeName="opacity" values="1;.3;1" dur="1.6s" repeatCount="indefinite"/></text>')
    write("journey.svg", svg(W, H, "".join(b), css,
          "Journey: 2025 DEPI testing track and team lead; Oct 2025 Lumofy QA intern, full-time April 2026; 2026 Test IO, Flutter apps, Spectara; now learning data engineering"))


def lighten(h, min_l=0.5):
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (1, 3, 5))
    lum = lambda r, g, b: 0.2126 * r + 0.7152 * g + 0.0722 * b
    t = 0.0
    while lum(r + (1 - r) * t, g + (1 - g) * t, b + (1 - b) * t) < min_l and t < 1:
        t += 0.05
    return "#" + "".join(f"{round((c + (1 - c) * t) * 255):02x}" for c in (r, g, b))


# ---------------------------------------------------------------- toolbox
def toolbox():
    rows = [
        ("testing", PASS, [("selenium", "Selenium"), ("postman", "Postman"), ("jira", "Jira"), ("junit5", "JUnit"),
                          ("openjdk", "Java"), ("apachemaven", "Maven"), ("jenkins", "Jenkins")]),
        ("data", INFO, [("python", "Python"), (None, "dbt"), ("apacheairflow", "Airflow"), ("snowflake", "Snowflake"),
                       ("duckdb", "DuckDB"), ("postgresql", "SQL")]),
        ("build", VIOLET, [("flutter", "Flutter"), ("dart", "Dart"), ("firebase", "Firebase"), ("javascript", "JS"),
                          ("googlechrome", "Chrome MV3"), ("git", "Git"), ("github", "GitHub")]),
    ]
    data = json.load(open(os.path.join(SI, "data", "simple-icons.json")))
    data = data if isinstance(data, list) else data["icons"]
    hexes = {(d.get("slug") or d["title"].lower()): "#" + d["hex"] for d in data}
    W, rowh, tile, gap, lx = 860, 100, 58, 22, 150
    H = 24 + rowh * len(rows)
    css = (f".fl{{animation:fl 3.2s ease-in-out infinite}}@keyframes fl{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-7px)}}}}"
           f".gl{{animation:gl 3.2s ease-in-out infinite}}@keyframes gl{{0%,100%{{opacity:.15}}50%{{opacity:.55}}}}"
           f"text{{font-family:{MONO}}}")
    b = [f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>']
    k = 0
    for r, (name, col, items) in enumerate(rows):
        y = 18 + r * rowh
        b.append(f'<text x="28" y="{y+36}" fill="{col}" font-size="15">▸ {name}</text>')
        b.append(f'<text x="28" y="{y+56}" fill="{T4}" font-size="11">{len(items)} tools</text>')
        for i, (slug, label) in enumerate(items):
            x = lx + i * (tile + gap + 12)
            d = (k * 0.17) % 3.2
            k += 1
            hc = hexes.get(slug, "#FF694B") if slug else "#FF694B"
            if slug in ("openjdk", "github"):
                hc = T1
            hc = lighten(hc)
            if slug:
                p = icon_path(slug)
                ic = f'<g transform="translate({tile/2-14} {tile/2-14}) scale(1.1667)"><path d="{p}" fill="{hc}"/></g>'
            else:
                ic = f'<text x="{tile/2}" y="{tile/2+7}" text-anchor="middle" font-size="20" font-weight="700" fill="{hc}">dbt</text>'
            b.append(
                f'<g transform="translate({x} {y})"><g class="fl" style="animation-delay:-{d:.2f}s">'
                f'<rect x="4" y="4" width="{tile-8}" height="{tile-8}" rx="14" fill="{hc}" class="gl" style="animation-delay:-{d:.2f}s;filter:blur(10px)"/>'
                f'<rect width="{tile}" height="{tile}" rx="14" fill="{PANEL}" stroke="{LINE}"/>{ic}</g>'
                f'<text x="{tile/2}" y="{tile+20}" text-anchor="middle" fill="{T3}" font-size="11">{escape(label)}</text></g>')
    write("toolbox.svg", svg(W, H, "".join(b), css,
          "Toolbox. Testing: Selenium, Postman, Jira, JUnit, Java, Maven, Jenkins. Data: Python, dbt, Airflow, Snowflake, DuckDB, SQL. Build: Flutter, Dart, Firebase, JavaScript, Chrome MV3, Git, GitHub"))


# ---------------------------------------------------------------- section headers
HEAD_ICONS = {
    "journey": (PASS,  # compass
        f'<circle cx="16" cy="16" r="13" fill="none" stroke="{PASS}" stroke-width="2.2"/>'
        f'<g class="sw"><path d="M16 5l4 11h-8z" fill="{FAIL}"/><path d="M16 27l-4-11h8z" fill="{T3}"/></g>'
        f'<circle cx="16" cy="16" r="2" fill="{BG}"/>',
        ".sw{transform-origin:16px 16px;animation:sw 4s ease-in-out infinite}@keyframes sw{0%,100%{transform:rotate(-35deg)}50%{transform:rotate(40deg)}}"),
    "featured": (WARN,  # flask with bubbles
        f'<path d="M12 3h8M13 3v9L5 26a2.5 2.5 0 0 0 2 3.5h18A2.5 2.5 0 0 0 27 26l-8-14V3" fill="none" stroke="{WARN}" stroke-width="2.2" stroke-linejoin="round"/>'
        f'<path d="M8.5 21h15L27 26a2.5 2.5 0 0 1-2 3.5H7A2.5 2.5 0 0 1 5 26z" fill="{WARN}" opacity=".35"/>'
        + "".join(f'<circle cx="{cx}" cy="26" r="{r}" fill="{WARN}" class="bb" style="animation-delay:{dl}s"/>' for cx, r, dl in [(12, 1.6, 0), (17, 1.2, .6), (21, 1.8, 1.2)]),
        ".bb{animation:bb 1.8s ease-in infinite}@keyframes bb{0%{transform:translateY(0);opacity:1}100%{transform:translateY(-16px);opacity:0}}"),
    "toolbox": (VIOLET,  # gear
        '<g class="gr">' + "".join(f'<rect x="14" y="1" width="4" height="7" rx="1" fill="{VIOLET}" transform="rotate({a} 16 16)"/>' for a in range(0, 360, 45))
        + f'<circle cx="16" cy="16" r="9" fill="none" stroke="{VIOLET}" stroke-width="3.2"/><circle cx="16" cy="16" r="3" fill="{VIOLET}"/></g>',
        ".gr{transform-origin:16px 16px;animation:gr 6s linear infinite}@keyframes gr{to{transform:rotate(360deg)}}"),
    "activity": (INFO,  # equalizer bars
        "".join(f'<rect x="{x}" y="4" width="5" height="24" rx="2" fill="{INFO}" class="eq" style="animation-delay:{d}s"/>' for x, d in [(3, 0), (10, -.4), (17, -.8), (24, -.2)]),
        ".eq{transform-origin:0 28px;transform-box:fill-box;animation:eq 1.2s ease-in-out infinite alternate}@keyframes eq{0%{transform:scaleY(.25)}100%{transform:scaleY(1)}}"),
    "more": (FAIL,  # bug crawling
        f'<g class="bug"><ellipse cx="16" cy="18" rx="7" ry="9" fill="{FAIL}"/><circle cx="16" cy="8" r="4" fill="{FAIL}"/>'
        f'<path d="M9 14l-5-3M9 19H3M9 24l-5 3M23 14l5-3M23 19h6M23 24l5 3" stroke="{FAIL}" stroke-width="2" stroke-linecap="round"/>'
        f'<line x1="16" y1="11" x2="16" y2="27" stroke="{BG}" stroke-width="1.5"/></g>',
        ".bug{transform-origin:16px 16px;animation:bug 2.4s ease-in-out infinite}@keyframes bug{0%,100%{transform:translateX(-2px) rotate(-8deg)}50%{transform:translateX(2px) rotate(8deg)}}"),
}


def header(key, title, sub):
    col, icon, css = HEAD_ICONS[key]
    W, H = 860, 64
    css += (f".sc{{animation:sc 4s linear infinite}}@keyframes sc{{0%{{transform:translateX(-220px)}}100%{{transform:translateX({W}px)}}}}")
    b = (f'<defs><linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{col}" stop-opacity="0"/>'
         f'<stop offset=".5" stop-color="{col}"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient></defs>'
         f'<g transform="translate(4 12)">{icon}</g>'
         f'<text x="50" y="37" font-family="{SANS}" font-size="24" font-weight="700" fill="{T1}">{escape(title)}</text>'
         f'<text x="{W-4}" y="37" text-anchor="end" font-family="{MONO}" font-size="13" fill="{T4}">{escape(sub)}</text>'
         f'<rect x="0" y="{H-3}" width="{W}" height="1.5" fill="{LINE}"/>'
         f'<rect x="0" y="{H-3.5}" width="220" height="2.5" fill="url(#l)" class="sc"/>')
    write(f"h-{key}.svg", svg(W, H, b, css, title))


# ---------------------------------------------------------------- card icons
def cards():
    S = 72
    base = f'<rect width="{S}" height="{S}" rx="18" fill="{PANEL}" stroke="{LINE}"/>'
    # Spectara: crosshair + cursor click
    sp = (base + f'<g fill="none" stroke="{PASS}" stroke-width="2">'
          f'<circle cx="36" cy="36" r="18" opacity=".5"/><circle cx="36" cy="36" r="8"/>'
          f'<path d="M36 12v10M36 50v10M12 36h10M50 36h10" stroke-linecap="round"/></g>'
          f'<circle cx="36" cy="36" r="8" fill="none" stroke="{PASS}" stroke-width="2" class="rp"/>'
          f'<path class="cur" d="M0 0l0 16 4.5-4 3 7 3-1.4-3-6.8 6 0z" fill="{T1}" stroke="{BG}" stroke-width="1"/>')
    write("card-spectara.svg", svg(S, S, sp,
          ".cur{animation:cur 3s ease-in-out infinite}@keyframes cur{0%{transform:translate(56px,58px)}40%,70%{transform:translate(36px,36px)}100%{transform:translate(56px,58px)}}"
          ".rp{transform-origin:36px 36px;animation:rp 3s ease-out infinite}@keyframes rp{0%,40%{transform:scale(1);opacity:0}42%{opacity:1}70%,100%{transform:scale(2.6);opacity:0}}",
          "Spectara"))
    # DEPI: 5 team nodes, highlight cycles
    import math
    pts = [(36 + 20 * math.sin(2 * math.pi * i / 5), 38 - 20 * math.cos(2 * math.pi * i / 5)) for i in range(5)]
    dp = base + f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{LINE2}" stroke-width="1.5"/>'
    dp += "".join(f'<line x1="36" y1="38" x2="{x:.1f}" y2="{y:.1f}" stroke="{LINE2}" stroke-width="1"/>' for x, y in pts)
    dp += f'<circle cx="36" cy="38" r="6" fill="{WARN}"/>'
    dp += "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{T3}" class="n" style="animation-delay:{i*0.5}s"/>' for i, (x, y) in enumerate(pts))
    write("card-depi.svg", svg(S, S, dp,
          f".n{{animation:n 2.5s infinite}}@keyframes n{{0%,30%{{fill:{PASS};r:6.5px}}40%,100%{{fill:{T3};r:5px}}}}", "DEPI team"))
    # Flutter: phone with list rows scrolling + checks
    rows = "".join(
        f'<g transform="translate(0 {i*12})"><rect x="28" y="0" width="5" height="5" rx="1.5" fill="{PASS}"/>'
        f'<rect x="36" y="0.5" width="{14 - (i % 2) * 5}" height="4" rx="2" fill="{T3}"/></g>' for i in range(6))
    fl = (base + f'<rect x="22" y="10" width="28" height="52" rx="6" fill="{BG}" stroke="{INFO}" stroke-width="2"/>'
          f'<rect x="32" y="13" width="8" height="2" rx="1" fill="{LINE2}"/>'
          f'<clipPath id="sc"><rect x="24" y="18" width="24" height="40"/></clipPath>'
          f'<g clip-path="url(#sc)"><g class="ls">{rows}</g></g>')
    write("card-flutter.svg", svg(S, S, fl,
          ".ls{animation:ls 3s linear infinite}@keyframes ls{0%{transform:translateY(20px)}100%{transform:translateY(-16px)}}", "Flutter apps"))
    # Data: layered warehouse with flowing dots
    layers = [("RAW", T4), ("BRZ", WARN), ("SLV", T2), ("GLD", "#f2c94c")]
    dt = base
    for i, (n, c) in enumerate(layers):
        y = 12 + i * 13
        dt += (f'<rect x="12" y="{y}" width="48" height="9" rx="4.5" fill="{PANEL2}" stroke="{c}" stroke-width="1.2"/>'
               f'<text x="16" y="{y+7}" font-family="{MONO}" font-size="6.5" fill="{c}">{n}</text>')
    dt += "".join(f'<circle cx="{x}" cy="10" r="2.2" fill="{INFO}" class="dr" style="animation-delay:{d}s"/>' for x, d in [(44, 0), (52, -.7), (48, -1.4)])
    write("card-data.svg", svg(S, S, dt,
          ".dr{animation:dr 2.1s linear infinite}@keyframes dr{0%{transform:translateY(0);opacity:0}10%{opacity:1}90%{opacity:1}100%{transform:translateY(52px);opacity:0}}",
          "Data warehouse layers"))


# ---------------------------------------------------------------- divider
def divider():
    W, H = 860, 14
    b = (f'<defs><linearGradient id="d" x1="0" x2="1"><stop offset="0" stop-color="{PASS}" stop-opacity="0"/>'
         f'<stop offset=".5" stop-color="{PASS}"/><stop offset="1" stop-color="{INFO}" stop-opacity="0"/></linearGradient></defs>'
         f'<rect y="6" width="{W}" height="1.5" fill="{LINE}"/>'
         f'<rect y="5" width="300" height="3.5" rx="2" fill="url(#d)" class="m"/>'
         + "".join(f'<circle cx="{x}" cy="7" r="2.5" fill="{c}" class="p" style="animation-delay:{i*0.3}s"/>'
                   for i, (x, c) in enumerate([(W/2-16, PASS), (W/2, INFO), (W/2+16, VIOLET)])))
    write("divider.svg", svg(W, H, b,
          f".m{{animation:m 5s ease-in-out infinite alternate}}@keyframes m{{0%{{transform:translateX(-300px)}}100%{{transform:translateX({W}px)}}}}"
          ".p{animation:p 1.2s ease-in-out infinite alternate}@keyframes p{0%{opacity:.2}100%{opacity:1}}", "divider"))


typing(); terminal(); journey(); toolbox(); cards(); divider()
header("journey", "The journey", "git log --reverse")
header("featured", "Featured work", "ls ./projects --pinned")
header("toolbox", "Toolbox", "cat stack.yml")
header("activity", "Activity", "git shortlog -sn")
header("more", "More projects", "ls ./projects --all")
print("ok", sorted(os.listdir(OUT)))
