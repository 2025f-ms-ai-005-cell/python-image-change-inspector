"""Local, aligned-image difference inspection; never semantic detection."""
import argparse
import json
import sys
import tempfile
import warnings
from pathlib import Path
from PIL import Image, ImageChops, ImageOps, ImageStat

MAX_PIXELS = 4_000_000

def load(path):
    with warnings.catch_warnings():
        warnings.simplefilter('error', Image.DecompressionBombWarning)
        with Image.open(path) as image:
            if image.width * image.height > MAX_PIXELS:
                raise ValueError('Image exceeds four million pixels')
            if getattr(image, 'n_frames', 1) != 1:
                raise ValueError('Only single-frame images supported')
            if 'A' in image.getbands() or 'transparency' in image.info:
                raise ValueError('Transparent images unsupported; flatten explicitly first')
            return ImageOps.exif_transpose(image).convert('RGB')

def compare(before, after, threshold=25):
    if not 0 <= threshold <= 255:
        raise ValueError('Threshold must be between 0 and 255')
    if before.size != after.size:
        raise ValueError('Images must have identical dimensions; no automatic alignment')
    delta = ImageChops.difference(before.convert('RGB'), after.convert('RGB'))
    red, green, blue = delta.split()
    peak = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    mask = peak.point(lambda value: 255 if value > threshold else 0)
    count = mask.histogram()[255]
    total = before.width * before.height
    metrics = {'threshold': threshold, 'width': before.width, 'height': before.height,
               'changed_pixels': count, 'total_pixels': total,
               'changed_fraction': count / total,
               'mean_absolute_rgb_difference': sum(ImageStat.Stat(delta).mean) / 3,
               'changed_bbox_exclusive': mask.getbbox()}
    overlay = Image.composite(Image.new('RGB', after.size, '#ff4c70'), after.convert('RGB'), mask)
    return metrics, delta, mask, overlay

def export(before_path, after_path, output, threshold=25):
    output = Path(output).resolve()
    if output.exists():
        raise ValueError('Output already exists; choose a new directory')
    before, after = load(before_path), load(after_path)
    metrics, delta, mask, overlay = compare(before, after, threshold)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Stage all artifacts before exposing a finished report; inputs never overwritten.
    with tempfile.TemporaryDirectory(dir=output.parent) as staging:
        stage = Path(staging) / 'report'
        stage.mkdir()
        for name, image in [('before', before), ('after', after), ('difference', delta),
                            ('mask', mask), ('overlay', overlay)]:
            image.save(stage / (name + '.png'))
        (stage / 'metrics.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
        cards = ''.join(f'<figure><img src="{name}.png" alt="{name}"><figcaption>{name.title()}</figcaption></figure>'
                        for name in ['before', 'after', 'difference', 'mask', 'overlay'])
        html = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Image Change Inspector</title>
<style>body{background:#0b1324;color:#e5eef9;font:18px system-ui;margin:0;padding:48px}h1{font-size:42px;color:#63e2c6}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:22px}figure{margin:0;padding:18px;background:#19283e;border-radius:16px}img{width:100%;image-rendering:auto}figcaption{padding-top:12px}p{line-height:1.7}a{color:#63e2c6}</style>
<h1>Image Change Inspector</h1><p>Aligned pixels. Explicit thresholds. Reproducible evidence.</p>'''
        html += f'<p>Changed pixels: {metrics["changed_pixels"]} / {metrics["total_pixels"]} · Threshold: {threshold} · Changed area: {metrics["changed_fraction"]:.2%}</p>'
        html += '<div class="grid">' + cards + '</div><p>Pixel differences are not object detection. Camera movement, shadows and exposure changes can dominate this result. Bounding box coordinates use exclusive right/bottom bounds.</p><a href="metrics.json">Download metrics JSON</a></html>'
        (stage / 'index.html').write_text(html, encoding='utf-8')
        stage.rename(output)
    return metrics

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before', type=Path)
    parser.add_argument('after', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--threshold', type=int, default=25)
    args = parser.parse_args()
    try:
        print(json.dumps(export(args.before, args.after, args.output, args.threshold), indent=2))
    except (OSError, ValueError, Image.DecompressionBombWarning, Image.DecompressionBombError):
        print('Inspection failed: check image format, dimensions, threshold and output permissions.', file=sys.stderr)
        return 2
    return 0

if __name__ == '__main__':
    sys.exit(main())
