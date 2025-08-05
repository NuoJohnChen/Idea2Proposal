from __future__ import annotations

import random
from typing import TYPE_CHECKING, List

from . import order_registry as OrderRegistry
from .base import BaseOrder

if TYPE_CHECKING:
    from agentverse.environments import BaseEnvironment


@OrderRegistry.register("chaotic")
class ChaoticOrder(BaseOrder):
    """
    Chaotic order designed to create confusion and interruptions
    Multiple agents can speak simultaneously, creating overlapping conversations
    This is designed for ablation studies to test system robustness
    IMPORTANT: The final turn always goes to the last agent (tool type) for proper summarization
    """

    def get_next_agent_idx(self, environment: BaseEnvironment) -> List[int]:
        num_agents = len(environment.agents)
        current_turn = environment.cnt_turn
        max_turns = environment.max_turns
        
        # CRITICAL: If this is the final turn, always let the last agent (summarizer) speak
        if current_turn >= max_turns - 1:
            return [num_agents - 1]  # Last agent is typically the tool/summarizer
        
        # Only apply chaos to conversation agents (not the final summarizer)
        available_agents = list(range(num_agents - 1))  # Exclude last agent from chaos
        
        if not available_agents:
            return [0]  # Fallback
        
        # 30% chance of multiple agents speaking at once (chaos)
        if random.random() < 0.3:
            # 2-4 conversation agents speak simultaneously
            num_speakers = random.randint(2, min(4, len(available_agents)))
            return random.sample(available_agents, num_speakers)
        
        # 40% chance of random single speaker
        elif random.random() < 0.7:
            return [random.choice(available_agents)]
        
        # 30% chance of the same agent speaking twice in a row (interruption)
        else:
            if len(environment.last_messages) > 0:
                last_speaker_name = environment.last_messages[-1].sender
                
                # Check if the last speaker already spoke in the previous turn
                # Avoid triple consecutive speaking
                if len(environment.last_messages) >= 2:
                    second_last_speaker = environment.last_messages[-2].sender
                    if last_speaker_name == second_last_speaker:
                        # Already spoke twice in a row, force different speaker
                        other_agents = []
                        for i in available_agents:
                            if environment.agents[i].name != last_speaker_name:
                                other_agents.append(i)
                        if other_agents:
                            return [random.choice(other_agents)]
                
                # Allow same speaker to continue (max 2 times in a row)
                for i in available_agents:
                    if environment.agents[i].name == last_speaker_name:
                        return [i]
            
            # Fallback to random conversation agent
            return [random.choice(available_agents)]


@OrderRegistry.register("competitive")
class CompetitiveOrder(BaseOrder):
    """
    Competitive order where agents "fight" to speak
    Simulates an argumentative discussion where everyone wants to interrupt
    IMPORTANT: The final turn always goes to the last agent (tool type) for proper summarization
    """

    def get_next_agent_idx(self, environment: BaseEnvironment) -> List[int]:
        num_agents = len(environment.agents)
        current_turn = environment.cnt_turn
        max_turns = environment.max_turns
        
        # CRITICAL: If this is the final turn, always let the last agent (summarizer) speak
        if current_turn >= max_turns - 1:
            return [num_agents - 1]  # Last agent is typically the tool/summarizer
        
        # Only apply competition to conversation agents
        available_agents = list(range(num_agents - 1))  # Exclude last agent from competition
        
        if not available_agents:
            return [0]  # Fallback
        
        # First turn - random start
        if len(environment.last_messages) == 0:
            return [random.choice(available_agents)]
        
        # 50% chance of interruption (multiple speakers)
        if random.random() < 0.5:
            # 2-3 conversation agents try to speak at once
            num_speakers = random.randint(2, min(3, len(available_agents)))
            return random.sample(available_agents, num_speakers)
        else:
            # Single speaker, but avoid the last speaker to create topic jumps
            last_speaker_name = environment.last_messages[-1].sender
            other_agents = []
            for i in available_agents:
                if environment.agents[i].name != last_speaker_name:
                    other_agents.append(i)
            
            if other_agents:
                return [random.choice(other_agents)]
            else:
                return [random.choice(available_agents)]


@OrderRegistry.register("disruptive")
class DisruptiveOrder(BaseOrder):
    """
    Highly disruptive order designed to maximize confusion
    Combines random timing, interruptions, and topic jumping
    IMPORTANT: The final turn always goes to the last agent (tool type) for proper summarization
    """
    
    def get_next_agent_idx(self, environment: BaseEnvironment) -> List[int]:
        num_agents = len(environment.agents)
        current_turn = environment.cnt_turn
        max_turns = environment.max_turns
        
        # CRITICAL: If this is the final turn, always let the last agent (summarizer) speak
        if current_turn >= max_turns - 1:
            return [num_agents - 1]  # Last agent is typically the tool/summarizer
        
        # Only apply disruption to conversation agents
        available_agents = list(range(num_agents - 1))  # Exclude last agent from disruption
        
        if not available_agents:
            return [0]  # Fallback
        
        # Every 3-5 turns, create chaos with multiple conversation agents
        if current_turn % random.randint(3, 5) == 0:
            num_speakers = random.randint(2, len(available_agents))
            return random.sample(available_agents, num_speakers)
        
        # 60% chance of topic disruption (different speaker than expected)
        elif random.random() < 0.6:
            return [random.choice(available_agents)]
        
        # 40% chance of double-speaking (same agent continues)
        else:
            if len(environment.last_messages) > 0:
                last_speaker_name = environment.last_messages[-1].sender
                for i in available_agents:
                    if environment.agents[i].name == last_speaker_name:
                        return [i]
            return [random.choice(available_agents)]