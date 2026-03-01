"""Lógica de participantes e sorteio de vencedores."""

from __future__ import annotations

import random


def unique_participants(authors: list[str]) -> list[str]:
    """Remove duplicados preservando a ordem de primeira aparição."""

    return list(dict.fromkeys(authors))


def draw_winners(
    participants: list[str], winners_count: int, seed: int | None = None
) -> list[str]:
    """Sorteia vencedores únicos a partir da lista de participantes."""

    if winners_count <= 0:
        raise ValueError("winners_count deve ser maior que zero.")
    if winners_count > len(participants):
        raise ValueError("winners_count não pode ser maior que o total de participantes.")

    rng = random.Random(seed)
    return rng.sample(participants, winners_count)
