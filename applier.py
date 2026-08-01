import os
import requests
import json
from datetime import datetime
from db import is_job_applied_or_skipped, record_job_application
from tailor_engine import tailor_resume_for_job, generate_pdf_resume
from cover_letter import generate_cover_letter, save_cover_letter_to_file
from matcher import calculate_match_score

OUT_DIR = os.path.join(os.path.dirname(__file__), "generated_applications")

def send_webhook_notification(webhook_url, title, company, match_score, platform, job_url):
    if not webhook_url:
        return
    payload = {
        "content": f"🚀 **Applied to New Job!**\n**Role:** {title}\n**Company:** {company}\n**Match Score:** {match_score}%\n**Platform:** {platform}\n**URL:** {job_url}"
    }
    try:
        requests.post(webhook_url, json=payload, timeout=5)
    except Exception as e:
        print(f"[Applier] Webhook alert error: {e}")

def process_and_apply_job(job, config, resume_parsed, dry_run=False):
    job_url = job["job_url"]
    
    # Check duplicate in SQLite DB
    existing_status = is_job_applied_or_skipped(job_url)
    if existing_status:
        return {"status": "SKIPPED_DUPLICATE", "reason": f"Already processed as {existing_status}"}

    candidate = config["candidate"]
    preferences = config["preferences"]
    min_score = preferences.get("min_match_score", 65)

    # 1. Match score calculation
    match_score = calculate_match_score(resume_parsed.get("skills", []), preferences, job)
    
    if match_score < min_score:
        record_job_application(
            job_id=job["id"],
            title=job["title"],
            company=job["company"],
            location=job["location"],
            platform=job["platform"],
            job_url=job_url,
            match_score=match_score,
            keywords=[],
            cover_letter="",
            status="SKIPPED_LOW_MATCH",
            notes=f"Score {match_score}% below threshold {min_score}%"
        )
        return {"status": "SKIPPED_LOW_MATCH", "match_score": match_score}

    # 2. Dynamically tailor resume keywords & summary
    tailored_data = tailor_resume_for_job(
        candidate_info=candidate,
        resume_parsed=resume_parsed,
        job_title=job["title"],
        company=job["company"],
        job_description=job.get("description", "")
    )
    
    job_slug = f"{job['company'].lower().replace(' ', '_')}_{job['id']}"
    pdf_path = os.path.join(OUT_DIR, job_slug, "tailored_resume.pdf")
    cl_path = os.path.join(OUT_DIR, job_slug, "cover_letter.txt")
    
    generate_pdf_resume(tailored_data, pdf_path)

    # 3. Generate tailored cover letter
    cover_letter_text = generate_cover_letter(
        candidate_info=candidate,
        tailored_data=tailored_data,
        job_title=job["title"],
        company=job["company"],
        job_description=job.get("description", "")
    )
    save_cover_letter_to_file(cover_letter_text, cl_path)

    # 4. Perform Playwright Browser auto-fill and submission
    from browser_applier import apply_via_browser
    browser_res = apply_via_browser(
        job_url=job_url,
        candidate_info=candidate,
        tailored_pdf_path=pdf_path,
        cover_letter_text=cover_letter_text,
        dry_run=dry_run
    )

    status = "APPLIED" if not dry_run else "SIMULATED_APPLIED"
    
    record_job_application(
        job_id=job["id"],
        title=job["title"],
        company=job["company"],
        location=job["location"],
        platform=job["platform"],
        job_url=job_url,
        match_score=match_score,
        keywords=tailored_data["extracted_keywords"],
        cover_letter=cover_letter_text,
        status=status,
        notes=f"Browser status: {browser_res.get('details')}. Tailored PDF at {pdf_path}"
    )

    # 5. Alert Notification
    webhook_url = config.get("cloud_runner", {}).get("webhook_notification_url", "")
    if webhook_url:
        send_webhook_notification(webhook_url, job["title"], job["company"], match_score, job["platform"], job_url)

    return {
        "status": status,
        "match_score": match_score,
        "tailored_pdf": pdf_path,
        "cover_letter_path": cl_path,
        "keywords": tailored_data["extracted_keywords"]
    }
