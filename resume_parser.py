import os
import re
import json

def extract_text_from_file(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Resume file not found at: {filepath}")
    
    ext = os.path.splitext(filepath)[1].lower()
    text = ""
    
    if ext == ".txt" or ext == ".md":
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    elif ext == ".pdf":
        try:
            import pdfplumber
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"
        except Exception:
            # Fallback to PyPDF2 or basic string extraction
            try:
                import pypdf
                reader = pypdf.PdfReader(filepath)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            except Exception as e:
                text = f"[Unable to extract PDF text directly: {e}]"
    elif ext == ".docx":
        try:
            import docx
            doc = docx.Document(filepath)
            text = "\n".join([p.text for p in doc.paragraphs if p.text])
        except Exception as e:
            text = f"[Unable to extract DOCX text: {e}]"
    else:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
            
    return text

def parse_resume(filepath_or_text):
    if os.path.exists(filepath_or_text):
        raw_text = extract_text_from_file(filepath_or_text)
    else:
        raw_text = filepath_or_text

    # Extract email
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_text)
    email = email_match.group(0) if email_match else ""

    # Extract phone
    phone_match = re.search(r'\(?\+?[0-9]{1,3}\)?[-. ]?\(?[0-9]{3}\)?[-. ]?[0-9]{3}[-. ]?[0-9]{4}', raw_text)
    phone = phone_match.group(0) if phone_match else ""

    # Common technical skill tokens
    skill_keywords = [
        "python", "javascript", "typescript", "react", "node.js", "next.js", "vue", "angular",
        "html", "css", "tailing", "sql", "postgresql", "mysql", "mongodb", "sqlite", "redis",
        "aws", "azure", "gcp", "docker", "kubernetes", "git", "ci/cd", "rest api", "graphql",
        "fastapi", "django", "flask", "express", "java", "c++", "c#", "go", "rust", "ruby",
        "agile", "scrum", "microservices", "system design", "unit testing", "playwright", "selenium"
    ]
    
    found_skills = []
    text_lower = raw_text.lower()
    for skill in skill_keywords:
        if re.search(rf'\b{re.escape(skill)}\b', text_lower):
            found_skills.append(skill.title() if len(skill) <= 4 else skill.capitalize())

    parsed = {
        "raw_text": raw_text,
        "email": email,
        "phone": phone,
        "skills": list(set(found_skills)),
        "summary": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text
    }
    return parsed
