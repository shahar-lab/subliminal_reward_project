"""STEP staircase (Elbaz, Yaron & Mudrik, 2025, Behav Res Methods 58:13) - pure logic, no PsychoPy.

Ported from Eden Elbaz's implementation (ISI_calcu.py: boundary, calculate_next_ISI,
step_isi) as used in the paper's Experiment 3 (contrast calibration), with two
deliberate differences, both to follow the paper's text:

  1. Each sequence of consecutive incorrect answers enters the threshold ONCE
     (paper Eq. 5). In the original, when CWIR reached the stop value before the
     minimum number of trials, the open sequence was added at that moment and again
     when it ended, i.e. twice.
  2. The "seen & incorrect -> no change" rule applies only while the step is above
     the minimal step (paper: "before reaching the minimal step size"). The original
     compared floats exactly, so 0.2 - 3*0.05 = 0.05000000000000002 kept the rule
     active for one extra trial (trial 4). Steps are rounded here.

Per trial (t = 1, 2, ...), with intensity x shown and boundary B:
  a. Boundary test on all trials so far with intensity in [x, B] (incl. this one):
     one-tailed binomial (correct > 0.5); alpha = 0.05 / (CWIR_before_this_trial + 1).
     If p <= alpha:  B = (1 - seenRatio) * B + seenRatio * x   (seenRatio over the same trials).
  b. CWIR: an incorrect answer that is the k-th in a row adds k (so a run of k adds k(k+1)/2).
  c. Step = max(min_step, initial_step - step_decrease * (t - 1)).
     Correct -> down; incorrect -> up; but incorrect & seen -> no change while step > min_step.
     New x is clipped to [min_intensity, B].
  d. Done when CWIR >= cwir_stop and t >= min_trials; or t >= max_trials (cap, flagged).
  e. Threshold = CWIR-weighted mean of the mean intensity of each incorrect sequence.
"""
from dataclasses import dataclass

from scipy.stats import binomtest

STEP_DECIMALS = 10   # rounding used when comparing step sizes


@dataclass
class StepParams:
    start_intensity: float = 1.0
    max_intensity: float = 1.0
    min_intensity: float = 0.1
    initial_step: float = 0.2
    step_decrease: float = 0.05
    min_step: float = 0.05
    cwir_stop: int = 50
    min_trials: int = 50
    max_trials: int = 300
    alpha: float = 0.05


class StepStaircase:
    def __init__(self, params=None):
        self.p = params or StepParams()
        self.intensity = self.p.start_intensity     # intensity to show on the NEXT trial
        self.boundary = self.p.max_intensity
        self.trial = 0                              # number of completed trials
        self.cwir = 0                               # cumulative weighted incorrect responses
        self.history = []                           # (intensity, correct, seen) per trial
        self.sequences = []                         # (mean intensity, CWIR weight) per closed sequence
        self._run_len = 0                           # length of the current incorrect run
        self._run_weight = 0                        # CWIR accumulated by the current run
        self._run_intensities = []

    # ── the trial update ─────────────────────────────────────────────────────
    def update(self, correct, seen):
        """Register the response to the trial just shown at self.intensity.

        correct: 1/0 (objective 2AFC).  seen: 1 if PAS > 0 else 0.
        Returns a dict describing this trial (for the data file).
        """
        p = self.p
        correct, seen = int(bool(correct)), int(bool(seen))
        x = self.intensity
        self.trial += 1
        t = self.trial
        self.history.append((x, correct, seen))
        log = {'step_trial': t, 'intensity': x, 'correct': correct, 'seen': seen,
               'boundary_before': self.boundary, 'cwir_before': self.cwir}

        # a. upper boundary
        in_range = [h for h in self.history if x <= h[0] <= self.boundary]
        n = len(in_range)
        n_correct = sum(h[1] for h in in_range)
        seen_ratio = sum(h[2] for h in in_range) / n
        p_value = binomtest(n_correct, n, 0.5, alternative='greater').pvalue
        alpha = p.alpha / (1 + self.cwir)
        boundary_updated = p_value <= alpha
        if boundary_updated:
            self.boundary = (1 - seen_ratio) * self.boundary + seen_ratio * x
        log.update({'boundary_n_trials': n, 'boundary_n_correct': n_correct,
                    'boundary_seen_ratio': seen_ratio, 'boundary_p': p_value,
                    'boundary_alpha': alpha, 'boundary_updated': int(boundary_updated),
                    'boundary_after': self.boundary})

        # b. CWIR and incorrect sequences
        if correct:
            self._close_run()
        else:
            self._run_len += 1
            self._run_weight += self._run_len
            self._run_intensities.append(x)
            self.cwir += self._run_len

        # c. next intensity
        step = round(max(p.min_step, p.initial_step - p.step_decrease * (t - 1)), STEP_DECIMALS)
        direction = -1 if correct else 1
        seen_rule = (not correct) and seen and step > round(p.min_step, STEP_DECIMALS)
        applied = 0.0 if seen_rule else direction * step
        self.intensity = min(self.boundary, max(p.min_intensity, x + applied))

        log.update({'step': step, 'direction': direction, 'seen_rule_applied': int(seen_rule),
                    'applied_step': applied, 'next_intensity': self.intensity,
                    'cwir_after': self.cwir, 'incorrect_run_length': self._run_len,
                    'done': int(self.done), 'cap_reached': int(self.cap_reached)})
        return log

    def _close_run(self):
        if self._run_len:
            mean_x = sum(self._run_intensities) / len(self._run_intensities)
            self.sequences.append((mean_x, self._run_weight))
        self._run_len = 0
        self._run_weight = 0
        self._run_intensities = []

    # ── status ───────────────────────────────────────────────────────────────
    @property
    def converged(self):
        return self.cwir >= self.p.cwir_stop and self.trial >= self.p.min_trials

    @property
    def cap_reached(self):
        return self.trial >= self.p.max_trials and not self.converged

    @property
    def done(self):
        return self.converged or self.cap_reached

    def threshold(self):
        """CWIR-weighted mean intensity of all incorrect sequences (an open one counts once)."""
        sequences = list(self.sequences)
        if self._run_len:
            sequences.append((sum(self._run_intensities) / len(self._run_intensities), self._run_weight))
        total = sum(w for _, w in sequences)
        if total == 0:
            return None
        return sum(m * w for m, w in sequences) / total
