# Verification — October 5, 2026

- Six `unittest` tests passed locally, zero failures.
- `python demo.py` completed and generated five PNG outputs, offline HTML and JSON.
- Deterministic fixture: 640 × 420; added 120 × 120 square. Observed 14,400 / 268,800 changed pixels (5.357142857%), threshold 25; bounding box [340,160,460,280]. These are synthetic fixture results only.
- CLI/report browser rendering, installation in a clean virtual environment and publication remain unverified. No GitHub repository or commit is claimed.
- Current pipeline rejects transparent/multi-frame/oversized images; no alignment or semantic recognition. Further adversarial format, output concurrency and platform testing remain.
