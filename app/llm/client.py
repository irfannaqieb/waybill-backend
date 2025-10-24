import os
import openai


class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        # TODO : replace placeholder with actual LLM call
        async def complete(self, prompt: str) -> str:
            return f"[LLM OUTPUT PLACEHOLDER] \n{prompt[:500]}"
