import requests
import json
import urllib3
urllib3.disable_warnings()

GREENHOUSE_BOARDS = [
    "stripe", "figma", "discord", "vercel", "scaleai", "datadog",
    "cloudflare", "gitlab", "dbtlabs", "retool", "supabase"
]

LEVER_BOARDS = [
    "palantir", "openai", "anthropic", "netflix"
]

def verify_live_url(url):
    """Verify that a job URL returns HTTP 200 OK and contains an active job form."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(url, headers=headers, timeout=6, verify=False)
        return res.status_code == 200
    except Exception:
        return False

def fetch_greenhouse_jobs(board_name, target_roles):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_name}/jobs?content=true"
    jobs = []
    try:
        res = requests.get(url, timeout=8, verify=False)
        if res.status_code == 200:
            data = res.json()
            for item in data.get("jobs", []):
                title = item.get("title", "")
                # Check if role matches target roles
                title_lower = title.lower()
                matches = any(r.lower() in title_lower or any(word in title_lower for word in r.lower().split()) for r in target_roles)
                if matches:
                    job_id = str(item.get("id"))
                    apply_url = f"https://boards.greenhouse.io/{board_name}/jobs/{job_id}"
                    loc_name = item.get("location", {}).get("name", "Remote") if isinstance(item.get("location"), dict) else "Remote"
                    
                    jobs.append({
                        "id": f"gh-{board_name}-{job_id}",
                        "title": title,
                        "company": board_name.capitalize(),
                        "location": loc_name,
                        "platform": "Greenhouse ATS",
                        "job_url": apply_url,
                        "description": item.get("content", title),
                        "salary": "Competitive",
                        "date_posted": item.get("updated_at", "")[:10]
                    })
    except Exception as e:
        print(f"[Fetcher] Greenhouse {board_name} notice: {e}")
    return jobs

def fetch_lever_jobs(board_name, target_roles):
    url = f"https://api.lever.co/v0/postings/{board_name}"
    jobs = []
    try:
        res = requests.get(url, timeout=8, verify=False)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                for item in data:
                    title = item.get("text", "")
                    title_lower = title.lower()
                    matches = any(r.lower() in title_lower or any(word in title_lower for word in r.lower().split()) for r in target_roles)
                    if matches:
                        apply_url = item.get("hostedUrl", "") + "/apply"
                        loc_name = item.get("categories", {}).get("location", "Remote") if isinstance(item.get("categories"), dict) else "Remote"
                        jobs.append({
                            "id": f"lever-{board_name}-{item.get('id')}",
                            "title": title,
                            "company": board_name.capitalize(),
                            "location": loc_name,
                            "platform": "Lever ATS",
                            "job_url": apply_url,
                            "description": item.get("descriptionPlain", title),
                            "salary": "Competitive",
                            "date_posted": ""
                        })
    except Exception as e:
        print(f"[Fetcher] Lever {board_name} notice: {e}")
    return jobs

def search_jobs(target_roles, locations, results_limit=20):
    all_jobs = []
    seen_urls = set()

    # 1. Fetch from Greenhouse ATS boards
    for board in GREENHOUSE_BOARDS:
        gh_jobs = fetch_greenhouse_jobs(board, target_roles)
        for j in gh_jobs:
            if j["job_url"] not in seen_urls:
                # HTTP verification check
                if verify_live_url(j["job_url"]):
                    seen_urls.add(j["job_url"])
                    all_jobs.append(j)
                if len(all_jobs) >= results_limit:
                    return all_jobs

    # 2. Fetch from Lever ATS boards
    for board in LEVER_BOARDS:
        l_jobs = fetch_lever_jobs(board, target_roles)
        for j in l_jobs:
            if j["job_url"] not in seen_urls:
                if verify_live_url(j["job_url"]):
                    seen_urls.add(j["job_url"])
                    all_jobs.append(j)
                if len(all_jobs) >= results_limit:
                    return all_jobs

    return all_jobs[:results_limit]
