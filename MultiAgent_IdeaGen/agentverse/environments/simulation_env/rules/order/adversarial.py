from __future__ import annotations

import random
from typing import TYPE_CHECKING, List

from . import order_registry as OrderRegistry
from .base import BaseOrder

if TYPE_CHECKING:
    from agentverse.environments import BaseEnvironment


@OrderRegistry.register("adversarial")
class AdversarialOrder(BaseOrder):
    """
    Adversarial order designed to create genuine conflicts and debates
    Introduces competitive dynamics and opposing viewpoints
    IMPORTANT: The final turn always goes to the last agent (tool type) for proper summarization
    """

    def get_next_agent_idx(self, environment: BaseEnvironment) -> List[int]:
        num_agents = len(environment.agents)
        current_turn = environment.cnt_turn
        max_turns = environment.max_turns
        
        # CRITICAL: If this is the final turn, always let the last agent (summarizer) speak
        if current_turn >= max_turns - 1:
            return [num_agents - 1]
        
        # Only apply adversarial logic to conversation agents
        available_agents = list(range(num_agents - 1))
        
        if not available_agents:
            return [0]
        
        # 40% chance of direct confrontation (multiple opposing voices)
        if random.random() < 0.4:
            # Select 2-3 agents for opposing viewpoints
            num_speakers = random.randint(2, min(3, len(available_agents)))
            return random.sample(available_agents, num_speakers)
        
        # 30% chance of interrupting the last speaker
        elif random.random() < 0.7 and len(environment.last_messages) > 0:
            last_speaker_name = environment.last_messages[-1].sender
            other_agents = []
            for i in available_agents:
                if environment.agents[i].name != last_speaker_name:
                    other_agents.append(i)
            
            if other_agents:
                return [random.choice(other_agents)]
            else:
                return [random.choice(available_agents)]
        
        # 30% chance of normal single speaker
        else:
            return [random.choice(available_agents)]


@OrderRegistry.register("toxic")
class ToxicOrder(BaseOrder):
    """
    Extremely disruptive order designed to create maximum conflict
    WARNING: This may lead to completely broken discussions
    Use only for stress testing the system's limits
    """

    def get_next_agent_idx(self, environment: BaseEnvironment) -> List[int]:
        num_agents = len(environment.agents)
        current_turn = environment.cnt_turn
        max_turns = environment.max_turns
        
        # CRITICAL: If this is the final turn, always let the last agent (summarizer) speak
        if current_turn >= max_turns - 1:
            return [num_agents - 1]
        
        available_agents = list(range(num_agents - 1))
        
        if not available_agents:
            return [0]
        
        # 60% chance of chaos (3-5 people speaking at once)
        if random.random() < 0.6:
            num_speakers = random.randint(3, min(5, len(available_agents)))
            return random.sample(available_agents, num_speakers)
        
        # 40% chance of single agent, but likely interrupting
        else:
            return [random.choice(available_agents)]