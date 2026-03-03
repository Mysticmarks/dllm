"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  pytest /workspace/dllm/scripts/tests/test_omnimodal_detection.py -v
"""

from dllm.omnimodal.contracts import Modality
from dllm.omnimodal.detection import detect_modality


def test_detect_known_extensions():
    assert detect_modality("/tmp/sample.txt").modality == Modality.TEXT
    assert detect_modality("/tmp/sample.pdf").modality == Modality.PDF
    assert detect_modality("/tmp/sample.mp4").modality == Modality.VIDEO
    assert detect_modality("/tmp/sample.mp3").modality == Modality.AUDIO
    assert detect_modality("/tmp/sample.midi").modality == Modality.MIDI


def test_detect_gif_policy_adaptive_to_video():
    result = detect_modality("/tmp/sample.gif", gif_policy="adaptive", gif_frame_count=3)
    assert result.modality == Modality.VIDEO
    assert "adaptive->video" in " ".join(result.trace.policy_notes)
