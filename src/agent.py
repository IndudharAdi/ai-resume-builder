import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from typing import Dict, List, Set, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    pass  # dotenv not required if env vars are set directly

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - optional until deps installed
    genai = None


SKILL_REGEX = re.compile(r"\b[A-Za-z][A-Za-z0-9+\-/#]{1,}\b")


@dataclass
class AnalysisResult:
    jd_skills: List[str]
    resume_skills: List[str]
    missing_skills: List[str]
    overlap_skills: List[str]
    rewritten_bullets: List[str]
    cover_letter: str
    tailored_resume: str


def validate_access_code(code: str) -> bool:
    """Validate the provided access code against the environment variable."""
    expected_code = os.getenv("APP_ACCESS_CODE")
    if not expected_code:
        # If no code is set in env, assume open access or handle as error depending on policy.
        # For this user request "limited users", we should probably default to blocking if not set,
        # but for ease of dev, let's allow if env var is missing, OR enforce it.
        # User said "give my gemini api for limited users", so we MUST enforce it.
        return False
    return code == expected_code


def parse_skills(text: str) -> Set[str]:
    """Extract a coarse set of skills/keywords from free text."""
    candidates = {match.group(0).strip() for match in SKILL_REGEX.finditer(text)}
    normalized = {c for c in (candidate.lower() for candidate in candidates) if len(c) > 2}
    return normalized


def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def ensure_gemini(
    model_name: str = None, api_key_env: str = "GEMINI_API_KEY", model_env: str = "GEMINI_MODEL"
):
    if genai is None:
        raise RuntimeError("google-generativeai is not installed. Install requirements first.")
    api_key = os.getenv(api_key_env)
    if not api_key:
        raise ValueError(f"Missing {api_key_env}. Export it or put it in a .env file.")
    genai.configure(api_key=api_key)
    model = model_name or os.getenv(model_env) or "gemini-flash-latest"
    return genai.GenerativeModel(model)


def rewrite_bullets(model, bullets: List[str], jd_text: str) -> List[str]:
    if not bullets:
        return []
    prompt = (
        "Rewrite each resume bullet to align with the job description. "
        "Preserve truthfulness, keep measurable outcomes, and keep each bullet concise.\n\n"
        f"Job description:\n{jd_text}\n\n"
        "Resume bullets (JSON array):\n"
        f"{json.dumps(bullets, indent=2)}\n\n"
        "Respond with a JSON array of rewritten bullets."
    )
    response = model.generate_content(prompt)
    try:
        return json.loads(response.text)
    except Exception:
        # Fall back to splitting lines if JSON is malformed
        return [line.strip("-• ").strip() for line in response.text.strip().splitlines() if line.strip()]


def generate_cover_letter(model, resume_text: str, jd_text: str) -> str:
    prompt = (
        "Write a concise, tailored cover letter in under 180 words. "
        "Use a confident, factual tone, first person singular. "
        "Highlight matching experience and relevance to the role.\n\n"
        f"Job description:\n{jd_text}\n\n"
        f"Resume:\n{resume_text}\n\n"
        "Output just the cover letter text."
    )
    response = model.generate_content(prompt)
    return response.text.strip()


def generate_tailored_resume(model, resume_text: str, jd_text: str) -> str:
    prompt = (
        "Rewrite the entire resume to better match the job description. "
        "Optimize the summary, skills, and experience sections. "
        "Maintain the original structure but emphasize relevant skills and achievements. "
        "Do NOT invent false information.\n\n"
        f"Job description:\n{jd_text}\n\n"
        f"Original Resume:\n{resume_text}\n\n"
        "Output the full tailored resume in Markdown format."
    )
    response = model.generate_content(prompt)
    return response.text.strip()


def analyze(resume_text: str, jd_text: str, bullets: List[str]) -> AnalysisResult:
    jd_skills = parse_skills(jd_text)
    resume_skills = parse_skills(resume_text)
    missing = sorted(jd_skills - resume_skills)
    overlap = sorted(jd_skills & resume_skills)

    model = ensure_gemini()
    rewritten = rewrite_bullets(model, bullets, jd_text)
    cover_letter = generate_cover_letter(model, resume_text, jd_text)
    tailored_resume = generate_tailored_resume(model, resume_text, jd_text)

    return AnalysisResult(
        jd_skills=sorted(jd_skills),
        resume_skills=sorted(resume_skills),
        missing_skills=missing,
        overlap_skills=overlap,
        rewritten_bullets=rewritten,
        cover_letter=cover_letter,
        tailored_resume=tailored_resume,
    )


def run_cli(args: argparse.Namespace):
    jd_text = load_text(args.jd)
    resume_text = load_text(args.resume)
    bullets = [b.strip() for b in args.bullets] if args.bullets else []

    try:
        result = analyze(resume_text, jd_text, bullets)
        output = asdict(result)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2)
        else:
            print(json.dumps(output, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Resume Tailoring & Job Application Automation Agent")
    parser.add_argument("--jd", required=True, help="Path to job description text file")
    parser.add_argument("--resume", required=True, help="Path to resume text file")
    parser.add_argument(
        "--bullets",
        nargs="*",
        default=[],
        help="Optional list of resume bullets to rewrite (pass each bullet as a separate argument)",
    )
    parser.add_argument("--output", help="Path to write JSON output (stdout if omitted)")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    run_cli(args)


if __name__ == "__main__":
    main()
