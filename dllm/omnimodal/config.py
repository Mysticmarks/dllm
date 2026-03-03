"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  python -c "from dllm.omnimodal.config import OmnimodalConfig"
"""

from dataclasses import dataclass, field


@dataclass
class IngestionPolicyConfig:
    enabled: bool = False
    source_folder: str | None = None
    source_manifest: str | None = None
    recursive: bool = True
    seed: int = 42
    shuffle: bool = False
    skip_corrupt: bool = True
    max_retries: int = 1
    quarantine_manifest_path: str | None = None
    gif_policy: str = "adaptive"
    pdf_policy: str = "auto"


@dataclass
class BatchingPolicyConfig:
    mode: str = "mixed"
    max_token_budget: int | None = None
    modality_weights: dict[str, float] = field(default_factory=dict)


@dataclass
class WeightedSamplingPolicyConfig:
    enabled: bool = False
    replacement: bool = True
    modality_weights: dict[str, float] = field(default_factory=dict)
    source_weights: dict[str, float] = field(default_factory=dict)


@dataclass
class CurriculumStageConfig:
    max_step: int
    allowed_modalities: list[str] = field(default_factory=list)
    min_confidence: float | None = None


@dataclass
class CurriculumPolicyConfig:
    enabled: bool = False
    stages: list[CurriculumStageConfig] = field(default_factory=list)


@dataclass
class TokenizerAdapterConfig:
    enabled_modalities: list[str] = field(default_factory=lambda: ["text"])
    adapter_backend: dict[str, str] = field(default_factory=dict)


@dataclass
class ObjectivePolicyConfig:
    strategy_names: list[str] = field(default_factory=lambda: ["masked_denoising"])
    objective_weights: dict[str, float] = field(default_factory=dict)


@dataclass
class OmnimodalConfig:
    enabled: bool = False
    ingestion: IngestionPolicyConfig = field(default_factory=IngestionPolicyConfig)
    tokenizers: TokenizerAdapterConfig = field(default_factory=TokenizerAdapterConfig)
    batching: BatchingPolicyConfig = field(default_factory=BatchingPolicyConfig)
    weighted_sampling: WeightedSamplingPolicyConfig = field(default_factory=WeightedSamplingPolicyConfig)
    curriculum: CurriculumPolicyConfig = field(default_factory=CurriculumPolicyConfig)
    objectives: ObjectivePolicyConfig = field(default_factory=ObjectivePolicyConfig)

    def validate(self) -> None:
        if not self.enabled:
            return
        if bool(self.ingestion.source_folder) == bool(self.ingestion.source_manifest):
            raise ValueError("omnimodal ingestion requires exactly one of source_folder/source_manifest")
        if self.ingestion.gif_policy not in {"adaptive", "image", "video"}:
            raise ValueError(f"invalid gif_policy: {self.ingestion.gif_policy}")
        if self.ingestion.pdf_policy not in {"auto", "text_only", "image_only", "hybrid"}:
            raise ValueError(f"invalid pdf_policy: {self.ingestion.pdf_policy}")
        if any(weight < 0 for weight in self.weighted_sampling.modality_weights.values()):
            raise ValueError("weighted_sampling.modality_weights must be non-negative")
        if any(weight < 0 for weight in self.weighted_sampling.source_weights.values()):
            raise ValueError("weighted_sampling.source_weights must be non-negative")
        for stage in self.curriculum.stages:
            if stage.max_step < 0:
                raise ValueError("curriculum stage max_step must be non-negative")
