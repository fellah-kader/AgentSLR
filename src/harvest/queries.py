# src/harvest/queries.py

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import tomllib


PATHOGEN_CHOICES = (
    "marburg",
    "ebola",
    "lassa",
    "sars",
    "zika",
    "nipah",
    "rvf",
    "cchf",
    "mers",
    "alzheimers",
    "parkinsons",
    "multiple_sclerosis",
    "epilepsy",
    "stroke",
)

NEURO_CONDITIONS = (
    "alzheimers",
    "parkinsons",
    "multiple_sclerosis",
    "epilepsy",
    "stroke",
)

QUERIES_DIR = Path(__file__).with_name("queries")


@lru_cache(maxsize=None)
def load_query_table(filename: str, table_name: str) -> dict[str, str]:
    path = QUERIES_DIR / filename
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    return data[table_name]


@lru_cache(maxsize=None)
def load_neuro_query(condition: str) -> dict[str, str]:
    path = Path(__file__).parent.parent.parent / "data" / "agentslr" / "queries" / "neurology.toml"
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    entry = data[condition]
    return entry["boolean_query"]


def normalize_pathogen_name(name: str) -> str | None:
    cleaned = name.strip().lower()
    return cleaned if cleaned in PATHOGEN_CHOICES else None


def is_neuro_condition(name: str) -> bool:
    return name.strip().lower() in NEURO_CONDITIONS


def get_queries_for_pathogen(pathogen: str) -> dict[str, str]:
    normalized = normalize_pathogen_name(pathogen)
    if normalized is None:
        raise ValueError(f"Unsupported pathogen: {pathogen}")

    if is_neuro_condition(normalized):
        query = load_neuro_query(normalized)
        return {
            "pubmed": query,
            "openalex": query,
            "europepmc": query,
        }

    pubmed = load_query_table("pubmed.toml", "PATHOGEN_QUERIES_PUBMED")
    openalex = load_query_table("openalex.toml", "PATHOGEN_QUERIES_OPENALEX")

    return {
        "pubmed": pubmed[normalized],
        "openalex": openalex[normalized],
        "europepmc": openalex[normalized],
    }
