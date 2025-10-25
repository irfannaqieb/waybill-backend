import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def complete(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=1.0,
                max_completion_tokens=500,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise ValueError(f"[LLM Error: {str(e)}]")
