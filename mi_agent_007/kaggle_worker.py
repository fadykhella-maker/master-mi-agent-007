import os
import httpx

DEFAULT_KAGGLE_URL = "https://rebuilt-unsorted-failing.ngrok-free.dev"
MODEL = "Qwen/Qwen2.5-1.5B-Instruct"


def worker_url() -> str:
    return os.getenv("KAGGLE_WORKER_URL", DEFAULT_KAGGLE_URL).rstrip("/")


async def health() -> bool:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{worker_url()}/v1/models")
        return r.status_code == 200
    except Exception:
        return False


async def execute_kaggle(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            f"{worker_url()}/v1/chat/completions",
            json={
                "model": MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are MI BOND, Agent 007. "
                            "You are an agentic AI command, reasoning, "
                            "orchestration and execution assistant. "
                            "Be concise, technically precise, and never claim "
                            "an external action occurred unless confirmed."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                "temperature": 0.4,
                "max_tokens": 400,
            },
        )

    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]
