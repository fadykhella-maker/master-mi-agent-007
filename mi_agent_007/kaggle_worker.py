import os
import httpx


MODEL = os.getenv(
    "MI_BOND_KAGGLE_MODEL",
    "Qwen/Qwen2.5-1.5B-Instruct",
)


def worker_url() -> str:
    url = os.getenv("KAGGLE_WORKER_URL", "").strip()

    if not url:
        raise RuntimeError(
            "KAGGLE_WORKER_URL is not configured for MI BOND."
        )

    return url.rstrip("/")


def worker_headers() -> dict[str, str]:
    token = os.getenv("KAGGLE_WORKER_TOKEN", "").strip()

    if not token:
        return {}

    return {
        "Authorization": f"Bearer {token}",
    }


async def health() -> bool:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{worker_url()}/v1/models",
                headers=worker_headers(),
            )

        return response.status_code == 200

    except Exception:
        return False


async def execute_kaggle(
    prompt: str,
    system_prompt: str | None = None,
    temperature: float = 0.4,
    max_tokens: int = 800,
) -> str:
    system = system_prompt or (
        "You are MI BOND, Agent 007. "
        "You are an independent provider-neutral agentic AI "
        "reasoning and orchestration system. "
        "Be concise, accurate and operationally useful. "
        "Never claim an external action occurred unless confirmed."
    )

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{worker_url()}/v1/chat/completions",
            headers=worker_headers(),
            json={
                "model": MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": system,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]
