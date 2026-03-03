"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  python -c "import dllm.omnimodal as om; print(om.Modality.TEXT.value)"
"""

from dllm.omnimodal.adapters import (
    AdapterNotConfiguredError,
    AdapterRegistry,
    MidiEventAdapter,
    TextTokenizationAdapter,
    TokenizationAdapter,
    build_default_registry,
)
from dllm.omnimodal.collators import OmnimodalCollator
from dllm.omnimodal.config import OmnimodalConfig
from dllm.omnimodal.contracts import Modality, OmnimodalManifestRecord, PackedBatch, TokenPackage
from dllm.omnimodal.detection import DetectionResult, detect_modality
from dllm.omnimodal.ingestion import IngestionConfig, load_records, scan_folder_records
from dllm.omnimodal.manifest import dump_manifest_line, load_manifest, parse_manifest_line
from dllm.omnimodal.sampler import OmnimodalSampler
from dllm.omnimodal.scheduling import (
    CurriculumPolicy,
    CurriculumStage,
    WeightedSamplingPolicy,
    apply_curriculum_stage,
    weighted_sample_records,
)
from dllm.omnimodal.strategies import build_default_strategies

__all__ = [
    "AdapterNotConfiguredError",
    "AdapterRegistry",
    "DetectionResult",
    "IngestionConfig",
    "MidiEventAdapter",
    "Modality",
    "OmnimodalCollator",
    "OmnimodalConfig",
    "OmnimodalManifestRecord",
    "OmnimodalSampler",
    "PackedBatch",
    "TextTokenizationAdapter",
    "TokenPackage",
    "TokenizationAdapter",
    "build_default_registry",
    "build_default_strategies",
    "CurriculumPolicy",
    "CurriculumStage",
    "detect_modality",
    "dump_manifest_line",
    "load_manifest",
    "apply_curriculum_stage",
    "load_records",
    "parse_manifest_line",
    "scan_folder_records",
    "WeightedSamplingPolicy",
    "weighted_sample_records",
]
