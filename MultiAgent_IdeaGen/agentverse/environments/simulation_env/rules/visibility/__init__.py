from typing import Dict

from agentverse.registry import Registry

visibility_registry = Registry(name="VisibilityRegistry")

from .base import BaseVisibility
from .all import AllVisibility
from .classroom import ClassroomVisibility
from .oneself import OneselfVisibility
