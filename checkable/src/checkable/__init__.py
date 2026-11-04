"""checkable: release an agent's database answers only when they can be checked, and say how often they are wrong.

- `periods`: the periods business questions name ("winter of 2023", "the past 3 quarters") and every reading.
"""
from .periods import Period, Reading, period_of, readings

__all__ = ["Period", "Reading", "period_of", "readings"]
__version__ = "0.1.0"
