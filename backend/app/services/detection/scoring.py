from typing import Iterable


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def band_from_score(score: float) -> str:
    if score < 30:
        return "low"
    if score < 60:
        return "medium"
    return "high"


def lsb_balance_suspicion(balance: float) -> float:
    """
    Convert LSB one-ratio into suspicion score in [0, 1].

    If balance is very close to 0.5, it can be suspicious for LSB replacement.
    The farther from 0.5, the lower the suspicion.
    """
    distance = abs(balance - 0.5)
    score = 1.0 - (distance / 0.1)
    return clamp(score, 0.0, 1.0)


def entropy_suspicion(entropy_value: float) -> float:
    """
    LSB entropy close to 1.0 can indicate highly randomized embedding.
    """
    score = entropy_value / 1.0
    return clamp(score, 0.0, 1.0)


def consistency_suspicion(values: Iterable[float]) -> float:
    """
    If channel statistics are very similar, that can be mildly suspicious.
    We use low spread -> higher suspicion.
    """
    vals = list(values)
    if not vals:
        return 0.0

    spread = max(vals) - min(vals)
    score = 1.0 - (spread / 0.08)
    return clamp(score, 0.0, 1.0)


def combine_scores(
    balance_scores: list[float],
    entropy_scores: list[float],
    consistency_score: float,
) -> float:
    """
    Weighted heuristic total score in [0, 100].
    """
    avg_balance = sum(balance_scores) / len(balance_scores) if balance_scores else 0.0
    avg_entropy = sum(entropy_scores) / len(entropy_scores) if entropy_scores else 0.0

    final_score = (
        0.45 * avg_balance
        + 0.35 * avg_entropy
        + 0.20 * consistency_score
    ) * 100.0

    return round(clamp(final_score, 0.0, 100.0), 2)