# src/evidence/run.py
"""
Runner script for the NeuroSLR Evidence Grader.
Reads included papers from abstract screening CSV and grades each one.
"""

from __future__ import annotations
import csv
import json
import logging
import os
from pathlib import Path
from openai import OpenAI
from src.evidence.grader import grade_all_papers, EvidenceGrade

logger = logging.getLogger(__name__)


def load_included_papers(screening_csv_path: Path) -> list[dict]:
    """Loads papers marked as INCLUDE from the abstract screening CSV."""
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
    logger.info(f"Loaded {len(included)} included papers for evidence grading")
    return included


def save_results(results: list[EvidenceGrade], output_path: Path) -> None:
    """Saves evidence grading results to a JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = []
    for r in results:
        data.append({
            "article_id": r.article_id,
            "title": r.title,
            "cebm_level": r.cebm_level,
            "cebm_label": r.cebm_label,
            "study_design": r.study_design,
            "sample_size": r.sample_size,
            "justification": r.justification,
            "confidence": r.confidence,
        })
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(data)} evidence grades to {output_path}")


def run_evidence_grading(config, logger) -> None:
    """
    Main entry point for evidence grading stage.
    Called from main.py pipeline dispatcher.
    """
    condition = config.pathogen
    screening_csv = config.client_root / "screening" / "abstract_screening.csv"

    if not screening_csv.exists():
        raise FileNotFoundError(
            f"Abstract screening results not found at {screening_csv}. "
            f"Run abstract_screen stage first."
        )

    included_papers = load_included_papers(screening_csv)

    if len(included_papers) == 0:
        logger.warning("No included papers found for evidence grading.")
        return

    # Set up LLM client
    llm_client = OpenAI(
        base_url=os.environ.get("OPENAI_BASE_URL", "https://api.groq.com/openai/v1"),
        api_key=os.environ.get("OPENAI_API_KEY", ""),
    )

    logger.info(f"Starting evidence grading for {condition} "
                f"with {len(included_papers)} included papers")

    results = grade_all_papers(
        included_papers=included_papers,
        condition=condition,
        llm_client=llm_client,
    )

    output_path = config.client_root / "evidence" / "evidence_grades.json"
    save_results(results, output_path)

    logger.info(f"Evidence grading complete — results saved to {output_path}")
