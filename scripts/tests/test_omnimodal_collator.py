"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  pytest /workspace/dllm/scripts/tests/test_omnimodal_collator.py -v
"""

from dllm.omnimodal.collators import OmnimodalCollator
from dllm.omnimodal.contracts import Modality, TokenPackage


def _pack(sample_id: str, tokens: list[int]) -> TokenPackage:
    return TokenPackage(
        tokens=tokens,
        modality=Modality.TEXT,
        sample_id=sample_id,
        modality_id=1,
        segment_ids=[0] * len(tokens),
        temporal_ids=[0] * len(tokens),
        target_mask=[1] * len(tokens),
    )


def test_collator_pads_to_longest():
    batch = OmnimodalCollator()([_pack("a", [1, 2]), _pack("b", [1, 2, 3, 4])])
    assert len(batch.input_ids) == 2
    assert len(batch.input_ids[0]) == 4
    assert batch.sample_ids == ["a", "b"]


def test_collator_honors_max_token_budget():
    collator = OmnimodalCollator(max_token_budget=3)
    batch = collator([_pack("a", [1, 2]), _pack("b", [1, 2, 3])])
    assert batch.sample_ids == ["a"]
