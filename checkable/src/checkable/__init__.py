"""checkable: release an agent's database answers only when they can be checked, and say how often they are wrong.

- `receipts`: keep the read-only queries an answer rests on, and re-run them later.
- `periods`: the periods business questions name ("winter of 2023", "the past 3 quarters") and every reading.
"""
from .periods import Period, Reading, period_of, readings
from .receipts import Recheck, Receipt, Recorder, recheck, rows_hash

__all__ = ["Period", "Reading", "period_of", "readings", "Recheck", "Receipt", "Recorder", "recheck", "rows_hash"]
__version__ = "0.1.0"
