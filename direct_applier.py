import os
import requests
import urllib3
urllib3.disable_warnings()

def submit_greenhouse_application(job_url, candidate_info, pdf_path, cover_letter_text, dry_run=False):
    """
    Submits application directly to Greenhouse ATS embed endpoint.
    Triggers official Greenhouse confirmation email to candidate.
    """
    if dry_run:
        return {"status": "SIMULATED_APPLIED", "confirmed": True, "details": "Simulated Greenhouse form submission"}
        
    full_name = candidate_info.get("full_name", "Kunguma Yashwanth Kumar")
    first_name = full_name.split()[0]
    last_name = " ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else full_name
    email = candidate_info.get("email", "yashwanthkumar644@gmail.com")
    phone = candidate_info.get("phone", "+91 6361679511")

    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "cover_letter_text": cover_letter_text
    }

    files = {}
    if os.path.exists(pdf_path):
        files["resume"] = (os.path.basename(pdf_path), open(pdf_path, "rb"), "application/pdf")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        res = requests.post(job_url, data=payload, files=files, headers=headers, timeout=15, verify=False)
        if files.get("resume"):
            files["resume"][1].close()

        if res.status_code in [200, 201, 302]:
            print(f"[DirectApplier] Greenhouse Submission HTTP {res.status_code} Success!")
            return {"status": "APPLIED", "confirmed": True, "details": f"Submitted to Greenhouse ATS (HTTP {res.status_code})"}
        else:
            print(f"[DirectApplier] Greenhouse returned HTTP {res.status_code}")
            return {"status": "FAILED", "confirmed": False, "details": f"HTTP {res.status_code}: {res.text[:200]}"}
    except Exception as e:
        print(f"[DirectApplier] Submission error: {e}")
        return {"status": "FAILED", "confirmed": False, "details": str(e)}

def submit_lever_application(job_url, candidate_info, pdf_path, cover_letter_text, dry_run=False):
    """
    Submits application directly to Lever ATS endpoint.
    """
    if dry_run:
        return {"status": "SIMULATED_APPLIED", "confirmed": True, "details": "Simulated Lever form submission"}

    full_name = candidate_info.get("full_name", "Kunguma Yashwanth Kumar")
    email = candidate_info.get("email", "yashwanthkumar644@gmail.com")
    phone = candidate_info.get("phone", "+91 6361679511")

    payload = {
        "name": full_name,
        "email": email,
        "phone": phone,
        "comments": cover_letter_text
    }

    files = {}
    if os.path.exists(pdf_path):
        files["resume"] = (os.path.basename(pdf_path), open(pdf_path, "rb"), "application/pdf")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        res = requests.post(job_url, data=payload, files=files, headers=headers, timeout=15, verify=False)
        if files.get("resume"):
            files["resume"][1].close()

        if res.status_code in [200, 201, 302]:
            return {"status": "APPLIED", "confirmed": True, "details": f"Submitted to Lever ATS (HTTP {res.status_code})"}
        else:
            return {"status": "FAILED", "confirmed": False, "details": f"HTTP {res.status_code}: {res.text[:200]}"}
    except Exception as e:
        return {"status": "FAILED", "confirmed": False, "details": str(e)}

def apply_direct_ats(job_url, candidate_info, pdf_path, cover_letter_text, dry_run=False):
    if "greenhouse.io" in job_url:
        return submit_greenhouse_application(job_url, candidate_info, pdf_path, cover_letter_text, dry_run)
    elif "lever.co" in job_url:
        return submit_lever_application(job_url, candidate_info, pdf_path, cover_letter_text, dry_run)
    else:
        return {"status": "SIMULATED_APPLIED", "confirmed": False, "details": "Generic URL processed"}
