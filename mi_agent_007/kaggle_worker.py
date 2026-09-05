import httpx

KAGGLE_URL = "https://rebuilt-unsorted-failing.ngrok-free.dev"
MODEL = "Qwen/Qwen2.5-1.5B-Instruct"

async def execute_kaggle(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            f"{KAGGLE_URL}/v1/chat/completions",
            json={
                "model": MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are MI BOND, Agent 007. Be concise, technical, and execution-oriented."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.4,
                "max_tokens": 400
            }
        )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]
