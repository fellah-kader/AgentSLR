# src/contradiction/run.py
"""
Runner script for the NeuroSLR Contradiction Analyser.
Reads included papers from abstract screening CSV and runs pairwise analysis.
"""

from __future__ import annotations
import csv
import json
import logging
import os
from pathlib import Path
from openai import OpenAI
from src.contradiction.analyser import analyse_all_pairs, ContradictionResult

logger = logging.getLogger(__name__)


def load_included_papers(screening_csv_path: Path) -> list[dict]:
    """
    Loads papers marked as INCLUDE from the abstract screening CSV.
    Returns a list of paper dictionaries.
    """
    included = []
    with open(screening_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("ai4epi_abstract_decision", "").strip().upper() == "INCLUDE":
                included.append({
                    "article_id": row.get("article_id", "unknown"),
                    "title": row.get("title", "No title"),
                    "abstract": row.get("abstract", "No abstract"),
                })
    logger.info(f"Loaded {len(included)} included papers for contradiction analysis")
    return included


def save_results(results: list[ContradictionResult], output_path: Path) -> None:
    """Saves contradiction results to a JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = []
    for r in results:
        data.append({
            "paper_a_id": r.paper_a_id,
            "paper_b_id": r.paper_b_id,
            "paper_a_title": r.paper_a_title,
            "paper_b_title": r.paper_b_title,
            "has_contradiction": r.has_contradiction,
            "severity": r.severity,
            "contradiction_type": r.contradiction_type,
            "description": r.description,
            "paper_a_claim": r.paper_a_claim,
            "paper_b_claim": r.paper_b_claim,
            "confidence": r.confidence,
        })
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(data)} contradiction results to {output_path}")


def run_contradiction_analysis(config, logger) -> None:
    """
    Main entry point for contradiction analysis stage.
    Called from main.py pipeline dispatcher.
    """
    condition = config.pathogen
    screening_csv = (
        config.client_root / "screening" / "abstract_screening.csv"
    )

    if not screening_csv.exists():
        raise FileNotFoundError(
            f"Abstract screening results not found at {screening_csv}. "
            f"Run abstract_screen stage first."
        )

    # Load included papers
    included_papers = load_included_papers(screening_csv)

    if len(included_papers) < 2:
        logger.warning(
            f"Only {len(included_papers)} included paper(s) found. "
            f"Need at least 2 papers for contradiction analysis."
        )
        return

    # Set up LLM client (Groq via OpenAI-compatible API)
    llm_client = OpenAI(
        base_url=os.environ.get("OPENAI_BASE_URL", "https://api.groq.com/openai/v1"),
        api_key=os.environ.get("OPENAI_API_KEY", ""),
    )

    # Run analysis
    logger.info(f"Starting contradiction analysis for {condition} "
                f"with {len(included_papers)} included papers")

    results = analyse_all_pairs(
        included_papers=included_papers,
        condition=condition,
        llm_client=llm_client,
        max_pairs=50,
    )

    # Save results
    output_path = config.client_root / "contradiction" / "contradiction_results.json"
    save_results(results, output_path)

    # Print summary
    contradictions = [r for r in results if r.has_contradiction]
    logger.info(f"Contradiction analysis complete:")
    logger.info(f"  Total pairs analysed: {len(results)}")
    logger.info(f"  Contradictions found: {len(contradictions)}")
    for r in contradictions:
        logger.info(f"  [{r.severity.upper()}] {r.paper_a_id} vs {r.paper_b_id}: {r.contradiction_type}")
