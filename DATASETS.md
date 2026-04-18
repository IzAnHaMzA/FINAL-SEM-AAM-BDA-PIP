# Public Dataset Downloader

This project includes a resumable downloader for a few large public datasets that are commonly used for language-model training, plus a PowerPoint generator and a small website for building exportable presentation decks.

Current dataset keys:

- `wikipedia_en_20220301`
- `open_web_math`
- `codeparrot_clean`
- `github_code`

Install:

```bash
pip install -r requirements-datasets.txt
```

Run one dataset:

```bash
python download_public_datasets.py --datasets wikipedia_en_20220301
```

Run multiple datasets:

```bash
python download_public_datasets.py --datasets wikipedia_en_20220301 open_web_math codeparrot_clean
```

Generate a presentation:

```bash
python generate_dataset_presentation.py
```

Write the PowerPoint somewhere else:

```bash
python generate_dataset_presentation.py --pptx outputs/dataset_deck.pptx
```

Pick a specific template:

```bash
python generate_dataset_presentation.py --template midnight-grid
```

Generate from custom slide text:

```bash
python generate_dataset_presentation.py --template studio-ink --title "Board Update" --slides-text "Intro\nQ2 Review\n- Wins\n- Risks\n---\nNext Steps\nPlan\n- Hire\n- Ship"
```

Run the website:

```bash
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

Website features:

- 20 visual templates
- custom slide text input
- dataset-manifest mode using `datasets/download_manifest.json`
- direct `.pptx` export

Notes:

- Downloads are large and may take a long time.
- Hugging Face downloads are resumable.
- Review licenses and dataset cards before training on any corpus.
- The presentation generator reads `datasets/download_manifest.json` when available and also inspects the local dataset folders for file counts and disk usage.
- Website exports are written to an `exports/` folder before download.
