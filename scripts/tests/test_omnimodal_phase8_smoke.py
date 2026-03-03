"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  pytest /workspace/dllm/scripts/tests/test_omnimodal_phase8_smoke.py -v
"""

import json
from pathlib import Path

from dllm.omnimodal.adapters import build_default_registry
from dllm.omnimodal.collators import OmnimodalCollator
from dllm.omnimodal.contracts import Modality
from dllm.omnimodal.ingestion import IngestionConfig, load_records, scan_folder_records


class _SimpleTokenizer:
    def __call__(self, text, add_special_tokens=False):
        del add_special_tokens
        return {"input_ids": [ord(ch) for ch in text]}

    def decode(self, tokens):
        return "".join(chr(token) for token in tokens)


def test_manifest_load_filters_unknown_records(tmp_path):
    manifest_path = Path(tmp_path) / "manifest.jsonl"
    rows = [
        {
            "sample_id": "known",
            "uri": "/tmp/a.txt",
            "modality": "text",
        },
        {
            "sample_id": "unknown",
            "uri": "/tmp/b.bin",
            "modality": "unknown",
        },
    ]
    manifest_path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")

    records = load_records(manifest_path=manifest_path.as_posix())

    assert len(records) == 1
    assert records[0].sample_id == "known"
    assert records[0].modality == Modality.TEXT


def test_scan_encode_and_collate_mixed_text_midi(tmp_path):
    data_dir = Path(tmp_path) / "dataset"
    data_dir.mkdir()
    (data_dir / "notes.txt").write_text("ok", encoding="utf-8")
    (data_dir / "riff.mid").write_bytes(b"MThd" + bytes(range(1, 40)))

    records = scan_folder_records(
        root_dir=data_dir.as_posix(),
        split="train",
        config=IngestionConfig(recursive=False, shuffle=False),
    )

    registry = build_default_registry(tokenizer=_SimpleTokenizer())
    packages = [registry.get_for_record(record).encode(record) for record in records]

    batch = OmnimodalCollator()(packages)

    assert len(batch.input_ids) == 2
    assert set(batch.sample_ids) == {"train:notes.txt", "train:riff.mid"}
    assert {package.modality for package in packages} == {Modality.TEXT, Modality.MIDI}
