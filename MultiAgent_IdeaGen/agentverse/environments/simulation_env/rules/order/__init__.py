from agentverse.registry import Registry
order_registry = Registry(name="OrderRegistry")

from .base import BaseOrder
from .sequential import SequentialOrder
from .random import RandomOrder
from .concurrent import ConcurrentOrder
from .classroom import ClassroomOrder
from .chaotic import ChaoticOrder, CompetitiveOrder, DisruptiveOrder
from .adversarial import AdversarialOrder, ToxicOrder
from .controlled_chaos import ControlledChaosOrder, DebateStyleOrder, LightChaosOrder, MediumChaosOrder, HighChaosOrder
from .intelligent_chaos import IntelligentChaosOrder, InterruptionChaosOrder
from .aggressive_chaos import AggressiveChaosOrder, DebateChaosOrder, TotalChaosOrder
