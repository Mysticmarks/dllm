"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  pytest /workspace/dllm/scripts/tests/test_omnimodal_adapters.py -v
"""

from pathlib import Path

from dllm.omnimodal.adapters import AdapterNotConfiguredError, MidiEventAdapter, StubAdapter
from dllm.omnimodal.contracts import Modality, OmnimodalManifestRecord


def test_stub_adapter_raises_clear_error():
    adapter = StubAdapter(modality=Modality.IMAGE, backend_hint="test backend")
    record = OmnimodalManifestRecord(sample_id="s", uri="/tmp/a.png", modality=Modality.IMAGE)
    try:
        adapter.encode(record)
        assert False, "expected AdapterNotConfiguredError"
    except AdapterNotConfiguredError as exc:
        assert "test backend" in str(exc)


def test_midi_adapter_minimal_tokenization(tmp_path):
    midi_path = Path(tmp_path) / "demo.mid"
    midi_path.write_bytes(b"MThd" + bytes(range(1, 30)))
    record = OmnimodalManifestRecord(sample_id="m1", uri=midi_path.as_posix(), modality=Modality.MIDI)
    package = MidiEventAdapter().encode(record)
    assert package.modality == Modality.MIDI
    assert len(package.tokens) > 4
