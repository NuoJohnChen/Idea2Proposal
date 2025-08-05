from agentverse.llms.base import BaseChatModel, BaseModelArgs, LLMResult
from agentverse.llms import llm_registry
from pydantic import Field
import os
import time

try:
    from openai import OpenAI
except ImportError:
    raise ImportError("Please install openai: pip install openai")

class DeepSeekArgs(BaseModelArgs):
    model: str = Field(default="deepseek-v3")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=8000)
    request_interval: float = Field(default=1.0, description="Request interval in seconds")

@llm_registry.register("deepseek")
class DeepSeekChat(BaseChatModel):
    args: DeepSeekArgs = Field(default_factory=DeepSeekArgs)

    def generate_response(self, prompt: str) -> LLMResult:
        # Add request interval to avoid rate limiting
        time.sleep(self.args.request_interval)
        
        # Use environment variables or fallback to placeholder (set your own API key)
        api_key = os.environ.get("DEEPSEEK_API_KEY", "YOUR_DEEPSEEK_API_KEY_HERE")
        base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
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