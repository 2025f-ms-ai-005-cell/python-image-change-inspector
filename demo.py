from pathlib import Path
from PIL import Image, ImageDraw
from inspect_change import export

def main():
    root = Path('demo-output')
    root.mkdir(exist_ok=False)
    before = Image.new('RGB', (640, 420), '#edf4f8')
    draw = ImageDraw.Draw(before)
    for x in range(0, 640, 40):
        draw.line((x, 0, x, 420), fill='#d1dee8')
    for y in range(0, 420, 40):
        draw.line((0, y, 640, y), fill='#d1dee8')
    draw.rectangle((80, 100, 219, 239), fill='#164459')
    after = before.copy()
    ImageDraw.Draw(after).rectangle((340, 160, 459, 279), fill='#198879')
    before.save(root / 'before.png')
    after.save(root / 'after.png')
    export(root / 'before.png', root / 'after.png', root / 'report')

if __name__ == '__main__':
    main()
