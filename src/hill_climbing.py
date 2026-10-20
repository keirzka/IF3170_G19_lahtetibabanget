import time
from generator import generate
from neighbor import get_neighbor_with_info, get_neighbor_sample
from objective import INVALID_VALUE, objective

MAX_ITERATION = 1000
NUM_NEIGHBOR = 20
MAXIMUM_SIDEWAYS_MOVE = 100
MAXIMUM_RESTART = 5

def get_best_state(states):
    best, best_value = None, INVALID_VALUE
    for s in states:
        score = objective(s)
        if score > best_value:
            best, best_value = s, score
    return best, best_value

def _result(initial_value, final_state, final_value, iterations, history, start, **extra):
    result = {
        "initial_value": initial_value,
        "final_state": final_state,
        "final_value": final_value,
        "iterations": iterations,
        "history": history,
        "duration": time.perf_counter() - start,
    }
    result.update(extra)
    return result

def steepest_ascent(initial_state, max_iteration=MAX_ITERATION, num_neighbor=NUM_NEIGHBOR):
    start = time.perf_counter()
    current, current_value = initial_state, objective(initial_state)
    history = [current_value]
    iterations = 0

    while iterations < max_iteration:
        iterations += 1
        neighbors = get_neighbor_sample(current, num_neighbor)
        if not neighbors:
            break
        best, best_value = get_best_state(neighbors)
        if best_value <= current_value:
            break
        current, current_value = best, best_value
        history.append(current_value)

    return _result(history[0], current, current_value, iterations, history, start,
                   max_iteration=max_iteration, num_neighbor=num_neighbor)

def sideways_move(initial_state, max_iteration=MAX_ITERATION,
                  max_sideways_move=MAXIMUM_SIDEWAYS_MOVE, num_neighbor=NUM_NEIGHBOR):
    start = time.perf_counter()
    current, current_value = initial_state, objective(initial_state)
    history = [current_value]
    iterations = 0
    consecutive_sideways = 0
    total_sideways = 0

    while iterations < max_iteration:
        iterations += 1
        neighbors = get_neighbor_sample(current, num_neighbor)
        if not neighbors:
            break
        best, best_value = get_best_state(neighbors)
        if best_value < current_value:
            break
        if best_value == current_value:
            if consecutive_sideways >= max_sideways_move:
                break
            consecutive_sideways += 1
            total_sideways += 1
        else:
            consecutive_sideways = 0
        current, current_value = best, best_value
        history.append(current_value)

    return _result(history[0], current, current_value, iterations, history, start,
                   max_iteration=max_iteration, num_neighbor=num_neighbor,
                   max_sideways_move=max_sideways_move, sideways_moves=total_sideways)

def stochastic(initial_state, max_iteration=MAX_ITERATION):
    start = time.perf_counter()
    current, current_value = initial_state, objective(initial_state)
    history = [current_value]
    iterations = 0

    while iterations < max_iteration:
        iterations += 1
        neighbor, move = get_neighbor_with_info(current)
        if move is None:
            break
        neighbor_value = objective(neighbor)
        if neighbor_value > current_value:
            current, current_value = neighbor, neighbor_value
        history.append(current_value)

    return _result(history[0], current, current_value, iterations, history, start,
                   max_iteration=max_iteration)

def random_restart(initial_state, max_restart=MAXIMUM_RESTART, max_iteration=MAX_ITERATION,
                   num_neighbor=NUM_NEIGHBOR):
    start = time.perf_counter()
    best, best_value = None, INVALID_VALUE
    history = []
    iterations_per_restart = []
    value_per_restart = []

    state = initial_state
    for attempt in range(max_restart + 1):
        if attempt > 0:
            state = generate(initial_state.trucks, initial_state.packages)
        result = steepest_ascent(state, max_iteration, num_neighbor)
        iterations_per_restart.append(result["iterations"])
        value_per_restart.append(result["final_value"])
        history.extend(result["history"])
        if result["final_value"] > best_value:
            best, best_value = result["final_state"], result["final_value"]

    return _result(objective(initial_state), best, best_value, sum(iterations_per_restart),
                   history, start, max_restart=max_restart, restarts=max_restart,
                   iterations_per_restart=iterations_per_restart,
                   value_per_restart=value_per_restart, num_neighbor=num_neighbor)