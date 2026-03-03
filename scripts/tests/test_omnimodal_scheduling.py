"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  pytest /workspace/dllm/scripts/tests/test_omnimodal_scheduling.py -v
"""

from dllm.omnimodal.config import (
    CurriculumPolicyConfig,
    CurriculumStageConfig,
    IngestionPolicyConfig,
    OmnimodalConfig,
    WeightedSamplingPolicyConfig,
)
from dllm.omnimodal.contracts import Modality, OmnimodalManifestRecord
from dllm.omnimodal.scheduling import (
    CurriculumPolicy,
    CurriculumStage,
    WeightedSamplingPolicy,
    apply_curriculum_stage,
    weighted_sample_records,
)


def _record(sample_id: str, modality: Modality, source: str | None = None, confidence: float | None = None):
    metadata = {"source": source} if source else None
    return OmnimodalManifestRecord(
        sample_id=sample_id,
        uri=f"/tmp/{sample_id}",
        modality=modality,
        metadata=metadata,
        confidence=confidence,
    )


def test_weighted_sampling_prefers_high_weight_modalities_deterministically():
    records = [
        _record("a", Modality.TEXT),
        _record("b", Modality.IMAGE),
    ]
    policy = WeightedSamplingPolicy(enabled=True, modality_weights={"text": 10.0, "image": 0.1})

    sampled = weighted_sample_records(records, sample_size=20, seed=7, policy=policy)

    text_count = sum(1 for item in sampled if item.modality == Modality.TEXT)
    assert text_count >= 18


def test_weighted_sampling_without_replacement_returns_unique_records():
    records = [_record("a", Modality.TEXT), _record("b", Modality.IMAGE), _record("c", Modality.AUDIO)]
    policy = WeightedSamplingPolicy(enabled=True, replacement=False, modality_weights={"text": 3.0, "image": 1.0, "audio": 1.0})

    sampled = weighted_sample_records(records, sample_size=3, seed=9, policy=policy)

    assert len({item.sample_id for item in sampled}) == 3


def test_curriculum_filters_by_stage_modalities_and_confidence():
    records = [
        _record("txt_lo", Modality.TEXT, confidence=0.2),
        _record("txt_hi", Modality.TEXT, confidence=0.9),
        _record("img_hi", Modality.IMAGE, confidence=0.95),
    ]
    policy = CurriculumPolicy(
        enabled=True,
        stages=[
            CurriculumStage(max_step=100, allowed_modalities={"text"}, min_confidence=0.8),
            CurriculumStage(max_step=1000, allowed_modalities={"text", "image"}, min_confidence=0.0),
        ],
    )

    early = apply_curriculum_stage(records, global_step=50, policy=policy)
    late = apply_curriculum_stage(records, global_step=500, policy=policy)

    assert [item.sample_id for item in early] == ["txt_hi"]
    assert {item.sample_id for item in late} == {"txt_lo", "txt_hi", "img_hi"}


def test_omnimodal_config_validates_non_negative_weight_policies():
    config = OmnimodalConfig(
        enabled=True,
        ingestion=IngestionPolicyConfig(source_folder="/tmp"),
        weighted_sampling=WeightedSamplingPolicyConfig(enabled=True, modality_weights={"text": -1.0}),
    )

    try:
        config.validate()
    except ValueError as exc:
        assert "non-negative" in str(exc)
    else:
        raise AssertionError("expected ValueError for negative modality weight")


def test_omnimodal_config_validates_curriculum_stage_boundaries():
    config = OmnimodalConfig(
        enabled=True,
        ingestion=IngestionPolicyConfig(source_folder="/tmp"),
        curriculum=CurriculumPolicyConfig(enabled=True, stages=[CurriculumStageConfig(max_step=-1)]),
    )

    try:
        config.validate()
    except ValueError as exc:
        assert "max_step" in str(exc)
    else:
        raise AssertionError("expected ValueError for negative curriculum max_step")


def test_omnimodal_config_validates_positive_gif_threshold():
    config = OmnimodalConfig(
        enabled=True,
        ingestion=IngestionPolicyConfig(source_folder="/tmp", gif_video_frame_threshold=0),
    )

    try:
        config.validate()
    except ValueError as exc:
        assert "gif_video_frame_threshold" in str(exc)
    else:
        raise AssertionError("expected ValueError for non-positive gif threshold")
