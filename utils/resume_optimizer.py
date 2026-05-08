import re

class ResumeOptimizer:

    def optimize_resume(self, resume_text, jd_analysis):
        jd_keywords = jd_analysis.get("keywords", [])

        optimized = resume_text
        added_keywords = []

        # ---------------------------
        # 1. ADD MISSING KEYWORDS
        # ---------------------------
        for keyword in jd_keywords:
            if keyword.lower() not in resume_text.lower():
                optimized += f"\n- Experience with {keyword}"
                added_keywords.append(keyword)

        # ---------------------------
        # 2. IMPROVE BULLET POINTS
        # ---------------------------
        action_verbs = [
            "Developed", "Implemented", "Designed",
            "Optimized", "Built", "Led"
        ]

        lines = optimized.split("\n")
        new_lines = []

        for i, line in enumerate(lines):
            if line.strip().startswith("-"):
                clean_line = line.strip()[1:].strip()

                # Skip if already good
                if any(verb.lower() in clean_line.lower() for verb in action_verbs):
                    new_lines.append(line)
                else:
                    verb = action_verbs[i % len(action_verbs)]
                    new_lines.append(f"- {verb} {clean_line}")
            else:
                new_lines.append(line)

        optimized = "\n".join(new_lines)

        # ---------------------------
        # 3. ADD PROFESSIONAL SUMMARY (IF MISSING)
        # ---------------------------
        if "summary" not in optimized.lower():
            summary = self.generate_summary(jd_keywords)
            optimized = f"SUMMARY\n{summary}\n\n" + optimized

        return {
            "optimized_resume": optimized,
            "keywords_added": added_keywords
        }

    def generate_summary(self, keywords):
        top_skills = ", ".join(keywords[:5]) if keywords else "various technologies"

        return f"""
Motivated professional with experience in {top_skills}. 
Skilled in developing scalable solutions and working with modern technologies.
Seeking opportunities to contribute and grow in a dynamic environment.
"""