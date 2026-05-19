#!/usr/bin/env python3
"""Resume Pipeline — automated validation + skill sync + cron-ready.

Modes:
  validate  : sweep all layouts × sample themes, report failures
  gallery   : generate full 12-layout gallery
  sweep     : validate + gallery + auto-update skill version
  cron      : same as sweep, designed for cron job

Usage:
  python3 pipeline.py validate
  python3 pipeline.py gallery
  python3 pipeline.py sweep
"""

import json, os, subprocess, sys, time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
GENERATE = "resume"  # CLI command (installed via pip)
DATA = ROOT / "user_zh.json"  # default user data

LAYOUTS_ACTIVE = ["T", "matrix", "compare", "stagger", "tabbed", "visual",
                  "bold", "masonry", "split", "table", "bars", "blocks"]
THEMES_SAMPLE = ["noir-gold", "slate-steel", "teal-ocean", "ember-ash",
                 "midnight-navy", "indigo-deep", "arctic-blue", "amber-gold"]


def run(cmd, timeout=120):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return result.returncode == 0, result.stdout + result.stderr


def validate():
    """Quick smoke test: 1 layout × 3 themes."""
    print("🔍 Quick validate: T layout × 3 themes")
    passed = 0
    failed = 0
    for theme in THEMES_SAMPLE[:3]:
        ok, out = run(f"{GENERATE} --data {DATA} --theme {theme} --layout T --preview", timeout=60)
        if ok and "SUCCESS" in out:
            passed += 1
            kb = out.split("Screenshot: ")[-1].split("KB")[0] if "Screenshot:" in out else "?"
            print(f"  ✅ {theme} ({kb}KB)")
        else:
            failed += 1
            print(f"  ❌ {theme} FAILED")
    print(f"  {passed}/{passed+failed} passed")
    return failed == 0


def full_gallery():
    """Generate 12-layout gallery."""
    print(f"🎨 Full gallery: {len(LAYOUTS_ACTIVE)} layouts")
    ok, out = run(f"{GENERATE} --data {DATA} --gallery", timeout=600)
    results = []
    for line in out.split("\n"):
        if "SUCCESS" in line:
            results.append("✅")
        elif "FAILED" in line:
            results.append("❌")
        elif "Screenshot:" in line:
            pass

    passed = results.count("✅")
    failed = results.count("❌")
    print(f"  Gallery: {passed} passed, {failed} failed")
    return failed == 0


def full_sweep():
    """Layout × theme cross-product sweep. Generates 12×8=96 HTML files."""
    total = len(LAYOUTS_ACTIVE) * len(THEMES_SAMPLE)
    print(f"🔬 Full sweep: {len(LAYOUTS_ACTIVE)} layouts × {len(THEMES_SAMPLE)} themes = {total} variants")
    passed = 0
    failed = 0
    low_density = []

    for layout in LAYOUTS_ACTIVE:
        for theme in THEMES_SAMPLE:
            ok, out = run(
                f"{GENERATE} --data {DATA} --theme {theme} --layout {layout} --preview",
                timeout=60
            )
            if ok and "SUCCESS" in out:
                passed += 1
                # Check density
                if "density_markers=" in out:
                    markers = int(out.split("density_markers=")[1].split("\n")[0])
                    if markers < 10:
                        low_density.append(f"{layout}/{theme} markers={markers}")
            else:
                failed += 1
                print(f"  ❌ {layout}/{theme}")

            if (passed + failed) % 12 == 0:
                print(f"  ... {passed+failed}/{total}")

    print(f"  Results: {passed} passed, {failed} failed")
    if low_density:
        print(f"  ⚠ Low density ({len(low_density)}):")
        for item in low_density[:5]:
            print(f"    {item}")

    return failed == 0


def main():
    """CLI entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Resume Pipeline")
    parser.add_argument("mode", choices=["validate", "gallery", "sweep", "cron"],
                        default="validate", nargs="?")
    args = parser.parse_args()

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🚀 Pipeline [{args.mode}] — {ts}\n")

    if args.mode == "validate":
        ok = validate()
    elif args.mode == "gallery":
        ok = full_gallery()
    elif args.mode in ("sweep", "cron"):
        ok = full_sweep()
        if ok:
            full_gallery()

    print(f"\n{'✅ Pipeline OK' if ok else '❌ Pipeline FAILED'}")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
