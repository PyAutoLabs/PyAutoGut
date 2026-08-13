"""Reusable detector registry across component, matrix, and likelihood tiers."""

from .active_set import ActiveSetCheck
from .backend_divergence import BackendDivergenceCheck
from .conditioning_floor import ConditioningFloorCheck
from .likelihood_conditioning import LikelihoodConditioningCheck
from .nonfinite_gradient import NonFiniteGradientCheck
from .saturation import SaturationCheck
from .solver_divergence import SolverDivergenceCheck
from .structural_degeneracy import StructuralDegeneracyCheck

CHECKS = (
    SaturationCheck(),
    NonFiniteGradientCheck(),
    BackendDivergenceCheck(),
    ConditioningFloorCheck(),
    ActiveSetCheck(),
    LikelihoodConditioningCheck(),
    SolverDivergenceCheck(),
    StructuralDegeneracyCheck(),
)

__all__ = ["CHECKS"]
