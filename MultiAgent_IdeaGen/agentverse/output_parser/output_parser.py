from __future__ import annotations

from abc import abstractmethod
from typing import Union, NamedTuple, TYPE_CHECKING

from . import output_parser_registry
from agentverse.utils import AgentAction, AgentFinish
from agentverse.llms import LLMResult
from pydantic import BaseModel

if TYPE_CHECKING:
    from agentverse.agents.base import BaseAgent
    from agentverse.environments.base import BaseEnvironment


class OutputParserError(Exception):
    """Exception raised when parsing output from a command fails."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "Failed to parse output of the model:%s\n " % self.message


class OutputParser(BaseModel):
    """Base class for output parsers."""

    @abstractmethod
    def parse(self, output: LLMResult) -> NamedTuple:
        pass


@output_parser_registry.register("dummy")
class CommonParser2(OutputParser):
    """Universal parser - directly returns content as AgentFinish"""
    def parse(self, output: LLMResult) -> Union[AgentAction, AgentFinish]:
        return AgentFinish({"output": output.content}, output.content)