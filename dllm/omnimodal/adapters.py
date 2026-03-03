"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  python -c "from dllm.omnimodal.adapters import build_default_registry"
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dllm.omnimodal.contracts import (
    Modality,
    OmnimodalManifestRecord,
    TokenPackage,
    TokenizationCapabilities,
)


class AdapterNotConfiguredError(RuntimeError):
    pass


class TokenizationAdapter(ABC):
    modality: Modality

    @property
    @abstractmethod
    def capabilities(self) -> TokenizationCapabilities: ...

    @abstractmethod
    def can_handle(self, record: OmnimodalManifestRecord) -> bool: ...

    @abstractmethod
    def encode(self, record: OmnimodalManifestRecord) -> TokenPackage: ...

    def batch_encode(self, records: list[OmnimodalManifestRecord]) -> list[TokenPackage]:
        return [self.encode(record) for record in records]

    def decode(self, tokens: list[int], metadata: dict[str, Any] | None = None) -> Any:
        raise AdapterNotConfiguredError(
            f"{self.__class__.__name__} does not support decode; configure a backend."
        )


@dataclass
class TextTokenizationAdapter(TokenizationAdapter):
    tokenizer: Any
    modality: Modality = Modality.TEXT

    @property
    def capabilities(self) -> TokenizationCapabilities:
        return TokenizationCapabilities(supports_decode=True)

    def can_handle(self, record: OmnimodalManifestRecord) -> bool:
        return record.modality == Modality.TEXT

    def encode(self, record: OmnimodalManifestRecord) -> TokenPackage:
        with open(record.uri, "r", encoding="utf-8") as handle:
            text = handle.read()
        token_ids = self.tokenizer(text, add_special_tokens=False)["input_ids"]
        length = len(token_ids)
        return TokenPackage(
            tokens=token_ids,
            modality=Modality.TEXT,
            sample_id=record.sample_id,
            modality_id=1,
            segment_ids=[0] * length,
            temporal_ids=[0] * length,
            target_mask=[1] * length,
            metadata={"uri": record.uri},
        )

    def decode(self, tokens: list[int], metadata: dict[str, Any] | None = None) -> str:
        return self.tokenizer.decode(tokens)


@dataclass
class StubAdapter(TokenizationAdapter):
    modality: Modality
    backend_hint: str

    @property
    def capabilities(self) -> TokenizationCapabilities:
        return TokenizationCapabilities()

    def can_handle(self, record: OmnimodalManifestRecord) -> bool:
        return record.modality == self.modality

    def encode(self, record: OmnimodalManifestRecord) -> TokenPackage:
        raise AdapterNotConfiguredError(
            f"No backend configured for modality={self.modality.value}. "
            f"Install/configure: {self.backend_hint}"
        )


@dataclass
class MidiEventAdapter(TokenizationAdapter):
    modality: Modality = Modality.MIDI

    @property
    def capabilities(self) -> TokenizationCapabilities:
        return TokenizationCapabilities(supports_temporal_chunks=True)

    def can_handle(self, record: OmnimodalManifestRecord) -> bool:
        return record.modality == Modality.MIDI

    def encode(self, record: OmnimodalManifestRecord) -> TokenPackage:
        raw = Path(record.uri).read_bytes()
        if len(raw) < 14 or raw[:4] != b"MThd":
            raise ValueError("invalid midi header")
        tokens = [raw[0], raw[1], raw[2], raw[3]] + [byte for byte in raw[4:64]]
        length = len(tokens)
        temporal_ids = list(range(length))
        return TokenPackage(
            tokens=tokens,
            modality=Modality.MIDI,
            sample_id=record.sample_id,
            modality_id=5,
            segment_ids=[0] * length,
            temporal_ids=temporal_ids,
            target_mask=[1] * length,
            metadata={"uri": record.uri, "tokenizer": "midi_header_bytes"},
        )


class AdapterRegistry:
    def __init__(self, adapters: list[TokenizationAdapter] | None = None):
        self._adapters = adapters or []

    def register(self, adapter: TokenizationAdapter) -> None:
        self._adapters.append(adapter)

    def get_for_record(self, record: OmnimodalManifestRecord) -> TokenizationAdapter:
        for adapter in self._adapters:
            if adapter.can_handle(record):
                return adapter
        raise KeyError(f"no adapter registered for modality={record.modality.value}")


def build_default_registry(tokenizer: Any | None = None) -> AdapterRegistry:
    adapters: list[TokenizationAdapter] = [
        MidiEventAdapter(),
        StubAdapter(Modality.IMAGE, "image discrete tokenizer backend"),
        StubAdapter(Modality.VIDEO, "video discrete tokenizer backend"),
        StubAdapter(Modality.AUDIO, "audio codec tokenizer backend"),
        StubAdapter(Modality.PDF, "pdf routing tokenizer backend"),
    ]
    if tokenizer is not None:
        adapters.append(TextTokenizationAdapter(tokenizer=tokenizer))
    else:
        adapters.append(StubAdapter(Modality.TEXT, "hf tokenizer backend"))
    return AdapterRegistry(adapters=adapters)
