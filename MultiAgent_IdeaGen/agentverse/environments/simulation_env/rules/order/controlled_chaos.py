from __future__ import annotations

import random
from typing import TYPE_CHECKING, List

from . import order_registry as OrderRegistry
from .base import BaseOrder

if TYPE_CHECKING:
    from agentverse.environments import BaseEnvironment


@OrderRegistry.register("controlled_chaos")
class ControlledChaosOrder(BaseOrder):
    """
    Controlled chaos with strict anti-repetition rules
    Prevents the same agent from speaking more than twice consecutively
    Balances chaos with logical conversation flow
    """

    def get_next_agent_idx(self, environment: BaseEnvironment) -> List[int]:
        num_agents = len(environment.agents)
        current_turn = environment.cnt_turn
        max_turns = environment.max_turns
        
        # CRITICAL: If this is the final turn, always let the last agent (summarizer) speak
        if current_turn >= max_turns - 1:
            return [num_agents - 1]
        
        # Only apply chaos to conversation agents
        available_agents = list(range(num_agents - 1))
        
        if not available_agents:
            return [0]
        
        # Get recent speaker history to avoid excessive repetition
        recent_speakers = []
        if len(environment.last_messages) >= 3:
            for i in range(min(3, len(environment.last_messages))):
                recent_speakers.append(environment.last_messages[-(i+1)].sender)
        
        # Rule 1: Never allow 3+ consecutive speakers
        if len(recent_speakers) >= 2 and recent_speakers[0] == recent_speakers[1]:
            # Last two messages from same person, force different speaker
            excluded_name = recent_speakers[0]
            other_agents = []
            for i in available_agents:
                if environment.agents[i].name != excluded_name:
                    other_agents.append(i)
            
            if other_agents:
                # 20% chance of multiple speakers for mild chaos
                if random.random() < 0.2 and len(other_agents) >= 2:
                    num_speakers = random.randint(2, min(3, len(other_agents)))
                    return random.sample(other_agents, num_speakers)
                else:
                    return [random.choice(other_agents)]
        
        # Rule 2: Avoid immediate repetition unless specifically triggered
        if len(recent_speakers) >= 1:
            last_speaker = recent_speakers[0]
            
            # 15% chance of immediate repetition (controlled interruption)
            if random.random() < 0.15:
                for i in available_agents:
                    if environment.agents[i].name == last_speaker:
                        return [i]
            
            # 25% chance of multiple speakers (moderate chaos)
            elif random.random() < 0.40:  # 0.15 + 0.25 = 0.40
                # Exclude the immediate last speaker to force variety
                other_agents = []
                for i in available_agents:
                    if environment.agents[i].name != last_speaker:
                        other_agents.append(i)
                
                if len(other_agents) >= 2:
                    # Moderate chaos: 2-3 speakers (reduced from 2-4)
                    num_speakers = random.randint(2, min(3, len(other_agents)))
                    return random.sample(other_agents, num_speakers)
                elif other_agents:
                    return [random.choice(other_agents)]
        
        # Rule 3: Default random selection (60% of cases)
        return [random.choice(available_agents)]


@OrderRegistry.register("debate_style")
class DebateStyleOrder(BaseOrder):
    """
    Structured debate-style order with turn-taking
    Reduces chaos while maintaining engagement
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
        
        # Ensure no one speaks more than twice in a row
        if len(environment.last_messages) >= 2:
            last_speaker = environment.last_messages[-1].sender
            second_last_speaker = environment.last_messages[-2].sender
            
            if last_speaker == second_last_speaker:
                # Force different speaker
                other_agents = []
                for i in available_agents:
                    if environment.agents[i].name != last_speaker:
                        other_agents.append(i)
                
                if other_agents:
                    return [random.choice(other_agents)]
        
        # Normal random selection with slight preference for variety
        if len(environment.last_messages) >= 1:
            last_speaker = environment.last_messages[-1].sender
            
            # 70% chance to pick someone different
            if random.random() < 0.7:
                other_agents = []
                for i in available_agents:
                    if environment.agents[i].name != last_speaker:
                        other_agents.append(i)
                
                if other_agents:
                    return [random.choice(other_agents)]
        
        # Fallback to random
        return [random.choice(available_agents)]


@OrderRegistry.register("light_chaos")
class LightChaosOrder(BaseOrder):
    """
    Light chaos - minimal API overhead with occasional multiple speakers
    15% chance of 2-3 people speaking, optimized for efficiency
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
        
        # 15% chance of multiple speakers (minimal chaos)
        if random.random() < 0.15:
            if len(available_agents) >= 2:
                # Only 2-3 people, keep API calls reasonable
                num_speakers = random.randint(2, min(3, len(available_agents)))
                return random.sample(available_agents, num_speakers)
        
        # 85% chance of single speaker (mostly normal)
        # But still randomize to avoid pure sequential
        return [random.choice(available_agents)]


@OrderRegistry.register("medium_chaos")
class MediumChaosOrder(BaseOrder):
    """
    Medium chaos - 50% chance of multiple speakers
    More chaos than controlled_chaos but still manageable
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
        
        # 50% chance of multiple speakers (high chaos)
        if random.random() < 0.5:
            if len(available_agents) >= 3:
                # 3-5 people speak at once
                num_speakers = random.randint(3, min(5, len(available_agents)))
                return random.sample(available_agents, num_speakers)
            else:
                # If too few agents, all speak
                return available_agents
        
        # 30% chance of forced interruption
        elif random.random() < 0.8:  # 0.5 + 0.3 = 0.8
            if len(environment.last_messages) > 0:
                last_speaker_name = environment.last_messages[-1].sender
                # Someone different interrupts
                interrupters = []
                for i in available_agents:
                    if environment.agents[i].name != last_speaker_name:
                        interrupters.append(i)
                
                if interrupters:
                    return [random.choice(interrupters)]
        
        # 20% chance of normal random
        return [random.choice(available_agents)]


@OrderRegistry.register("high_chaos")  
class HighChaosOrder(BaseOrder):
    """
    High chaos - 70% multiple speakers, frequent interruptions
    Designed to stress test the conversation system
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
        
        # 70% chance of multiple speakers
        if random.random() < 0.7:
            # Very high chaos: up to 6 people or half the available agents
            max_speakers = min(6, max(2, len(available_agents) // 2))
            num_speakers = random.randint(2, max_speakers)
            return random.sample(available_agents, num_speakers)
        
        # 30% chance of single speaker (often interrupting)
        else:
            if len(environment.last_messages) > 0:
                last_speaker_name = environment.last_messages[-1].sender
                
                # 80% chance to interrupt with someone different
                if random.random() < 0.8:
                    others = []
                    for i in available_agents:
                        if environment.agents[i].name != last_speaker_name:
                            others.append(i)
                    
                    if others:
                        return [random.choice(others)]
            
            # Fallback to random
            return [random.choice(available_agents)]