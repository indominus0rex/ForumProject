"""Gate for the prototype: run default sim, assert sane metrics. stdlib only."""
import subprocess
import sys

r = subprocess.run([sys.executable, "prototype/run.py", "--seconds", "10",
                    "--seed", "7", "--csv", "prototype/out.csv"],
                   capture_output=True, text=True, cwd=".")
assert r.returncode == 0, "run.py failed:\n" + r.stderr
lines = r.stdout.strip().splitlines()
get = {}
for ln in lines:
    if "=" in ln and ln.split("=", 1)[0].strip() in (
            "residual_ratio", "lock_time_s", "locked_frac", "mean_duty"):
        k, v = ln.split("=", 1)
        get[k.strip()] = float(v)
for k in ("residual_ratio", "lock_time_s", "locked_frac", "mean_duty"):
    assert k in get, "missing metric %r in:\n%s" % (k, r.stdout)
assert get["residual_ratio"] < 1.0, "suppression must remove something"
assert 0.0 < get["lock_time_s"] < 5.0, "must lock within 5 s, got %r" % get["lock_time_s"]
assert get["locked_frac"] > 0.8, "must stay locked, got %r" % get["locked_frac"]
print("prototype check passed!")
