# Resume Engine

> 12 layouts × 20 themes × 9 fonts × 8 decorations × 7 shapes = 920,000+ unique resume combinations.  
> One command → printable HTML + PDF.

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## ✨ Why Resume Engine?

Most resume tools give you 5–10 fixed templates. Resume Engine gives you a **parametric design system** — every element is a variable you can tweak:

| Dimension | Options | Examples |
|-----------|---------|----------|
| **Layout** | 12 architectures | T-modular, Skills Matrix, Magazine Cover, Split Screen, Progress Bars… |
| **Theme** | 20 color palettes | Noir Gold, Midnight Navy, Teal Ocean, Amber Gold… |
| **Font** | 9 families | Sans-serif, Serif, Mono, Heiti, Handwriting, Bold Condensed… |
| **Decoration** | 8 styles | Bar, Corner cut, Geometric, Gradient BG, Grid lines, Glow orb… |
| **Hero Shape** | 7 clip-paths | Right slant, V-cut, Gentle wave, Deep wave… |
| **Card Style** | 3 corners | Sharp, Soft, Curved |
| **Density** | 4 levels | Breathing, Standard, Compact, Minimal |
| **Border Radius** | 5 levels | 0px → 8px |

All combinations pass a **5-stage automated gate** before output.

---

## 🚀 Quick Start

```bash
# Install
pip install resume-engine

# Generate with demo data
resume --data $(python -c "import resume_engine; print(resume_engine.__path__[0])")/user_zh.json \
       --theme noir-gold --layout T --pdf

# Explore all 12 layouts
resume --gallery
```

### CLI Reference

```
resume [OPTIONS]

--data PATH          User data JSON file
--theme NAME         Theme (noir-gold, slate-steel, teal-ocean…)
--font NAME          Font (sans, serif, mono, heiti, round, handwriting…)
--deco NAME          Decoration (none, bar, corner, geo, gradient-bg…)
--shape NAME         Hero shape (right-slant, v-cut, gentle-wave…)
--card-style STYLE   Card corners (sharp, soft, curve)
--density LEVEL      Content density (breathing, standard, compact, minimal)
--radius R0-R4       Border radius (r0=0px … r4=8px)
--layout NAME        Layout (T, matrix, compare, stagger, tabbed…)
--pdf                Generate PDF output
--preview            Screenshot only (faster)
--lang zh|en         Language override
--gallery            Generate all 12 layout variants
```

### Pipeline (batch validation)

```bash
resume-pipeline validate   # Quick smoke test: T layout × 3 themes
resume-pipeline gallery     # 12-layout gallery
resume-pipeline sweep       # Full 12 layouts × 8 themes = 96 variants
```

---

## 📁 Project Structure

```
resume-engine/
├── pyproject.toml
├── README.md
└── src/resume_engine/
    ├── cli.py              # CLI entry point
    ├── pipeline.py          # Batch validation pipeline
    ├── layouts.py           # 12 layout body generators
    ├── user_zh.json         # Demo data (Chinese)
    ├── user_en.json         # Demo data (English)
    └── modules/             # CSS + design configs
        ├── base.css         # Page structure
        ├── hero.css         # Hero section
        ├── cards.css        # Card components
        ├── icons.css        # CSS-only SVG icons
        ├── print.css        # Print/PDF rules
        ├── themes.json      # 20 color palettes
        ├── fonts.json       # 9 font families
        ├── decos.json       # 8 decoration styles
        ├── shapes.json      # 7 hero clip-paths
        ├── card-styles.json # 3 card corner styles
        ├── densities.json   # 4 content densities
        └── radius.json      # 5 border radius levels
```

---

## 🔧 Development

```bash
git clone https://github.com/cherishUandl/resume-engine.git
cd resume-engine
pip install -e .
```

No external dependencies — pure Python 3.10+ standard library.

---

## 📄 License

MIT © [cherishUandl](https://github.com/cherishUandl)

---

*Built for people who want their resume to look like they mean it.*
