import re

class JDAnalyzer:
    def __init__(self):
        # Predefined important keywords (you can expand later)
        self.tech_keywords = [
            "python", "java", "c++", "javascript", "typescript",
            "react", "node", "django", "flask",
            "sql", "mongodb", "postgresql",
            "aws", "docker", "kubernetes",
            "machine learning", "deep learning", "nlp",
            "data analysis", "pandas", "numpy",
            "git", "linux"
        ]

    def analyze(self, jd_text):
        """
        Main function
        """
        return {
            "keywords": self.extract_keywords(jd_text),
            "skills": self.extract_skills(jd_text),
            "experience": self.extract_experience(jd_text),
            "job_title": self.extract_job_title(jd_text)
        }

    def extract_keywords(self, text):
        found = []
        text_lower = text.lower()

        for word in self.tech_keywords:
            if word in text_lower:
                found.append(word)

        return list(set(found))

    def extract_skills(self, text):
        skills = []

        patterns = [
            r"experience with ([^,\n]+)",
            r"knowledge of ([^,\n]+)",
            r"proficient in ([^,\n]+)"
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            for m in matches:
                skills.append(m.strip())

        return list(set(skills))

    def extract_experience(self, text):
        match = re.search(r'(\d+\+?\s*years)', text.lower())
        if match:
            return match.group(1)
        return "Not specified"

    def extract_job_title(self, text):
        lines = text.split("\n")

        for line in lines[:5]:
            if "engineer" in line.lower() or "developer" in line.lower():
                return line.strip()

        return "Not specified"

    def keyword_match(self, resume_text, jd_keywords):
        resume_lower = resume_text.lower()

        matched = []
        missing = []

        for word in jd_keywords:
            if word in resume_lower:
                matched.append(word)
            else:
                missing.append(word)

        percentage = (len(matched) / len(jd_keywords) * 100) if jd_keywords else 0

        return {
            "matched": matched,
            "missing": missing,
            "match_percent": round(percentage, 2)
        }