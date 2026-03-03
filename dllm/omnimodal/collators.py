"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  python -c "from dllm.omnimodal.collators import OmnimodalCollator"
"""

from dataclasses import dataclass

from dllm.omnimodal.contracts import PackedBatch, TokenPackage


@dataclass
class OmnimodalCollator:
    pad_token_id: int = 0
    label_pad_token_id: int = -100
    max_token_budget: int | None = None

    def _pad(self, values: list[int], target_len: int, pad: int) -> list[int]:
        if len(values) >= target_len:
            return values[:target_len]
        return values + [pad] * (target_len - len(values))

    def __call__(self, packages: list[TokenPackage]) -> PackedBatch:
        if self.max_token_budget is not None:
            total = 0
            selected: list[TokenPackage] = []
            for package in packages:
                if total + len(package.tokens) > self.max_token_budget:
                    break
                selected.append(package)
                total += len(package.tokens)
            packages = selected

        if not packages:
            raise ValueError("OmnimodalCollator received empty package list")

        max_len = max(len(package.tokens) for package in packages)

        return PackedBatch(
            input_ids=[self._pad(package.tokens, max_len, self.pad_token_id) for package in packages],
            labels=[self._pad(package.tokens, max_len, self.label_pad_token_id) for package in packages],
            modality_ids=[self._pad([package.modality_id] * len(package.tokens), max_len, 0) for package in packages],
            segment_ids=[self._pad(package.segment_ids, max_len, 0) for package in packages],
            temporal_ids=[self._pad(package.temporal_ids, max_len, 0) for package in packages],
            target_mask=[self._pad(package.target_mask, max_len, 0) for package in packages],
            sample_ids=[package.sample_id for package in packages],
            metadata=[package.metadata for package in packages],
        )
