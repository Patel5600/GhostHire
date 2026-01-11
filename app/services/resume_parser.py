import re

def parse_resume(text: str) -> dict:
    data = {}

    # Extract email
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    if email_match:
        data["email"] = email_match.group(0)

    # Extract phone
    phone_match = re.search(r"\+?\d[\d\s\-]{8,15}", text)
    if phone_match:
        data["phone"] = phone_match.group(0)

    # Extract skills (simple keyword scan)
    skills_keywords = [
        "python", "java", "javascript", "react", "node", "docker",
        "aws", "sql", "fastapi", "django", "flask"
    ]

    found_skills = [skill for skill in skills_keywords if skill.lower() in text.lower()]
    data["skills"] = found_skills

    return data
