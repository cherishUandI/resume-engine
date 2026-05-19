# Resume Engine

> 12 layouts × 20 themes × 9 fonts × 8 decorations × 7 shapes = 920,000+ unique resume combinations.  
> One command → printable HTML + PDF.

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 🚀 Quick Start（三步上手）

```bash
# 1. 克隆并安装
git clone https://github.com/cherishUandI/resume-engine.git
cd resume-engine
pip install -e .

# 2. 填写你的信息（用任何文本编辑器）
cp src/resume_engine/user_zh.json my_resume.json
nano my_resume.json   # 改名字、经历、技能等

# 3. 生成 PDF
resume --data my_resume.json --theme noir-gold --layout T --pdf
```

浏览器打开 `src/resume_engine/output/` 目录即可看到 HTML 和 PDF。

---

## ✨ 为什么用 Resume Engine？

大多数简历工具给你 5-10 个固定模板。Resume Engine 是一个**参数化设计系统**——每个视觉元素都可以独立调整：

| 维度 | 选项数量 | 示例 |
|-----------|---------|----------|
| **布局架构** | 12 种 | T 型模块化、技能矩阵、杂志封面、左右分屏、进度条… |
| **配色主题** | 20 套 | Noir Gold、Midnight Navy、Teal Ocean、Amber Gold… |
| **字体** | 9 套 | 无衬线、衬线、等宽、黑体、手写、窄粗体… |
| **装饰元素** | 8 种 | 侧边条、切角、几何图形、渐变底、网格线、发光球… |
| **Hero 形状** | 7 种 | 右斜切、V 型切、波浪、深波浪… |
| **卡片切角** | 3 种 | 直角、微圆、曲面 |
| **信息密度** | 4 档 | 舒朗、标准、紧凑、极致 |
| **圆角** | 5 级 | 0px → 8px |

所有组合在输出前经过 **5 级自动化门禁** 验证。

---

## 📖 完整用法

### 单份生成

```bash
resume --data my_resume.json \
       --theme noir-gold \
       --font sans \
       --deco none \
       --shape right-slant \
       --layout T \
       --lang zh \
       --pdf
```

### 浏览全部布局

```bash
resume --data my_resume.json --gallery   # 生成 12 种布局对比
```

### 批量验证流水线

```bash
resume-pipeline validate   # 快速检查：T 布局 × 3 主题
resume-pipeline sweep      # 全量：12 布局 × 8 主题 = 96 变体
```

### 全部参数

```
--data PATH         用户数据 JSON
--theme NAME        主题：noir-gold, slate-steel, teal-ocean, midnight-navy…
--font NAME         字体：sans, serif, mono, heiti, round, handwriting…
--deco NAME         装饰：none, bar, corner, geo, gradient-bg, grid-lines, glow-orb, dividers
--shape NAME        Hero 形状：right-slant, left-slant, v-cut, gentle-wave, asymm-wave, sharp-wave, deep-wave
--card-style STYLE  卡片风格：sharp, soft, curve
--density LEVEL     密度：breathing, standard, compact, minimal
--radius R0-R4      圆角：r0=0px, r1=2px, r2=4px, r3=6px, r4=8px
--layout NAME       布局：T, matrix, compare, stagger, tabbed, visual, bold, masonry, split, table, bars, blocks
--pdf               生成 PDF
--preview           仅截图（更快）
--lang zh|en        语言
--photo PATH        头像照片
--gallery           生成全部 12 种布局
```

### 数据文件格式

`user_zh.json` 示例（删改即可）：

```json
{
  "name": "张三",
  "title": "高级软件工程师",
  "email": "zhangsan@example.com",
  "phone": "138-0000-0000",
  "city": "北京",
  "metrics": [["8", "年经验"], ["500万", "峰值用户"]],
  "skills": ["Python", "Go", "React", "Docker", "Kubernetes"],
  "experience": [
    {
      "company": "某互联网公司",
      "role": "资深工程师",
      "date": "2023.06 — 至今",
      "summary": "一句话描述",
      "bullets": ["要点1", "要点2", "要点3"],
      "dark": false
    }
  ],
  "education": [{"school": "某大学", "degree": "本科", "date": "2012 — 2016"}],
  "languages": [["中文", "母语"], ["英语", "CET-6"]],
  "certs": ["认证1", "认证2"],
  "lang": "zh"
}
```

---

## 📁 项目结构

```
resume-engine/
├── pyproject.toml
├── README.md
└── src/resume_engine/
    ├── cli.py              # CLI 入口
    ├── pipeline.py          # 批量验证流水线
    ├── layouts.py           # 12 种布局生成器
    ├── user_zh.json         # 中文示例数据
    ├── user_en.json         # 英文示例数据
    └── modules/             # CSS + 设计配置
        ├── base.css
        ├── hero.css
        ├── cards.css
        ├── icons.css
        ├── print.css
        ├── themes.json      # 20 套配色
        ├── fonts.json       # 9 套字体
        ├── decos.json       # 8 种装饰
        ├── shapes.json      # 7 种形状
        └── ...
```

---

## 🔧 开发

```bash
git clone https://github.com/cherishUandI/resume-engine.git
cd resume-engine
pip install -e .
```

零外部依赖——纯 Python 3.10+ 标准库。

---

## 📄 License

MIT

---

*你的简历，应该看起来像你很重视它。*
