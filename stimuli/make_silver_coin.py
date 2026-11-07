"""Makes the silver no-reward coin and measures the coin pair against the scene greys.

Decision and rationale: stimuli/COIN_PAIR.md.

    python stimuli/make_silver_coin.py            (from the repository root; needs numpy + Pillow)

What it does
  1. Source: rewards/coin_no_reward_light.png (an achromatic silver coin, same silhouette as the gold coin).
  2. Each pixel's luminance is remapped (in linear light) so that the silver coin has the SAME mean and
     the SAME standard deviation of luminance as the gold coin (rewards/coin_reward.png). Statistics are
     weighted by the pixels' alpha. Colour stays achromatic (R = G = B); the alpha channel is unchanged.
  3. Writes rewards/coin_no_reward_silver.png, copies it to online/stimuli/, and writes
     coin_pair_comparison.png (old vs new pair at several opacities, on the old and new box grey).
  4. Prints the luminance and the Weber contrast of each coin against the box at several opacities.

Luminance = Rec.709 relative luminance of sRGB values (no monitor calibration; real screens differ).
"""
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
GOLD = os.path.join(HERE, 'rewards', 'coin_reward.png')
BLACK = os.path.join(HERE, 'rewards', 'coin_no_reward.png')
SOURCE = os.path.join(HERE, 'rewards', 'coin_no_reward_light.png')
OUT = os.path.join(HERE, 'rewards', 'coin_no_reward_silver.png')
ONLINE_COPY = os.path.join(HERE, '..', 'online', 'stimuli', 'coin_no_reward_silver.png')
COMPARISON = os.path.join(HERE, 'coin_pair_comparison.png')
OLD_BOX, NEW_BOX = (169, 169, 169), (124, 124, 124)       # 'darkgray' (v1) and #7c7c7c (v2)
OPACITIES = [1.0, 0.5, 0.3, 0.2, 0.1]


def to_linear(v):
    v = np.asarray(v, float) / 255
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


def to_srgb(lin):
    lin = np.clip(lin, 0, 1)
    return np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055) * 255


def luminance(rgb):
    lin = to_linear(rgb)
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


def load(path):
    return np.asarray(Image.open(path).convert('RGBA')).astype(float)


def stats(img):
    """alpha-weighted mean and SD of luminance."""
    w = img[..., 3] / 255
    lum = luminance(img[..., :3])
    mean = (lum * w).sum() / w.sum()
    sd = np.sqrt((w * (lum - mean) ** 2).sum() / w.sum())
    return mean, sd


def make_silver():
    gold, src = load(GOLD), load(SOURCE)
    g_mean, g_sd = stats(gold)
    s_mean, s_sd = stats(src)
    lum = luminance(src[..., :3])
    target = (lum - s_mean) * (g_sd / s_sd) + g_mean          # same mean and SD as gold
    grey = to_srgb(target)
    out = src.copy()
    out[..., 0] = out[..., 1] = out[..., 2] = grey
    out = np.clip(np.round(out), 0, 255).astype(np.uint8)
    Image.fromarray(out, 'RGBA').save(OUT)
    os.makedirs(os.path.dirname(ONLINE_COPY), exist_ok=True)
    shutil.copyfile(OUT, ONLINE_COPY)
    return out


def contrast_report():
    rows = [('gold', GOLD), ('black (v1)', BLACK), ('silver (v2)', OUT)]
    for name, path in rows:
        m, sd = stats(load(path))
        print(f'{name:12s} mean luminance {m:.3f}  SD {sd:.3f}')
    for box_name, box in [('v1 box 169', OLD_BOX), ('v2 box 124', NEW_BOX)]:
        lbox = float(luminance(np.array([box], float))[0])
        print(f'\nWeber contrast against the {box_name} (box luminance {lbox:.3f}), mean over the coin:')
        for name, path in rows:
            img = load(path)
            a = img[..., 3:] / 255
            inside = a[..., 0] > 0.5
            cells = []
            for op in OPACITIES:
                comp = np.array(box, float) * (1 - a * op) + img[..., :3] * a * op   # blended as the renderers do
                cells.append(f'{op:.1f}: {(luminance(comp)[inside].mean() - lbox) / lbox:+.2f}')
            print(f'  {name:12s} ' + '   '.join(cells))


def comparison_image():
    cell, box, coin, left = 130, 104, 84, 230
    rows = [('v1: gold, box 169', GOLD, OLD_BOX), ('v1: black, box 169', BLACK, OLD_BOX),
            ('v2: gold, box 124', GOLD, NEW_BOX), ('v2: silver, box 124', OUT, NEW_BOX)]
    img = Image.new('RGB', (left + cell * len(OPACITIES), 40 + cell * len(rows)), 'black')
    draw = ImageDraw.Draw(img)
    for j, op in enumerate(OPACITIES):
        draw.text((left + j * cell + 38, 12), f'opacity {op}', fill='white')
    for i, (name, path, colour) in enumerate(rows):
        c = Image.open(path).convert('RGBA').resize((coin, coin), Image.LANCZOS)
        y = 40 + i * cell
        draw.text((10, y + cell // 2 - 8), name, fill='white')
        for j, op in enumerate(OPACITIES):
            tile = Image.new('RGBA', (box, box), colour + (255,))
            cc = c.copy()
            cc.putalpha(cc.split()[3].point(lambda v, op=op: int(v * op)))
            tile.alpha_composite(cc, ((box - coin) // 2, (box - coin) // 2))
            img.paste(tile.convert('RGB'), (left + j * cell + (cell - box) // 2, y + (cell - box) // 2))
    img.save(COMPARISON)


if __name__ == '__main__':
    make_silver()
    contrast_report()
    comparison_image()
    print(f'\nwrote {os.path.relpath(OUT)}, {os.path.relpath(ONLINE_COPY)}, {os.path.relpath(COMPARISON)}')
