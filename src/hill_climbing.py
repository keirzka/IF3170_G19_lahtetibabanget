from generator import generate
from models import Package, Truck, State
from neighbor import get_neighbor_sample
from objective import objective, INVALID_VALUE
from time import time 
from typing import List
import random

MAXIMUM_SIDEWAYS_MOVE = 100

MAX_ITERATION = 1000

NUM_NEIGHBOR = 20

def steepest_ascent(truck : Truck, packages : List[Package], max_iteration = MAX_ITERATION)  :
    # Inisialisasi state
    initial_state = generate(truck, packages)

    current_state = initial_state
    current_value = objective(current_state)

    # Mulai timer
    start_time = time()

    # Membangkitkan tetangga dan memilih neighbor dengan value >= current state
    for i in range(max_iteration) : 
        neighbors = get_neighbor_sample(current_state, n = NUM_NEIGHBOR)

        if not neighbors : break

        best_neighbor, best_neighbor_value = get_best_state(neighbors)

        if(best_neighbor_value <= current_value) :
            break

        current_state = best_neighbor
        current_value = best_neighbor_value

    end_time = time()

    duration = end_time - start_time

    return i, duration, initial_state, current_state, current_value


def sideways_move(truck : Truck, packages : List[Package], max_iteration = MAX_ITERATION, max_sideways_move = MAXIMUM_SIDEWAYS_MOVE) :
    # Inisialisasi state
    initial_state = generate(truck, packages)

    current_state = initial_state
    current_value = objective(current_state)

    sideways_count = 0

    # Mulai timer
    start_time = time()

    # Membangkitkan tetangga dan memilih neighbor dengan value >= current state
    for i in range(max_iteration) : 
        neighbors = get_neighbor_sample(current_state, n = NUM_NEIGHBOR)

        if not neighbors : break

        best_neighbor, best_neighbor_value = get_best_state(neighbors)

        if(best_neighbor_value < current_value) :
            break

        # Kurangi Jatah Batasan Sideways Move (di shoulder)
        if(best_neighbor_value == current_value) : 
            if(sideways_count >= max_sideways_move) :
                break
                
            sideways_count += 1

        else : 
            sideways_count = 0

        current_state = best_neighbor
        current_value = best_neighbor_value

    end_time = time()

    duration = end_time - start_time

    return i, duration, initial_state, current_state, current_value

def random_restart(truck : Truck, packages : List[Package], max_restart) : 
    total_iteration = 0
    initial_state = None

    best_state = None
    best_value = INVALID_VALUE

    start_time = time()

    for i in range(max_restart) :
        it, _, init, finding, finding_value = steepest_ascent(truck, packages) 

        total_iteration += it

        if(not initial_state) : 
            initial_state = init

        if(finding_value > best_value) :
            best_state = finding
            best_value = finding_value

    end_time = time()

    duration = end_time - start_time

    return total_iteration, duration, initial_state, best_state, best_value
    
def stochastic(truck : Truck, packages : List[Package], max_iteration = MAX_ITERATION) : 
    # Inisialisasi state
    initial_state = generate(truck, packages)

    current_state = initial_state
    current_value = objective(current_state)

    # Mulai timer
    start_time = time()

    for i in range(max_iteration) : 
        neighbors = get_neighbor_sample(current_state, n = NUM_NEIGHBOR)

        if(not neighbors) : break

        random_neighbor = random.choice(neighbors)

        if(not random_neighbor) : break

        random_neighbor_value = objective(random_neighbor)

        # Ganti current state kalau neighbor random lebih baik
        if(random_neighbor_value > current_value) :
            current_state =  random_neighbor
            current_value = random_neighbor_value

    end_time = time()

    duration = end_time - start_time

    return i, duration, initial_state, current_state, current_value


# Helper : Get best State
def get_best_state(states : List[State]) :
        best = None
        best_value = INVALID_VALUE
        for s in states : 
            score = objective(s)
            if(score > best_value) : 
                best = s
                best_value = score

        return best, best_value