from agentverse.registry import Registry

llm_registry = Registry(name="LLMRegistry")
LOCAL_LLMS = [
    "llama-2-7b-chat-hf",
    "llama-2-13b-chat-hf",
    "llama-2-70b-chat-hf",
    "vicuna-7b-v1.5",
    "vicuna-13b-v1.5",
]
LOCAL_LLMS_MAPPING = {
    "llama-2-7b-chat-hf": {
        "hf_model_name": "meta-llama/Llama-2-7b-chat-hf",
        "base_url": "http://localhost:5000/v1",
        "api_key": "EMPTY",
    },
    "llama-2-13b-chat-hf": {
        "hf_model_name": "meta-llama/Llama-2-13b-chat-hf",
        "base_url": "http://localhost:5000/v1",
        "api_key": "EMPTY",
    },
    "llama-2-70b-chat-hf": {
        "hf_model_name": "meta-llama/Llama-2-70b-chat-hf",
        "base_url": "http://localhost:5000/v1",
        "api_key": "EMPTY",
    },
    "vicuna-7b-v1.5": {
        "hf_model_name": "lmsys/vicuna-7b-v1.5",
        "base_url": "http://localhost:5000/v1",
        "api_key": "EMPTY",
    },
    "vicuna-13b-v1.5": {
        "hf_model_name": "lmsys/vicuna-13b-v1.5",
        "base_url": "http://localhost:5000/v1",
        "api_key": "EMPTY",
    },
}


# Base classes and main functionality
from .base import BaseLLM, BaseChatModel, BaseCompletionModel, LLMResult

# Main LLM implementations
from .deepseek import DeepSeekChat  # Primary LLM for this project

# Compatibility placeholders (not actively used)
from .openai import OpenAIChat
try:
    from .o1mini import *
except ImportError:
    pass  # Skip if module has issues
try:
    from .gpt_4omini import *
except ImportError:
    pass  # Skip if module has issues
