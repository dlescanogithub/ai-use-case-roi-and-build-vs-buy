"""Seeded Monte Carlo with triangular and PERT draws."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from roi_model.assumptions import CaseFile, Parameter, apply_parameter, assumptions_from_case
from roi_model.model import build_result


@dataclass(frozen=True)
class MonteCarloResult:
    draws: int
    seed: int
    npv_p10: float
    npv_p50: float
    npv_p90: float
    net_p10: float
    net_p50: float
    net_p90: float
    drivers: tuple[tuple[str, float], ...]


def percentile(values: list[float], p: float) -> float:
    """Linear interpolation percentile. ``p`` is in [0, 100]."""
    if not values:
        raise ValueError("percentile of an empty sample")
    if not 0 <= p <= 100:
        raise ValueError("percentile must be between 0 and 100")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (p / 100.0) * (len(ordered) - 1)
    low = math.floor(rank)
    high = math.ceil(rank)
    weight = rank - low
    return ordered[low] * (1.0 - weight) + ordered[high] * weight


def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    cursor = 0
    while cursor < len(values):
        end = cursor
        while end + 1 < len(values) and values[order[end + 1]] == values[order[cursor]]:
            end += 1
        average = (cursor + 1 + end + 1) / 2.0
        for position in range(cursor, end + 1):
            ranks[order[position]] = average
        cursor = end + 1
    return ranks


def _pearson(left: list[float], right: list[float]) -> float:
    count = len(left)
    mean_left = sum(left) / count
    mean_right = sum(right) / count
    numerator = sum((x - mean_left) * (y - mean_right) for x, y in zip(left, right, strict=True))
    spread_left = math.sqrt(sum((x - mean_left) ** 2 for x in left))
    spread_right = math.sqrt(sum((y - mean_right) ** 2 for y in right))
    if spread_left == 0 or spread_right == 0:
        return 0.0
    return numerator / (spread_left * spread_right)


def spearman(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("spearman needs two equal non-empty samples")
    return _pearson(_ranks(left), _ranks(right))


def sample_parameter(rng: random.Random, spec: Parameter) -> float:
    if spec.high == spec.low:
        return spec.low
    if spec.distribution == "triangular":
        return rng.triangular(spec.low, spec.high, spec.value)
    return _sample_pert(rng, spec.low, spec.value, spec.high)


def _sample_pert(rng: random.Random, low: float, mode: float, high: float, lamb: float = 4.0) -> float:
    span = high - low
    alpha = 1.0 + lamb * (mode - low) / span
    beta = 1.0 + lamb * (high - mode) / span
    draw = rng.betavariate(alpha, beta)
    return low + draw * span


def run_monte_carlo(case: CaseFile, *, draws: int, seed: int, override: float | None = None) -> MonteCarloResult:
    if draws < 1:
        raise ValueError("draws must be >= 1")
    rng = random.Random(seed)
    names = tuple(case.parameters)
    samples: dict[str, list[float]] = {name: [] for name in names}
    npvs: list[float] = []
    nets: list[float] = []
    for _ in range(draws):
        assumptions = assumptions_from_case(case, override=override)
        for name in names:
            drawn = sample_parameter(rng, case.parameters[name])
            assumptions = apply_parameter(assumptions, name, drawn)
            samples[name].append(drawn)
        result = build_result(assumptions)
        npvs.append(result.npv)
        nets.append(result.net_monthly_steady)
    drivers = tuple(
        sorted(
            ((name, spearman(samples[name], npvs)) for name in names),
            key=lambda item: abs(item[1]),
            reverse=True,
        )
    )
    return MonteCarloResult(
        draws=draws,
        seed=seed,
        npv_p10=percentile(npvs, 10),
        npv_p50=percentile(npvs, 50),
        npv_p90=percentile(npvs, 90),
        net_p10=percentile(nets, 10),
        net_p50=percentile(nets, 50),
        net_p90=percentile(nets, 90),
        drivers=drivers,
    )
