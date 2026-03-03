"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  python -c "from dllm.omnimodal.sampler import OmnimodalSampler"
"""

from dataclasses import dataclass
from typing import Any

from dllm.omnimodal.adapters import AdapterRegistry, AdapterNotConfiguredError
from dllm.omnimodal.contracts import OmnimodalManifestRecord


@dataclass
class OmnimodalSampler:
    registry: AdapterRegistry

    def prepare_conditioning(self, record: OmnimodalManifestRecord) -> dict[str, Any]:
        adapter = self.registry.get_for_record(record)
        encoded = adapter.encode(record)
        return {"tokens": encoded.tokens, "modality": encoded.modality.value, "metadata": encoded.metadata}

    def decode(self, record: OmnimodalManifestRecord, tokens: list[int]) -> Any:
        adapter = self.registry.get_for_record(record)
        try:
            return adapter.decode(tokens=tokens, metadata={"sample_id": record.sample_id})
        except AdapterNotConfiguredError as exc:
            raise NotImplementedError(
                f"Decode not implemented for modality={record.modality.value}; configure backend."
            ) from exc
