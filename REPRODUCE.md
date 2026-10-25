# Reproduce

Everything runs from the repository root with Python 3.11 or later.

```
pip install -r requirements.txt
python3 -m playwright install chromium
```

## 1. From the files in this repository

The analysis outputs are included, so the story's numbers, the page, the slides and METHODOLOGY.md can be rebuilt directly. Each step overwrites its outputs; with unchanged inputs they come out the same.

```
python3 analysis_export.py
python3 analysis/story.py
python3 site/build_data.py
python3 site/build_site.py
python3 slides/fetch_photos.py
python3 slides/make_slides.py
python3 methods/build_methodology.py
```

- `analysis_export.py` copies the analysis outputs the page and slides read into `data/`.
- `analysis/story.py` writes `data/story.json`, every number the slides and the page use.
- `site/build_data.py` writes `data/site.json`; `site/build_site.py` writes `index.html`.
- `slides/fetch_photos.py` downloads any slide photo that is missing (all eight are included).
- `slides/make_slides.py` writes the slides to `slides/out/` and reports any text outside the centre 720 px, any labels that touch and any banned word.
- `methods/build_methodology.py` writes METHODOLOGY.md from `data/story.json`.

## 2. From the official downloads

Raw downloads are not in the repository. Each research thread in `analysis/<thread>/` lists every file it downloaded, with its link, in `manifest.json`, and describes its scripts and checks in `results.md`. To rebuild from the sources:

1. Download each thread's files into `analysis/<thread>/raw/` as listed in its `manifest.json`.
2. Run each thread's scripts in `analysis/<thread>/scripts/` (its `results.md` says what each one does): `results24` (2024 and 2020 results by riding and voting area), `history` (1928 to 2024), `polls`, `census` (2021 Census by riding), `geo` (boundaries, voting areas, dissemination blocks, water), `federal25` (the 2025 federal vote on provincial ridings), `live` (Elections BC's 2026 results files; the snapshot used is kept in `analysis/live/results_snapshot/`), `model` and `next`.
3. Run the joined analysis: `python3 analysis/core/full.py`, then `python3 analysis/core/meta/meta.py`. The checks are in `analysis/core/verify/`.
4. Rebuild the detailed map files: `python3 analysis/build_map_detail.py` (needs the geo thread's outputs and its Freshwater Atlas downloads).
5. Run the steps in section 1.

`site/build_data.py` rebuilds the place index for "Find your riding" (`data/places.json`) when Statistics Canada's 2021 geographic attribute file is in `analysis/geo/raw/statcan/`; otherwise it reuses the published index.

The Median Canadian. A curious Canadian explaining Canada through numbers, every week.
