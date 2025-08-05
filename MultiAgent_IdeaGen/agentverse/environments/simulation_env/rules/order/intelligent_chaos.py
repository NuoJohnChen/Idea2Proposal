from __future__ import annotations

import random
from typing import TYPE_CHECKING, List

from . import order_registry as OrderRegistry
from .base import BaseOrder

if TYPE_CHECKING:
    from agentverse.environments import BaseEnvironment


@OrderRegistry.register("intelligent_chaos")
class IntelligentChaosOrder(BaseOrder):
    """
    Intelligent chaos that creates realistic discussion dynamics:
    1. Prevents content repetition by tracking speaker history
    2. Ensures context awareness by forcing response to recent content
    3. Implements realistic interruptions (mid-sentence breaks)
    4. Maintains logical conversation flow with controlled chaos
    """

    def get_next_agent_idx(self, environment: BaseEnvironment) -> List[int]:
        num_agents = len(environment.agents)
        current_turn = environment.cnt_turn
        max_turns = environment.max_turns
        
        # CRITICAL: Final turn protection
        if current_turn >= max_turns - 1:
            return [num_agents - 1]
        
        available_agents = list(range(num_agents - 1))
        
        if not available_agents:
            return [0]
        
        # Strategy 1: Prevent excessive repetition
        speaker_history = self._get_recent_speaker_history(environment, look_back=4)
        
        # Strategy 2: Force context responsiveness 
        should_respond_to_context = self._should_respond_to_recent_context(environment)
        
        # Strategy 3: Implement realistic interruptions
        should_interrupt = self._should_interrupt_current_speaker(environment)
        
        return self._select_next_speakers(
            available_agents, 
            environment, 
            speaker_history, 
            should_respond_to_context, 
            should_interrupt
        )
    
    def _get_recent_speaker_history(self, environment, look_back=4):
        """Get recent speaker names to prevent repetition"""
        history = []
        messages = environment.last_messages
        for i in range(min(look_back, len(messages))):
            history.append(messages[-(i+1)].sender)
        return history
    
    def _should_respond_to_recent_context(self, environment):
        """Determine if someone should directly respond to recent content"""
        if len(environment.last_messages) < 2:
            return False
        
        # 40% chance to force contextual response
        return random.random() < 0.4
    
    def _should_interrupt_current_speaker(self, environment):
        """Determine if current speaker should be interrupted"""
        if len(environment.last_messages) < 1:
            return False
        
        # 25% chance of interruption
        return random.random() < 0.25
    
    def _select_next_speakers(self, available_agents, environment, speaker_history, 
                            should_respond_to_context, should_interrupt):
        """Select next speaker(s) based on intelligent rules"""
        
        # Rule 1: Handle interruptions first
        if should_interrupt:
            return self._handle_interruption(available_agents, environment, speaker_history)
        
        # Rule 2: Force contextual responses
        if should_respond_to_context:
            return self._select_contextual_responder(available_agents, environment, speaker_history)
        
        # Rule 3: Prevent excessive same-speaker repetition
        if len(speaker_history) >= 2 and speaker_history[0] == speaker_history[1]:
            # Last speaker spoke twice, force different speaker
            return self._select_different_speaker(available_agents, environment, speaker_history[0])
        
        # Rule 4: Controlled chaos (20% multi-speaker, 80% single)
        if random.random() < 0.2:
            return self._select_multiple_speakers(available_agents, environment, speaker_history)
        else:
            return self._select_single_speaker(available_agents, environment, speaker_history)
    
    def _handle_interruption(self, available_agents, environment, speaker_history):
        """Handle interruption scenario"""
        if len(environment.last_messages) == 0:
            return [random.choice(available_agents)]
        
        last_speaker_name = environment.last_messages[-1].sender
        
        # Find someone different to interrupt
        interrupters = []
        for i in available_agents:
            if environment.agents[i].name != last_speaker_name:
                interrupters.append(i)
        
        if interrupters:
            # 30% chance multiple people interrupt at once (chaos!)
            if random.random() < 0.3 and len(interrupters) >= 2:
                num_interrupters = random.randint(2, min(3, len(interrupters)))
                return random.sample(interrupters, num_interrupters)
            else:
                return [random.choice(interrupters)]
        
        return [random.choice(available_agents)]
    
    def _select_contextual_responder(self, available_agents, environment, speaker_history):
        """Select someone to respond to recent context"""
        if len(environment.last_messages) == 0:
            return [random.choice(available_agents)]
        
        last_speaker_name = environment.last_messages[-1].sender
        
        # Prefer someone who hasn't spoken recently
        fresh_speakers = []
        for i in available_agents:
            agent_name = environment.agents[i].name
            if agent_name != last_speaker_name and agent_name not in speaker_history[:2]:
                fresh_speakers.append(i)
        
        if fresh_speakers:
            return [random.choice(fresh_speakers)]
        
        # Fallback: anyone except last speaker
        others = []
        for i in available_agents:
            if environment.agents[i].name != last_speaker_name:
                others.append(i)
        
        return [random.choice(others)] if others else [random.choice(available_agents)]
    
    def _select_different_speaker(self, available_agents, environment, excluded_name):
        """Force a different speaker than the excluded one"""
        others = []
        for i in available_agents:
            if environment.agents[i].name != excluded_name:
                others.append(i)
        
        if others:
            return [random.choice(others)]
        
        return [random.choice(available_agents)]
    
    def _select_multiple_speakers(self, available_agents, environment, speaker_history):
        """Select multiple speakers for chaos"""
        if len(available_agents) < 2:
            return [random.choice(available_agents)]
        
        # Avoid recent speakers in multi-speaker scenarios
        fresh_speakers = []
        for i in available_agents:
            agent_name = environment.agents[i].name
            if agent_name not in speaker_history[:2]:  # Not in last 2 speakers
                fresh_speakers.append(i)
        
        pool = fresh_speakers if len(fresh_speakers) >= 2 else available_agents
        num_speakers = random.randint(2, min(3, len(pool)))
        
        return random.sample(pool, num_speakers)
    
    def _select_single_speaker(self, available_agents, environment, speaker_history):
        """Select single speaker with variety preference"""
        if len(speaker_history) == 0:
            return [random.choice(available_agents)]
        
        last_speaker_name = speaker_history[0]
        
        # 70% chance to pick someone different
        if random.random() < 0.7:
            others = []
            for i in available_agents:
                if environment.agents[i].name != last_speaker_name:
                    others.append(i)
            
            if others:
                return [random.choice(others)]
        
        # 30% chance same speaker continues (but controlled)
        return [random.choice(available_agents)]


@OrderRegistry.register("interruption_chaos") 
class InterruptionChaosOrder(BaseOrder):
    """
    Specialized order for realistic interruptions and context-aware responses
    Focuses on creating natural discussion flow with strategic chaos
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
        
        # Get conversation context
        recent_messages = environment.last_messages[-3:] if len(environment.last_messages) >= 3 else environment.last_messages
        
        # Strategy selection based on conversation state
        if len(recent_messages) == 0:
            # First message
            return [random.choice(available_agents)]
        
        elif len(recent_messages) == 1:
            # Second message - high chance of direct response
            if random.random() < 0.8:
                return self._select_responder(available_agents, environment, recent_messages[-1].sender)
            else:
                return [random.choice(available_agents)]
        
        else:
            # Ongoing conversation - apply intelligent rules
            return self._apply_conversation_rules(available_agents, environment, recent_messages)
    
    def _select_responder(self, available_agents, environment, last_speaker_name):
        """Select someone to respond to the last speaker"""
        responders = []
        for i in available_agents:
            if environment.agents[i].name != last_speaker_name:
                responders.append(i)
        
        return [random.choice(responders)] if responders else [random.choice(available_agents)]
    
    def _apply_conversation_rules(self, available_agents, environment, recent_messages):
        """Apply intelligent conversation flow rules"""
        last_speaker = recent_messages[-1].sender
        
        # Check for repetitive speakers
        speaker_counts = {}
        for msg in recent_messages:
            speaker_counts[msg.sender] = speaker_counts.get(msg.sender, 0) + 1
        
        # Rule 1: If someone dominated recent conversation, force others
        if speaker_counts.get(last_speaker, 0) >= 2:
            others = []
            for i in available_agents:
                if environment.agents[i].name != last_speaker:
                    others.append(i)
            
            if others:
                # 15% chance of interruption by multiple people
                if random.random() < 0.15 and len(others) >= 2:
                    return random.sample(others, 2)
                else:
                    return [random.choice(others)]
        
        # Rule 2: 30% interruption chance
        if random.random() < 0.3:
            # Someone interrupts
            interrupters = []
            for i in available_agents:
                if environment.agents[i].name != last_speaker:
                    interrupters.append(i)
            
            return [random.choice(interrupters)] if interrupters else [random.choice(available_agents)]
        
        # Rule 3: 40% contextual response
        elif random.random() < 0.7:  # 0.3 + 0.4 = 0.7
            return self._select_responder(available_agents, environment, last_speaker)
        
        # Rule 4: 30% random continuation
        else:
            return [random.choice(available_agents)]