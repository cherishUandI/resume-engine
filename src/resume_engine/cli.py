#!/usr/bin/env python3
"""
Resume Generator CLI — P0 optimized
Usage:
  python3 generate.py --data user.json --theme noir-gold --pdf
  python3 generate.py --data user.json --gallery
  python3 generate.py --data user.json --theme slate-steel --font mono --deco bar --pdf
"""

import argparse, json, os, re, subprocess, sys, time
from pathlib import Path
from datetime import datetime

MODULES = Path(__file__).parent / "modules"
OUTPUT = Path(__file__).parent / "output"
CACHE = Path.home() / ".cache" / "resume-engine"

# ═══════════════════════════════════════════════════════════════
# CSS ASSEMBLY
# ═══════════════════════════════════════════════════════════════

def load_css_modules():
    """Load and concatenate CSS modules in correct order."""
    order = ["base.css", "hero.css", "layout-t.css", "cards.css",
             "photo.css", "icons.css", "pagination.css", "print.css"]
    css = ""
    for fn in order:
        with open(MODULES / fn) as f:
            css += f.read() + "\n"
    return css

def load_data(path):
    """Load JSON data file."""
    with open(path) as f:
        return json.load(f)

def apply_theme(css, theme):
    """Replace Noir Gold colors in CSS with target theme colors."""
    # Noir Gold → placeholders → target theme
    noir = {
        "#c4a46c":"__A__","#d4b87a":"__AL__","#8b7355":"__AD__",
        "#dcd8cf":"__BE__","#faf9f6":"__BG__","#fdfdfb":"__CD__",
        "#faf8f4":"__C2__","#f5f1e8":"__TG__","#e8e4dc":"__BD__",
        "#d4cec0":"__B2__","#e8e2d6":"__B3__","#e0d4b8":"__BT__",
        "#f9f7f2":"__DK__","#1a1f25":"__H1__","#232a33":"__H2__",
        "#f2ede4":"__HT__","#b0a080":"__HM__","#8a8a8a":"__HD__",
        "#1a1a1a":"__TD__","#3a3a3a":"__TX__","#888":"__M1__",
        "#777":"__M2__","#aaa":"__M3__","#bbb":"__M4__","#555":"__M5__",
        "#5a4a3a":"__TT__","#4a4a4a":"__CT__","#fdf6ea":"__NB__",
    }
    for old, new in noir.items():
        css = css.replace(old, new)

    tmap = {
        "__A__":theme["accent"],"__AL__":theme["acc_light"],"__AD__":theme["acc_dim"],
        "__BE__":theme["bg_ext"],"__BG__":theme["bg"],"__CD__":theme["card"],
        "__C2__":theme["card2"],"__TG__":theme["tag"],"__BD__":theme["border"],
        "__B2__":theme["border2"],"__B3__":theme["border3"],"__BT__":theme["border_tag"],
        "__DK__":theme["card_dark"],"__H1__":theme["hero_bg1"],"__H2__":theme["hero_bg2"],
        "__HT__":theme["hero_text"],"__HM__":theme["hero_muted"],"__HD__":theme["hero_dim"],
        "__TD__":theme["text_dark"],"__TX__":theme["text"],"__M1__":theme["muted1"],
        "__M2__":theme["muted2"],"__M3__":theme["muted3"],"__M4__":theme["muted4"],
        "__M5__":theme["muted5"],"__TT__":theme["tag_text"],"__CT__":theme["cert_text"],
        "__NB__":theme["num_bg"],
    }
    for old, new in tmap.items():
        css = css.replace(old, new)
    return css

def inject_font_deco(css, font_css, deco_css, theme):
    """Inject font and decoration CSS overrides."""
    result = css.rstrip() + "\n"
    if font_css:
        result += font_css + "\n"
    if deco_css:
        # Replace decoration placeholders with theme colors
        deco = deco_css.replace("@@ACC@@", theme["accent"])
        deco = deco.replace("@@ACCL@@", theme["acc_light"])
        deco = deco.replace("@@ACC_DIM@@", theme["acc_dim"])
        deco = deco.replace("@@BG@@", theme["bg"])
        deco = deco.replace("@@H1@@", theme["hero_bg1"])
        deco = deco.replace("@@H2@@", theme["hero_bg2"])
        result += deco + "\n"
    return result

# ═══════════════════════════════════════════════════════════════
# HTML BODY GENERATION
# ═══════════════════════════════════════════════════════════════

def gen_body(user, photo_path=None, lang="zh"):
    """Generate HTML body from user data dict. photo_path: optional base64 data URI or file path."""
    u = user

    L = {
        "exp": {"zh": "工作经验", "en": "Work Experience"},
        "proj": {"zh": "项目经历", "en": "Projects"},
        "skills": {"zh": "核心能力", "en": "Core Skills"},
        "edu": {"zh": "教育背景", "en": "Education"},
        "lang_title": {"zh": "语言能力", "en": "Languages"},
        "certs": {"zh": "证书资质", "en": "Certifications"},
        "contact": {"zh": "联系方式", "en": "Contact"},
    }
    label = lambda k: L[k][lang]

    # Photo
    photo_html = ""
    if photo_path:
        photo_html = f'<img class="hero-photo" src="{photo_path}" alt="{u["name"]}">'

    # Metrics
    metrics_html = ""
    for val, lbl in u["metrics"]:
        sp = ""; vp = val
        if "万" in val:
            vp = val.split("万")[0]; sp = '<span> 万</span>'
        metrics_html += f'<div class="hero-metric"><div class="val">{vp}{sp}</div><div class="lbl">{lbl}</div></div>'

    # Experience cards
    exp_cards = ""
    for exp in u["experience"]:
        dark = " card-dark" if exp.get("dark") else ""
        bullets = "\n".join(f"<li>{b}</li>" for b in exp["bullets"])
        exp_cards += f'''
      <div class="exp-card{dark}"><div class="exp-card-inner">
        <div class="exp-top"><div><span class="exp-company">{exp['company']}</span><span class="exp-role">· {exp['role']}</span></div><div class="exp-date-badge"><span>{exp['date']}</span></div></div>
        <div class="exp-summary">{exp['summary']}</div>
        <ul class="exp-list">
          {bullets}
        </ul>
      </div></div>'''

    # Project cards
    proj_cards = ""
    for proj in u.get("projects", []):
        bullets = "\n".join(f"<li>{b}</li>" for b in proj["bullets"])
        proj_cards += f'''
      <div class="exp-card proj"><div class="exp-card-inner">
        <div class="exp-top"><div><span class="exp-company">{proj['name']}</span><span class="exp-role">· {proj['role']}</span></div><div class="exp-date-badge"><span>{proj['date']}</span></div></div>
        <div class="exp-summary">{proj['summary']}</div>
        <ul class="exp-list">
          {bullets}
        </ul>
      </div></div>'''

    # Skills
    tags_html = "\n".join(f'<span class="tag">{s}</span>' for s in u["skills"])

    # Education
    edu_html = "\n".join(
        f'<div class="edu-card"><div class="edu-degree">{e["school"]}</div><div class="edu-school">{e["degree"]}</div><div class="edu-date">{e["date"]}</div></div>'
        for e in u["education"]
    )

    # Languages
    lang_html = "\n".join(
        f'<div class="lang-row"><span>{l[0]}</span><span class="lang-level">{l[1]}</span></div>'
        for l in u["languages"]
    )

    # Certs
    cert_html = "\n".join(f'<div class="cert-row">{c}</div>' for c in u.get("certs", []))

    # Contact — SVG icons
    contact_html = "\n".join(
        f'<div class="contact-row"><div class="ico {icon_class}"></div><span>{val}</span></div>'
        for icon_class, val in [
            ("ico-email", u["email"]),
            ("ico-phone", u["phone"]),
            ("ico-location", u["city"]),
        ]
    )

    footer_name = u["name"] + " · " + u["title"].split("·")[0].strip()

    return f'''<div class="page">

  <div class="hero">
    <div class="hero-inner">
      <div class="hero-left">
        {photo_html}
        <div class="hero-text-block">
          <div class="hero-name">{u['name']}</div>
          <div class="hero-title">{u['title']}</div>
        </div>
      </div>
      <div class="hero-right">
        {metrics_html}
      </div>
    </div>
  </div>

  <div class="content"><div class="cols">
    <div class="main-col">
      <div class="sec-header"><div class="diamond"></div><div class="diamond sm"></div><div class="txt">{label('exp')}</div></div>
      {exp_cards}
      <div class="sec-header" style="margin-top:4px;"><div class="diamond"></div><div class="txt">{label('proj')}</div></div>
      {proj_cards}
    </div>

    <div class="side-col">
      <div class="side-card"><div class="side-sec-title"><span></span>{label('skills')}</div>
        <div class="tags">{tags_html}</div>
      </div>
      <div class="side-card"><div class="side-sec-title"><span></span>{label('edu')}</div>
        {edu_html}
      </div>
      <div class="side-card"><div class="side-sec-title"><span></span>{label('lang_title')}</div>
        {lang_html}
      </div>
      <div class="side-card"><div class="side-sec-title"><span></span>{label('certs')}</div>
        {cert_html}
      </div>
      <div class="side-card"><div class="side-sec-title"><span></span>{label('contact')}</div>
        {contact_html}
      </div>
    </div>
  </div></div>

  <div class="footer-bar">
    <span>{footer_name}</span>
    <span>{u['email']}</span>
    <span>{u['phone']}</span>
  </div>

</div>'''

# ═══════════════════════════════════════════════════════════════
# VERIFICATION
# ═══════════════════════════════════════════════════════════════

def count_pdf_pages(pdf_path):
    """Count pages in a PDF file. Returns int, or None if unable."""
    try:
        # Use pdfinfo from poppler-utils
        result = subprocess.run(
            ["pdfinfo", pdf_path], capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.split("\n"):
            if line.startswith("Pages:"):
                return int(line.split(":")[1].strip())
    except Exception:
        pass
    # Fallback: count /Page objects in raw PDF
    try:
        with open(pdf_path, "rb") as f:
            content = f.read().decode("latin-1", errors="ignore")
        return len(re.findall(r'/Type\s*/Page[^s]', content))
    except Exception:
        return None


def verify(html_path, pdf_path=None, screenshot_path=None, user=None, max_pages=2):
    """Run verification checks. Returns (passed, report_lines)."""
    report = []
    passed = True

    # 1. HTML starts with <!DOCTYPE
    with open(html_path) as f:
        first = f.readline().strip()
    if first.startswith("<!DOCTYPE"):
        report.append("✓ HTML header: <!DOCTYPE")
    else:
        report.append(f"✗ HTML header: {first[:50]}... (corrupted!)")
        passed = False

    # 2. No leftover placeholders
    with open(html_path) as f:
        content = f.read()
    placeholders = re.findall(r'__[A-Z_]+__', content)
    if placeholders:
        report.append(f"✗ Placeholder residue: {placeholders}")
        passed = False
    else:
        report.append("✓ No placeholder residue")

    # 3. Count verification
    if user:
        exp_count = content.count("exp-company")
        tag_count = content.count('<span class="tag">')
        bullet_count = content.count('<li>')
        # Non-T layouts use different class names — only warn if T layout
        if exp_count > 0 or tag_count > 0:
            report.append(f"✓ Experience cards: {exp_count} (expected {len(user['experience'])+len(user.get('projects',[]))})")
            report.append(f"✓ Skill tags: {tag_count} (expected {len(user['skills'])})")
            report.append(f"✓ Bullets: {bullet_count}")
            if exp_count < len(user['experience']):
                report.append("⚠ Experience card count lower than expected")
            if tag_count != len(user['skills']):
                report.append("⚠ Skill tag count mismatch")
        else:
            # Non-T layout — verify data presence
            name_present = user['name'] in content
            email_present = user['email'] in content
            # Universal bullet check: count experience companies as proxy
            company_count = sum(1 for exp in user['experience'] if exp['company'][:4] in content)
            # Count <p> tags + <br> + · bullet markers as content density gauge
            p_count = content.count('<p>') + content.count('<p ') + content.count('<br>') + content.count(' · ')
            report.append(f"✓ Data integrity: name={'✓' if name_present else '✗'}, email={'✓' if email_present else '✗'}, companies={company_count}/{len(user['experience'])}, density_markers={p_count}")
            if p_count < len(user['experience']):
                report.append("⚠ Low content density — bullets may be missing!")

    # 4. Screenshot size check
    if screenshot_path and os.path.exists(screenshot_path):
        size = os.path.getsize(screenshot_path)
        if size > 50000:
            report.append(f"✓ Screenshot: {size//1024}KB (>50KB)")
        else:
            report.append(f"✗ Screenshot: {size//1024}KB (too small, render failed!)")
            passed = False

    # 5. PDF size check
    if pdf_path and os.path.exists(pdf_path):
        size = os.path.getsize(pdf_path)
        if size > 50000:
            report.append(f"✓ PDF: {size//1024}KB (>50KB)")
        else:
            report.append(f"✗ PDF: {size//1024}KB (too small, render failed!)")
            passed = False

        # 5b. Page count check
        pages = count_pdf_pages(pdf_path)
        if pages is not None:
            if pages <= max_pages:
                report.append(f"✓ Pages: {pages}/{max_pages}")
            else:
                report.append(f"⚠ Pages: {pages}/{max_pages} — OVERFLOW!")
                # Don't fail, just warn — caller can retry with compact

    return passed, report

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def generate(args):
    """Main generation flow."""
    os.makedirs(str(OUTPUT), exist_ok=True)
    os.makedirs(CACHE / "screenshots", exist_ok=True)
    os.makedirs(CACHE / "documents", exist_ok=True)

    # Load data
    user = load_data(args.data)
    themes = load_data(MODULES / "themes.json")
    fonts = load_data(MODULES / "fonts.json")
    decos = load_data(MODULES / "decos.json")
    shapes = load_data(MODULES / "shapes.json")
    card_styles = load_data(MODULES / "card-styles.json")
    densities = load_data(MODULES / "densities.json")
    radius_map = load_data(MODULES / "radius.json")

    theme_key = args.theme
    font_key = args.font
    deco_key = args.deco

    if theme_key not in themes:
        print(f"ERROR: Unknown theme '{theme_key}'. Available: {list(themes.keys())}")
        sys.exit(1)
    if font_key not in fonts:
        print(f"ERROR: Unknown font '{font_key}'. Available: {list(fonts.keys())}")
        sys.exit(1)
    if deco_key not in decos:
        print(f"ERROR: Unknown deco '{deco_key}'. Available: {list(decos.keys())}")
        sys.exit(1)
    if args.shape not in shapes:
        print(f"ERROR: Unknown shape '{args.shape}'. Available: {list(shapes.keys())}")
        sys.exit(1)
    if args.card_style not in card_styles:
        print(f"ERROR: Unknown card-style '{args.card_style}'. Available: {list(card_styles.keys())}")
        sys.exit(1)
    if args.density not in densities:
        print(f"ERROR: Unknown density '{args.density}'. Available: {list(densities.keys())}")
        sys.exit(1)
    if args.radius not in radius_map:
        print(f"ERROR: Unknown radius '{args.radius}'. Available: {list(radius_map.keys())}")
        sys.exit(1)

    theme = themes[theme_key]
    font_css = fonts[font_key]
    deco_css = decos[deco_key]
    shape = shapes[args.shape]
    card = card_styles[args.card_style]
    density = densities[args.density]
    border_radius = radius_map[args.radius]

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = f"resume-{theme_key}-{font_key}-{deco_key}-{args.shape}-{args.card_style}-{timestamp}"

    # Photo
    photo_uri = getattr(args, "photo", None)
    if photo_uri and os.path.exists(photo_uri):
        import base64
        ext = os.path.splitext(photo_uri)[1].lower()
        mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(ext.lstrip("."), "jpeg")
        with open(photo_uri, "rb") as pf:
            photo_uri = f"data:image/{mime};base64,{base64.b64encode(pf.read()).decode()}"
    elif photo_uri and photo_uri.startswith("data:"):
        pass  # Already a data URI
    else:
        photo_uri = None

    max_pages = getattr(args, "max_pages", 2)
    layout_code = getattr(args, "layout", "T")
    lang = getattr(args, "lang", None) or user.get("lang", "zh")

    # ── Layout branching ──
    if layout_code != "T":
        # Non-T layouts: load self-contained CSS from JSON + use layout body generator
        from resume_engine import layouts as layouts_mod

        layout_css_map = {}
        for fname in ["layouts_K_T.json", "layouts_K_O.json"]:
            fp = MODULES / fname
            if os.path.exists(fp):
                with open(fp) as f:
                    layout_css_map.update(json.load(f))

        # Map user-friendly names to JSON keys
        LAYOUT_KEY_MAP = {
            "minimal": "N-minimal",
            "classic": "Q-classic",
            "gallery": "M-gallery",
            "matrix": "K-matrix",
            "compare": "L-compare",
            "stagger": "P-stagger",
            "tabbed": "R-tabbed",
            "visual": "S-visual",
            "bold": "U-bold",
            "masonry": "V-masonry",
            "split": "W-split",
            "table": "Y-table",
            "bars": "Z-bars",
            "blocks": "AA-blocks",
        }
        json_key = LAYOUT_KEY_MAP.get(layout_code, layout_code)
        if json_key not in layout_css_map:
            print(f"ERROR: Unknown layout '{layout_code}'. Available: T, {list(LAYOUT_KEY_MAP.keys())}")
            sys.exit(1)

        css = layout_css_map[json_key]["css"]
        css = apply_theme(css, theme)  # Noir Gold → placeholder → target
        css = layouts_mod.apply_layout_theme(css, theme)

        # Inject font, density, radius overrides for non-T layouts
        import re as _re
        ff_match = _re.search(r'font-family:\s*([^;!]+)', font_css)
        font_family = ff_match.group(1).strip() if ff_match else "-apple-system, 'Microsoft YaHei', 'PingFang SC', sans-serif"
        css += f"\n/* === Injected overrides === */\n"
        css += f"*,body{{font-family:{font_family};}}\n"
        css += f"body{{font-size:{density['body_size']};line-height:{density['line_height']};}}\n"
        css += f".classic-item,.classic-top,.classic-mid .col,.classic-bot{{border-radius:{border_radius};}}\n"
        css += f".minimal-item,.minimal-section{{border-radius:{border_radius};}}\n"
        css += f".gallery-card{{border-radius:{border_radius};}}\n"
        css += f".matrix-cell,.compare-card,.stag-block,.tab-item,.vis-card,.wf-item{{border-radius:{border_radius};}}\n"
        css += f".bold-card,.mason-card,.split-item,.metro-tile{{border-radius:{border_radius};}}\n"
        css += ".bold-card .summary{font-size:8pt;color:__MUTED1__;font-style:italic;margin-bottom:4px;line-height:1.5;}\n"
        css += ".split-item .summary{font-size:8pt;color:__MUTED1__;font-style:italic;margin-bottom:4px;line-height:1.5;}\n"
        # Inject missing class styles for richer content
        css += ".classic-item .role{font-size:9pt;color:__ACCENT__;margin:2px 0 4px;font-weight:500;}\n"
        css += ".classic-item .summary{font-size:8pt;color:__MUTED1__;font-style:italic;margin-bottom:4px;line-height:1.5;}\n"
        css += ".classic-item p{font-size:8.5pt;color:__TEXT__;line-height:1.6;margin-bottom:3px;}\n"
        css += ".minimal-item .summary{font-size:8.5pt;color:__MUTED1__;font-style:italic;margin:4px 0;line-height:1.5;}\n"
        css += ".minimal-item p{font-size:8.5pt;color:__TEXT__;line-height:1.6;margin-bottom:2px;padding-left:12px;position:relative;}\n"
        css += ".minimal-item p::before{content:'';position:absolute;left:0;top:5px;width:5px;height:5px;background:__ACCENT__;border-radius:50%;}\n"
        css = layouts_mod.apply_layout_theme(css, theme)  # Re-apply after adding new placeholders

        body_gen = layouts_mod.BODY_GENERATORS.get(layout_code)
        if not body_gen:
            print(f"ERROR: No body generator for layout '{layout_code}'")
            sys.exit(1)
        body = body_gen(user, photo_uri)

    else:
        # T layout: modular CSS assembly + gen_body
        # 1. Assemble CSS
        css = load_css_modules()
        css = apply_theme(css, theme)
        # Inject shape
        css = css.replace("@@HERO_CLIP@@", shape["clip"])
        css = css.replace("@@HERO_PAD@@", shape["padding"])
        # Inject card style
        css = css.replace("@@EXP_CLIP@@", card["exp_clip"])
        css = css.replace("@@PROJ_CLIP@@", card["proj_clip"])
        css = css.replace("@@EXP_BEFORE_TOP@@", card["exp_before_top"])
        css = css.replace("@@PROJ_BEFORE_TOP@@", card["exp_before_top"])
        # Inject density (adjust font-size, line-height, spacing)
        css = css.replace("font-size: 9pt", f"font-size: {density['body_size']}")
        css = css.replace("line-height: 1.65", f"line-height: {density['line_height']}")
        css = css.replace("line-height: 1.6", f"line-height: {density['line_height']}")
        # Inject border-radius on cards
        css = re.sub(r'border-radius:\s*0px', f'border-radius: {border_radius}', css)
        css = css.replace("border-radius: 0 0px 0px 0", f"border-radius: 0 {border_radius} {border_radius} 0")
        css = inject_font_deco(css, font_css, deco_css, theme)

        # 2. Generate body
        body = gen_body(user, photo_uri, lang)

    # 3. Assemble HTML
    title = f"{user['name']} · {theme_key} | {font_key} | {deco_key}"
    html_lang = "en" if lang == "en" else "zh-CN"
    meta_author = user['name']
    meta_keywords = ", ".join(user.get('skills', [])[:10])
    html = f'<!DOCTYPE html>\n<html lang="{html_lang}">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<meta name="generator" content="resume-generator v3.0">\n<meta name="author" content="{meta_author}">\n<meta name="keywords" content="{meta_keywords}">\n<meta name="theme" content="{theme_key}">\n<meta name="font" content="{font_key}">\n<meta name="deco" content="{deco_key}">\n<meta name="lang" content="{lang}">\n<meta name="timestamp" content="{timestamp}">\n<title>{title}</title>\n<style>\n{css}\n</style>\n</head>\n<body>\n{body}\n</body>\n</html>'

    html_path = OUTPUT / f"{slug}.html"
    with open(html_path, "w") as f:
        f.write(html)
    print(f"[1/4] HTML generated: {html_path} ({len(html)}B)")

    # Gate: verify HTML
    passed, report = verify(html_path, user=user)
    for line in report:
        print(f"  {line}")
    if not passed:
        print("❌ Verification FAILED — aborting")
        sys.exit(1)

    if args.preview or args.pdf:
        # 4a. Start HTTP server
        print("[2/4] Starting HTTP server...")
        server = subprocess.Popen(
            ["python3", "-m", "http.server", "8790"],
            cwd=str(OUTPUT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(2)

        # Verify server
        try:
            import urllib.request
            resp = urllib.request.urlopen(f"http://localhost:8790/{slug}.html")
            if resp.status != 200:
                raise Exception("Server not ready")
        except:
            print("  Retrying server on 8791...")
            server.kill()
            server = subprocess.Popen(
                ["python3", "-m", "http.server", "8791"],
                cwd=str(OUTPUT),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(2)
            port = 8791
        else:
            port = 8790

        # 4b. Screenshot
        ss_path = CACHE / "screenshots" / f"{slug}.png"
        print(f"[3/4] Screenshot → {slug}.png")
        subprocess.run([
            "chromium-browser", "--headless", "--disable-gpu",
            f"--screenshot={ss_path}",
            "--window-size=794,1123", "--no-sandbox",
            f"http://localhost:{port}/{slug}.html",
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)

        pdf_path = None
        if args.pdf:
            # 4c. PDF
            pdf_path = CACHE / "documents" / f"{user['name']}简历-{theme_key}-{font_key}-{deco_key}-{timestamp}.pdf"
            print(f"[4/4] PDF → {os.path.basename(pdf_path)}")
            subprocess.run([
                "chromium-browser", "--headless", "--disable-gpu",
                f"--print-to-pdf={pdf_path}",
                "--no-sandbox",
                f"http://localhost:{port}/{slug}.html",
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)

        # Kill server
        server.kill()
        server.wait()

        # Final verification
        passed2, report2 = verify(html_path, pdf_path=pdf_path, screenshot_path=ss_path, max_pages=max_pages)
        for line in report2:
            print(f"  {line}")

        overflow = any("OVERFLOW" in l for l in report2)

        if passed2:
            print(f"\n✅ SUCCESS")
            print(f"   HTML: {html_path}")
            if ss_path:
                print(f"   Screenshot: {ss_path}")
            if pdf_path:
                print(f"   PDF: {pdf_path}")
            if overflow:
                print(f"   ⚠ Content overflows {max_pages} page(s). Try --density compact or --density minimal.")
        else:
            print(f"\n❌ Output verification FAILED")
            sys.exit(1)
    else:
        print(f"\n✅ HTML only mode — {html_path}")

# ═══════════════════════════════════════════════════════════════
# GALLERY MODE
# ═══════════════════════════════════════════════════════════════

def gallery(args):
    """Generate 12 variants covering all layout types."""
    variants = [
        # Theme          Font       Deco         Shape          Card    Density     Layout
        ("noir-gold",    "sans",    "none",      "right-slant",  "sharp","standard",  "T"),
        ("slate-steel",  "mono",    "bar",       "left-slant",   "soft", "compact",   "matrix"),
        ("teal-ocean",   "serif",   "corner",    "v-cut",        "curve","standard",  "compare"),
        ("ember-ash",    "heiti",   "geo",       "gentle-wave",  "sharp","breathing", "stagger"),
        ("midnight-navy","round",   "corner",    "asymm-wave",   "soft", "standard",  "tabbed"),
        ("burgundy-blush","mixed",  "none",      "sharp-wave",   "curve","standard",  "visual"),
        ("forest-moss",  "sans",    "bar",       "deep-wave",    "sharp","compact",   "bold"),
        ("plum-noir",    "mono",    "geo",       "right-slant",  "sharp","breathing", "masonry"),
        ("indigo-deep",  "serif",   "dividers",  "v-cut",        "soft", "standard",  "split"),
        ("coral-pink",   "handwriting","gradient-bg","left-slant","sharp","minimal",  "table"),
        ("amber-gold",   "bold-condensed","glow-orb","gentle-wave","soft","compact",  "bars"),
        ("arctic-blue",  "mono",    "grid-lines","deep-wave",    "curve","standard",  "blocks"),
    ]

    print(f"🎨 Gallery mode: {len(variants)} variants\n")

    for theme, font, deco, shape, card_style, density, layout in variants:
        ns = argparse.Namespace(
            data=args.data, theme=theme, font=font, deco=deco,
            shape=shape, card_style=card_style, density=density,
            radius="r0", layout=layout,
            preview=True, pdf=args.pdf,
            photo=getattr(args, "photo", None),
            max_pages=getattr(args, "max_pages", 2),
            lang=getattr(args, "lang", None),
        )
        try:
            generate(ns)
        except SystemExit as e:
            if e.code != 0:
                print(f"  ⚠ {theme}/{font}/{deco} failed, continuing...\n")
        print()

    print("🎨 Gallery complete")


# ═══════════════════════════════════════════════════════════════

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Resume Generator v3.0")
    parser.add_argument("--data", default="user.json", help="User data JSON file")
    parser.add_argument("--theme", default="noir-gold", help="Theme name")
    parser.add_argument("--font", default="sans", help="Font variant")
    parser.add_argument("--deco", default="none", help="Decoration variant")
    parser.add_argument("--shape", default="right-slant", help="Hero clip-path shape")
    parser.add_argument("--card-style", default="sharp", help="Card corner style (sharp/soft/curve)")
    parser.add_argument("--density", default="standard", help="Content density (breathing/standard/compact/minimal)")
    parser.add_argument("--radius", default="r0", help="Border radius (r0-r4 = 0-8px)")
    parser.add_argument("--layout", default="T", help="Layout: T, matrix, compare, stagger, tabbed, visual, bold, masonry, split, table, bars, blocks")
    parser.add_argument("--pdf", action="store_true", help="Generate PDF output")
    parser.add_argument("--preview", action="store_true", help="Screenshot only (faster)")
    parser.add_argument("--photo", default=None, help="Path to photo/avatar image for hero section")
    parser.add_argument("--lang", default=None, help="Language: zh (Chinese) or en (English). Default: from user.json")
    parser.add_argument("--max-pages", type=int, default=2, help="Max pages before overflow warning (default: 2)")
    parser.add_argument("--gallery", action="store_true", help="Generate 8-variant comparison")

    args = parser.parse_args()

    if args.gallery:
        gallery(args)
    else:
        generate(args)


if __name__ == "__main__":
    main()
