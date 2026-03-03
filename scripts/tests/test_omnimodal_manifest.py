"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  pytest /workspace/dllm/scripts/tests/test_omnimodal_manifest.py -v
"""

from dllm.omnimodal.contracts import Modality
from dllm.omnimodal.manifest import parse_manifest_line


def test_parse_manifest_line_with_optional_fields():
    line = '{"sample_id":"a1","uri":"/tmp/a.txt","modality":"text","split":"train","labels":{"target":"ok"}}'
    record = parse_manifest_line(line)
    assert record.sample_id == "a1"
    assert record.modality == Modality.TEXT
    assert record.labels == {"target": "ok"}


def test_parse_manifest_line_rejects_bad_modality():
    line = '{"sample_id":"a1","uri":"/tmp/a.txt","modality":"alien"}'
    try:
        parse_manifest_line(line)
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "invalid modality" in str(exc)
