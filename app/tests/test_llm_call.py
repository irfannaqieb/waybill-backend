import asyncio
from app.llm.client import LLMClient


async def main():
    llm = LLMClient()
    result = await llm.complete("Summarize DHL’s shipping zones in 3 bullet points.")
    print("\nLLM Response:\n", result)


if __name__ == "__main__":
    asyncio.run(main())
