from agentverse.llms.base import BaseChatModel, BaseModelArgs, LLMResult
from agentverse.llms import llm_registry
from pydantic import Field
import os

try:
    from openai import OpenAI
except ImportError:
    raise ImportError("Please install openai: pip install openai")

class OpenAIArgs(BaseModelArgs):
    model: str = Field(default="o1-mini")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=8000)

@llm_registry.register("o1mini")
class OpenAIChat(BaseChatModel):
    args: OpenAIArgs = Field(default_factory=OpenAIArgs)

    def generate_response(self, prompt: str) -> LLMResult:
        # Use environment variables or fallback to empty string (set your own API key)
        api_key = os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=self.args.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.args.temperature,
            max_tokens=self.args.max_tokens,
            stream=False
        )
        content = response.choices[0].message.content or ""
        return LLMResult(content=content)

    async def agenerate_response(self, prompt: str):
        # Simple async wrapper using thread execution
        import asyncio
        return await asyncio.to_thread(self.generate_response, prompt)

    def get_spend(self) -> int:
        # Return 0 for now, implement cost calculation if needed
        return 0