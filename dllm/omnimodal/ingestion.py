"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  python -c "from dllm.omnimodal.ingestion import scan_folder_records"
"""

import json
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from dllm.omnimodal.contracts import Modality, OmnimodalManifestRecord
from dllm.omnimodal.detection import detect_modality
from dllm.omnimodal.manifest import load_manifest
from dllm.utils.utils import get_default_logger

logger = get_default_logger(__name__)


@dataclass(frozen=True)
class IngestionConfig:
    recursive: bool = True
    seed: int = 42
    shuffle: bool = False
    skip_corrupt: bool = True
    max_retries: int = 1
    gif_policy: str = "adaptive"


def _iter_paths(root: Path, recursive: bool) -> list[Path]:
    entries = root.rglob("*") if recursive else root.glob("*")
    files = sorted([entry for entry in entries if entry.is_file()], key=lambda p: p.as_posix())
    return files


def _write_quarantine(path: str | None, item: dict) -> None:
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, ensure_ascii=False) + "\n")


def scan_folder_records(
    root_dir: str,
    split: str = "train",
    config: IngestionConfig | None = None,
    quarantine_manifest_path: str | None = None,
) -> list[OmnimodalManifestRecord]:
    cfg = config or IngestionConfig()
    root = Path(root_dir)
    if not root.exists():
        raise FileNotFoundError(f"ingestion root not found: {root_dir}")

    files = _iter_paths(root, recursive=cfg.recursive)
    if cfg.shuffle:
        rng = random.Random(cfg.seed)
        rng.shuffle(files)

    records: list[OmnimodalManifestRecord] = []
    for file_path in files:
        retries = 0
        while retries <= cfg.max_retries:
            try:
                if file_path.stat().st_size == 0:
                    raise ValueError("empty_file")
                detection = detect_modality(
                    file_path.as_posix(),
                    gif_policy=cfg.gif_policy,
                )
                relative_id = file_path.relative_to(root).as_posix().replace("/", "__")
                records.append(
                    OmnimodalManifestRecord(
                        sample_id=f"{split}:{relative_id}",
                        uri=file_path.as_posix(),
                        modality=detection.modality,
                        split=split,
                        metadata={"detection_trace": detection.trace.__dict__},
                    )
                )
                break
            except Exception as exc:
                retries += 1
                if retries > cfg.max_retries:
                    quarantine_item = {
                        "uri": file_path.as_posix(),
                        "reason": str(exc),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                    _write_quarantine(quarantine_manifest_path, quarantine_item)
                    if cfg.skip_corrupt:
                        logger.warning("dropping sample %s due to %s", file_path, exc)
                        break
                    raise
    return records


def load_records(
    folder: str | None = None,
    manifest_path: str | None = None,
    config: IngestionConfig | None = None,
) -> list[OmnimodalManifestRecord]:
    if folder and manifest_path:
        raise ValueError("Provide either folder or manifest_path, not both")
    if not folder and not manifest_path:
        raise ValueError("Either folder or manifest_path must be provided")
    if folder:
        return scan_folder_records(root_dir=folder, config=config)
    records = load_manifest(manifest_path)
    return [record for record in records if record.modality != Modality.UNKNOWN]
