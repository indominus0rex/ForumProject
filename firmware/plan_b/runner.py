"""Select and run a plan_b combo by name with fallback chain."""
import importlib
from plan_b import PLAN_B_REGISTRY, FALLBACK_CHAIN


def load(name: str):
    mod = importlib.import_module(PLAN_B_REGISTRY[name])
    if not mod.GATE_OK:
        raise RuntimeError("plan_b %s quarantined: %s" % (name, mod.DESCRIPTION))
    return mod.Combo()


def run_with_fallback(frame: dict, chain=None):
    chain = chain or list(FALLBACK_CHAIN)
    last_err = None
    for name in chain:
        try:
            combo = load(name)
            return combo.process(frame)
        except RuntimeError as e:
            last_err = e
            continue
    raise RuntimeError("all plan_b combos failed: %s" % last_err)
