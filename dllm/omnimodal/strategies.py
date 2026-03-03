"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  python -c "from dllm.omnimodal.strategies import StrategyRegistry"
"""

from dataclasses import dataclass

from dllm.omnimodal.contracts import StrategyDecision, TokenPackage


@dataclass(frozen=True)
class StrategySpec:
    name: str
    objective_name: str
    requires_labels: bool
    compatible_modalities: set[str]


class Strategy:
    spec: StrategySpec

    def decide(self, package: TokenPackage) -> StrategyDecision:
        raise NotImplementedError


class MaskedDenoisingStrategy(Strategy):
    spec = StrategySpec(
        name="masked_denoising",
        objective_name="denoising",
        requires_labels=False,
        compatible_modalities={"text", "image", "video", "audio", "midi", "pdf"},
    )

    def decide(self, package: TokenPackage) -> StrategyDecision:
        target_mask = [1 if index % 5 != 0 else 0 for index, _ in enumerate(package.tokens)]
        return StrategyDecision(
            strategy_name=self.spec.name,
            objective_name=self.spec.objective_name,
            target_mask=target_mask,
            metadata={"deterministic_stride": 5},
        )


class SupervisedIfLabelsStrategy(Strategy):
    spec = StrategySpec(
        name="supervised_if_labels",
        objective_name="supervised",
        requires_labels=True,
        compatible_modalities={"text", "audio", "video", "image", "pdf", "midi"},
    )

    def decide(self, package: TokenPackage) -> StrategyDecision:
        labels_available = bool(package.metadata.get("labels"))
        target_mask = [1] * len(package.tokens) if labels_available else [0] * len(package.tokens)
        return StrategyDecision(
            strategy_name=self.spec.name,
            objective_name=self.spec.objective_name,
            target_mask=target_mask,
            metadata={"labels_available": labels_available},
        )


class StrategyRegistry:
    def __init__(self):
        self._strategies: dict[str, Strategy] = {}

    def register(self, strategy: Strategy) -> None:
        self._strategies[strategy.spec.name] = strategy

    def resolve(self, name: str) -> Strategy:
        if name not in self._strategies:
            raise KeyError(f"unknown strategy {name}")
        return self._strategies[name]


def build_default_strategies() -> StrategyRegistry:
    registry = StrategyRegistry()
    registry.register(MaskedDenoisingStrategy())
    registry.register(SupervisedIfLabelsStrategy())
    return registry
