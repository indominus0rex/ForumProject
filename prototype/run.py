"""Run sim -> loop, print metrics, write CSV. Usage: python prototype/run.py [--seconds 10] [--seed 7] [--csv prototype/out.csv]."""
import argparse
import math
import sys

sys.path.insert(0, "prototype")
from sim import Hand
from loop import Loop, MAX_DUTY


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=10.0)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--csv", default="prototype/out.csv")
    a = ap.parse_args()
    hand = Hand(seed=a.seed)
    loop = Loop()
    n = int(a.seconds * 100.0)
    res_before = 0.0
    res_after = 0.0
    duties = []
    lock_at = None
    locked_n = 0
    rows = []
    for i in range(n):
        x, y, z = hand.sample()
        duty, amp = loop.step(x, y, z)
        duties.append(duty)
        if loop.locked:
            locked_n += 1
            if lock_at is None:
                lock_at = i / 100.0
        # ideal-push residual model: push cancels sin component proportionally
        push = (duty / MAX_DUTY) * (1.0 if amp > 1e-9 else 0.0)
        left = max(0.0, amp - push * amp)
        res_before += amp * amp
        res_after += left * left
        rows.append((round(i / 100.0, 2), round(x, 4), round(amp, 4), duty, loop.locked))
    with open(a.csv, "w") as f:
        f.write("t,x,amp,duty,locked\n")
        for r in rows:
            f.write("%s,%s,%s,%s,%s\n" % r)
    import math as m
    ratio = m.sqrt(res_after / res_before) if res_before > 0 else 1.0
    print("residual_ratio=%.3f" % ratio)
    print("lock_time_s=%.2f" % (lock_at if lock_at is not None else -1))
    print("locked_frac=%.3f" % (locked_n / n))
    print("mean_duty=%.1f" % (sum(duties) / n))
    print("note=ideal-push model, not on-body effect; LRA force unmodeled")


if __name__ == "__main__":
    main()
