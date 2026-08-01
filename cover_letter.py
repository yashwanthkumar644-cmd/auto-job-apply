import os

COVER_LETTER_TEMPLATE = """Dear Hiring Manager at {company},

I am writing to express my strong enthusiasm for the {job_title} role at {company}. With {years_exp}+ years of software engineering experience and a proven track record of developing scalable applications using {top_skills}, I am confident in my ability to immediately contribute to your engineering team's mission.

In reviewing the position requirements for {job_title}, I was particularly excited to see your emphasis on {key_requirement}. Throughout my career, I have specialized in building robust software solutions, optimizing performance, and delivering clean, well-tested code in collaborative agile environments.

Key highlights of my qualifications include:
- Expertise in {top_skills} and modern development methodologies.
- Hands-on experience architecting backend microservices and responsive user interfaces.
- Strong problem-solving mindset with a focus on code quality, performance, and user satisfaction.

I am eager to bring my technical skills and enthusiasm to {company}. Thank you for your time and consideration. I welcome the opportunity to discuss how my background aligns with your team's goals in an interview.

Sincerely,

{candidate_name}
{email} | {phone}
{linkedin}
"""

def generate_cover_letter(candidate_info, tailored_data, job_title, company, job_description=""):
    top_skills_list = tailored_data.get("extracted_keywords", []) or ["software engineering", "python", "system design"]
    top_skills_str = ", ".join(top_skills_list[:3])
    
    key_req = top_skills_list[0] if top_skills_list else "high-quality software development"
    
    letter_text = COVER_LETTER_TEMPLATE.format(
        company=company,
        job_title=job_title,
        years_exp=candidate_info.get("years_experience", 4),
        top_skills=top_skills_str,
        key_requirement=key_req,
        candidate_name=candidate_info.get("full_name", "Candidate"),
        email=candidate_info.get("email", ""),
        phone=candidate_info.get("phone", ""),
        linkedin=candidate_info.get("linkedin", "")
    )
    
    return letter_text

def save_cover_letter_to_file(letter_text, output_filepath):
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    with open(output_filepath, 'w', encoding='utf-8') as f:
        f.write(letter_text)
    return output_filepath
