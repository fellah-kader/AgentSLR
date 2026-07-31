# src/screening/prompts.py
from __future__ import annotations

from functools import lru_cache
from pathlib import Path


WHO_PATHOGENS = {
    "cchf": "Crimean-Congo haemorrhagic fever virus",
    "rvf": "Rift Valley fever virus",
    "marburg": "Marburg virus",
    "ebola": "Ebola virus",
    "lassa": "Lassa fever or Lassa mammarenavirus",
    "mers": "Middle East respiratory syndrome coronavirus (MERS-CoV)",
    "sars": "Severe Acute Respiratory Syndrome coronavirus (SARS-CoV)",
    "zika": "Zika virus",
    "nipah": "Henipa virus (Nipah virus, Hendra virus)",
}

NEURO_CONDITIONS = {
    "alzheimers": "Alzheimer's Disease",
    "parkinsons": "Parkinson's Disease",
    "multiple_sclerosis": "Multiple Sclerosis",
    "epilepsy": "Epilepsy",
    "stroke": "Stroke",
}

NEURO_INCLUSION = {
    "alzheimers": [
        "Studies involving patients with confirmed Alzheimer's disease or mild cognitive impairment",
        "Studies reporting cognitive outcomes (MMSE, ADAS-Cog, CDR scores)",
        "Studies involving pharmacological or non-pharmacological interventions",
        "Biomarker studies (amyloid, tau, neuroimaging)",
        "Randomised controlled trials, cohort studies, systematic reviews",
    ],
    "parkinsons": [
        "Studies involving patients with confirmed Parkinson's disease diagnosis",
        "Studies reporting motor outcomes (UPDRS, Hoehn and Yahr scale)",
        "Studies involving dopaminergic or non-dopaminergic interventions",
        "Studies on alpha-synuclein, Lewy body pathology",
        "Randomised controlled trials, cohort studies, systematic reviews",
    ],
    "multiple_sclerosis": [
        "Studies involving patients with confirmed MS diagnosis",
        "Studies reporting relapse rates, disability progression (EDSS scores)",
        "Studies involving disease-modifying therapies",
        "Neuroimaging studies (MRI lesion load)",
        "Randomised controlled trials, cohort studies, systematic reviews",
    ],
    "epilepsy": [
        "Studies involving patients with confirmed epilepsy diagnosis",
        "Studies reporting seizure frequency or seizure-free rates",
        "Studies involving antiepileptic drug interventions",
        "EEG-based outcome studies",
        "Randomised controlled trials, cohort studies, systematic reviews",
    ],
    "stroke": [
        "Studies involving patients with confirmed ischaemic or haemorrhagic stroke",
        "Studies reporting functional outcomes (mRS, Barthel Index, NIHSS)",
        "Studies involving thrombolysis, thrombectomy, or rehabilitation",
        "Studies on stroke recurrence or mortality",
        "Randomised controlled trials, cohort studies, systematic reviews",
    ],
}

NEURO_EXCLUSION = {
    "alzheimers": [
        "Non-human animal studies unless biomarker validation",
        "Studies not reporting quantitative cognitive outcomes",
        "Case reports with fewer than 5 participants",
    ],
    "parkinsons": [
        "Non-human animal studies",
        "Studies not reporting motor or non-motor outcome measures",
        "Case reports with fewer than 5 participants",
    ],
    "multiple_sclerosis": [
        "Non-human animal studies",
        "Studies not reporting relapse or disability outcomes",
        "Case reports with fewer than 5 participants",
    ],
    "epilepsy": [
        "Non-human animal studies",
        "Studies not reporting seizure frequency or seizure-free outcomes",
        "Case reports with fewer than 5 participants",
    ],
    "stroke": [
        "Non-human animal studies",
        "Studies not reporting functional outcome measures",
        "Case reports with fewer than 5 participants",
    ],
}

TEMPLATE_DIR = Path(__file__).with_name("prompt_templates")


@lru_cache(maxsize=None)
def _load_template(filename: str) -> str:
    return (TEMPLATE_DIR / filename).read_text(encoding="utf-8")


def get_neuro_study_objectives(condition: str) -> str:
    display_name = NEURO_CONDITIONS.get(condition, condition)
    inclusion = "\n".join(f"- {c}" for c in NEURO_INCLUSION.get(condition, []))
    exclusion = "\n".join(f"- {c}" for c in NEURO_EXCLUSION.get(condition, []))
    return f"""# Study Objectives
This systematic review aims to synthesise clinical evidence for *{display_name}*.

The review seeks to:
1. Collate evidence on pharmacological and non-pharmacological interventions
2. Document key clinical outcome measures and their reported values
3. Identify high-quality randomised controlled trials and systematic reviews
4. Summarise biomarker, neuroimaging, and functional outcome data
5. Support evidence-based clinical guideline development for {display_name}

## Inclusion Criteria
{inclusion}

## Exclusion Criteria
{exclusion}
"""


def get_study_objectives(pathogen_name: str) -> str:
    template = _load_template("study_objectives.md")
    return template.replace("__PATHOGEN_NAME__", pathogen_name)


def get_abstract_screenprompt(pathogen_name: str, is_neuro: bool = False, condition: str = "") -> str:
    template = _load_template("abstract_screening.md")
    objectives = get_neuro_study_objectives(condition) if is_neuro else get_study_objectives(pathogen_name)
    return (
        template.replace("__PATHOGEN_NAME__", pathogen_name)
        .replace("__STUDY_OBJECTIVES__", objectives)
    )


def get_fulltext_screenprompt(pathogen_name: str, is_neuro: bool = False, condition: str = "") -> str:
    template = _load_template("fulltext_screening.md")
    objectives = get_neuro_study_objectives(condition) if is_neuro else get_study_objectives(pathogen_name)
    return (
        template.replace("__PATHOGEN_NAME__", pathogen_name)
        .replace("__STUDY_OBJECTIVES__", objectives)
    )


def get_prompt(stage: str, pathogen: str | None = None) -> str:
    if stage not in {"abstract_screening", "fulltext_review"}:
        raise ValueError(f"No prompt for stage {stage}")

    if pathogen is None:
        raise ValueError(
            f"Stage {stage} requires 'pathogen' parameter. Choose from: {list(WHO_PATHOGENS.keys())}"
        )

    is_neuro = pathogen.strip().lower() in NEURO_CONDITIONS
    condition = pathogen.strip().lower()

    if is_neuro:
        display_name = NEURO_CONDITIONS[condition]
    else:
        display_name = WHO_PATHOGENS.get(pathogen, pathogen)

    if stage == "abstract_screening":
        return get_abstract_screenprompt(display_name, is_neuro=is_neuro, condition=condition)
    return get_fulltext_screenprompt(display_name, is_neuro=is_neuro, condition=condition)
