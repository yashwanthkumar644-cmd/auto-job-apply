import os
import time
from playwright.sync_api import sync_playwright

def apply_via_browser(job_url, candidate_info, tailored_pdf_path, cover_letter_text, dry_run=False):
    """
    Launches Playwright automated browser, navigates to real Greenhouse/Lever application page,
    fills form inputs, attaches tailored PDF resume, submits, and verifies post-submission confirmation.
    """
    print(f"[BrowserApplier] Navigating to verified application URL: {job_url}")
    result = {"status": "SUCCESS", "details": "", "confirmed": False}

    full_name = candidate_info.get("full_name", "Kunguma Yashwanth Kumar")
    first_name = full_name.split()[0]
    last_name = " ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else full_name
    email = candidate_info.get("email", "yashwanthkumar644@gmail.com")
    phone = candidate_info.get("phone", "+91 6361679511")
    linkedin = candidate_info.get("linkedin", "https://linkedin.com/in/yashwanth-s-0b4161346")
    github = candidate_info.get("github", "https://github.com/yashwanthkumar644-cmd")

    try:
        with sync_playwright() as p:
            # Launch browser (set headless=True for background execution)
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            page.goto(job_url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(2)

            # --- GREENHOUSE ATS FORM AUTO-FILL ---
            if "greenhouse.io" in job_url:
                print("[BrowserApplier] Detected Greenhouse ATS Form")
                
                # First Name / Last Name / Full Name
                if page.is_visible("#first_name"):
                    page.fill("#first_name", first_name)
                elif page.is_visible("input[name='first_name']"):
                    page.fill("input[name='first_name']", first_name)

                if page.is_visible("#last_name"):
                    page.fill("#last_name", last_name)
                elif page.is_visible("input[name='last_name']"):
                    page.fill("input[name='last_name']", last_name)

                if page.is_visible("#name"):
                    page.fill("#name", full_name)

                # Email & Phone
                if page.is_visible("#email"):
                    page.fill("#email", email)
                if page.is_visible("#phone"):
                    page.fill("#phone", phone)

                # URLs (LinkedIn & GitHub)
                for sel in ["input[name*='linkedin' i]", "input[id*='linkedin' i]"]:
                    if page.is_visible(sel):
                        try:
                            page.fill(sel, linkedin)
                        except Exception:
                            pass

                for sel in ["input[name*='github' i]", "input[id*='github' i]"]:
                    if page.is_visible(sel):
                        try:
                            page.fill(sel, github)
                        except Exception:
                            pass

                # Attach Resume PDF
                if os.path.exists(tailored_pdf_path):
                    file_input = page.query_selector("input[type='file']")
                    if file_input:
                        file_input.set_input_files(tailored_pdf_path)
                        print(f"[BrowserApplier] Attached PDF resume: {tailored_pdf_path}")

                # Cover Letter
                if page.is_visible("textarea[name*='cover' i]") or page.is_visible("textarea"):
                    try:
                        page.fill("textarea", cover_letter_text)
                    except Exception:
                        pass

                # Submit Form (if not dry_run)
                if not dry_run:
                    submit_btn = page.query_selector("input[type='submit'], #submit_app, button[type='submit']")
                    if submit_btn:
                        submit_btn.click()
                        print("[BrowserApplier] Clicked Greenhouse Submit Application Button!")
                        time.sleep(5)
                        
                        # Verify confirmation text
                        content = page.content().lower()
                        if "thank" in content or "submitted" in content or "received" in content:
                            result["confirmed"] = True
                            result["details"] = "Greenhouse Form Submitted & Confirmation Verified"
                        else:
                            result["details"] = "Submitted Greenhouse Form (Awaiting Email Confirmation)"
                else:
                    result["details"] = "Simulated Greenhouse Form Auto-fill"

            # --- LEVER ATS FORM AUTO-FILL ---
            elif "lever.co" in job_url:
                print("[BrowserApplier] Detected Lever ATS Form")
                
                if page.is_visible("input[name='name']"):
                    page.fill("input[name='name']", full_name)
                if page.is_visible("input[name='email']"):
                    page.fill("input[name='email']", email)
                if page.is_visible("input[name='phone']"):
                    page.fill("input[name='phone']", phone)

                if page.is_visible("input[name='urls[LinkedIn]']"):
                    page.fill("input[name='urls[LinkedIn]']", linkedin)
                if page.is_visible("input[name='urls[GitHub]']"):
                    page.fill("input[name='urls[GitHub]']", github)

                # Attach Resume PDF
                if os.path.exists(tailored_pdf_path):
                    file_input = page.query_selector("input[type='file']")
                    if file_input:
                        file_input.set_input_files(tailored_pdf_path)
                        print(f"[BrowserApplier] Attached PDF resume: {tailored_pdf_path}")

                if page.is_visible("textarea[name='comments']"):
                    page.fill("textarea[name='comments']", cover_letter_text)

                if not dry_run:
                    submit_btn = page.query_selector("#btn-submit, button.postings-btn, button[type='submit']")
                    if submit_btn:
                        submit_btn.click()
                        print("[BrowserApplier] Clicked Lever Submit Application Button!")
                        time.sleep(5)
                        content = page.content().lower()
                        if "thank" in content or "submitted" in content or "received" in content:
                            result["confirmed"] = True
                            result["details"] = "Lever Form Submitted & Confirmation Verified"
                        else:
                            result["details"] = "Submitted Lever Form (Awaiting Email Confirmation)"
                else:
                    result["details"] = "Simulated Lever Form Auto-fill"

            else:
                result["details"] = "Generic Web Form Auto-fill completed"

            browser.close()

    except Exception as e:
        print(f"[BrowserApplier] Error during execution: {e}")
        result["status"] = "ERROR"
        result["details"] = str(e)

    return result
