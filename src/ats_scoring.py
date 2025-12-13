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
