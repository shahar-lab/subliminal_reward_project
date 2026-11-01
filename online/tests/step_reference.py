"""Generate reference STEP runs from the Python implementation (tasks/calibration/step.py).
Usage (from the repository root): python online/tests/step_reference.py > online/tests/step_reference.json
Needs scipy. tests/test_step.js replays the same responses through js/step.js and compares."""
import json, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tasks.calibration.step import StepStaircase, StepParams

runs = []
for seed in range(12):
    rng = random.Random(seed)
    params = StepParams(max_trials=rng.choice([60, 120, 300]), min_trials=rng.choice([10, 50]),
                        cwir_stop=rng.choice([10, 50]))
    s = StepStaircase(params)
    true_thr = rng.uniform(0.1, 0.9)
    responses, logs = [], []
    while not s.done:
        x = s.intensity
        visible = x > true_thr
        seen = int(visible and rng.random() < 0.8 or rng.random() < 0.1)
        correct = int(rng.random() < (0.95 if visible else 0.5))
        responses.append([correct, seen])
        logs.append(s.update(correct, seen))
    runs.append({'params': params.__dict__, 'responses': responses,
                 'logs': [{k: (float(v) if isinstance(v, float) else v) for k, v in l.items()} for l in logs],
                 'threshold': s.threshold(), 'trials': s.trial, 'cap_reached': s.cap_reached})
json.dump(runs, sys.stdout)
