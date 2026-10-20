import bisect
import copy
import random
import time
from itertools import accumulate

from generator import generate
from models import State
from neighbor import get_neighbor
from objective import objective
from validator import is_fit_in_truck, is_melayang, is_overlap, is_support


def clone_state(state):
    return State(state.trucks, [copy.copy(p) for p in state.packages])

def _can_add(cand, accepted, weight, truck):
    if weight + cand.weight > truck.max_capacity:
        return False
    if not is_fit_in_truck(cand, truck):
        return False
    for q in accepted:
        if is_overlap(cand, q):
            return False
    if is_melayang(cand, accepted + [cand]):
        return False
    for q in accepted:
        if q.is_fragile and is_support(q, [cand]):
            return False
    return True


def repair(state):
    original = [(p.position, p.truck_id) for p in state.packages]
    result = [copy.copy(p) for p in state.packages]
    for p in result:
        p.position = None

    order = sorted(
        (i for i, (pos, _) in enumerate(original) if pos is not None),
        key=lambda i: (original[i][0][2], i),
    )

    accepted = {t: [] for t in range(len(state.trucks))}
    weight = {t: 0 for t in range(len(state.trucks))}
    for i in order:
        pos, truck_id = original[i]
        if truck_id not in accepted:
            continue
        cand = result[i]
        cand.position = pos
        cand.truck_id = truck_id
        if _can_add(cand, accepted[truck_id], weight[truck_id], state.trucks[truck_id]):
            accepted[truck_id].append(cand)
            weight[truck_id] += cand.weight
        else:
            cand.position = None
    return State(state.trucks, result)

def make_roulette(population, fitness):
    cumulative = list(accumulate(fitness))
    total = cumulative[-1]

    def pick():
        if total <= 0:
            return random.choice(population)
        idx = bisect.bisect_right(cumulative, random.uniform(0, total))
        return population[min(idx, len(population) - 1)]

    return pick


def crossover(parent_x, parent_y):
    n = len(parent_x.packages)
    if n < 2:
        return repair(parent_x)
    point = random.randint(1, n - 1)
    genes = [
        copy.copy(parent_x.packages[i] if i < point else parent_y.packages[i])
        for i in range(n)
    ]
    return repair(State(parent_x.trucks, genes))


def mutate(state):
    return get_neighbor(state)

def genetic_algorithm(trucks, packages, population_size=50, generations=100,
                      mutation_rate=0.1, elitism=False, seed=None):
    if population_size < 2:
        raise ValueError("population_size minimal 2")
    if generations < 0:
        raise ValueError("generations tidak boleh negatif")
    if seed is not None:
        random.seed(seed)

    start = time.perf_counter()

    population = [generate(trucks, packages) for _ in range(population_size)]
    fitness = [max(0, objective(s)) for s in population]

    best_idx = max(range(population_size), key=fitness.__getitem__)
    initial_state = clone_state(population[best_idx])
    history = [(max(fitness), sum(fitness) / population_size)]

    for _ in range(generations):
        new_population = []
        if elitism:
            best_idx = max(range(population_size), key=fitness.__getitem__)
            new_population.append(clone_state(population[best_idx]))

        pick = make_roulette(population, fitness)
        while len(new_population) < population_size:
            child = crossover(pick(), pick())
            if random.random() < mutation_rate:
                child = mutate(child)
            new_population.append(child)

        population = new_population
        fitness = [max(0, objective(s)) for s in population]
        history.append((max(fitness), sum(fitness) / population_size))

    best_idx = max(range(population_size), key=fitness.__getitem__)
    duration = time.perf_counter() - start
    return generations, duration, initial_state, population[best_idx], fitness[best_idx], history