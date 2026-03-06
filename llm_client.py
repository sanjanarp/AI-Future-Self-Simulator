"""
LLM client wrapper for the Future Self Simulator.
Supports Gemini (default), standard OpenAI, and Azure OpenAI backends.
Priority: Gemini > Azure OpenAI > OpenAI
"""

from openai import OpenAI, AzureOpenAI
import httpx
from config import settings


def get_client():
    """Create and return the appropriate client based on configuration."""
    if getattr(settings, "use_gemini", False):
        # Gemini via its OpenAI-compatible REST endpoint — no extra package needed
        return OpenAI(
            api_key=getattr(settings, "GEMINI_API_KEY", ""),
            base_url=getattr(settings, "GEMINI_BASE_URL", ""),
        )
    if settings.use_azure:
        return AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        )
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def _get_model() -> str:
    """Return the model name based on the active backend."""
    if getattr(settings, "use_gemini", False):
        return getattr(settings, "GEMINI_MODEL", "")
    if settings.use_azure:
        return settings.AZURE_OPENAI_DEPLOYMENT_NAME
    return settings.OPENAI_MODEL


def chat_completion(messages: list[dict], temperature: float = 0.7, max_tokens: int = 4096) -> str:
    """
    Send a chat completion request and return the response text.
    Automatically uses the correct backend (Gemini, Azure OpenAI, or OpenAI).

    Args:
        messages: List of message dicts with 'role' and 'content' keys.
        temperature: Sampling temperature (0.0 - 1.0).
        max_tokens: Maximum tokens in the response.

    Returns:
        The assistant's response text.
    """
    # For Azure data-plane, call the REST API directly to ensure correct parameter names
    if settings.use_azure:
        endpoint = settings.AZURE_OPENAI_ENDPOINT.rstrip("/")
        deployment = settings.AZURE_OPENAI_DEPLOYMENT_NAME
        apiver = settings.AZURE_OPENAI_API_VERSION
        url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={apiver}"
        payload = {"messages": messages, "max_completion_tokens": max_tokens}
        headers = {"api-key": settings.AZURE_OPENAI_API_KEY, "Content-Type": "application/json"}
        with httpx.Client(timeout=120) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"]

    # Fallback to SDK for non-Azure backends
    client = get_client()
    kwargs = {"model": _get_model(), "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content
