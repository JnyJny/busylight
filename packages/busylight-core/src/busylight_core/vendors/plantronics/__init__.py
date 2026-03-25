"""Plantronics status light devices."""

from .plantronics_base import PlantronicsBase as PlantronicsLights
from .status_indicator import StatusIndicator

__all__ = ["PlantronicsLights", "StatusIndicator"]
