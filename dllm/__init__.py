"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  python -c "import dllm; print(dllm.__all__)"
"""

import importlib

__all__ = ["core", "data", "omnimodal", "pipelines", "utils"]


def __getattr__(name: str):
    if name in __all__:
        module = importlib.import_module(f"dllm.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module 'dllm' has no attribute {name!r}")
