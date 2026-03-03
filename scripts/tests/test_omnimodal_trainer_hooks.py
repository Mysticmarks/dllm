"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  pytest /workspace/dllm/scripts/tests/test_omnimodal_trainer_hooks.py -v
"""

from dllm.omnimodal.trainer_hooks import ModalityAwareLossAggregator, OmnimodalTrainerHooksMixin


class _Hooks(OmnimodalTrainerHooksMixin):
    pass


def test_modality_aware_loss_aggregator_applies_weights():
    agg = ModalityAwareLossAggregator(objective_weights={"supervised": 2.0})
    total, components = agg.combine({"supervised": 1.5, "denoising": 0.5})
    assert total == 3.5
    assert components["supervised"] == 3.0
    assert components["denoising"] == 0.5


def test_build_omnimodal_metrics_exposes_objective_and_modality_stats():
    hooks = _Hooks()
    metrics = hooks.build_omnimodal_metrics(
        objective_losses={"supervised": 2.0, "denoising": 1.0},
        modality_losses={"text": 1.5, "image": 2.5},
    )
    assert metrics["omni/objective/supervised"] == 2.0
    assert metrics["omni/modality/image"] == 2.5
    assert metrics["omni/loss_objective_mean"] == 1.5
    assert metrics["omni/loss_modality_mean"] == 2.0
