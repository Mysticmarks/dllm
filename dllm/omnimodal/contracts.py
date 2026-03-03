"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  python -c "from dllm.omnimodal.contracts import OmnimodalManifestRecord"
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Modality(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    MIDI = "midi"
    PDF = "pdf"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ModalityDetectionTrace:
    guessed_by_extension: str | None = None
    guessed_by_mime: str | None = None
    parser_check: str | None = None
    policy_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class OmnimodalManifestRecord:
    sample_id: str
    uri: str
    modality: Modality
    split: str = "train"
    labels: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    timestamp: float | None = None
    sequence_index: int | None = None
    group_id: str | None = None
    provenance: dict[str, Any] | None = None
    confidence: float | None = None
    preprocessing: dict[str, Any] | None = None


@dataclass(frozen=True)
class TokenizationCapabilities:
    supports_streaming: bool = False
    supports_temporal_chunks: bool = False
    supports_decode: bool = False
    supports_loss_masks: bool = True


@dataclass(frozen=True)
class TokenPackage:
    tokens: list[int]
    modality: Modality
    sample_id: str
    modality_id: int
    segment_ids: list[int]
    temporal_ids: list[int]
    target_mask: list[int]
    alignment_ids: list[int] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PackedBatch:
    input_ids: list[list[int]]
    labels: list[list[int]]
    modality_ids: list[list[int]]
    segment_ids: list[list[int]]
    temporal_ids: list[list[int]]
    target_mask: list[list[int]]
    sample_ids: list[str]
    metadata: list[dict[str, Any]]


@dataclass(frozen=True)
class StrategyDecision:
    strategy_name: str
    objective_name: str
    target_mask: list[int]
    metadata: dict[str, Any] = field(default_factory=dict)
