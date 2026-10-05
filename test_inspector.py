import tempfile
import unittest
from pathlib import Path
from PIL import Image
from inspect_change import compare, export, load

class InspectorTests(unittest.TestCase):
    def test_identical(self):
        a = Image.new('RGB', (4, 4), 'white')
        metrics, *_ = compare(a, a)
        self.assertEqual(metrics['changed_pixels'], 0)
        self.assertIsNone(metrics['changed_bbox_exclusive'])

    def test_boundary(self):
        a = Image.new('RGB', (2, 2))
        b = a.copy()
        b.putpixel((1, 0), (25, 0, 0))
        self.assertEqual(compare(a, b, 25)[0]['changed_pixels'], 0)
        metrics, *_ = compare(a, b, 24)
        self.assertEqual(metrics['changed_pixels'], 1)
        self.assertEqual(metrics['changed_bbox_exclusive'], (1, 0, 2, 1))
        self.assertEqual(metrics['changed_fraction'], .25)

    def test_dimensions(self):
        with self.assertRaises(ValueError):
            compare(Image.new('RGB', (2, 2)), Image.new('RGB', (3, 2)))

    def test_threshold(self):
        for value in [-1, 256]:
            with self.assertRaises(ValueError):
                compare(Image.new('RGB', (2, 2)), Image.new('RGB', (2, 2)), value)

    def test_export_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source.png'
            Image.new('RGB', (8, 8), 'white').save(source)
            original = source.read_bytes()
            export(source, source, root / 'report')
            self.assertTrue((root / 'report/index.html').exists())
            self.assertEqual(source.read_bytes(), original)
            with self.assertRaises(ValueError):
                export(source, source, root / 'report')

    def test_transparency(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'alpha.png'
            Image.new('RGBA', (2, 2)).save(path)
            with self.assertRaises(ValueError):
                load(path)

if __name__ == '__main__':
    unittest.main()
