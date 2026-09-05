from dataclasses import dataclass


@dataclass
class ComputeTarget:
    name: str
    accelerator: str
    status: str


COMPUTE_TARGETS = [
    ComputeTarget("Auto", "Smart Router", "online"),
    ComputeTarget("Kaggle", "NVIDIA T4 x2", "standby"),
    ComputeTarget("Mac", "Apple Silicon", "local"),
    ComputeTarget("Lightning", "Cloud GPU", "standby"),
    ComputeTarget("NVIDIA CUDA Lab", "CUDA", "standby"),
    ComputeTarget("AMD ROCm Lab", "ROCm", "future"),
]
