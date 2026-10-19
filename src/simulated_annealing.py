# sumber parameter dari Johnson dkk. (1989), Operations Research 37(6), dan Ben-Ameur (2004), COAP 29(3)
import math
import random
import time
from neighbor import get_neighbor_with_info
from objective import objective
from validator import is_valid

INITPROB = 0.4
TEMPFACTOR = 0.95
SIZEFACTOR = 16
MINPERCENT = 0.02
FROZEN_LIMIT = 5

def _acceptance_fraction(worse, T):
    return sum(math.exp(-w / T) for w in worse) / len(worse)

def find_initial_temperature(state, objective_fn, is_valid_fn, rng, n_samples, init_prob=INITPROB, iterations=60):
    base = objective_fn(state)
    worse = []
    for _ in range(n_samples):
        candidate, name = get_neighbor_with_info(state, rng, is_valid_fn)
        if name is None:
            continue
        d = objective_fn(candidate) - base
        if d < 0:
            worse.append(-d)
    if not worse:
        return 1.0
    scale = sum(worse) / len(worse)
    lo, hi = scale * 1e-6, scale * 1e6
    for _ in range(iterations):
        mid = math.sqrt(lo * hi)
        if _acceptance_fraction(worse, mid) < init_prob:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)

def simulated_annealing(initial_state, objective_fn=objective, is_valid_fn=is_valid, init_prob=INITPROB, temp_factor=TEMPFACTOR, size_factor=SIZEFACTOR, min_percent=MINPERCENT, frozen_limit=FROZEN_LIMIT, neighborhood_size=None, T0=None, max_iter=1_000_000, seed=None, verbose=False):
    rng = random.Random(seed) if seed is not None else random
    start = time.perf_counter()
    N = neighborhood_size or len(initial_state.packages)
    L = max(1, int(size_factor * N))
    if T0 is None:
        T0 = find_initial_temperature(initial_state, objective_fn, is_valid_fn, rng, n_samples=L, init_prob=init_prob)
    current = initial_state
    current_value = objective_fn(current)
    best, best_value = current, current_value
    history = [current_value]
    best_history = [best_value]
    prob_history, temp_history, acceptance_rate_history = [], [], []
    stuck_count, stuck_iterations = 0, []
    frozen_counter = 0
    accepted = 0
    move_counts = {"swap": 0, "move": 0, "rotate": 0, "none": 0}
    T = T0
    iteration = 0
    temperatures = 0
    stopped_by = "frozen"
    while frozen_counter < frozen_limit:
        temperatures += 1
        tried_worse, accepted_worse = 0, 0
        new_champion = False
        for _ in range(L):
            if iteration >= max_iter:
                break
            iteration += 1
            candidate, move_name = get_neighbor_with_info(current, rng, is_valid_fn)
            move_counts[move_name or "none"] += 1
            candidate_value = objective_fn(candidate)
            delta = candidate_value - current_value
            prob = 1.0 if delta > 0 else math.exp(delta / T)
            is_accepted = delta > 0 or rng.random() < prob
            if is_accepted:
                current, current_value = candidate, candidate_value
                if move_name is not None:
                    accepted += 1
            if delta < 0:
                tried_worse += 1
                accepted_worse += int(is_accepted)
            if current_value > best_value:
                best, best_value = current, current_value
                new_champion = True
                frozen_counter = 0
            history.append(current_value)
            best_history.append(best_value)
            prob_history.append(prob)
            temp_history.append(T)
        rate = accepted_worse / tried_worse if tried_worse else 0.0
        acceptance_rate_history.append(rate)
        if not new_champion:
            stuck_count += 1
            stuck_iterations.append(iteration)
        if rate <= min_percent:
            frozen_counter += 1
        if verbose:
            print(f"[SA] suhu ke-{temperatures:3d}  T={T:10.4f}  accept={rate:6.2%}  current={current_value:8}  best={best_value:8}  frozen={frozen_counter}")
        if iteration >= max_iter:
            stopped_by = "max_iter"
            break
        T *= temp_factor
    duration = time.perf_counter() - start

    return {
        "algorithm": "Simulated Annealing",
        "initial_state": initial_state,
        "initial_value": history[0],
        "final_state": current,
        "final_value": current_value,
        "best_state": best,
        "best_value": best_value,
        "history": history,
        "best_history": best_history,
        "prob_history": prob_history,
        "temp_history": temp_history,
        "acceptance_rate_history": acceptance_rate_history,
        "stuck_count": stuck_count,
        "stuck_iterations": stuck_iterations,
        "iterations": iteration,
        "temperatures": temperatures,
        "accepted_moves": accepted,
        "move_counts": move_counts,
        "stopped_by": stopped_by,
        "duration": duration,
        "params": {
            "T0": T0, "init_prob": init_prob, "temp_factor": temp_factor,
            "size_factor": size_factor, "neighborhood_size": N,
            "temp_length": L, "min_percent": min_percent,
            "frozen_limit": frozen_limit, "max_iter": max_iter, "seed": seed,
        },
    }