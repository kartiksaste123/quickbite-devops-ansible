"""Turns the saved terminal outputs in evidence/*.txt into terminal style
PNG screenshots in screenshots/. Long outputs are split into parts.
Colours follow the normal ansible colours (ok=green, changed=yellow, failed=red)."""
import glob
import os
import re
import textwrap

from PIL import Image, ImageDraw, ImageFont

FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 15)
FONT_B = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 15)
TITLE_FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)

PROMPT = "kartik@devops-lab:~/devops-ansible-assignment$"
WRAP, PAGE = 118, 58
BG, FG = (24, 24, 27), (212, 212, 212)
GREEN, YELLOW, RED, CYAN, BLUE = (78, 201, 112), (229, 192, 80), (240, 85, 85), (90, 190, 210), (110, 160, 240)


def colour(line):
    s = line.lstrip()
    if s.startswith(("ok:", "SUCCESS")) or " | SUCCESS" in line or "PASSED" in line or s.startswith("Passed:"):
        return GREEN
    if s.startswith("changed:") or " | CHANGED" in line:
        return YELLOW
    if s.startswith(("fatal:", "failed:", "FAILED", "[ERROR]")):
        return RED
    if s.startswith("skipping:"):
        return CYAN
    return FG


def recap_colour(line):
    m = re.match(r"^(\S+)\s+: ok=\d+\s+changed=(\d+)\s+unreachable=(\d+)\s+failed=(\d+)", line)
    if not m:
        return None
    if int(m.group(3)) or int(m.group(4)):
        return RED
    return YELLOW if int(m.group(2)) else GREEN


def draw_page(lines, title, out):
    cw = FONT.getbbox("M")[2]
    lh, pad, bar = 21, 18, 32
    width = max(1000, WRAP * cw + 2 * pad)
    height = bar + 2 * pad + lh * len(lines)
    img = Image.new("RGB", (width, height), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, width, bar], fill=(48, 48, 52))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([12 + i * 20, 10, 24 + i * 20, 22], fill=c)
    d.text(((width - d.textlength(title, font=TITLE_FONT)) / 2, 8), title, fill=(190, 190, 195), font=TITLE_FONT)
    y = bar + pad
    for line in lines:
        if line.startswith(PROMPT):
            d.text((pad, y), PROMPT, fill=GREEN, font=FONT_B)
            d.text((pad + (len(PROMPT) + 1) * cw, y), line[len(PROMPT) + 1:], fill=FG, font=FONT)
        elif recap_colour(line):
            host = line.split()[0]
            d.text((pad, y), host, fill=recap_colour(line), font=FONT)
            d.text((pad + len(host) * cw, y), line[len(host):], fill=FG, font=FONT)
        else:
            d.text((pad, y), line, fill=colour(line), font=FONT)
        y += lh
    img.save(out, optimize=True)


def render(path):
    name = os.path.splitext(os.path.basename(path))[0]
    raw = [l.rstrip("\n").replace("\t", "    ") for l in open(path, encoding="utf-8")]
    while raw and not raw[-1].strip():
        raw.pop()
    lines = []
    for l in raw:
        lines += textwrap.wrap(l, WRAP, replace_whitespace=False, drop_whitespace=False) or [""]
    pages = [lines[i:i + PAGE] for i in range(0, len(lines), PAGE)]
    outs = []
    for n, page in enumerate(pages, 1):
        suffix = f"_part{n}" if len(pages) > 1 else ""
        out = f"screenshots/{name}{suffix}.png"
        title = "kartik@devops-lab: ~/devops-ansible-assignment"
        if len(pages) > 1:
            title += f"   ({n}/{len(pages)})"
        draw_page(page, title, out)
        outs.append(out)
    return outs


if __name__ == "__main__":
    os.makedirs("screenshots", exist_ok=True)
    for f in sorted(glob.glob("evidence/*.txt")):
        for o in render(f):
            print(o)
