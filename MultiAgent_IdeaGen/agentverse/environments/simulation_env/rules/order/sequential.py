from __future__ import annotations

from typing import TYPE_CHECKING, List

from . import order_registry as OrderRegistry
from .base import BaseOrder

if TYPE_CHECKING:
    from agentverse.environments import BaseEnvironment


@OrderRegistry.register("sequential")
class SequentialOrder(BaseOrder):
    """
    Order for sequential conversation
    The agents speak in a round-robin fashion
    """

    next_agent_idx: int = 0

    def get_next_agent_idx(self, environment: BaseEnvironment) -> List[int]:
        """Return the index of the next agent to speak"""
        # 如果是最后一轮，只让最后一个agent发言（idea）
        if environment.cnt_turn == environment.max_turns - 1:
            return [len(environment.agents) - 1]  # 只让最后一个agent发言
        # 前max_turns-1轮让所有对话agent轮流发言（除了最后一个idea agent）
        conversation_agents_count = len(environment.agents) - 1
        ret = self.next_agent_idx % conversation_agents_count
        self.next_agent_idx = (self.next_agent_idx + 1) % conversation_agents_count
        return [ret]

    def reset(self) -> None:
        self.next_agent_idx = 0
