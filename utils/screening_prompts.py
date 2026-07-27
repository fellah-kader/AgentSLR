# utils/screening_prompts.py

# WHO Blueprint Pathogens
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

# Neurology Conditions
NEURO_CONDITIONS_DISPLAY = {
    "alzheimers": "Alzheimer's Disease",
    "parkinsons": "Parkinson's Disease",
    "multiple_sclerosis": "Multiple Sclerosis",
    "epilepsy": "Epilepsy",
    "stroke": "Stroke",
}

NEURO_INCLUSION_CRITERIA = {
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
        "Studies involving patients with confirmed MS diagnosis (relapsing-remitting, progressive)",
        "Studies reporting relapse rates, disability progression (EDSS scores)",
        "Studies involving disease-modifying therapies or symptomatic treatments",
        "Neuroimaging studies (MRI lesion load, brain volume)",
        "Randomised controlled trials, cohort studies, systematic reviews",
    ],
    "epilepsy": [
        "Studies involving patients with confirmed epilepsy diagnosis",
        "Studies reporting seizure frequency, seizure-free rates",
        "Studies involving antiepileptic drug interventions or surgical treatments",
        "EEG-based outcome studies",
        "Randomised controlled trials, cohort studies, systematic reviews",
    ],
    "stroke": [
        "Studies involving patients with confirmed ischaemic or haemorrhagic stroke",
        "Studies reporting functional outcomes (mRS, Barthel Index, NIHSS scores)",
        "Studies involving thrombolysis, thrombectomy, or rehabilitation interventions",
        "Studies on stroke recurrence, mortality, or disability",
        "Randomised controlled trials, cohort studies, systematic reviews",
    ],
}

NEURO_EXCLUSION_CRITERIA = {
    "alzheimers": [
        "Non-human animal studies (unless biomarker validation)",
        "Studies not reporting quantitative cognitive outcomes",
        "Case reports with fewer than 5 participants",
        "Studies on other forms of dementia without Alzheimer's component",
    ],
    "parkinsons": [
        "Non-human animal studies",
        "Studies on atypical parkinsonism only (PSP, MSA) without PD comparison",
        "Studies not reporting motor or non-motor outcome measures",
        "Case reports with fewer than 5 participants",
    ],
    "multiple_sclerosis": [
        "Non-human animal studies",
        "Studies on clinically isolated syndrome without MS conversion data",
        "Studies not reporting relapse or disability outcomes",
        "Case reports with fewer than 5 participants",
    ],
    "epilepsy": [
        "Non-human animal studies",
        "Studies on febrile seizures in otherwise healthy children only",
        "Studies not reporting seizure frequency or seizure-free outcomes",
        "Case reports with fewer than 5 participants",
    ],
    "stroke": [
        "Non-human animal studies",
        "Studies on transient ischaemic attack only without stroke outcomes",
        "Studies not reporting functional outcome measures",
        "Case reports with fewer than 5 participants",
    ],
}


def get_study_objectives(pathogen_name):
    """Generate pathogen-specific study objectives."""
    return f"""# Study Objectives
This systematic review aims to collate transmission and modelling parameters for *{pathogen_name}*.

The review seeks to:
1. Provide estimates of key infectious disease metrics (reproduction number, CFR, generation time, serial interval, incubation period, etc.)
2. Document historical outbreak characteristics (size, location, duration, deaths)
3. Identify mathematical/statistical models of transmission
4. Collate risk factors for infection, severe disease, and death
5. Summarize seroprevalence data
6. Support infectious disease modelling and outbreak response efforts

This information enables effective outbreak preparedness, resource targeting, and mathematical modelling for nowcasting and forecasting of *{pathogen_name}*.
"""


def get_neuro_study_objectives(condition: str) -> str:
    """Generate neurology-specific study objectives."""
    display_name = NEURO_CONDITIONS_DISPLAY.get(condition, condition)
    inclusion = NEURO_INCLUSION_CRITERIA.get(condition, [])
    exclusion = NEURO_EXCLUSION_CRITERIA.get(condition, [])

    inclusion_text = "\n".join(f"- {c}" for c in inclusion)
    exclusion_text = "\n".join(f"- {c}" for c in exclusion)

    return f"""# Study Objectives
This systematic review aims to synthesise clinical evidence for *{display_name}*.

The review seeks to:
1. Collate evidence on pharmacological and non-pharmacological interventions
2. Document key clinical outcome measures and their reported values
3. Identify high-quality randomised controlled trials and systematic reviews
4. Summarise biomarker, neuroimaging, and functional outcome data
5. Support evidence-based clinical guideline development for {display_name}

## Inclusion Criteria
{inclusion_text}

## Exclusion Criteria
{exclusion_text}
"""


def get_screening_objectives(topic: str) -> str:
    """Smart router — returns correct objectives based on topic type."""
    from src.harvest.queries import NEURO_CONDITIONS
    if topic.strip().lower() in NEURO_CONDITIONS:
        return get_neuro_study_objectives(topic.strip().lower())
    return get_study_objectives(WHO_PATHOGENS.get(topic, topic))
