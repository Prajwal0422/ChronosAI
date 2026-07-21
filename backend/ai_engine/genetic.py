import random
import uuid
from copy import deepcopy
from collections import defaultdict

from ai_engine.models import CSPState
from ai_engine.constraints import (
    check_hard_constraints,
    filter_domain_state,
    count_soft_violations,
    slots_overlap,
)
from ai_engine.scoring import score_solution


POPULATION_SIZE = 50
GENERATIONS = 100
MUTATION_RATE = 0.15
TOURNAMENT_SIZE = 5
ELITE_COUNT = 3
ROOM_MUTATION_RATE = 0.10


def _random_individual(
    state: CSPState,
    domains: dict[int, list[uuid.UUID]],
) -> dict[int, uuid.UUID]:
    individual: dict[int, uuid.UUID] = {}
    for idx in range(len(state.assignments)):
        domain = domains.get(idx, [])
        individual[idx] = random.choice(domain) if domain else None
    return individual


def _assign_rooms_labs(
    state: CSPState,
    solution: dict[int, uuid.UUID],
) -> tuple[dict[uuid.UUID, uuid.UUID | None], dict[uuid.UUID, uuid.UUID | None]]:
    room_assignments: dict[uuid.UUID, uuid.UUID | None] = {}
    lab_assignments: dict[uuid.UUID, uuid.UUID | None] = {}
    used_classrooms: dict[uuid.UUID, set[uuid.UUID]] = defaultdict(set)
    used_labs: dict[uuid.UUID, set[uuid.UUID]] = defaultdict(set)
    slot_map = state.slot_map

    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        assignment = state.assignments[idx]
        if assignment.is_lab:
            for lab in state.laboratories:
                if lab.id not in used_labs[slot_id]:
                    lab_assignments[slot_id] = lab.id
                    used_labs[slot_id].add(lab.id)
                    break
            room_assignments[slot_id] = None
        else:
            for cr in state.classrooms:
                if cr.id not in used_classrooms[slot_id]:
                    room_assignments[slot_id] = cr.id
                    used_classrooms[slot_id].add(cr.id)
                    break
            lab_assignments[slot_id] = None

    return room_assignments, lab_assignments


def _repair(
    individual: dict[int, uuid.UUID],
    state: CSPState,
    domains: dict[int, list[uuid.UUID]],
) -> dict[int, uuid.UUID]:
    repaired = dict(individual)
    assigned = {}
    order = sorted(range(len(state.assignments)), key=lambda i: len(domains.get(i, [])))
    for idx in order:
        current = repaired[idx]
        if current and current in domains.get(idx, []):
            temp = dict(assigned)
            temp[idx] = current
            if check_hard_constraints(idx, current, temp, state):
                assigned[idx] = current
                continue
        domain = domains.get(idx, [])
        random.shuffle(domain)
        found = False
        for slot_id in domain:
            temp = dict(assigned)
            temp[idx] = slot_id
            if check_hard_constraints(idx, slot_id, temp, state):
                repaired[idx] = slot_id
                assigned[idx] = slot_id
                found = True
                break
        if not found:
            repaired[idx] = random.choice(domain) if domain else None
    return repaired


def _room_aware_crossover(
    parent1: dict[int, uuid.UUID],
    parent2: dict[int, uuid.UUID],
    state: CSPState,
) -> dict[int, uuid.UUID]:
    child: dict[int, uuid.UUID] = {}
    slot_map = state.slot_map

    for idx in parent1:
        if random.random() < 0.5:
            child[idx] = parent1[idx]
        else:
            child[idx] = parent2[idx]

    _resolve_crossover_overlaps(child, state, slot_map)
    return child


def _resolve_crossover_overlaps(
    child: dict[int, uuid.UUID],
    state: CSPState,
    slot_map: dict[uuid.UUID, uuid.UUID],
):
    teacher_slots: dict[uuid.UUID, list[tuple[int, uuid.UUID]]] = defaultdict(list)
    section_slots: dict[uuid.UUID, list[tuple[int, uuid.UUID]]] = defaultdict(list)

    for idx, slot_id in child.items():
        if slot_id is None:
            continue
        assignment = state.assignments[idx]
        teacher_slots[assignment.teacher_id].append((idx, slot_id))
        section_slots[assignment.section_id].append((idx, slot_id))

    for tid, entries in teacher_slots.items():
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                idx_i, sid_i = entries[i]
                idx_j, sid_j = entries[j]
                if sid_i == sid_j:
                    continue
                si = slot_map.get(sid_i)
                sj = slot_map.get(sid_j)
                if si and sj and slots_overlap(si, sj):
                    if random.random() < 0.5:
                        child[idx_j] = None
                    else:
                        child[idx_i] = None

    for sid, entries in section_slots.items():
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                idx_i, sid_i = entries[i]
                idx_j, sid_j = entries[j]
                if sid_i == sid_j:
                    continue
                si = slot_map.get(sid_i)
                sj = slot_map.get(sid_j)
                if si and sj and slots_overlap(si, sj):
                    if random.random() < 0.5:
                        child[idx_j] = None
                    else:
                        child[idx_i] = None


def _room_aware_mutate(
    individual: dict[int, uuid.UUID],
    domains: dict[int, list[uuid.UUID]],
) -> dict[int, uuid.UUID]:
    mutated = dict(individual)
    for idx in mutated:
        if random.random() < MUTATION_RATE:
            domain = domains.get(idx, [])
            if domain:
                current = mutated[idx]
                if current and len(domain) > 1:
                    alternatives = [s for s in domain if s != current]
                    if alternatives:
                        mutated[idx] = random.choice(alternatives)
                else:
                    mutated[idx] = random.choice(domain)
    return mutated


def _tournament_selection(
    population: list[dict[int, uuid.UUID]],
    fitness: list[float],
    k: int = TOURNAMENT_SIZE,
) -> dict[int, uuid.UUID]:
    best = None
    best_fitness = -1.0
    for _ in range(k):
        i = random.randint(0, len(population) - 1)
        if fitness[i] > best_fitness:
            best_fitness = fitness[i]
            best = population[i]
    return best


def _evaluate(
    individual: dict[int, uuid.UUID],
    state: CSPState,
) -> float:
    return score_solution(state, individual)


def genetic_refine(
    state: CSPState,
    initial_solution: dict[int, uuid.UUID] | None = None,
) -> dict[int, uuid.UUID]:
    domains = filter_domain_state(state)
    if not domains:
        return {}

    population: list[dict[int, uuid.UUID]] = []
    if initial_solution:
        repaired = _repair(initial_solution, state, domains)
        population.append(repaired)
        for _ in range(POPULATION_SIZE - 1):
            ind = _random_individual(state, domains)
            population.append(_repair(ind, state, domains))
    else:
        for _ in range(POPULATION_SIZE):
            ind = _random_individual(state, domains)
            population.append(_repair(ind, state, domains))

    fitness = [_evaluate(ind, state) for ind in population]

    for generation in range(GENERATIONS):
        new_population: list[dict[int, uuid.UUID]] = []

        elites = sorted(
            zip(population, fitness), key=lambda x: x[1], reverse=True
        )[:ELITE_COUNT]
        new_population.extend([deepcopy(e[0]) for e in elites])

        while len(new_population) < POPULATION_SIZE:
            p1 = _tournament_selection(population, fitness)
            p2 = _tournament_selection(population, fitness)
            child = _room_aware_crossover(p1, p2, state)
            child = _room_aware_mutate(child, domains)
            child = _repair(child, state, domains)
            new_population.append(child)

        population = new_population
        fitness = [_evaluate(ind, state) for ind in population]

    best_idx = max(range(len(fitness)), key=lambda i: fitness[i])
    return population[best_idx]
