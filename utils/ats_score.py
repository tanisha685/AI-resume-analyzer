class ATSScorer:

    def calculate_score(self, match_data, resume_text):
        score = 0

        # --------------------------
        # 1. Keyword Match (50%)
        # --------------------------
        match_percent = match_data.get("match_percent", 0)
        score += match_percent * 0.5

        # --------------------------
        # 2. Resume Length (20%)
        # --------------------------
        word_count = len(resume_text.split())

        if word_count > 300:
            score += 20
        elif word_count > 150:
            score += 10
        else:
            score += 5

        # --------------------------
        # 3. Sections Present (20%)
        # --------------------------
        sections = ["experience", "education", "skills"]
        section_score = 0

        for sec in sections:
            if sec in resume_text.lower():
                section_score += 1

        score += (section_score / len(sections)) * 20

        # --------------------------
        # 4. Action Words (10%)
        # --------------------------
        action_words = ["developed", "built", "designed", "implemented"]

        if any(word in resume_text.lower() for word in action_words):
            score += 10

        return round(score)

    def get_grade(self, score):
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        else:
            return "Needs Improvement"

    def get_suggestions(self, match_data):
        suggestions = []

        if match_data.get("missing"):
            suggestions.append(
                f"Add missing keywords: {', '.join(match_data['missing'][:5])}"
            )

        if match_data.get("match_percent", 0) < 60:
            suggestions.append("Improve keyword alignment with job description")

        return suggestions