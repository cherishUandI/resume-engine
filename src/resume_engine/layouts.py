#!/usr/bin/env python3
"""Layout registry -- maps layout codes to CSS + HTML body generators."""

import json, os

# ── Theme mapping for K-T layout placeholders ──
def apply_layout_theme(css, theme):
    tmap = {
        "__BG_EXT__": theme["bg_ext"],
        "__BG__": theme["bg"],
        "__HERO_BG1__": theme["hero_bg1"],
        "__HERO_BG2__": theme["hero_bg2"],
        "__HERO_TEXT__": theme["hero_text"],
        "__HERO_MUTED__": theme["hero_muted"],
        "__HERO_DIM__": theme["hero_dim"],
        "__ACCENT__": theme["accent"],
        "__ACC_DIM__": theme["acc_dim"],
        "__CARD__": theme["card"],
        "__CARD2__": theme["card2"],
        "__BORDER__": theme["border"],
        "__TEXT_DARK__": theme["text_dark"],
        "__TEXT__": theme["text"],
        "__MUTED1__": theme["muted1"],
        "__TAG__": theme["tag"],
    }
    for old, new in tmap.items():
        css = css.replace(old, new)
    return css


def _exp_bullets(exp):
    """Render experience bullets as <p> lines."""
    bullets = "".join(f"<p>{b}</p>" for b in exp["bullets"])
    return f'''<div class="minimal-item">
  <div class="head"><b>{exp['company']}</b><span>{exp['date']}</span></div>
  <div class="role">{exp['role']}</div>
  <p class="summary">{exp['summary']}</p>
  {bullets}
</div>'''


# ── Body generators ──

def body_minimal(user, photo_uri=None):
    u = user
    ph = f'<img class="hero-photo" src="{photo_uri}" alt="{u["name"]}">' if photo_uri else ""

    exp_html = "".join(_exp_bullets(e) for e in u["experience"])

    proj_html = ""
    for p in u.get("projects", []):
        proj_html += "".join(f"<p>{b}</p>" for b in p["bullets"])
        proj_html = f'<div class="minimal-item"><div class="head"><b>{p["name"]}</b><span>{p["date"]}</span></div><div class="role">{p["role"]}</div><p class="summary">{p["summary"]}</p>{proj_html}</div>'

    tags_html = " ".join(f'<span class="minimal-tag">{s}</span>' for s in u["skills"])
    edu_html = " | ".join(f'{e["school"]} - {e["degree"]} ({e["date"]})' for e in u["education"])
    cert_html = " | ".join(u.get("certs", []))
    lang_html = " | ".join(f'{l[0]} ({l[1]})' for l in u["languages"])

    sections = []
    sections.append(("Experience", exp_html))
    if proj_html:
        sections.append(("Projects", proj_html))
    sections.append(("Skills", f'<div class="minimal-tags">{tags_html}</div>'))
    sections.append(("Education", f"<p>{edu_html}</p>"))
    if cert_html:
        sections.append(("Certifications", f"<p>{cert_html}</p>"))
    sections.append(("Languages", f"<p>{lang_html}</p>"))

    sec_html = "\n".join(
        f'<div class="minimal-section"><h2>{title}</h2>{content}</div>'
        for title, content in sections
    )

    return f'''<div class="page">
  <div class="minimal-top">
    {ph}
    <div class="minimal-name">{u['name']}</div>
    <div class="minimal-title">{u['title']}</div>
    <div class="minimal-contact">{u['email']} | {u['phone']} | {u['city']}</div>
  </div>
  {sec_html}
</div>'''


def body_classic(user, photo_uri=None):
    u = user
    ph = f'<img class="hero-photo" src="{photo_uri}" alt="{u["name"]}">' if photo_uri else ""

    # Left col: Experience + Projects (with bullets)
    left_items = []
    for exp in u["experience"]:
        bullets = "".join(f"<p>{b}</p>" for b in exp["bullets"])
        left_items.append(f'<div class="classic-item"><div class="hd"><b>{exp["company"]}</b><span>{exp["date"]}</span></div><p class="role">{exp["role"]}</p><p class="summary">{exp["summary"]}</p>{bullets}</div>')
    for proj in u.get("projects", []):
        bullets = "".join(f"<p>{b}</p>" for b in proj["bullets"])
        left_items.append(f'<div class="classic-item"><div class="hd"><b>{proj["name"]}</b><span>{proj["date"]}</span></div><p class="role">{proj["role"]}</p><p class="summary">{proj["summary"]}</p>{bullets}</div>')

    # Right col: Education + Languages + Certs
    right_items = []
    for e in u["education"]:
        right_items.append(f'<div class="classic-item"><div class="hd"><b>{e["school"]}</b><span>{e["date"]}</span></div><p>{e["degree"]}</p></div>')
    for l in u["languages"]:
        right_items.append(f'<div class="classic-item"><p>{l[0]} — {l[1]}</p></div>')
    for c in u.get("certs", []):
        right_items.append(f'<div class="classic-item"><p>{c}</p></div>')

    tags_html = " ".join(f"<span>{s}</span>" for s in u["skills"])

    return f'''<div class="page">
  <div class="classic-top">
    {ph}
    <h1>{u['name']}</h1>
    <div class="title">{u['title']}</div>
    <div class="contact">{u['email']} | {u['phone']} | {u['city']}</div>
  </div>
  <div class="classic-mid">
    <div class="col">
      <h2>Experience</h2>
      {"".join(left_items)}
    </div>
    <div class="col">
      <h2>Education & More</h2>
      {"".join(right_items)}
    </div>
  </div>
  <div class="classic-bot">
    <div class="tag-group">{tags_html}</div>
  </div>
</div>'''


def body_gallery(user, photo_uri=None):
    u = user
    ph = f'<img class="hero-photo" src="{photo_uri}" alt="{u["name"]}">' if photo_uri else ""

    cards = []
    for i, exp in enumerate(u["experience"]):
        wide = " wide" if i == 0 else ""
        bullets = "<br>".join(exp["bullets"])
        cards.append(f'''<div class="gallery-card{wide}">
  <div class="head">{exp['company']} — {exp['date']}</div>
  <div class="body">
    <div class="line"><b>{exp['role']}</b></div>
    <div class="line">{exp['summary']}</div>
    <div class="line">{bullets}</div>
  </div>
</div>''')

    for proj in u.get("projects", []):
        bullets = "<br>".join(proj["bullets"])
        cards.append(f'''<div class="gallery-card">
  <div class="head">{proj['name']} — {proj['date']}</div>
  <div class="body">
    <div class="line"><b>{proj['role']}</b></div>
    <div class="line">{proj['summary']}</div>
    <div class="line">{bullets}</div>
  </div>
</div>''')

    # Skills as tag strip
    tags_html = " ".join(f'<span class="minimal-tag">{s}</span>' for s in u["skills"])
    # Education + certs as a wide card
    edu_lines = " | ".join(f'{e["school"]} ({e["date"]})' for e in u["education"])
    cert_lines = " | ".join(u.get("certs", []))
    lang_lines = " | ".join(f'{l[0]} ({l[1]})' for l in u["languages"])

    return f'''<div class="page">
  <div class="gallery-hero">
    {ph}
    <h1>{u['name']}</h1>
    <div class="sub">{u['title']}</div>
    <div class="contact">{u['email']} | {u['phone']} | {u['city']}</div>
  </div>
  <div class="gallery-grid">
    {"".join(cards)}
  </div>
  <div style="padding:12px 18mm; display:flex; flex-wrap:wrap; gap:6px; justify-content:center; border-top:1px solid #e0dcd4;">
    {tags_html}
  </div>
  <div style="padding:8px 18mm 20px; text-align:center; font-size:8pt; color:#888;">
    <p>{edu_lines}</p>
    <p style="margin-top:4px;">{cert_lines} &nbsp;|&nbsp; {lang_lines}</p>
  </div>
</div>'''


def body_matrix(user, photo_uri=None):
    """K-matrix: 3-column skill grid + experience strip with bullets."""
    u = user
    ph = f'<img class="hero-photo" src="{photo_uri}" alt="{u["name"]}">' if photo_uri else ""

    skill_chunks = [u["skills"][i:i+5] for i in range(0, len(u["skills"]), 5)]
    cells = []
    labels = ["Core Stack", "Frameworks", "Specialties"]
    for i, chunk in enumerate(skill_chunks):
        chips = "".join(f'<span class="matrix-chip">{s}</span>' for s in chunk)
        cells.append(f'<div class="matrix-cell"><h3>{labels[i] if i < len(labels) else "More"}</h3><div class="items">{chips}</div></div>')

    exp_rows = ""
    for exp in u["experience"]:
        bullets = " · ".join(exp["bullets"])
        exp_rows += f'<div class="row"><div class="date">{exp["date"]}</div><div class="info"><b>{exp["company"]}</b> — {exp["role"]}<br><small>{exp["summary"]}</small><br><small style="color:#666;">{bullets}</small></div></div>'

    return f'''<div class="page">
  <div class="hero-matrix">
    {ph}
    <h1>{u['name']}</h1>
    <div class="sub">{u['title']}</div>
    <div class="contact">{u['email']} | {u['phone']} | {u['city']}</div>
  </div>
  <div class="matrix-grid">{"".join(cells)}</div>
  <div class="exp-strip">{exp_rows}</div>
</div>'''


def body_compare(user, photo_uri=None):
    """L-compare: header bar + left/right comparison columns with bullets."""
    u = user
    ph = f'<img class="hero-photo" src="{photo_uri}" alt="{u["name"]}">' if photo_uri else ""

    left = ""
    for exp in u["experience"]:
        bullets = "<br>".join(f"· {b}" for b in exp["bullets"])
        left += f'<div class="compare-card"><div class="title">{exp["company"]}</div><div class="sub">{exp["role"]}</div><div class="date">{exp["date"]}</div><p style="font-size:8pt;color:#666;line-height:1.5;margin-top:4px;">{exp["summary"]}<br>{bullets}</p></div>'

    right = ""
    for e in u["education"]:
        right += f'<div class="compare-card"><div class="title">{e["school"]}</div><div class="sub">{e["degree"]}</div><div class="date">{e["date"]}</div></div>'
    for c in u.get("certs", []):
        right += f'<div class="compare-card"><div class="title">{c}</div></div>'
    for l in u["languages"]:
        right += f'<div class="compare-card"><div class="title">{l[0]}</div><div class="sub">{l[1]}</div></div>'

    skills = "".join(f'<span class="sk">{s}</span>' for s in u["skills"])

    return f'''<div class="page">
  <div class="header-bar">
    <div>{ph}<h1>{u['name']}</h1></div>
    <div class="meta">{u['title']}<br>{u['email']} | {u['phone']}</div>
  </div>
  <div class="skills-bar">{skills}</div>
  <div class="compare-grid">
    <div class="compare-col"><h2>Experience</h2>{left}</div>
    <div class="compare-col"><h2>Background</h2>{right}</div>
  </div>
</div>'''


def body_stagger(user, photo_uri=None):
    """P-stagger: diagonal hero + staggered flow blocks with bullets."""
    u = user
    ph = f'<img class="hero-photo" src="{photo_uri}" alt="{u["name"]}">' if photo_uri else ""

    blocks = ""
    for i, exp in enumerate(u["experience"]):
        side = "right" if i % 2 == 0 else "left"
        bullets = "".join(f"<p>{b}</p>" for b in exp["bullets"][:3])
        blocks += f'<div class="stag-block {side}"><h3>{exp["company"]}</h3><div class="meta">{exp["role"]} · {exp["date"]}</div><p class="summary">{exp["summary"]}</p>{bullets}</div>'

    chips = "".join(f'<span class="stag-chip">{s}</span>' for s in u["skills"])

    return f'''<div class="page">
  <div class="stag-hero">
    {ph}
    <h1>{u['name']}</h1>
    <div class="sub">{u['title']}<br>{u['email']} | {u['phone']} | {u['city']}</div>
  </div>
  <div class="stag-flow">{blocks}</div>
  <div class="stag-skills">{chips}</div>
</div>'''


def body_tabbed(user, photo_uri=None):
    """R-tabbed: sidebar with tabs + main content area."""
    u = user
    ph = f'<img class="hero-photo" src="{photo_uri}" alt="{u["name"]}">' if photo_uri else ""

    # Experience section
    exp_items = ""
    for exp in u["experience"]:
        bullets = "".join(f"<p>{b}</p>" for b in exp["bullets"])
        exp_items += f'<div class="tab-item"><div class="head"><b>{exp["company"]}</b><span>{exp["date"]}</span></div><p class="role">{exp["role"]}</p><p class="summary">{exp["summary"]}</p>{bullets}</div>'

    # Skills section
    skill_tags = "".join(f'<span class="tab-tag">{s}</span>' for s in u["skills"])

    # Education section
    edu_items = ""
    for e in u["education"]:
        edu_items += f'<div class="tab-item"><div class="head"><b>{e["school"]}</b><span>{e["date"]}</span></div><p>{e["degree"]}</p></div>'
    for c in u.get("certs", []):
        edu_items += f'<div class="tab-item"><p>{c}</p></div>'

    return f'''<div class="page">
  <div class="tab-layout">
    <div class="tab-sidebar">
      <div class="avatar">{u["name"][0]}</div>
      <div class="name">{u['name']}</div>
      <div class="role">{u['title']}</div>
      <div class="tabs">
        <div class="tab-btn active">Experience</div>
        <div class="tab-btn">Skills</div>
        <div class="tab-btn">Education</div>
        <div class="tab-btn">Contact</div>
      </div>
    </div>
    <div class="tab-main">
      <div class="tab-section"><h3>Experience</h3>{exp_items}</div>
      <div class="tab-section"><h3>Core Skills</h3><div class="tab-tags">{skill_tags}</div></div>
      <div class="tab-section"><h3>Education & Certs</h3>{edu_items}</div>
      <div class="tab-section"><h3>Contact</h3><p>{u['email']}<br>{u['phone']}<br>{u['city']}</p></div>
    </div>
  </div>
</div>'''


def body_visual(user, photo_uri=None):
    """S-visual: gradient hero + 2/3 main + 1/3 sidebar with icon cards."""
    u = user
    ph = f'<img class="hero-photo" src="{photo_uri}" alt="{u["name"]}">' if photo_uri else ""

    # Main: Experience cards
    vis_cards = ""
    for exp in u["experience"]:
        bullets = "".join(f"<p>{b}</p>" for b in exp["bullets"])
        vis_cards += f'<div class="vis-card"><div class="date">{exp["date"]}</div><b>{exp["company"]}</b><div class="role">{exp["role"]}</div><p>{exp["summary"]}</p>{bullets}</div>'

    # Side: Skills box + Education box
    skill_tags = "".join(f'<span class="tab-tag">{s}</span>' for s in u["skills"])
    edu_lines = "<br>".join(f'{e["school"]} — {e["degree"]} ({e["date"]})' for e in u["education"])
    cert_lines = "<br>".join(u.get("certs", []))
    lang_lines = "<br>".join(f'{l[0]}: {l[1]}' for l in u["languages"])

    return f'''<div class="page">
  <div class="vis-hero">
    {ph}
    <h1>{u['name']}</h1>
    <div class="sub">{u['title']}</div>
    <div class="sub" style="font-size:8pt;opacity:0.7;margin-top:4px;">{u['email']} | {u['phone']} | {u['city']}</div>
  </div>
  <div class="vis-body">
    <div class="vis-main">
      <div class="sec"><h2><span class="icon">E</span>Experience</h2>{vis_cards}</div>
    </div>
    <div class="vis-side">
      <div class="box"><h3>Skills</h3><div class="tab-tags">{skill_tags}</div></div>
      <div class="box"><h3>Education</h3><p>{edu_lines}</p></div>
      <div class="box"><h3>Certs</h3><p>{cert_lines}</p></div>
      <div class="box"><h3>Languages</h3><p>{lang_lines}</p></div>
    </div>
  </div>
</div>'''


def body_waterfall(user, photo_uri=None):
    """T-waterfall: centered header + cascading waterfall items + footer."""
    u = user
    ph = f'<img class="hero-photo" src="{photo_uri}" alt="{u["name"]}">' if photo_uri else ""

    items = ""
    for exp in u["experience"]:
        bullets = "".join(f"<p>{b}</p>" for b in exp["bullets"])
        items += f'<div class="wf-item"><div class="wf-date">{exp["date"]}</div><b>{exp["company"]}</b><div class="role">{exp["role"]}</div><p>{exp["summary"]}</p>{bullets}</div>'

    chips = "".join(f'<span class="chip">{s}</span>' for s in u["skills"])

    return f'''<div class="page">
  <div class="wf-header">
    {ph}
    <h1>{u['name']}</h1>
    <div class="sub">{u['title']}</div>
    <div class="contact">{u['email']} | {u['phone']} | {u['city']}</div>
  </div>
  <div class="wf-cascade">{items}</div>
  <div class="wf-footer">{chips}</div>
</div>'''


def body_bold(user, photo_uri=None):
    """U-bold: magazine cover — centered bold hero + 2-col content."""
    u = user
    ph = f'<img class="hero-photo" src="{photo_uri}" alt="{u["name"]}">' if photo_uri else ""

    metrics = "".join(
        f'<div class="met"><div class="num">{m[0]}</div><div class="lbl">{m[1]}</div></div>'
        for m in u.get("metrics", [])
    )

    left = ""
    for exp in u["experience"]:
        bullets = "".join(f"<p>{b}</p>" for b in exp["bullets"])
        left += f'<div class="bold-card"><div class="hd"><b>{exp["company"]}</b><span>{exp["date"]}</span></div><div class="role">{exp["role"]}</div><p class="summary">{exp["summary"]}</p>{bullets}</div>'

    for proj in u.get("projects", []):
        bullets = "".join(f"<p>{b}</p>" for b in proj["bullets"])
        left += f'<div class="bold-card"><div class="hd"><b>{proj["name"]}</b><span>{proj["date"]}</span></div><div class="role">{proj["role"]}</div><p class="summary">{proj["summary"]}</p>{bullets}</div>'

    right = ""
    for e in u["education"]:
        right += f'<div class="bold-card"><div class="hd"><b>{e["school"]}</b><span>{e["date"]}</span></div><p>{e["degree"]}</p></div>'
    for l in u["languages"]:
        right += f'<div class="bold-card"><p>{l[0]} — {l[1]}</p></div>'
    for c in u.get("certs", []):
        right += f'<div class="bold-card"><p>{c}</p></div>'

    chips = "".join(f'<span class="chip">{s}</span>' for s in u["skills"])

    return f'''<div class="page">
  <div class="bold-hero">
    {ph}
    <h1>{u['name']}</h1>
    <div class="tagline">{u['title']}</div>
    <div class="tagline" style="font-size:8pt;opacity:0.6;margin-bottom:18px;">{u['email']} | {u['phone']} | {u['city']}</div>
    <div class="metrics-row">{metrics}</div>
  </div>
  <div class="bold-body">
    <div class="bold-col"><h2>Experience</h2>{left}</div>
    <div class="bold-col"><h2>Background</h2>{right}</div>
  </div>
  <div class="bold-footer">{chips}</div>
</div>'''


def body_masonry(user, photo_uri=None):
    """V-masonry: masonry card collage."""
    u = user
    ph = f'<img class="hero-photo" src="{photo_uri}" alt="{u["name"]}">' if photo_uri else ""

    # Experience as masonry cards — first one big, rest varied
    cards = []
    widths = ["w3", "w2", "w3", "w2", "w3", "w2"]
    for i, exp in enumerate(u["experience"]):
        w = widths[i % len(widths)]
        bullets = "".join(f"<p>{b}</p>" for b in exp["bullets"][:2])
        cards.append(f'<div class="mason-card {w}"><h3>{exp["company"]}</h3><p>{exp["role"]} · {exp["date"]}</p><p class="summary">{exp["summary"]}</p>{bullets}</div>')

    # Skills as accent cards
    skill_chunks = [u["skills"][i:i+4] for i in range(0, min(12, len(u["skills"])), 4)]
    for i, chunk in enumerate(skill_chunks):
        w = "w2" if i % 2 == 0 else "w3"
        tags = "".join(f'<span class="mason-chip">{s}</span>' for s in chunk)
        cards.append(f'<div class="mason-card {w} accent"><h3>{"Core Skills" if i==0 else "More Skills"}</h3><div class="mason-tags">{tags}</div></div>')

    # Education card
    edu_lines = "<br>".join(f'{e["school"]} — {e["degree"]} ({e["date"]})' for e in u["education"])
    cards.append(f'<div class="mason-card w2"><h3>Education</h3><p>{edu_lines}</p></div>')

    return f'''<div class="page">
  <div class="mason-hero">
    <div>{ph}<h1>{u['name']}</h1></div>
    <div class="sub">{u['title']}<br>{u['email']} | {u['phone']}</div>
  </div>
  <div class="mason-grid">{"".join(cards)}</div>
</div>'''


def body_split(user, photo_uri=None):
    """W-split: left sidebar + right content."""
    u = user
    ph = f'<img class="hero-photo" src="{photo_uri}" alt="{u["name"]}">' if photo_uri else ""

    # Left sidebar
    skill_dots = "".join(f'<span class="skill-dot">{s}</span>' for s in u["skills"])
    edu_lines = "<br>".join(f'{e["school"]}<br>{e["degree"]}<br>{e["date"]}' for e in u["education"])
    cert_lines = "<br>".join(u.get("certs", []))
    lang_lines = "<br>".join(f'{l[0]}: {l[1]}' for l in u["languages"])

    # Right: experience items
    items = ""
    for exp in u["experience"]:
        bullets = "".join(f"<p>{b}</p>" for b in exp["bullets"])
        items += f'<div class="split-item"><div class="head"><b>{exp["company"]}</b><span>{exp["date"]}</span></div><div class="sub">{exp["role"]}</div><p class="summary">{exp["summary"]}</p>{bullets}</div>'

    return f'''<div class="page">
  <div class="split-wrap">
    <div class="split-left">
      <div class="avatar-circle">{u["name"][0]}</div>
      <h1>{u['name']}</h1>
      <div class="role">{u['title']}</div>
      <div class="info-block"><h4>Contact</h4><p>{u['email']}<br>{u['phone']}<br>{u['city']}</p></div>
      <div class="info-block"><h4>Education</h4><p>{edu_lines}</p></div>
      <div class="info-block"><h4>Languages</h4><p>{lang_lines}</p></div>
    </div>
    <div class="split-right">
      <h2>Experience</h2>
      {items}
    </div>
  </div>
</div>'''


def body_metro(user, photo_uri=None):
    """X-metro: bold tile grid with rich content."""
    u = user
    ph = f'<img class="hero-photo" src="{photo_uri}" alt="{u["name"]}">' if photo_uri else ""

    tiles = []

    # BIG accent tile: first experience — most prominent
    e0 = u["experience"][0]
    bullets0 = "".join(f"<p>{b}</p>" for b in e0["bullets"][:3])
    tiles.append(f'<div class="metro-tile big accent"><div class="tile-label">Current Role</div><h3>{e0["company"]}</h3><p>{e0["role"]} · {e0["date"]}</p><p style="font-style:italic;opacity:0.85;">{e0["summary"]}</p><div class="bullets">{bullets0}</div></div>')

    # TALL dark tile: Skills
    skill_tags = "".join(f'<span class="metro-tag">{s}</span>' for s in u["skills"])
    tiles.append(f'<div class="metro-tile tall dark"><div class="tile-label">Core Skills</div><h3>Tech Stack</h3><div class="metro-tags">{skill_tags}</div></div>')

    # WIDE tile: second experience
    e1 = u["experience"][1]
    bullets1 = "".join(f"<p>{b}</p>" for b in e1["bullets"][:2])
    tiles.append(f'<div class="metro-tile wide"><div class="tile-label">Previous</div><h3>{e1["company"]}</h3><p>{e1["role"]} · {e1["date"]}</p><p style="font-style:italic;">{e1["summary"]}</p><div class="bullets">{bullets1}</div></div>')

    # WIDE tile: third + fourth experience stacked
    exp34 = ""
    for exp in u["experience"][2:4]:
        exp34 += f'<p><b>{exp["company"]}</b> — {exp["role"]}<br><span style="font-size:6.5pt;opacity:0.6;">{exp["date"]}</span></p>'
    tiles.append(f'<div class="metro-tile wide"><div class="tile-label">Earlier Roles</div><h3>Career Path</h3>{exp34}</div>')

    # WIDE tile: Education + Certs + Languages
    edu = "<br>".join(f'{e["school"]} — {e["degree"]} ({e["date"]})' for e in u["education"])
    certs = " · ".join(u.get("certs", [])[:2])
    langs = " · ".join(f'{l[0]} ({l[1]})' for l in u["languages"])
    tiles.append(f'<div class="metro-tile wide"><div class="tile-label">Background</div><h3>Education & More</h3><p>{edu}</p><p style="margin-top:6px;"><b>Certs:</b> {certs}</p><p><b>Languages:</b> {langs}</p></div>')

    return f'''<div class="page">
  <div class="metro-hero">
    <div class="left">{ph}<h1>{u['name']}</h1><div class="sub">{u['title']}</div></div>
    <div class="right">{u['email']}<br>{u['phone']}<br>{u['city']}</div>
  </div>
  <div class="metro-grid">{"".join(tiles)}</div>
</div>'''


def body_table(user, photo_uri=None):
    """Y-table: clean tabular layout."""
    u = user
    ph = f'<img class="hero-photo" src="{photo_uri}" alt="{u["name"]}">' if photo_uri else ""

    # Experience table rows
    exp_rows = ""
    for exp in u["experience"]:
        bullets = "<br>".join(f"· {b}" for b in exp["bullets"])
        exp_rows += f'<tr><td class="date">{exp["date"]}</td><td><div class="company">{exp["company"]}</div><div class="role">{exp["role"]}</div><div class="summary">{exp["summary"]}</div><div style="font-size:7.5pt;">{bullets}</div></td></tr>'

    # Skills tag row
    tags_html = "".join(f'<span class="tbl-tag">{s}</span>' for s in u["skills"])

    # Education rows
    edu_rows = ""
    for e in u["education"]:
        edu_rows += f'<tr><td class="date">{e["date"]}</td><td><div class="company">{e["school"]}</div><div class="role">{e["degree"]}</div></td></tr>'

    # Certs + languages
    extra_rows = ""
    for c in u.get("certs", []):
        extra_rows += f'<tr><td></td><td><div class="role">{c}</div></td></tr>'
    for l in u["languages"]:
        extra_rows += f'<tr><td></td><td><div class="role">{l[0]} — {l[1]}</div></td></tr>'

    return f'''<div class="page">
  <div class="tbl-header">
    <div>{ph}<h1>{u['name']}</h1></div>
    <div class="meta">{u['title']}<br>{u['email']} | {u['phone']} | {u['city']}</div>
  </div>
  <div class="tbl-section">
    <h2>Experience</h2>
    <table class="tbl-table"><tbody>{exp_rows}</tbody></table>
  </div>
  <div class="tbl-section">
    <h2>Skills</h2>
    <div class="tbl-tags">{tags_html}</div>
  </div>
  <div class="tbl-section">
    <h2>Education & More</h2>
    <table class="tbl-table"><tbody>{edu_rows}{extra_rows}</tbody></table>
  </div>
</div>'''


def body_bars(user, photo_uri=None):
    """Z-bars: skill proficiency bars + experience."""
    u = user
    ph = f'<img class="hero-photo" src="{photo_uri}" alt="{u["name"]}">' if photo_uri else ""

    # Skill bars — generate fake proficiency levels
    import hashlib
    levels = {"Expert": 95, "Advanced": 80, "Proficient": 65, "Skilled": 50}
    skill_bars = ""
    for s in u["skills"]:
        h = int(hashlib.md5(s.encode()).hexdigest()[:2], 16)
        pct = 55 + (h % 41)
        skill_bars += f'<div class="bars-skill-row"><div class="label">{s}</div><div class="bar-track"><div class="bar-fill" style="width:{pct}%;"></div></div></div>'

    # Left: Experience
    left = ""
    for exp in u["experience"]:
        bullets = "".join(f"<p>{b}</p>" for b in exp["bullets"])
        left += f'<div class="bars-item"><div class="hd"><b>{exp["company"]}</b><span>{exp["date"]}</span></div><div class="role">{exp["role"]}</div><p class="summary">{exp["summary"]}</p>{bullets}</div>'

    # Right: Skill bars + Education
    right = skill_bars
    edu_lines = "<br>".join(f'{e["school"]} — {e["degree"]} ({e["date"]})' for e in u["education"])
    cert_lines = "<br>".join(u.get("certs", []))
    lang_lines = "<br>".join(f'{l[0]}: {l[1]}' for l in u["languages"])
    right += f'<div class="bars-item" style="margin-top:14px;"><div class="hd"><b>Education</b></div><p>{edu_lines}</p></div>'
    right += f'<div class="bars-item"><div class="hd"><b>Certs & Languages</b></div><p>{cert_lines}</p><p>{lang_lines}</p></div>'

    chips = "".join(f'<span class="chip">{s}</span>' for s in u["skills"])

    return f'''<div class="page">
  <div class="bars-hero">
    <div class="left">{ph}<h1>{u['name']}</h1><div class="sub">{u['title']}</div></div>
    <div class="right">{u['email']}<br>{u['phone']}<br>{u['city']}</div>
  </div>
  <div class="bars-body">
    <div class="bars-col"><h2>Experience</h2>{left}</div>
    <div class="bars-col"><h2>Proficiency</h2>{right}</div>
  </div>
  <div class="bars-sidebar">{chips}</div>
</div>'''


def body_blocks(user, photo_uri=None):
    """AA-blocks: full-width stacked sections."""
    u = user
    ph = f'<img class="hero-photo" src="{photo_uri}" alt="{u["name"]}">' if photo_uri else ""

    # Experience section
    exp_cards = ""
    for exp in u["experience"]:
        bullets = "".join(f"<p>{b}</p>" for b in exp["bullets"])
        exp_cards += f'<div class="block-card"><div class="date-col">{exp["date"]}</div><div class="content-col"><b>{exp["company"]}</b><div class="role">{exp["role"]}</div><p class="summary">{exp["summary"]}</p>{bullets}</div></div>'

    # Projects section
    proj_cards = ""
    for proj in u.get("projects", []):
        bullets = "".join(f"<p>{b}</p>" for b in proj["bullets"])
        proj_cards += f'<div class="block-card"><div class="date-col">{proj["date"]}</div><div class="content-col"><b>{proj["name"]}</b><div class="role">{proj["role"]}</div><p class="summary">{proj["summary"]}</p>{bullets}</div></div>'

    # Education section
    edu_items = ""
    for e in u["education"]:
        edu_items += f'<div class="block-card"><div class="date-col">{e["date"]}</div><div class="content-col"><b>{e["school"]}</b><div class="role">{e["degree"]}</div></div></div>'
    for c in u.get("certs", []):
        edu_items += f'<div class="block-card"><div class="content-col"><b>{c}</b></div></div>'
    for l in u["languages"]:
        edu_items += f'<div class="block-card"><div class="content-col"><b>{l[0]}</b><div class="role">{l[1]}</div></div></div>'

    btags = "".join(f'<span class="btag">{s}</span>' for s in u["skills"])

    return f'''<div class="page">
  <div class="block-hero">
    {ph}
    <h1>{u['name']}</h1>
    <div class="tagline">{u['title']}</div>
    <div class="contact">{u['email']} | {u['phone']} | {u['city']}</div>
  </div>
  <div class="block-section">
    <h2><span class="accent">Work</span> Experience</h2>
    {exp_cards}
  </div>
  {"".join(f'<div class="block-section alt"><h2><span class="accent">Project</span> Highlights</h2>{proj_cards}</div>' if proj_cards else '')}
  <div class="block-section{' alt' if not proj_cards else ''}">
    <h2><span class="accent">Education</span> & Background</h2>
    {edu_items}
  </div>
  <div class="block-tag-strip">{btags}</div>
</div>'''


BODY_GENERATORS = {
    "minimal": body_minimal,
    "classic": body_classic,
    "gallery": body_gallery,
    "matrix": body_matrix,
    "compare": body_compare,
    "stagger": body_stagger,
    "tabbed": body_tabbed,
    "visual": body_visual,
    "waterfall": body_waterfall,
    "bold": body_bold,
    "masonry": body_masonry,
    "split": body_split,
    "metro": body_metro,
    "table": body_table,
    "bars": body_bars,
    "blocks": body_blocks,
}
