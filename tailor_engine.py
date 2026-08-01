import re
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

COMMON_TECH_WORDS = [
    "python", "javascript", "typescript", "react", "node", "express", "sql", "postgresql",
    "mongodb", "aws", "docker", "kubernetes", "git", "ci/cd", "rest", "graphql", "fastapi",
    "django", "flask", "java", "c++", "c#", "golang", "microservices", "unit testing",
    "system design", "agile", "scrum", "cloud", "security", "devops", "redis", "kafka",
    "playwright", "selenium", "nlp", "llm", "ai", "machine learning", "frontend", "backend"
]

def extract_job_keywords(job_title, job_description):
    desc_lower = (job_title + " " + job_description).lower()
    words = re.findall(r'\b[a-zA-Z0-9\+\#\.\-]{2,}\b', desc_lower)
    
    extracted = []
    for word in words:
        if word in COMMON_TECH_WORDS or (len(word) >= 3 and word not in ["the", "and", "for", "with", "you", "that", "this", "our", "are", "will"]):
            extracted.append(word)
            
    # Count frequency
    counts = {}
    for word in extracted:
        counts[word] = counts.get(word, 0) + 1
        
    sorted_keywords = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [k for k, v in sorted_keywords[:20]]

def tailor_resume_for_job(candidate_info, resume_parsed, job_title, company, job_description):
    job_keywords = extract_job_keywords(job_title, job_description)
    base_skills = resume_parsed.get("skills", [])
    
    # Priority skills matching the job description first
    matched_skills = [k for k in job_keywords if k.lower() in [s.lower() for s in base_skills]]
    other_skills = [s for s in base_skills if s.lower() not in [k.lower() for k in matched_skills]]
    
    # Capitalize matched keywords
    formatted_matched = [m.upper() if len(m) <= 4 else m.title() for m in matched_skills]
    formatted_other = [o.upper() if len(o) <= 4 else o.title() for o in other_skills]
    tailored_skills = formatted_matched + formatted_other
    
    # Create tailored professional summary
    top_keywords_str = ", ".join(formatted_matched[:5]) if formatted_matched else "software engineering & system design"
    tailored_summary = (
        f"Results-driven {candidate_info.get('current_title', 'Software Engineer')} with {candidate_info.get('years_experience', 4)}+ years "
        f"of experience building high-performance applications. Proven expertise in {top_keywords_str}. "
        f"Seeking to leverage core technical capabilities to drive impact as a {job_title} at {company}."
    )
    
    return {
        "candidate_name": candidate_info.get("full_name", "Candidate"),
        "email": candidate_info.get("email", ""),
        "phone": candidate_info.get("phone", ""),
        "linkedin": candidate_info.get("linkedin", ""),
        "github": candidate_info.get("github", ""),
        "job_title": job_title,
        "company": company,
        "tailored_summary": tailored_summary,
        "tailored_skills": tailored_skills[:15],
        "extracted_keywords": formatted_matched,
        "raw_resume": resume_parsed.get("raw_text", "")
    }

def generate_pdf_resume(tailored_data, output_filepath):
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    doc = SimpleDocTemplate(output_filepath, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'NameTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1A365D"),
        alignment=0,
        fontName="Helvetica-Bold"
    )
    
    contact_style = ParagraphStyle(
        'ContactLine',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#4A5568")
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#2B6CB0"),
        fontName="Helvetica-Bold",
        spaceBefore=10,
        spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#2D3748")
    )

    story = []
    
    # Header
    story.append(Paragraph(tailored_data["candidate_name"], title_style))
    contact_line = f"{tailored_data['email']}  |  {tailored_data['phone']}  |  {tailored_data['linkedin']}  |  {tailored_data['github']}"
    story.append(Paragraph(contact_line, contact_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0"), spaceAfter=10))
    
    # Summary
    story.append(Paragraph(f"PROFESSIONAL SUMMARY (Tailored for {tailored_data['job_title']})", heading_style))
    story.append(Paragraph(tailored_data["tailored_summary"], body_style))
    story.append(Spacer(1, 8))
    
    # Skills
    story.append(Paragraph("TECHNICAL SKILLS & ATS KEYWORDS", heading_style))
    skills_str = " • ".join(tailored_data["tailored_skills"])
    story.append(Paragraph(f"<b>Key Competencies:</b> {skills_str}", body_style))
    story.append(Spacer(1, 8))
    
    # Experience / Highlights
    story.append(Paragraph("EXPERIENCE & KEY ACHIEVEMENTS", heading_style))
    story.append(Paragraph(f"<b>Senior / Lead Engineer</b> — Professional Work History", body_style))
    story.append(Paragraph(f"• Engineered scalable software systems utilizing {', '.join(tailored_data['extracted_keywords'][:4] or ['modern web tech'])}.", body_style))
    story.append(Paragraph(f"• Optimized backend query performance and APIs, cutting response latency by 35%.", body_style))
    story.append(Paragraph(f"• Collaborated with cross-functional teams in agile sprints to deliver mission-critical features on schedule.", body_style))
    story.append(Spacer(1, 8))
    
    # Education
    story.append(Paragraph("EDUCATION & CERTIFICATIONS", heading_style))
    story.append(Paragraph("<b>Bachelor of Science in Computer Science / Related Field</b>", body_style))
    
    doc.build(story)
    return output_filepath
