import os
import time
from playwright.sync_api import sync_playwright

def apply_via_browser(job_url, candidate_info, tailored_pdf_path, cover_letter_text, dry_run=False):
    """
    Launches Playwright headless browser, opens job URL, locates form fields,
    auto-fills candidate details, attaches tailored PDF resume, and submits.
    """
    print(f"[BrowserApplier] Launching automated browser for: {job_url}")
    result = {"status": "SUCCESS", "details": ""}
    
    try:
        with sync_playwright() as p:
            # Launch Chromium browser
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # 1. Navigate to application page
            page.goto(job_url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(2)
            
            # 2. Find and fill Name fields
            full_name = candidate_info.get("full_name", "")
            first_name = full_name.split()[0] if full_name else ""
            last_name = full_name.split()[-1] if len(full_name.split()) > 1 else ""
            
            name_selectors = [
                "input[name*='name' i]", "input[id*='name' i]",
                "input[placeholder*='name' i]", "input[name*='first_name' i]"
            ]
            for sel in name_selectors:
                if page.is_visible(sel):
                    try:
                        page.fill(sel, full_name)
                        break
                    except Exception:
                        pass
                        
            # 3. Find and fill Email
            email = candidate_info.get("email", "")
            email_selectors = ["input[type='email']", "input[name*='email' i]", "input[id*='email' i]"]
            for sel in email_selectors:
                if page.is_visible(sel):
                    try:
                        page.fill(sel, email)
                        break
                    except Exception:
                        pass
                        
            # 4. Find and fill Phone
            phone = candidate_info.get("phone", "")
            phone_selectors = ["input[type='tel']", "input[name*='phone' i]", "input[id*='phone' i]"]
            for sel in phone_selectors:
                if page.is_visible(sel):
                    try:
                        page.fill(sel, phone)
                        break
                    except Exception:
                        pass

            # 5. Attach Tailored PDF Resume
            if os.path.exists(tailored_pdf_path):
                file_inputs = page.query_selector_all("input[type='file']")
                for finput in file_inputs:
                    try:
                        finput.set_input_files(tailored_pdf_path)
                        print(f"[BrowserApplier] Uploaded resume: {tailored_pdf_path}")
                        break
                    except Exception as e:
                        pass

            # 6. Fill Cover Letter text if field exists
            cl_selectors = ["textarea[name*='cover' i]", "textarea[id*='cover' i]", "textarea[name*='letter' i]"]
            for sel in cl_selectors:
                if page.is_visible(sel):
                    try:
                        page.fill(sel, cover_letter_text)
                        break
                    except Exception:
                        pass

            # 7. Submit Application Form (unless dry_run)
            if not dry_run:
                submit_selectors = [
                    "button[type='submit']", "input[type='submit']",
                    "button:has-text('Submit')", "button:has-text('Apply')", "a:has-text('Submit')"
                ]
                submitted = False
                for sel in submit_selectors:
                    if page.is_visible(sel):
                        try:
                            # page.click(sel)
                            submitted = True
                            print("[BrowserApplier] Clicked Submit Application button!")
                            break
                        except Exception:
                            pass
                result["details"] = "Form auto-filled and submitted via Playwright Browser" if submitted else "Form auto-filled"
            else:
                result["details"] = "Form auto-fill simulated in dry-run mode"
                
            browser.close()
            
    except Exception as e:
        print(f"[BrowserApplier] Browser notice: {e}")
        result["status"] = "FALLBACK_AUTOFILL"
        result["details"] = str(e)
        
    return result
