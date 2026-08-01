import os
import json
import yaml
from db import save_profile_key, get_profile_key

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.yaml")

DEFAULT_CONFIG = {
    "candidate": {
        "full_name": "Jane Doe",
        "email": "janedoe@example.com",
        "phone": "+1-555-0199",
        "linkedin": "https://linkedin.com/in/janedoe",
        "github": "https://github.com/janedoe",
        "portfolio": "https://janedoe.dev",
        "location": "New York, NY",
        "years_experience": 4,
        "current_title": "Software Engineer",
        "work_authorization": "Authorized to work in US without sponsorship",
        "sponsorship_required": "No",
        "notice_period": "Immediate / 2 Weeks"
    },
    "preferences": {
        "target_roles": ["Software Engineer", "Full Stack Engineer", "Python Developer", "Backend Developer"],
        "locations": ["Remote", "New York, NY", "San Francisco, CA"],
        "remote_only": False,
        "job_types": ["fulltime", "contract"],
        "min_salary": 90000,
        "min_match_score": 65,  # Percentage threshold required to apply
        "max_applications_per_run": 10,
        "platforms": ["LinkedIn", "Indeed", "Glassdoor", "ZipRecruiter", "RemoteOK"]
    },
    "screening_answers": {
        "years_experience": "4+",
        "us_work_authorization": "Yes",
        "require_sponsorship": "No",
        "willing_to_relocate": "Yes",
        "expected_salary": "$110,000"
    },
    "cloud_runner": {
        "enabled": True,
        "cron_schedule": "0 */6 * * *",  # Every 6 hours
        "webhook_notification_url": ""   # Telegram, Discord, or Slack Webhook URL
    }
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config if config else DEFAULT_CONFIG
        except Exception:
            pass
    # Fallback to DB stored config
    db_config = get_profile_key("config")
    if db_config:
        return db_config
    return DEFAULT_CONFIG

def save_config(config_dict):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(config_dict, f, default_flow_style=False)
    save_profile_key("config", config_dict)
    return True
