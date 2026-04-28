"""
evaluator.py — Scores a job lead against the candidate profile.

Score meaning (calibrated for practical use):
  0  – 20 : Wrong field entirely (healthcare, retail, finance ops, etc.)
  21 – 40 : Adjacent tech role but candidate lacks the core stack
  41 – 60 : Reasonable match — candidate has transferable skills, some gaps
  61 – 75 : Good match — candidate has most required skills
  76 – 89 : Strong match — candidate's projects directly demonstrate this work
  90 – 100: Elite match — near-perfect alignment on stack, seniority, and domain
"""

from pydantic import BaseModel, Field
from typing import List


class _Score(BaseModel):
    score:        int
    reason:       str
    match_points: List[str] = Field(default_factory=list)
    gaps:         List[str] = Field(default_factory=list)


def _build_proof(candidate_data: dict) -> str:
    """
    Build a proof-of-work string directly from the profile dict.
    Bypasses PROJ_UTILIZES / EXP_UTILIZES graph edges which are only
    populated by the ingestor, not by manual UI edits.
    """
    parts: list[str] = []

    for proj in candidate_data.get("projects", []):
        stack = proj.get("stack", [])
        if isinstance(stack, list):
            stack = ", ".join(stack)
        title  = proj.get("title", "")
        impact = proj.get("impact", "")
        if title:
            parts.append(f"Project: {title} | Stack: {stack} | Impact: {impact}")

    for exp in candidate_data.get("exp", []):
        role   = exp.get("role", "")
        co     = exp.get("co", "")
        period = exp.get("period", "")
        desc   = exp.get("d", "")
        if role:
            parts.append(f"Role: {role} at {co} ({period}) | {desc}")

    skills = [s["n"] for s in candidate_data.get("skills", []) if s.get("n")]
    if skills:
        parts.append(f"Skills: {', '.join(skills)}")

    return "\n".join(parts) if parts else "No profile data found."


def _infer_experience_level(candidate_data: dict) -> str:
    """Mirror the same logic as query_gen so scoring is consistent."""
    exp_entries = candidate_data.get("exp", [])
    if not exp_entries:
        return "fresher"
    real_roles = [e for e in exp_entries if e.get("role") and
                  not any(kw in (e.get("role") or "").lower()
                          for kw in ["intern", "trainee", "student", "assistant"])]
    if not real_roles:
        return "fresher"
    if len(real_roles) == 1:
        return "junior"
    return "mid"


def score(jd: str, candidate_data: dict) -> dict:
    from llm import call_llm

    target_role      = candidate_data.get("s") or "Software / AI Engineer"
    proof            = _build_proof(candidate_data)
    experience_level = _infer_experience_level(candidate_data)

    # Seniority mismatch instruction tailored to candidate level
    seniority_rule = {
        "fresher": (
            "SENIORITY RULE (CRITICAL): The candidate is a FRESHER with no full-time experience. "
            "Any job requiring 3+ years of experience, titled 'Senior', 'Lead', 'Staff', 'Principal', "
            "or 'Manager' MUST score 30 or below regardless of stack alignment. "
            "Only jobs explicitly tagged 'junior', 'entry level', 'fresher', 'graduate', "
            "'0–2 years', or with no experience requirement should score above 40."
        ),
        "junior": (
            "SENIORITY RULE: The candidate is JUNIOR (1–2 years experience). "
            "Jobs requiring 5+ years or titled 'Senior/Lead/Staff/Principal' must score 35 or below. "
            "Jobs requiring 3–4 years may score up to 55 at most. "
            "Junior and entry-level roles can score normally."
        ),
        "mid": (
            "SENIORITY RULE: The candidate is MID-LEVEL. "
            "Jobs requiring 7+ years or titled 'Staff/Principal/Director' should score 45 or below. "
            "Senior roles (3–5 yr) are fine. Junior roles should score 50–65 (slightly overqualified)."
        ),
    }.get(experience_level, "")

    system = f"""You are a practical technical recruiter scoring job-candidate fit.
Your goal is ACCURATE calibration — not gatekeeping.  Most relevant jobs should
score between 40 and 80.  Only irrelevant roles (nursing, retail, finance ops)
score below 20.  Reserve 90+ for near-perfect stack alignment.

CANDIDATE TARGET ROLE: {target_role}
CANDIDATE EXPERIENCE LEVEL: {experience_level.upper()}

CANDIDATE PROOF OF WORK:
{proof}

SCORING RUBRIC:
  0  – 20 : Completely wrong field (medical, retail, manual labour, legal, finance ops)
  21 – 40 : Adjacent tech but candidate clearly lacks the primary required stack OR severe seniority mismatch
  41 – 60 : Transferable skills exist; candidate could ramp up with moderate effort
  61 – 75 : Solid match — candidate has most of the listed requirements
  76 – 89 : Strong match — candidate's past projects directly demonstrate this work
  90 – 100: Elite — stack, seniority, and domain are nearly identical

SCORING RULES:
1. Read the job title and description carefully.  If the role is clearly outside
   tech/engineering/AI, return score=0 immediately.
2. {seniority_rule}
3. For every tech term in the JD, check if the candidate's proof of work shows
   evidence of it (exact or closely related skill).
4. Partial matches count.  A candidate with FastAPI experience matches a "Python
   backend" role at ~60 even if Django is listed.
5. Do NOT require perfect stack overlap for a 60+ score (when seniority matches).
6. List specific match_points (what aligns) AND gaps (what is missing).
   Always include seniority as a gap if the role requires significantly more experience.
7. reason must be 1–3 sentences explaining the score concisely."""

    result = call_llm(
        system,
        f"JOB TO EVALUATE:\n{jd}",
        _Score,
        step="evaluator",
    )
    return {
        "score":        result.score,
        "reason":       result.reason,
        "match_points": result.match_points,
        "gaps":         result.gaps,
    }
