"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  pytest /workspace/dllm/scripts/tests/test_omnimodal_sampler.py -v
"""

from pathlib import Path

import pytest

from dllm.omnimodal.adapters import StubAdapter
from dllm.omnimodal.contracts import Modality, OmnimodalManifestRecord
from dllm.omnimodal.sampler import OmnimodalSampler


class _FakeTextAdapter:
    modality = Modality.TEXT

    @property
    def capabilities(self):
        return None

    def can_handle(self, record):
        return record.modality == Modality.TEXT

    def encode(self, record):
        return type("Pkg", (), {"tokens": [1, 2, 3], "modality": Modality.TEXT, "metadata": {"uri": record.uri}})()

    def decode(self, tokens, metadata=None):
        return "decoded"


class _Registry:
    def __init__(self, adapter):
        self._adapter = adapter

    def get_for_record(self, _record):
        return self._adapter


def test_prepare_conditioning_validates_payload(tmp_path):
    txt = Path(tmp_path) / "a.txt"
    txt.write_text("hello", encoding="utf-8")
    record = OmnimodalManifestRecord(sample_id="s1", uri=txt.as_posix(), modality=Modality.TEXT)
    sampler = OmnimodalSampler(registry=_Registry(_FakeTextAdapter()))
    payload = sampler.prepare_conditioning(record)
    assert payload["modality"] == "text"
    assert payload["tokens"] == [1, 2, 3]


def test_validate_conditioning_rejects_bad_tokens():
    sampler = OmnimodalSampler(registry=_Registry(_FakeTextAdapter()))
    with pytest.raises(ValueError, match="tokens"):
        sampler.validate_conditioning({"tokens": ["x"], "modality": "text"})


def test_decode_raises_actionable_error_for_unconfigured_backends(tmp_path):
    png = Path(tmp_path) / "a.png"
    png.write_bytes(b"x")
    record = OmnimodalManifestRecord(sample_id="img1", uri=png.as_posix(), modality=Modality.IMAGE)
    sampler = OmnimodalSampler(registry=_Registry(StubAdapter(modality=Modality.IMAGE, backend_hint="image")))
    with pytest.raises(NotImplementedError, match="decode-capable backend"):
        sampler.decode(record, tokens=[1, 2])
