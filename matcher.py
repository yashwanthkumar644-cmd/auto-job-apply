import re

def calculate_match_score(resume_skills, candidate_info, job):
    title = job.get("title", "").lower()
    description = job.get("description", "").lower()
    target_roles = [r.lower() for r in candidate_info.get("target_roles", ["software engineer"])]
    
    score = 50.0  # Base starting match score
    
    # Title alignment (+20 points max)
    for role in target_roles:
        if role in title:
            score += 20.0
            break
        elif any(word in title for word in role.split()):
            score += 10.0
            break
            
    # Skill matching (+30 points max)
    if resume_skills:
        matched_count = 0
        for skill in resume_skills:
            if re.search(rf'\b{re.escape(skill.lower())}\b', description):
                matched_count += 1
        skill_ratio = min(1.0, matched_count / max(3, len(resume_skills)))
        score += skill_ratio * 30.0
    else:
        score += 15.0
        
    # Remote / Location bonus (+5 points)
    pref_locations = [l.lower() for l in candidate_info.get("locations", ["remote"])]
    job_loc = job.get("location", "").lower()
    if "remote" in pref_locations and "remote" in job_loc:
        score += 5.0

    return min(99.0, max(35.0, round(score, 1)))
