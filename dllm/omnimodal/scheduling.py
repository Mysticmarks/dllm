"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  python -c "from dllm.omnimodal.scheduling import weighted_sample_records"
"""

import random
from dataclasses import dataclass, field

from dllm.omnimodal.contracts import OmnimodalManifestRecord


@dataclass(frozen=True)
class WeightedSamplingPolicy:
    enabled: bool = False
    modality_weights: dict[str, float] = field(default_factory=dict)
    source_weights: dict[str, float] = field(default_factory=dict)
    replacement: bool = True


@dataclass(frozen=True)
class CurriculumStage:
    max_step: int
    allowed_modalities: set[str] = field(default_factory=set)
    min_confidence: float | None = None


@dataclass(frozen=True)
class CurriculumPolicy:
    enabled: bool = False
    stages: list[CurriculumStage] = field(default_factory=list)


def _record_source(record: OmnimodalManifestRecord) -> str | None:
    provenance = record.provenance or {}
    if "source" in provenance:
        return str(provenance["source"])
    metadata = record.metadata or {}
    if "source" in metadata:
        return str(metadata["source"])
    return None


def record_sampling_weight(
    record: OmnimodalManifestRecord,
    modality_weights: dict[str, float] | None = None,
    source_weights: dict[str, float] | None = None,
) -> float:
    modality_factor = (modality_weights or {}).get(record.modality.value, 1.0)
    source = _record_source(record)
    source_factor = (source_weights or {}).get(source, 1.0) if source else 1.0
    return max(float(modality_factor) * float(source_factor), 0.0)


def weighted_sample_records(
    records: list[OmnimodalManifestRecord],
    sample_size: int,
    seed: int,
    policy: WeightedSamplingPolicy,
) -> list[OmnimodalManifestRecord]:
    if sample_size < 0:
        raise ValueError("sample_size must be >= 0")
    if sample_size == 0 or not records:
        return []
    if not policy.enabled:
        return records[:sample_size]

    weights = [record_sampling_weight(record, policy.modality_weights, policy.source_weights) for record in records]
    if sum(weights) <= 0:
        raise ValueError("weighted sampling requires at least one positive record weight")

    rng = random.Random(seed)
    if policy.replacement:
        return rng.choices(records, weights=weights, k=sample_size)

    if sample_size > len(records):
        raise ValueError("sample_size cannot exceed dataset size when replacement=False")

    pool = list(records)
    pool_weights = list(weights)
    chosen: list[OmnimodalManifestRecord] = []
    for _ in range(sample_size):
        picked = rng.choices(range(len(pool)), weights=pool_weights, k=1)[0]
        chosen.append(pool.pop(picked))
        pool_weights.pop(picked)
    return chosen


def apply_curriculum_stage(
    records: list[OmnimodalManifestRecord],
    global_step: int,
    policy: CurriculumPolicy,
) -> list[OmnimodalManifestRecord]:
    if not policy.enabled or not policy.stages:
        return records

    ordered_stages = sorted(policy.stages, key=lambda stage: stage.max_step)
    selected_stage = ordered_stages[-1]
    for stage in ordered_stages:
        if global_step <= stage.max_step:
            selected_stage = stage
            break

    filtered = records
    if selected_stage.allowed_modalities:
        allowed = {item.lower() for item in selected_stage.allowed_modalities}
        filtered = [record for record in filtered if record.modality.value in allowed]
    if selected_stage.min_confidence is not None:
        filtered = [
            record
            for record in filtered
            if record.confidence is None or record.confidence >= selected_stage.min_confidence
        ]
    return filtered
