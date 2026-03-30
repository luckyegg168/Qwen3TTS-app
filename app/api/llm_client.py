"""Unified multi-provider LLM client for 潤稿 / translate functions.

Supported providers
-------------------
* ``"ollama"``  — local Ollama server  (POST /api/generate, GET /api/tags)
* ``"openai"``  — OpenAI API           (POST /v1/chat/completions, GET /v1/models)
* ``"fastapi"`` — custom FastAPI server (POST /v1/chat/completions, GET /v1/models)

All three provide the same high-level helpers: :meth:`polish`, :meth:`translate`,
:meth:`simplify_chinese`, :meth:`traditional_chinese`, :meth:`custom_process`.
"""

from __future__ import annotations

import requests

# ─── Exceptions ───────────────────────────────────────────────────────────────

class LLMError(Exception):
    """Raised when an LLM API call fails."""


# ─── Client ───────────────────────────────────────────────────────────────────

class LLMClient:
    """Unified LLM client supporting Ollama, OpenAI, and FastAPI providers.

    Parameters
    ----------
    provider:
        ``"ollama"`` | ``"openai"`` | ``"fastapi"``
    base_url:
        Server root URL.  For OpenAI this should be ``"https://api.openai.com"``.
        For Ollama typically ``"http://localhost:11434"``.
    api_key:
        Bearer token / API key.  Required for ``"openai"``; optional for ``"fastapi"``.
    model:
        Model name / ID used in every request.
    timeout:
        HTTP timeout in seconds (default 60).
    """

    def __init__(
        self,
        provider: str = "ollama",
        base_url: str = "http://localhost:11434",
        api_key: str = "",
        model: str = "llama3.2:latest",
        timeout: int = 60,
    ) -> None:
        self.provider = provider.lower()
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        # Legacy compat: some callers access `.default_model`
        self.default_model = model

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _headers(self) -> dict[str, str]:
        h: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def _generate(self, prompt: str) -> str:
        """Low-level text-generation call, dispatched by provider."""
        if self.provider == "ollama":
            return self._generate_ollama(prompt)
        # openai / fastapi both use the OpenAI Chat Completions schema
        return self._generate_openai_compat(prompt)

    def _generate_ollama(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "").strip()
        except requests.RequestException as exc:
            raise LLMError(f"Ollama 請求失敗：{exc}") from exc

    def _generate_openai_compat(self, prompt: str) -> str:
        """Works for both OpenAI API and OpenAI-compatible FastAPI servers."""
        url = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        try:
            resp = requests.post(
                url,
                json=payload,
                headers=self._headers(),
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except (requests.RequestException, KeyError, IndexError) as exc:
            raise LLMError(f"LLM 請求失敗（{self.provider}）：{exc}") from exc

    # ── Public API ────────────────────────────────────────────────────────────

    def generate(self, prompt: str) -> str:
        """Generate a response for the given prompt (public alias)."""
        return self._generate(prompt)

    def health_check(self) -> bool:
        """Return *True* when the server is reachable."""
        try:
            if self.provider == "ollama":
                url = f"{self.base_url}/api/tags"
                resp = requests.get(url, timeout=5)
            else:
                url = f"{self.base_url}/v1/models"
                resp = requests.get(url, headers=self._headers(), timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
        """Return a list of available model names from the provider."""
        try:
            if self.provider == "ollama":
                url = f"{self.base_url}/api/tags"
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                return [m["name"] for m in data.get("models", [])]
            else:
                url = f"{self.base_url}/v1/models"
                resp = requests.get(url, headers=self._headers(), timeout=10)
                resp.raise_for_status()
                data = resp.json()
                return [m["id"] for m in data.get("data", [])]
        except Exception:
            return []

    # ── Task helpers ──────────────────────────────────────────────────────────

    def polish(self, text: str) -> str:
        prompt = (
            f"請潤稿以下文字，保持原有語言，改善文章流暢度、用詞和表達方式，"
            f"不要改變原文的核心意思：\n\n{text}"
        )
        return self._generate(prompt)

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        lang_map = {
            "zh": "中文",
            "en": "英文",
            "ja": "日文",
            "ko": "韓文",
            "fr": "法文",
            "de": "德文",
        }
        src = lang_map.get(source_lang, source_lang)
        tgt = lang_map.get(target_lang, target_lang)
        prompt = f"請將以下{src}文字翻譯成{tgt}，保持原文的語氣和風格：\n\n{text}"
        return self._generate(prompt)

    def simplify_chinese(self, text: str) -> str:
        prompt = f"請將以下繁體中文轉換為簡體中文：\n\n{text}"
        return self._generate(prompt)

    def traditional_chinese(self, text: str) -> str:
        prompt = f"請將以下簡體中文轉換為繁體中文：\n\n{text}"
        return self._generate(prompt)

    def custom_process(self, text: str, instruction: str) -> str:
        prompt = f"{instruction}\n\n{text}"
        return self._generate(prompt)
