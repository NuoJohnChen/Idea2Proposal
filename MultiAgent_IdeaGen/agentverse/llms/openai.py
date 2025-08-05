"""
Minimal openai.py - Only provides placeholders to avoid import errors
User uses deepseek, create your own py files for other interfaces if needed
"""
import numpy as np
from typing import Dict, List, Optional, Union
from pydantic import Field

from agentverse.llms.base import LLMResult
from agentverse.logging import logger
from . import llm_registry
from .base import BaseChatModel, BaseModelArgs

# Required placeholder variables
DEFAULT_CLIENT = None
DEFAULT_CLIENT_ASYNC = None
api_key = None
base_url = None

class OpenAIChatArgs(BaseModelArgs):
    """Placeholder class"""
    model: str = Field(default="gpt-4o")
    max_tokens: int = Field(default=2048)
    temperature: float = Field(default=1.0)
    top_p: int = Field(default=1)

class OpenAIChat(BaseChatModel):
    """Placeholder class - not actually used"""
    args: OpenAIChatArgs = Field(default_factory=OpenAIChatArgs)

    def __init__(self, max_retry: int = 3, **kwargs):
        args = OpenAIChatArgs().dict()
        for k, v in args.items():
            args[k] = kwargs.pop(k, v)
        super().__init__(args=args, max_retry=max_retry)
    
    def generate_response(self, *args, **kwargs) -> LLMResult:
        raise NotImplementedError("Please use deepseek or create your own interface")
    
    async def agenerate_response(self, *args, **kwargs) -> LLMResult:
        raise NotImplementedError("Please use deepseek or create your own interface")

    @classmethod
    def send_token_limit(self, model: str) -> int:
        return 4096

    def get_spend(self) -> int:
        return 0

def get_embedding(text: str, attempts=3) -> np.array:
    """Placeholder function"""
    logger.warn("get_embedding not configured, please use your own embedding service")
    return np.random.rand(1536).astype(np.float32)