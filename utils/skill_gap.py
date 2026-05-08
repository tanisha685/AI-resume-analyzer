class SkillGapAnalyzer:

    def analyze(self, match_data):
        missing = match_data.get("missing", [])

        recommendations = []
        priority = "Low"

        if len(missing) >= 5:
            priority = "High"
        elif len(missing) >= 3:
            priority = "Medium"

        for skill in missing:
            recommendations.append(self.get_learning_suggestion(skill))

        return {
            "missing_skills": missing,
            "recommendations": recommendations,
            "priority": priority
        }

    def get_learning_suggestion(self, skill):
        return f"Learn {skill} through projects and online courses"