# ResumeBoost 🚀

Ever felt like your resume just disappears into the void when you apply for jobs? Yeah, me too. That's why I built ResumeBoost - a web app that helps you understand how well your resume matches a job posting and gives you actionable feedback to improve it.

## What Does It Do?

ResumeBoost analyzes your resume against any job description and gives you:

- **ATS Score** - See how well your resume would perform with Applicant Tracking Systems (those robots that filter resumes before humans even see them)
- **Skill Gap Analysis** - Find out which skills from the job posting you're missing and which ones you already have
- **AI-Powered Bullet Points** - Get your resume bullets rewritten to better match the job using Google's Gemini AI
- **Custom Cover Letter** - Generate a tailored cover letter based on the job description
- **Downloadable Resume** - Get a professionally formatted .docx file ready to submit

The whole thing runs in your browser with a clean, modern interface. Just upload your resume (PDF or TXT), paste the job description, and hit analyze.

## How It Works

When you submit your resume and a job description, here's what happens behind the scenes:

1. **Text Extraction** - The backend pulls text from your resume file (works with PDFs and plain text)
2. **Skill Parsing** - A regex-based parser identifies technical skills, tools, and keywords from both your resume and the job posting
3. **Gap Analysis** - Compares the two lists to show you what's missing and what matches
4. **ATS Scoring** - Calculates a compatibility score based on keyword matches, formatting, and other ATS-friendly factors
5. **AI Enhancement** - Sends your bullet points to Google's Gemini AI to rewrite them with better impact and relevance
6. **Cover Letter Generation** - Uses Gemini to craft a personalized cover letter
7. **Document Creation** - Packages everything into a downloadable Word document

## Tech Stack

I wanted to keep this simple and free to run, so here's what I used:

**Frontend:**
- React + Vite for the UI
- Tailwind CSS for styling (because I'm not a designer and Tailwind makes things look good fast)
- Lucide icons for the interface elements

**Backend:**
- Python with Flask for the API
- Google Gemini AI (free tier) for the smart stuff
- python-docx for creating Word documents
- PyPDF2 for reading PDF resumes

**Deployment:**
- Vercel for hosting (completely free)
- Serverless functions for the backend

## Why I Built This

Job hunting sucks. You spend hours customizing your resume for each application, never knowing if it'll even make it past the initial screening. I wanted a tool that could:

1. Tell me if my resume would actually get past ATS filters
2. Show me exactly what skills I need to highlight
3. Help me write better bullet points without spending hours on it
4. Generate cover letters that don't sound generic

And I wanted it to be free - no subscriptions, no credits, no BS. Just a useful tool.

## The Challenges

Building this taught me a few things:

- **PDF parsing is messy** - Different PDF formats extract text differently. Had to handle a lot of edge cases.
- **ATS scoring is subjective** - There's no "official" ATS algorithm, so I based the scoring on common best practices and keyword matching.
- **AI can be unpredictable** - Gemini sometimes gets creative in ways you don't expect. Had to fine-tune the prompts a lot.
- **Serverless has limits** - Vercel's free tier has execution time limits, so I had to optimize the backend to run fast.

## What's Next?

This is a working MVP, but there's always room to improve:

- Better ATS scoring algorithm
- Support for more file formats (DOCX uploads)
- Resume templates with different styles
- Job description scraping from LinkedIn/Indeed
- Browser extension for one-click analysis

## License

MIT - feel free to check out the code and learn from it.

---

Built with ☕ and frustration from too many rejected applications.
