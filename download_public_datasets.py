import argparse
import json
from pathlib import Path


DATASETS = {
    "wikipedia_en_20220301": {
        "repo_id": "wikipedia",
        "kind": "snapshot",
        "allow_patterns": ["data/20220301.en/*"],
        "notes": "English Wikipedia parquet snapshot from the legacy mirrored dataset repo.",
    },
    "wikipedia_en_20231101": {
        "repo_id": "wikimedia/wikipedia",
        "kind": "snapshot",
        "allow_patterns": ["20231101.en/*"],
        "notes": "Current English Wikipedia parquet snapshot from the Wikimedia dataset repo.",
    },
    "open_web_math": {
        "repo_id": "open-web-math/open-web-math",
        "kind": "snapshot",
        "notes": "Large public math-heavy pretraining corpus.",
    },
    "codeparrot_clean": {
        "repo_id": "codeparrot/codeparrot-clean",
        "kind": "snapshot",
        "notes": "Deduplicated public Python code corpus.",
    },
    "github_code": {
        "repo_id": "codeparrot/github-code",
        "kind": "snapshot",
        "notes": "Multilanguage GitHub code dataset.",
    },
}


def download_snapshot(repo_id: str, target_dir: Path, allow_patterns: list[str] | None = None) -> None:
    from huggingface_hub import snapshot_download

    snapshot_download(
        repo_id=repo_id,
        repo_type="dataset",
        local_dir=str(target_dir),
        local_dir_use_symlinks=False,
        resume_download=True,
        allow_patterns=allow_patterns,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Download public AI training datasets.")
    parser.add_argument(
        "--datasets",
        nargs="+",
        default=["wikipedia_en_20220301"],
        choices=sorted(DATASETS.keys()),
        help="One or more dataset keys to download.",
    )
    parser.add_argument(
        "--output-dir",
        default="datasets",
        help="Folder where datasets will be stored.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "selected": args.datasets,
        "datasets": {name: DATASETS[name] for name in args.datasets},
    }
    (output_dir / "download_manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    for name in args.datasets:
        spec = DATASETS[name]
        target_dir = output_dir / name
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"Downloading {name} into {target_dir} ...")

        if spec["kind"] == "snapshot":
            download_snapshot(spec["repo_id"], target_dir, spec.get("allow_patterns"))
        else:
            raise ValueError(f"Unsupported dataset kind: {spec['kind']}")

        print(f"Finished {name}")

    print("All requested downloads completed.")


if __name__ == "__main__":
    main()
