"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  python -c "from dllm.omnimodal.manifest import parse_manifest_line"
"""

import json
from dataclasses import asdict

from dllm.omnimodal.contracts import Modality, OmnimodalManifestRecord


def parse_manifest_line(line: str) -> OmnimodalManifestRecord:
    payload = json.loads(line)
    if "sample_id" not in payload:
        raise ValueError("manifest missing required field: sample_id")
    if "uri" not in payload:
        raise ValueError("manifest missing required field: uri")

    modality_value = payload.get("modality", "unknown")
    try:
        modality = Modality(modality_value)
    except ValueError as exc:
        raise ValueError(f"manifest has invalid modality: {modality_value}") from exc

    return OmnimodalManifestRecord(
        sample_id=str(payload["sample_id"]),
        uri=str(payload["uri"]),
        modality=modality,
        split=str(payload.get("split", "train")),
        labels=payload.get("labels"),
        metadata=payload.get("metadata"),
        timestamp=payload.get("timestamp"),
        sequence_index=payload.get("sequence_index"),
        group_id=payload.get("group_id"),
        provenance=payload.get("provenance"),
        confidence=payload.get("confidence"),
        preprocessing=payload.get("preprocessing"),
    )


def dump_manifest_line(record: OmnimodalManifestRecord) -> str:
    output = asdict(record)
    output["modality"] = record.modality.value
    return json.dumps(output, ensure_ascii=False)


def load_manifest(path: str) -> list[OmnimodalManifestRecord]:
    records: list[OmnimodalManifestRecord] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            normalized = line.strip()
            if not normalized:
                continue
            try:
                records.append(parse_manifest_line(normalized))
            except Exception as exc:
                raise ValueError(f"invalid manifest line {line_no}: {exc}") from exc
    return records
