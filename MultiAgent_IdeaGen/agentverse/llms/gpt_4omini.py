# Placeholder file - user uses deepseek, this is only for compatibility
from agentverse.llms.base import BaseChatModel, BaseModelArgs, LLMResult
from agentverse.llms import llm_registry
from pydantic import Field

class GPT4OMiniArgs(BaseModelArgs):
    """Placeholder class"""
    model: str = Field(default="gpt-4o-mini")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=8000)

@llm_registry.register("gpt_4omini")
class GPT4OMiniChat(BaseChatModel):
    """Placeholder class - not actually used"""
    args: GPT4OMiniArgs = Field(default_factory=GPT4OMiniArgs)

    def generate_response(self, prompt: str) -> LLMResult:
        raise NotImplementedError("Please use deepseek or create your own interface")

    async def agenerate_response(self, prompt: str):
        raise NotImplementedError("Please use deepseek or create your own interface")

    def get_spend(self) -> int:
        return 0