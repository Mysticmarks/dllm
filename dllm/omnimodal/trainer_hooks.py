"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  python -c "from dllm.omnimodal.trainer_hooks import ModalityAwareLossAggregator"
"""

from dataclasses import dataclass


@dataclass
class ModalityAwareLossAggregator:
    objective_weights: dict[str, float]

    def combine(self, losses: dict[str, float]) -> tuple[float, dict[str, float]]:
        combined = 0.0
        components: dict[str, float] = {}
        for name, loss in losses.items():
            weight = self.objective_weights.get(name, 1.0)
            weighted = weight * loss
            components[name] = weighted
            combined += weighted
        return combined, components


class OmnimodalTrainerHooksMixin:
    def preprocess_omnimodal_batch(self, batch):
        return batch

    def aggregate_omnimodal_losses(self, losses: dict[str, float]) -> tuple[float, dict[str, float]]:
        aggregator = ModalityAwareLossAggregator(objective_weights={})
        return aggregator.combine(losses)
