"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  pytest /workspace/dllm/scripts/tests/test_omnimodal_ingestion.py -v
"""

import json
from pathlib import Path

from dllm.omnimodal.ingestion import IngestionConfig, scan_folder_records


def test_scan_folder_records_and_quarantine(tmp_path):
    data_dir = Path(tmp_path) / "data"
    data_dir.mkdir()
    (data_dir / "a.txt").write_text("hello", encoding="utf-8")
    (data_dir / "bad.mp3").write_bytes(b"")

    quarantine = Path(tmp_path) / "quarantine.jsonl"
    records = scan_folder_records(
        root_dir=data_dir.as_posix(),
        config=IngestionConfig(skip_corrupt=True),
        quarantine_manifest_path=quarantine.as_posix(),
    )
    assert len(records) == 1
    assert records[0].uri.endswith("a.txt")

    lines = quarantine.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["uri"].endswith("bad.mp3")
