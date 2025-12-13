import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from typing import Dict, List, Set, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import google.generativeai as genai
except ImportError:
    genai = None


SKILL_REGEX = re.compile(r"\b[A-Za-z][A-Za-z0-9+\-/#]{1,}\b")

COMMON_WORDS = {
    'a', 'about', 'above', 'across', 'after', 'against', 'all', 'along', 'also', 'although', 'am', 'an', 'and',
    'any', 'are', 'as', 'asked', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both',
    'but', 'by', 'came', 'can', 'come', 'could', 'did', 'do', 'does', 'doing', 'done', 'down', 'during', 'each',
    'either', 'else', 'even', 'ever', 'every', 'few', 'find', 'first', 'for', 'found', 'from', 'get', 'give',
    'go', 'going', 'got', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'him', 'his', 'how', 'however',
    'i', 'if', 'in', 'into', 'is', 'it', 'its', 'just', 'keep', 'know', 'last', 'later', 'least', 'left', 'less',
    'like', 'long', 'look', 'made', 'make', 'making', 'many', 'may', 'me', 'might', 'more', 'most', 'much', 'must',
    'my', 'never', 'next', 'no', 'not', 'now', 'of', 'off', 'often', 'on', 'once', 'one', 'only', 'or', 'other',
    'our', 'out', 'over', 'own', 'put', 'said', 'same', 'saw', 'say', 'see', 'seem', 'she', 'should', 'show',
    'since', 'so', 'some', 'still', 'such', 'take', 'than', 'that', 'the', 'their', 'them', 'then', 'there',
    'these', 'they', 'thing', 'think', 'this', 'those', 'through', 'time', 'to', 'too', 'two', 'under', 'until',
    'up', 'upon', 'us', 'use', 'used', 'using', 'very', 'want', 'was', 'way', 'we', 'well', 'were', 'what',
    'when', 'where', 'which', 'while', 'who', 'will', 'with', 'would', 'you', 'your'
}

NON_TECHNICAL_WORDS = {
    # Soft skills and adjectives
    'ability', 'accident', 'accidents', 'accounts', 'additional', 'affordable', 'allowance', 'ancillary',
    'annual', 'area', 'assistance', 'austin', 'benefits', 'best', 'care', 'change', 'comfortable', 'communication',
    'company', 'competitive', 'comprehensive', 'confidential', 'considerable', 'continuing', 'continuous',
    'convenient', 'costs', 'covered', 'creating', 'critical', 'dental', 'dependent', 'dependents', 'disability',
    'discounted', 'distributed', 'effective', 'eligible', 'employee', 'employees', 'enhancement', 'etc', 'event',
    'expenses', 'extra', 'familiarity', 'financial', 'follows', 'foundation', 'fully', 'funding', 'generous',
    'headquarters', 'health', 'highly', 'hire', 'home', 'identifies', 'identity', 'illness', 'indemnity',
    'information', 'initiative', 'issues', 'job', 'life', 'listed', 'living', 'match', 'medical', 'meetings',
    'mind', 'monthly', 'note', 'occasional', 'offer', 'office', 'onboarding', 'one-time', 'opportunities',
    'optional', 'options', 'orientation', 'paid', 'peace', 'personal', 'pet', 'phone', 'plan', 'please', 'plus',
    'position', 'preferred', 'principles', 'program', 'protection', 'provides', 'pursuits', 'related',
    'reimbursement', 'reimbursements', 'required', 'responsibilities', 'restricted', 'retirement', 'safeguard',
    'savings', 'sense', 'serious', 'shift', 'skill', 'solely', 'subject', 'support', 'tailored', 'takes',
    'tax-advantaged', 'texas', 'theft', 'travel', 'understanding', 'unexpected', 'vision', 'wellness', 'wifi',
    'without', 'work',
    # Common adjectives and quality descriptors
    'bad', 'good', 'great', 'better', 'worse', 'attitude', 'color', 'colour', 'quality', 'strong', 'weak',
    'positive', 'negative', 'nice', 'poor', 'excellent', 'amazing', 'awesome', 'terrible', 'wonderful',
    'beautiful', 'ugly', 'clean', 'dirty', 'new', 'old', 'young', 'modern', 'traditional', 'current',
    'previous', 'next', 'last', 'first', 'second', 'third', 'final', 'initial', 'primary', 'secondary',
    # Common verbs and action words
    'actions', 'aligning', 'always', 'bring', 'challenge', 'collaboration', 'communicator', 'delivery',
    'elevating', 'engineers', 'ensure', 'environment', 'excellent', 'expectations', 'experienced', 'external',
    'fast-paced', 'flex', 'grow', 'hands-on', 'high', 'high-quality', 'junior', 'mentoring', 'mobile',
    'monitoring', 'multiple', 'non-technical', 'ownership', 'practices', 'preferably', 'qualifications',
    'scope', 'setting', 'specifications', 'stakeholders', 'standards', 'systems', 'tooling', 'tools',
    'tuning', 'uis', 'verbal', 'working', 'written',
    # Business/organizational terms
    'cross-functional', 'ecosystems', 'platforms', 'service-oriented', 'observability',
    # Generic tech terms that are too vague
    'big', 'core', 'web', 'boot', 'native', 'message', 'queues', 'dependencies', 'fault-tolerant',
    'globally-distributed', 'infrastructure', 'architecture', 'architectures', 'automation',
    # Additional generic words that appear in job descriptions
    'availability', 'building', 'code', 'components', 'data', 'development', 'experience',
    'including', 'professional', 'proficient', 'software', 'successfully', 'team', 'technical',
    'years', 'apis', 'context', 'degree', 'dynamic', 'frameworks', 'minimum', 'robust',
    'scalable', 'skilled', 'containerization', 'hooks', 'jvm'
}


@dataclass
class AnalysisResult:
    jd_skills: List[str]
    resume_skills: List[str]
    missing_skills: List[str]
    overlap_skills: List[str]
    rewritten_bullets: List[str]
    cover_letter: str
    tailored_resume: str
    ats_score: int
    ats_breakdown: Dict[str, int]
    ats_recommendations: List[str]


def validate_access_code(code: str) -> bool:
    expected_code = os.getenv("APP_ACCESS_CODE")
    if not expected_code or not code:
        return False
    return code.strip() == expected_code.strip()


def extract_skills_with_ai(model, text: str) -> Set[str]:
    """Use AI to extract technical skills from text."""
    prompt = (
        "Extract ONLY technical skills, tools, technologies, programming languages, frameworks, "
        "databases, cloud platforms, and certifications from the following text. "
        "Do NOT include soft skills, verbs, adjectives, or generic business terms. "
        "Return as a JSON array of lowercase strings.\n\n"
        f"Text:\n{text[:2000]}\n\n"
        "Technical skills only:"
    )
    try:
        response = model.generate_content(prompt)
        skills = json.loads(response.text)
        return set(s.lower() for s in skills if isinstance(s, str))
    except Exception:
        # Fallback to regex if AI fails
        return parse_skills_regex(text)


def parse_skills_regex(text: str) -> Set[str]:
    """Regex-based skill extraction with improved filtering."""
    candidates = {match.group(0).strip() for match in SKILL_REGEX.finditer(text)}
    normalized = {
        c.lower() for c in candidates 
        if len(c) > 2 and c.lower() not in COMMON_WORDS and c.lower() not in NON_TECHNICAL_WORDS
    }
    return normalized


def parse_skills(text: str) -> Set[str]:
    """Parse skills using regex (legacy method for backward compatibility)."""
    return parse_skills_regex(text)


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
        "Write a professional, tailored cover letter in 250-300 words. "
        "Use a confident, engaging tone in first person. "
        "Structure it with: opening paragraph (why you're interested), "
        "middle paragraph(s) (relevant experience and skills), "
        "and closing paragraph (call to action). "
        "Highlight specific matching experience and demonstrate genuine interest in the role.\n\n"
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
        "Correct any obvious OCR errors (e.g., 'REV A' -> 'REVA', 'Mana ger' -> 'Manager'). "
        "Do NOT invent false information.\n\n"
        f"Job description:\n{jd_text}\n\n"
        f"Original Resume:\n{resume_text}\n\n"
        "Output the full tailored resume in Markdown format."
    )
    response = model.generate_content(prompt)
    return response.text.strip()


def check_standard_sections(resume_text: str) -> int:
    """Check for presence and quality of standard resume sections. Returns score 0-15."""
    score = 0
    text_lower = resume_text.lower()
    lines = resume_text.split('\n')
    
    # Critical sections (must have at least 2 of these)
    critical_sections = {
        'experience': ['experience', 'work experience', 'employment', 'work history'],
        'education': ['education', 'academic', 'degree'],
        'skills': ['skills', 'technical skills', 'competencies']
    }
    
    critical_found = 0
    for section_type, keywords in critical_sections.items():
        for keyword in keywords:
            if keyword in text_lower:
                # Check if there's actual content after the section header
                for i, line in enumerate(lines):
                    if keyword in line.lower() and i + 1 < len(lines):
                        # Check next few lines have content (not just another header)
                        has_content = any(len(lines[j].strip()) > 20 for j in range(i+1, min(i+4, len(lines))))
                        if has_content:
                            critical_found += 1
                            score += 5
                            break
                break
    
    # Penalty if missing critical sections
    if critical_found < 2:
        score = max(0, score - 5)
    
    return min(15, score)


def check_contact_info(resume_text: str) -> int:
    """Check for email, phone, and LinkedIn. Returns score 0-10."""
    score = 0
    
    # Check for email pattern
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
    if email_match:
        email = email_match.group(0).lower()
        # Bonus for professional email domains
        if any(domain in email for domain in ['gmail.com', 'outlook.com', 'yahoo.com', 'protonmail.com']):
            score += 4
        else:
            score += 3  # Custom domain (could be professional or not)
    
    # Check for phone pattern
    if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b|\(\d{3}\)\s*\d{3}[-.]?\d{4}', resume_text):
        score += 4
    
    # Bonus for LinkedIn
    if re.search(r'linkedin\.com/in/[\w-]+', resume_text.lower()):
        score += 2
    
    return min(10, score)


def check_resume_length(resume_text: str) -> int:
    """Check resume length with stricter criteria. Returns score 0-8."""
    word_count = len(resume_text.split())
    # Stricter ideal range: 450-700 words
    if 450 <= word_count <= 700:
        return 8
    elif 400 <= word_count < 450 or 700 < word_count <= 850:
        return 6
    elif 350 <= word_count < 400 or 850 < word_count <= 1000:
        return 4
    elif 250 <= word_count < 350 or 1000 < word_count <= 1200:
        return 2
    else:
        return 0  # Too short or too long


def check_format_quality(resume_text: str) -> int:
    """Check resume formatting quality. Returns score 0-15."""
    score = 15  # Start with full points, deduct for issues
    
    # Check for bullet points (good formatting)
    bullet_patterns = [r'[•\-\*]\s', r'^\s*[\u2022\u2023\u2043\u204C\u204D\u2219\u25C9\u25D8\u25E6\u2619\u2765\u2767]\s']
    has_bullets = any(re.search(pattern, resume_text, re.MULTILINE) for pattern in bullet_patterns)
    if not has_bullets:
        score -= 3
    
    # Check for excessive special characters (messy formatting)
    special_char_count = sum(1 for char in resume_text if char in '@#$%^&*(){}[]|\\<>')
    if special_char_count > len(resume_text) * 0.02:  # More than 2% special chars
        score -= 3
    
    # Check for proper capitalization (not all caps or all lowercase)
    lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
    if lines:
        all_caps_lines = sum(1 for line in lines if line.isupper() and len(line) > 10)
        all_lower_lines = sum(1 for line in lines if line.islower() and len(line) > 10)
        
        if all_caps_lines > len(lines) * 0.3:  # More than 30% all caps
            score -= 4
        if all_lower_lines > len(lines) * 0.3:  # More than 30% all lowercase
            score -= 4
    
    # Check for consistent spacing (not too many blank lines)
    blank_lines = resume_text.count('\n\n\n')
    if blank_lines > 5:
        score -= 2
    
    return max(0, score)


def check_action_verbs(resume_text: str) -> int:
    """Check for strong action verbs. Returns score 0-7."""
    action_verbs = [
        'achieved', 'improved', 'developed', 'created', 'designed', 'implemented', 'managed',
        'led', 'increased', 'reduced', 'optimized', 'built', 'launched', 'delivered',
        'established', 'streamlined', 'automated', 'engineered', 'architected', 'spearheaded'
    ]
    
    text_lower = resume_text.lower()
    found_verbs = sum(1 for verb in action_verbs if verb in text_lower)
    
    # Score based on number of action verbs found
    if found_verbs >= 8:
        return 7
    elif found_verbs >= 5:
        return 5
    elif found_verbs >= 3:
        return 3
    elif found_verbs >= 1:
        return 1
    else:
        return 0


def check_quantifiable_achievements(resume_text: str) -> int:
    """Check for quantifiable achievements (numbers, percentages, metrics). Returns score 0-10."""
    score = 0
    
    # Check for percentages
    percentage_count = len(re.findall(r'\d+%', resume_text))
    score += min(3, percentage_count)
    
    # Check for dollar amounts
    dollar_count = len(re.findall(r'\$[\d,]+', resume_text))
    score += min(2, dollar_count)
    
    # Check for numbers with context (e.g., "20 projects", "500 users")
    number_context = len(re.findall(r'\d+\s+\w+', resume_text))
    score += min(3, number_context // 2)
    
    # Check for metrics keywords
    metrics_keywords = ['increased', 'decreased', 'reduced', 'improved', 'grew', 'saved']
    metrics_with_numbers = sum(1 for keyword in metrics_keywords 
                               if re.search(rf'{keyword}.*?\d+', resume_text.lower()))
    score += min(2, metrics_with_numbers)
    
    return min(10, score)


def generate_ats_recommendations(model, resume_text: str, jd_text: str, score_data: dict) -> List[str]:
    """Generate AI-powered ATS improvement recommendations."""
    prompt = (
        f"Analyze this resume's ATS compatibility score of {score_data['total_score']}/100.\n\n"
        f"Score breakdown:\n"
        f"- Keywords: {score_data['breakdown']['keywords']}/40\n"
        f"- Sections: {score_data['breakdown']['sections']}/20\n"
        f"- Contact: {score_data['breakdown']['contact']}/10\n"
        f"- Length: {score_data['breakdown']['length']}/10\n\n"
        f"Job Description:\n{jd_text[:500]}...\n\n"
        f"Resume excerpt:\n{resume_text[:500]}...\n\n"
        "Provide 3-5 specific, actionable recommendations to improve the ATS score. "
        "Focus on the lowest-scoring areas. Be concise and practical. "
        "Format as a JSON array of strings."
    )
    try:
        response = model.generate_content(prompt)
        recommendations = json.loads(response.text)
        return recommendations if isinstance(recommendations, list) else []
    except Exception:
        # Fallback recommendations
        recs = []
        if score_data['breakdown']['keywords'] < 25:
            recs.append("Add more keywords from the job description to your resume")
        if score_data['breakdown']['sections'] < 15:
            recs.append("Use standard section headers like 'Experience', 'Education', 'Skills'")
        if score_data['breakdown']['contact'] < 8:
            recs.append("Ensure your email and phone number are clearly visible")
        return recs[:5]


def calculate_ats_score(model, resume_text: str, jd_text: str, jd_skills: Set[str], resume_skills: Set[str]) -> dict:
    """Calculate overall ATS compatibility score with strict criteria."""
    # 1. Keyword match score (0-40 points) - Most important
    keyword_match = len(jd_skills & resume_skills) / len(jd_skills) if jd_skills else 0
    keyword_score = int(keyword_match * 40)
    
    # 2. Section score (0-15 points) - Stricter validation
    section_score = check_standard_sections(resume_text)
    
    # 3. Contact info score (0-10 points) - With LinkedIn bonus
    contact_score = check_contact_info(resume_text)
    
    # 4. Format quality score (0-15 points) - Actually evaluated now!
    format_score = check_format_quality(resume_text)
    
    # 5. Length score (0-8 points) - Stricter ideal range
    length_score = check_resume_length(resume_text)
    
    # 6. Action verbs score (0-7 points) - NEW!
    action_verbs_score = check_action_verbs(resume_text)
    
    # 7. Quantifiable achievements score (0-10 points) - NEW!
    achievements_score = check_quantifiable_achievements(resume_text)
    
    # Total: 40 + 15 + 10 + 15 + 8 + 7 + 10 = 105 points (capped at 100)
    total_score = (keyword_score + section_score + contact_score + format_score + 
                   length_score + action_verbs_score + achievements_score)
    
    score_data = {
        "total_score": min(100, total_score),
        "keyword_match_percentage": int(keyword_match * 100),
        "breakdown": {
            "keywords": keyword_score,
            "sections": section_score,
            "contact": contact_score,
            "format": format_score,
            "length": length_score,
            "action_verbs": action_verbs_score,
            "achievements": achievements_score
        }
    }
    
    recommendations = generate_ats_recommendations(model, resume_text, jd_text, score_data)
    
    return {
        "score": score_data["total_score"],
        "breakdown": score_data["breakdown"],
        "recommendations": recommendations
    }


def analyze(resume_text: str, jd_text: str, bullets: List[str]) -> AnalysisResult:
    model = ensure_gemini()
    
    # Use AI-powered skill extraction for better accuracy
    jd_skills = extract_skills_with_ai(model, jd_text)
    resume_skills = extract_skills_with_ai(model, resume_text)
    missing = sorted(jd_skills - resume_skills)
    overlap = sorted(jd_skills & resume_skills)

    # Model already initialized above
    rewritten = rewrite_bullets(model, bullets, jd_text)
    cover_letter = generate_cover_letter(model, resume_text, jd_text)
    tailored_resume = generate_tailored_resume(model, resume_text, jd_text)
    
    # Calculate ATS score
    ats_data = calculate_ats_score(model, resume_text, jd_text, jd_skills, resume_skills)

    return AnalysisResult(
        jd_skills=sorted(jd_skills),
        resume_skills=sorted(resume_skills),
        missing_skills=missing,
        overlap_skills=overlap,
        rewritten_bullets=rewritten,
        cover_letter=cover_letter,
        tailored_resume=tailored_resume,
        ats_score=ats_data["score"],
        ats_breakdown=ats_data["breakdown"],
        ats_recommendations=ats_data["recommendations"],
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
