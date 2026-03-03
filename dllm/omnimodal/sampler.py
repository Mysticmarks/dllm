"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  python -c "from dllm.omnimodal.sampler import OmnimodalSampler"
"""

from dataclasses import dataclass
from typing import Any

from dllm.omnimodal.adapters import AdapterRegistry, AdapterNotConfiguredError
from dllm.omnimodal.contracts import Modality, OmnimodalManifestRecord


@dataclass
class OmnimodalSampler:
    registry: AdapterRegistry

    def prepare_conditioning(self, record: OmnimodalManifestRecord) -> dict[str, Any]:
        adapter = self.registry.get_for_record(record)
        encoded = adapter.encode(record)
        payload = {
            "tokens": encoded.tokens,
            "modality": encoded.modality.value,
            "metadata": encoded.metadata,
        }
        self.validate_conditioning(payload)
        return payload

    def validate_conditioning(self, payload: dict[str, Any]) -> None:
        tokens = payload.get("tokens")
        modality = payload.get("modality")

        if not isinstance(tokens, list) or not tokens:
            raise ValueError("conditioning payload requires non-empty list field: tokens")
        if not all(isinstance(token, int) for token in tokens):
            raise ValueError("conditioning payload tokens must be integers")
        if not isinstance(modality, str) or modality not in {item.value for item in Modality}:
            raise ValueError(f"conditioning payload has invalid modality: {modality}")

    def decode(self, record: OmnimodalManifestRecord, tokens: list[int]) -> Any:
        adapter = self.registry.get_for_record(record)
        try:
            return adapter.decode(tokens=tokens, metadata={"sample_id": record.sample_id})
        except AdapterNotConfiguredError as exc:
            raise NotImplementedError(
                "Decode not implemented for "
                f"modality={record.modality.value}; adapter={adapter.__class__.__name__}; "
                "configure a decode-capable backend."
            ) from exc
