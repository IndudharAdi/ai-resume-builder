import re
import json
from typing import Set

def extract_skills_with_ai_improved(model, text: str) -> Set[str]:
    """Use AI to extract technical skills from text with improved prompt."""
    prompt = (
        "You are a technical recruiter. Extract ONLY technical skills from the text below.\\n\\n"
        "Include:\\n"
        "- Programming languages (Python, Java, JavaScript, TypeScript, etc.)\\n"
        "- Frameworks and libraries (React, Spring, Django, Redux, etc.)\\n"
        "- Databases (PostgreSQL, MongoDB, Redis, DynamoDB, etc.)\\n"
        "- Cloud platforms and services (AWS, Azure, GCP, S3, Lambda, EKS, RDS, etc.)\\n"
        "- Tools and technologies (Docker, Kubernetes, Git, Jenkins, Terraform, etc.)\\n"
        "- Certifications (AWS Certified, PMP, etc.)\\n\\n"
        "Exclude:\\n"
        "- Soft skills (communication, leadership, teamwork)\\n"
        "- Action verbs (developed, managed, created, building)\\n"
        "- Adjectives (experienced, professional, skilled, proficient)\\n"
        "- Generic terms (software, development, data, code, team, years)\\n\\n"
        f"Text:\\n{text[:2000]}\\n\\n"
        "Return ONLY a valid JSON array of lowercase skill names, nothing else.\\n"
        "Example: [\"python\", \"aws\", \"docker\", \"react\"]\\n\\n"
        "JSON array:"
    )
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Try to extract JSON array if wrapped in markdown code blocks
        if "```" in response_text:
            json_match = re.search(r'```(?:json)?\\s*(\\[.*?\\])\\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
        
        # Clean up the response
        response_text = response_text.strip()
        if not response_text.startswith('['):
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start != -1 and end > start:
                response_text = response_text[start:end]
        
        skills = json.loads(response_text)
        if not isinstance(skills, list):
            raise ValueError("Response is not a list")
            
        # Filter out any remaining generic terms
        filtered_skills = set()
        generic_words = {'software', 'development', 'data', 'code', 'team', 'years', 'experience', 
                        'professional', 'building', 'availability', 'including', 'successfully',
                        'technical', 'components', 'rest', 'apis', 'frameworks'}
        
        for s in skills:
            if isinstance(s, str) and len(s) > 1:
                skill_lower = s.lower().strip()
                if skill_lower not in generic_words:
                    filtered_skills.add(skill_lower)
                    
        return filtered_skills
    except Exception as e:
        print(f"AI skill extraction failed: {e}")
        if 'response' in locals():
            print(f"Response was: {response.text[:200]}")
        # Return empty set if AI fails completely
        return set()
