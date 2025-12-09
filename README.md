# ResumeBoost - AI-Powered Resume Optimizer

AI-powered tool that analyzes job descriptions, compares them with your resume, provides ATS compatibility scoring, rewrites bullet points with Gemini, and generates tailored cover letters.

## Setup
1) Create a virtual env and install deps:
```bash
python -m venv .venv
. .venv/Scripts/activate  # or source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
```
2) Set your Gemini key:
```bash
cp .env.example .env
# Edit .env and add your actual API keys
```

## Usage
Prepare text files:
- `job.txt` containing the job description
- `resume.txt` containing your resume text

Run the agent:
```bash
python -m src.agent --jd job.txt --resume resume.txt --bullets "Built X using Y to achieve Z" "Other bullet" --output result.json
```
- Output includes parsed skills, overlap/missing skills, rewritten bullets, and a generated cover letter. If `--output` is omitted, JSON prints to stdout.

## Optional Selenium automation
- `src/automation.py` has a `submit_application` stub. Replace the locators with those of your target form/ATS. Example:
```python
from src.automation import ApplicationData, submit_application

data = ApplicationData(
    name="Ada Lovelace",
    email="ada@example.com",
    phone="555-123-4567",
    cover_letter="Cover letter text...",
    resume_path=r"C:\path\to\resume.pdf",
    extras={"linkedin": "https://linkedin.com/in/ada"}
)

submit_application("https://example.com/apply", data)
```
- Requires a webdriver in PATH (e.g., ChromeDriver). Remove the `driver.quit()` call if you want to inspect the filled form before submission.

## Notes
- Simple regex-based skill parsing keeps dependencies light; adjust `SKILL_REGEX` in `src/agent.py` for your domain (e.g., add cloud cert patterns).
- Gemini model defaults to `gemini-1.5-flash`; change via `ensure_gemini` if you want a different model.
