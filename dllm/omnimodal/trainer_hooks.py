"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  python -c "from dllm.omnimodal.trainer_hooks import OmnimodalTrainerHooksMixin"
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

    def aggregate_omnimodal_losses(
        self,
        losses: dict[str, float],
        objective_weights: dict[str, float] | None = None,
    ) -> tuple[float, dict[str, float]]:
        aggregator = ModalityAwareLossAggregator(objective_weights=objective_weights or {})
        return aggregator.combine(losses)

    def build_omnimodal_metrics(
        self,
        objective_losses: dict[str, float],
        modality_losses: dict[str, float] | None = None,
    ) -> dict[str, float]:
        metrics: dict[str, float] = {}
        for objective_name, loss in objective_losses.items():
            metrics[f"omni/objective/{objective_name}"] = float(loss)
        for modality_name, loss in (modality_losses or {}).items():
            metrics[f"omni/modality/{modality_name}"] = float(loss)
        if objective_losses:
            metrics["omni/loss_objective_mean"] = sum(objective_losses.values()) / len(objective_losses)
        if modality_losses:
            metrics["omni/loss_modality_mean"] = sum(modality_losses.values()) / len(modality_losses)
        return metrics
