# ⚡ CloudApply - Terminal Job Search & Continuous Cloud Auto-Applier

**CloudApply** is an automated, terminal-based job application platform. It parses your resume, automatically extracts ATS (Applicant Tracking System) keywords, dynamically tailors your resume PDF and cover letter for each position, and applies to relevant jobs. 

It includes **GitHub Actions Cloud Runner integration**, allowing your job search and applications to continue running 24/7 in the cloud **even if your laptop is powered off**.

---

## 🌟 Key Features

1. **Terminal Interactive CLI (`cli.py`)**: Beautiful terminal interface powered by `Rich` and `Typer`.
2. **ATS Keyword Tailoring (`tailor_engine.py`)**: Scans each job posting, extracts top requested tech skills, reorders skills, and injects ATS keywords into your tailored resume.
3. **Personalized Cover Letter Generator (`cover_letter.py`)**: Automatically crafts job-specific cover letters linking your background to the company's requirements.
4. **Tailored Resume PDF Creator**: Dynamically generates sleek, formatted PDF resumes tailored per application.
5. **Continuous Cloud Worker (`cloud-deploy`)**: Deploys a free GitHub Actions Cron workflow (`.github/workflows/job_applier.yml`) so your job application sweeps run automatically every 6 hours without needing your machine powered on.
6. **SQLite Tracking (`jobs.db`)**: Tracks application history, match scores, tailored documents, and prevents duplicate applications.

---

## 🚀 Quick Start Guide

### 1. Setup Environment
```bash
pip install -r requirements.txt
```

### 2. Configure Candidate Profile
Run the interactive terminal wizard:
```bash
python cli.py setup
```

### 3. Upload & Parse Your Resume
Upload your PDF, DOCX, or TXT resume:
```bash
python cli.py upload-resume path/to/your_resume.pdf
```

### 4. Run Job Search & Application Sweep
Run a local dry-run (simulation):
```bash
python cli.py run --dry-run --limit 5
```
Or run live applications:
```bash
python cli.py run --limit 10
```

### 5. Check Application Dashboard
View your match scores and applied job history:
```bash
python cli.py status
```

---

## ☁️ Continuous Background Execution (Laptop Powered Off)

To keep applying for jobs automatically while your laptop is closed/turned off:

1. Generate the cloud deployment workflow:
   ```bash
   python cli.py cloud-deploy
   ```
2. Initialize Git and push to GitHub (Public or Private repository):
   ```bash
   git init
   git add .
   git commit -m "Initialize CloudApply"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/auto-job-apply.git
   git push -u origin main
   ```
3. GitHub Actions will execute every 6 hours automatically (100% free), search for new jobs, tailor resumes/cover letters, submit applications, and commit updated application logs back to your repository!
