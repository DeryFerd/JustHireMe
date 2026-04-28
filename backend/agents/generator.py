import os
from db.client import get_profile

_assets = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
    "BoomBoom", "assets",
)
os.makedirs(_assets, exist_ok=True)


def _build_proof(profile: dict) -> str:
    """Build proof-of-work string from profile dict -- avoids dead PROJ_UTILIZES graph edges."""
    parts = []
    for proj in profile.get("projects", []):
        stack = proj.get("stack", [])
        if isinstance(stack, list):
            stack = ", ".join(stack)
        title  = proj.get("title", "")
        impact = proj.get("impact", "")
        if title:
            parts.append(f"Project: {title} | Stack: {stack} | Impact: {impact}")
    for exp in profile.get("exp", []):
        role   = exp.get("role", "")
        co     = exp.get("co", "")
        period = exp.get("period", "")
        desc   = exp.get("d", "")
        if role:
            parts.append(f"Role: {role} at {co} ({period}) | {desc}")
    skills = [s["n"] for s in profile.get("skills", []) if s.get("n")]
    if skills:
        parts.append(f"Skills: {', '.join(skills)}")
    return "\n".join(parts) if parts else ""


def _draft(proof: str, j: dict, template: str = "") -> str:
    from llm import call_raw
    mp = "\n".join(f"- {pt}" for pt in j.get("match_points", []))
    candidate_name = j.get("candidate_name", "")
    desc = j.get("description", "")

    template_instruction = (
        "\nIMPORTANT: Use the provided resume template as the structural and formatting guide. "
        "Preserve section order, heading style, and layout. Replace content with tailored material."
        if template else
        ""
    )
    template_block = (
        f"\n\nRESUME TEMPLATE TO FOLLOW:\n{template[:3000]}"
        if template else ""
    )

    system = (
        "You are an expert resume and cover letter writer. "
        "Generate a tailored, ATS-optimised resume followed by a cover letter in Markdown. "
        + template_instruction +
        " Use ## Resume and ## Cover Letter as section headers. "
        "Explicitly weave in the provided match points. "
        "Keep language concise, factual, and impactful."
    )
    user = (
        f"JOB TITLE: {j.get('title','')}\n"
        f"COMPANY: {j.get('company','')}\n"
        + (f"JOB DESCRIPTION: {desc}\n" if desc else "") +
        f"\nMATCH POINTS:\n{mp}\n\n"
        f"CANDIDATE PROOF OF WORK:\n{proof}"
        + template_block
    )
    return call_raw(system, user, step="generator")


def _clean(text: str) -> str:
    """
    Replace every character that Helvetica (Latin-1) cannot encode,
    then NFKD-normalise and re-encode to latin-1 so nothing slips through.
    """
    import unicodedata
    _subs = {
        # Bullets & boxes
        "•": "-", "‣": "-", "●": "-", "▪": "-",
        "■": "-", "▫": "-", "▶": ">",
        # Dashes
        "–": "-", "—": "--", "―": "--", "‐": "-",
        "‑": "-", "‒": "-",
        # Quotes
        "‘": "'", "’": "'", "‚": ",",
        "“": '"', "”": '"', "„": '"',
        # Arrows & misc symbols
        "→": "->", "←": "<-", "↔": "<->",
        "…": "...",
        "✓": "(v)", "✔": "(v)", "✗": "(x)", "✘": "(x)",
        "®": "(R)", "©": "(C)", "™": "(TM)",
        # Zero-width / special spaces
        "​": "", "‌": "", "‍": "",
        " ": " ", " ": " ", " ": " ", " ": " ",
        # Middle dot
        "·": "-",
        # Checkmarks and crosses sometimes used in LLM output
        "✅": "(v)", "❌": "(x)",
    }
    for ch, rep in _subs.items():
        text = text.replace(ch, rep)
    text = unicodedata.normalize("NFKD", text)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _strip_inline(text: str) -> str:
    """Remove **bold**, *italic*, `code`, and [link](url) inline markers."""
    import re
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*',     r'\1', text)
    text = re.sub(r'`(.+?)`',       r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    return text.strip()


def _render(md_text: str, filename: str) -> str:
    """
    Convert Markdown to PDF using direct multi_cell() calls.
    No write_html / HTMLMixin -- avoids the entity-unescaping bug in fpdf2
    that re-introduces unicode characters after sanitisation.
    """
    import re
    from fpdf import FPDF

    text = _clean(md_text)
    lines = text.splitlines()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)
    eff_w = pdf.w - pdf.l_margin - pdf.r_margin

    def emit(txt: str, size: int = 11, bold: bool = False, indent: float = 0):
        pdf.set_font("Helvetica", style="B" if bold else "", size=size)
        pdf.set_x(pdf.l_margin + indent)
        pdf.multi_cell(eff_w - indent, size * 0.5, txt)

    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        i += 1

        if not stripped:
            pdf.ln(2)
            continue

        # Horizontal rule  (--- or ***)
        if re.match(r'^[-*]{3,}$', stripped):
            pdf.set_draw_color(180, 180, 180)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(3)
            continue

        # Headings
        if stripped.startswith("#### "):
            emit(_strip_inline(stripped[5:]), size=11, bold=True)
            continue
        if stripped.startswith("### "):
            pdf.ln(2)
            emit(_strip_inline(stripped[4:]), size=12, bold=True)
            continue
        if stripped.startswith("## "):
            pdf.ln(3)
            emit(_strip_inline(stripped[3:]), size=14, bold=True)
            pdf.set_draw_color(100, 100, 100)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(2)
            continue
        if stripped.startswith("# "):
            pdf.ln(4)
            emit(_strip_inline(stripped[2:]), size=16, bold=True)
            pdf.ln(2)
            continue

        # Blockquote
        if stripped.startswith("> "):
            emit(_strip_inline(stripped[2:]), size=10, indent=8)
            continue

        # Unordered list  (- item  or  * item)
        m = re.match(r'^[-*+]\s+(.*)', stripped)
        if m:
            emit("- " + _strip_inline(m.group(1)), size=11, indent=6)
            continue

        # Numbered list
        m = re.match(r'^\d+\.\s+(.*)', stripped)
        if m:
            emit(_strip_inline(stripped), size=11, indent=6)
            continue

        # Plain paragraph
        emit(_strip_inline(stripped), size=11)

    out = os.path.join(_assets, filename)
    pdf.output(out)
    return out


def run(lead: dict, template: str = "") -> str:
    profile = get_profile()
    proof   = _build_proof(profile)

    # Enrich lead with candidate name so the draft can use it
    lead_with_ctx = {**lead, "candidate_name": profile.get("n", "")}

    try:
        m = _draft(proof, lead_with_ctx, template=template)
    except Exception as exc:
        import sys
        print(f"[generator] LLM draft failed for {lead.get('job_id','?')}: {exc}", file=sys.stderr)
        raise RuntimeError(f"Draft generation failed: {exc}") from exc

    try:
        path = _render(m, f"{lead['job_id']}.pdf")
    except Exception as exc:
        import sys
        print(f"[generator] PDF render failed for {lead.get('job_id','?')}: {exc}", file=sys.stderr)
        raise RuntimeError(f"PDF render failed: {exc}") from exc

    return path
