import os
from dataclasses import dataclass
from typing import Optional

import httpx

from mi_agent_007.kaggle_worker import health as kaggle_health
from mi_agent_007.kaggle_worker import worker_url


KAGGLE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"


AGENT_PROMPTS = {
    "Bond": (
        "You are MI BOND, Agent 007: the primary agentic AI command, "
        "reasoning, orchestration and execution assistant. "
        "Be concise, technically precise and operationally useful. "
        "Plan before acting. Never claim an external action occurred unless "
        "the tool or provider confirmed it."
    ),
    "Research": (
        "You are MI BOND Research Agent. Investigate deeply, distinguish "
        "facts from inference, synthesize findings clearly, and identify "
        "uncertainty. Never claim research or tool execution occurred unless "
        "it was actually performed."
    ),
    "Executive": (
        "You are MI BOND Executive Agent. Produce concise, high-signal "
        "executive analysis, decisions, options, risks and recommended next "
        "actions. Avoid unnecessary technical detail unless it affects the "
        "decision."
    ),
    "Engineering": (
        "You are MI BOND Engineering Agent. Think like a senior systems and "
        "AI infrastructure engineer. Diagnose carefully, provide executable "
        "technical guidance, preserve security, and do not claim commands "
        "were run unless confirmed."
    ),
    "Communications": (
        "You are MI BOND Communications Agent. Draft polished, credible, "
        "executive-quality communications while preserving the operator's "
        "intent and voice."
    ),
}


@dataclass
class RouteResult:
    text: str
    provider: str
    model: str
    runtime: str
    compute: str


def _agent_prompt(agent: str) -> str:
    return AGENT_PROMPTS.get(agent, AGENT_PROMPTS["Bond"])


def provider_configured(provider: str) -> bool:
    p = provider.lower()

    if p == "openai":
        return bool(os.getenv("OPENAI_API_KEY"))

    if p == "anthropic":
        return bool(os.getenv("ANTHROPIC_API_KEY"))

    if p == "xai":
        return bool(os.getenv("XAI_API_KEY"))

    if p == "ollama":
        return bool(os.getenv("OLLAMA_BASE_URL"))

    return False


async def provider_health() -> dict[str, bool]:
    result = {
        "kaggle": False,
        "openai": provider_configured("openai"),
        "anthropic": provider_configured("anthropic"),
        "xai": provider_configured("xai"),
        "ollama": False,
    }

    try:
        result["kaggle"] = await kaggle_health()
    except Exception:
        result["kaggle"] = False

    base = os.getenv("OLLAMA_BASE_URL", "").rstrip("/")
    if base:
        try:
            async with httpx.AsyncClient(timeout=4) as client:
                r = await client.get(f"{base}/api/tags")
            result["ollama"] = r.status_code == 200
        except Exception:
            result["ollama"] = False

    return result


async def _kaggle(
    prompt: str,
    system: str,
    temperature: float,
    max_tokens: int,
) -> RouteResult:
    token = os.getenv("KAGGLE_WORKER_TOKEN", "")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            f"{worker_url()}/v1/chat/completions",
            headers=headers,
            json={
                "model": KAGGLE_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )

    r.raise_for_status()

    data = r.json()

    return RouteResult(
        text=data["choices"][0]["message"]["content"],
        provider="Kaggle",
        model="Qwen2.5-1.5B-Instruct",
        runtime="vLLM",
        compute="Kaggle T4",
    )


async def _openai(
    prompt: str,
    system: str,
    temperature: float,
    max_tokens: int,
    model: Optional[str] = None,
) -> RouteResult:
    key = os.environ["OPENAI_API_KEY"]
    chosen = model or os.getenv("OPENAI_MODEL", "gpt-5-mini")

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "model": chosen,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )

    r.raise_for_status()
    data = r.json()

    return RouteResult(
        text=data["choices"][0]["message"]["content"],
        provider="OpenAI",
        model=chosen,
        runtime="Provider API",
        compute="OpenAI Cloud",
    )


async def _anthropic(
    prompt: str,
    system: str,
    temperature: float,
    max_tokens: int,
    model: Optional[str] = None,
) -> RouteResult:
    key = os.environ["ANTHROPIC_API_KEY"]
    chosen = model or os.getenv(
        "ANTHROPIC_MODEL",
        "claude-sonnet-4-20250514",
    )

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": chosen,
                "system": system,
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )

    r.raise_for_status()
    data = r.json()

    blocks = data.get("content", [])
    text = "\n".join(
        block.get("text", "")
        for block in blocks
        if block.get("type") == "text"
    ).strip()

    return RouteResult(
        text=text,
        provider="Anthropic",
        model=chosen,
        runtime="Provider API",
        compute="Anthropic Cloud",
    )


async def _xai(
    prompt: str,
    system: str,
    temperature: float,
    max_tokens: int,
    model: Optional[str] = None,
) -> RouteResult:
    key = os.environ["XAI_API_KEY"]
    chosen = model or os.getenv("XAI_MODEL", "grok-4-latest")

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "model": chosen,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )

    r.raise_for_status()
    data = r.json()

    return RouteResult(
        text=data["choices"][0]["message"]["content"],
        provider="xAI",
        model=chosen,
        runtime="Provider API",
        compute="xAI Cloud",
    )


async def _ollama(
    prompt: str,
    system: str,
    temperature: float,
    model: Optional[str] = None,
) -> RouteResult:
    base = os.environ["OLLAMA_BASE_URL"].rstrip("/")
    chosen = model or os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            f"{base}/api/chat",
            json={
                "model": chosen,
                "stream": False,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "options": {
                    "temperature": temperature,
                },
            },
        )

    r.raise_for_status()
    data = r.json()

    return RouteResult(
        text=data["message"]["content"],
        provider="Ollama",
        model=chosen,
        runtime="Ollama",
        compute="Mac / Local",
    )


def _requested_provider(
    selected_model: str,
    selected_compute: str,
) -> str:
    model = selected_model.lower()
    compute = selected_compute.lower()

    if "openai" in model:
        return "openai"

    if "claude" in model:
        return "anthropic"

    if "grok" in model:
        return "xai"

    if "ollama" in model:
        return "ollama"

    if "qwen" in model or "kaggle" in compute:
        return "kaggle"

    if "mac" in compute:
        return "ollama"

    return "auto"


async def execute(
    prompt: str,
    agent: str = "Bond",
    selected_model: str = "Auto",
    selected_runtime: str = "Auto",
    selected_compute: str = "Auto",
    temperature: float = 0.4,
    max_tokens: int = 800,
) -> RouteResult:
    system = _agent_prompt(agent)

    requested = _requested_provider(
        selected_model,
        selected_compute,
    )

    health = await provider_health()

    if requested == "kaggle":
        if not health["kaggle"]:
            raise RuntimeError(
                "Kaggle was explicitly selected but the worker is offline."
            )
        return await _kaggle(
            prompt,
            system,
            temperature,
            max_tokens,
        )

    if requested == "openai":
        if not health["openai"]:
            raise RuntimeError(
                "OpenAI was selected but OPENAI_API_KEY is not configured."
            )
        return await _openai(
            prompt,
            system,
            temperature,
            max_tokens,
        )

    if requested == "anthropic":
        if not health["anthropic"]:
            raise RuntimeError(
                "Claude was selected but ANTHROPIC_API_KEY is not configured."
            )
        return await _anthropic(
            prompt,
            system,
            temperature,
            max_tokens,
        )

    if requested == "xai":
        if not health["xai"]:
            raise RuntimeError(
                "Grok was selected but XAI_API_KEY is not configured."
            )
        return await _xai(
            prompt,
            system,
            temperature,
            max_tokens,
        )

    if requested == "ollama":
        if not health["ollama"]:
            raise RuntimeError(
                "Local Ollama was selected but OLLAMA_BASE_URL "
                "is not configured or reachable."
            )
        return await _ollama(
            prompt,
            system,
            temperature,
        )

    errors = []

    if health["kaggle"]:
        try:
            return await _kaggle(
                prompt,
                system,
                temperature,
                max_tokens,
            )
        except Exception as exc:
            errors.append(f"Kaggle: {exc}")

    if health["openai"]:
        try:
            return await _openai(
                prompt,
                system,
                temperature,
                max_tokens,
            )
        except Exception as exc:
            errors.append(f"OpenAI: {exc}")

    if health["anthropic"]:
        try:
            return await _anthropic(
                prompt,
                system,
                temperature,
                max_tokens,
            )
        except Exception as exc:
            errors.append(f"Anthropic: {exc}")

    if health["xai"]:
        try:
            return await _xai(
                prompt,
                system,
                temperature,
                max_tokens,
            )
        except Exception as exc:
            errors.append(f"xAI: {exc}")

    if health["ollama"]:
        try:
            return await _ollama(
                prompt,
                system,
                temperature,
            )
        except Exception as exc:
            errors.append(f"Ollama: {exc}")

    detail = "; ".join(errors)

    if detail:
        raise RuntimeError(
            "No provider completed the mission. " + detail
        )

    raise RuntimeError(
        "No inference provider is currently available. "
        "Start the Kaggle worker or configure an API provider."
    )
