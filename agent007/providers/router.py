from dataclasses import dataclass


@dataclass
class Provider:
    name: str
    kind: str
    status: str = "standby"


PROVIDERS = [
    Provider("Auto", "router", "online"),
    Provider("Kaggle / Hugging Face", "open-source"),
    Provider("Mac Local", "local"),
    Provider("OpenAI", "api"),
    Provider("Anthropic", "api"),
    Provider("xAI", "api"),
]
