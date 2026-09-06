# MI BOND Independent Kaggle Worker

This worker belongs only to MI BOND / Agent 007.

It is separate from the NVIDIA CUDA project.

Architecture:

MI BOND / Reflex Cloud
→ Agent 007 Router
→ MI BOND Worker Endpoint
→ Kaggle GPU
→ vLLM
→ Qwen

Required Reflex secrets:

KAGGLE_WORKER_URL
KAGGLE_WORKER_TOKEN

Required Kaggle secrets:

MI_BOND_NGROK_AUTHTOKEN
MI_BOND_WORKER_TOKEN

Optional Kaggle secret:

MI_BOND_NGROK_DOMAIN

No secrets should be stored in GitHub.
