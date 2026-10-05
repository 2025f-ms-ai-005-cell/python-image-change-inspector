# Verification — October 5, 2026

- Six `unittest` tests passed locally, zero failures.
- `python demo.py` completed and generated five PNG outputs, offline HTML and JSON.
- Deterministic fixture: 640 × 420; added 120 × 120 square. Observed 14,400 / 268,800 changed pixels (5.357142857%), threshold 25; bounding box [340,160,460,280]. These are synthetic fixture results only.
- Published source/demo: https://github.com/2025f-ms-ai-005-cell/python-image-change-inspector/commit/6b553bcb8af54e02acb8d1e4d3867ccf69ed0833 .
- Local report rendered in the browser October 5: all five images loaded; displayed 14,400 changed pixels and 5.36% rounded changed area. `preview.jpg` is an actual report screenshot, not a mockup.
- Installation in a clean virtual environment and adversarial CLI testing remain unchecked.
- Current pipeline rejects transparent/multi-frame/oversized images; no alignment or semantic recognition. Further adversarial format, output concurrency and platform testing remain.
