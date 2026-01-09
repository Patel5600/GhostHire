import abc
from typing import Dict, Any, Optional
import httpx
import logging

logger = logging.getLogger(__name__)

class LLMProvider(abc.ABC):
    @abc.abstractmethod
    async def generate_text(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        pass

    @abc.abstractmethod
    async def generate_json(self, system_prompt: str, user_prompt: str, schema: Dict = None) -> Dict[str, Any]:
        """Expects JSON output"""
        pass

class MockProvider(LLMProvider):
    async def generate_text(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        return "This is a mock response from the MockProvider. The AI is sleeping."

    async def generate_json(self, system_prompt: str, user_prompt: str, schema: Dict = None) -> Dict[str, Any]:
        return {"mock": True, "message": "This is a mock JSON response.", "score": 85}

class OpenAILikeProvider(LLMProvider):
    """
    Generic provider for OpenAI-compatible APIs (Groq, Together, local vLLM).
    """
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    async def _request(self, messages: list, json_mode: bool = False) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3, 
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                return data['choices'][0]['message']['content']
            except Exception as e:
                logger.error(f"LLM Request failed: {e}")
                raise e

    async def generate_text(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        return await self._request(messages)

    async def generate_json(self, system_prompt: str, user_prompt: str, schema: Dict = None) -> Dict[str, Any]:
        import json
        messages = [
            {"role": "system", "content": system_prompt + "\nIMPORTANT: Output ONLY valid JSON."},
            {"role": "user", "content": user_prompt}
        ]
        content = await self._request(messages, json_mode=True)
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback cleanup
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
