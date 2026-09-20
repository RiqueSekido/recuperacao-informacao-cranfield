"""Consultas reformuladas manualmente para o experimento obrigatório."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QueryModification:
    query_id: str
    modified_text: str
    strategy: str


@dataclass
class QueryModificationResult:
    query_id: str
    original_text: str
    modified_text: str
    strategy: str
    rankings: dict[str, dict[str, list]]


QUERY_MODIFICATIONS = (
    QueryModification(
        "22",
        "turbulent skin friction viscosity temperature relationship",
        "simplificação e remoção de termos genéricos",
    ),
    QueryModification(
        "31",
        "end plate size two-dimensional flow bluff cylindrical body",
        "simplificação e foco nos termos técnicos",
    ),
    QueryModification(
        "44",
        "Chapman Enskog theory kinetic gases",
        "priorização do termo técnico central",
    ),
    QueryModification(
        "216",
        "wave system static pressure distribution liquid surface",
        "remoção de termos funcionais",
    ),
    QueryModification(
        "13",
        "transonic aileron buzz mechanism",
        "encurtamento e priorização de termos técnicos",
    ),
)
