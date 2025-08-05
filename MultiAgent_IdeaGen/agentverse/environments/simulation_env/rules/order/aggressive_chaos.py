from __future__ import annotations

import random
from typing import TYPE_CHECKING, List

from . import order_registry as OrderRegistry
from .base import BaseOrder

if TYPE_CHECKING:
    from agentverse.environments import BaseEnvironment


@OrderRegistry.register("aggressive_chaos")
class AggressiveChaosOrder(BaseOrder):
    """
    Aggressive chaos designed to break normal conversation patterns:
    - High probability of interruptions and overlapping speech
    - Forces topic jumps and prevents linear discussion
    - Creates genuine chaos to test system limits
    """

    def get_next_agent_idx(self, environment: BaseEnvironment) -> List[int]:
        num_agents = len(environment.agents)
        current_turn = environment.cnt_turn
        max_turns = environment.max_turns
        
        # Final turn protection
        if current_turn >= max_turns - 1:
            return [num_agents - 1]
        
        available_agents = list(range(num_agents - 1))
        
        if not available_agents:
            return [0]
        
        # AGGRESSIVE CHAOS RULES (much higher chaos probability)
        
        # 50% chance of multiple people speaking at once (CHAOS!)
        if random.random() < 0.5:
            num_speakers = random.randint(2, min(4, len(available_agents)))
            return random.sample(available_agents, num_speakers)
        
        # 30% chance of forced interruption
        elif random.random() < 0.8:  # 0.5 + 0.3 = 0.8
            if len(environment.last_messages) > 0:
                last_speaker_name = environment.last_messages[-1].sender
                
                # Force someone DIFFERENT to interrupt
                interrupters = []
                for i in available_agents:
                    if environment.agents[i].name != last_speaker_name:
                        interrupters.append(i)
                
                if interrupters:
                    return [random.choice(interrupters)]
        
        # Only 20% chance of "normal" continuation
        return [random.choice(available_agents)]


@OrderRegistry.register("debate_chaos")
class DebateChaosOrder(BaseOrder):
    """
    Creates argumentative, competitive discussion dynamics
    Forces disagreement and intellectual combat
    """

    def get_next_agent_idx(self, environment: BaseEnvironment) -> List[int]:
        num_agents = len(environment.agents)
        current_turn = environment.cnt_turn
        max_turns = environment.max_turns
        
        # Final turn protection
        if current_turn >= max_turns - 1:
            return [num_agents - 1]
        
        available_agents = list(range(num_agents - 1))
        
        if not available_agents:
            return [0]
        
        # DEBATE-STYLE CHAOS
        
        # 40% chance of "argument pile-on" (multiple people respond to disagreement)
        if random.random() < 0.4 and len(available_agents) >= 3:
            # 3-4 people jump in to argue
            num_arguers = random.randint(3, min(4, len(available_agents)))
            return random.sample(available_agents, num_arguers)
        
        # 35% chance of direct challenge/interruption
        elif random.random() < 0.75:  # 0.4 + 0.35 = 0.75
            if len(environment.last_messages) > 0:
                last_speaker_name = environment.last_messages[-1].sender
                
                # Someone different challenges the last speaker
                challengers = []
                for i in available_agents:
                    if environment.agents[i].name != last_speaker_name:
                        challengers.append(i)
                
                if challengers:
                    return [random.choice(challengers)]
        
        # 25% chance of normal flow
        return [random.choice(available_agents)]


@OrderRegistry.register("total_chaos")
class TotalChaosOrder(BaseOrder):
    """
    Maximum chaos - designed to completely break conversation flow
    WARNING: This will likely produce incoherent results
    Use only for extreme stress testing
    """

    def get_next_agent_idx(self, environment: BaseEnvironment) -> List[int]:
        num_agents = len(environment.agents)
        current_turn = environment.cnt_turn
        max_turns = environment.max_turns
        
        print(f"[TOTAL_CHAOS DEBUG] Turn {current_turn}, {num_agents} total agents")
        
        # Final turn protection
        if current_turn >= max_turns - 1:
            print(f"[TOTAL_CHAOS DEBUG] Final turn - returning last agent: [{num_agents - 1}]")
            return [num_agents - 1]
        
        available_agents = list(range(num_agents - 1))
        print(f"[TOTAL_CHAOS DEBUG] Available agents: {available_agents}")
        
        if not available_agents:
            return [0]
        
        # TOTAL CHAOS - NO RULES!
        
        # 70% chance of multiple speakers (up to ALL conversation agents)
        if random.random() < 0.7:
            if len(available_agents) >= 5:
                # Sometimes EVERYONE speaks at once
                if random.random() < 0.3:
                    print(f"[TOTAL_CHAOS DEBUG] ALL AGENTS SPEAK: {available_agents}")
                    return available_agents  # ALL conversation agents speak!
                else:
                    num_speakers = random.randint(3, len(available_agents))
                    selected = random.sample(available_agents, num_speakers)
                    print(f"[TOTAL_CHAOS DEBUG] Multiple speakers ({num_speakers}): {selected}")
                    return selected
            else:
                num_speakers = random.randint(2, len(available_agents))
                selected = random.sample(available_agents, num_speakers)
                print(f"[TOTAL_CHAOS DEBUG] Multiple speakers ({num_speakers}): {selected}")
                return selected
        
        # 30% chance of single speaker (random)
        selected = [random.choice(available_agents)]
        print(f"[TOTAL_CHAOS DEBUG] Single speaker: {selected}")
        return selected