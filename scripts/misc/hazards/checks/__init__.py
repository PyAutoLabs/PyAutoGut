"""Phase-one detector registry."""

from .backend_divergence import BackendDivergenceCheck
from .conditioning_floor import ConditioningFloorCheck
from .nonfinite_gradient import NonFiniteGradientCheck
from .saturation import SaturationCheck

CHECKS = (
    SaturationCheck(),
    NonFiniteGradientCheck(),
    BackendDivergenceCheck(),
    ConditioningFloorCheck(),
)

__all__ = ["CHECKS"]
