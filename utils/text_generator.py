class TextGenerator:

    def generate_cover_letter(self, resume_text, jd_analysis):
        job_title = jd_analysis.get("job_title", "the position")
        keywords = jd_analysis.get("keywords", [])

        skills_text = ", ".join(keywords[:5]) if keywords else "relevant technical skills"

        cover_letter = f"""
Dear Hiring Manager,

I am excited to apply for the {job_title} role.

With my experience in {skills_text}, I have developed strong technical and problem-solving abilities. I have worked on projects involving these technologies and have consistently delivered efficient and scalable solutions.

I am particularly interested in this role as it aligns well with my skill set and career goals. I am eager to contribute my knowledge and continue learning in a professional environment.

I would welcome the opportunity to discuss how my skills and experiences align with your requirements.

Thank you for your time and consideration.

Sincerely,  
Tanisha Srivastava
"""

        return cover_letter.strip()


    def generate_outreach_mail(self, jd_analysis):
        job_title = jd_analysis.get("job_title", "this role")
        company = jd_analysis.get("company_name", "your company")

        message = f"""
Hi,

I recently came across the {job_title} opportunity at {company}, and I found it very interesting.

My background aligns well with the skills required for this role, and I would love to connect and learn more about this opportunity.

Looking forward to your response.

Best regards,  
Tanisha
"""

        return message.strip()


    def generate_jd_match_summary(self, keyword_match):
        match_percent = keyword_match.get("match_percent", 0)
        matched = keyword_match.get("matched", [])
        missing = keyword_match.get("missing", [])

        summary = f"""
Match Score: {match_percent}%

Matched Skills:
{", ".join(matched[:10]) if matched else "None"}

Missing Skills:
{", ".join(missing[:10]) if missing else "None"}

Recommendation:
Focus on adding missing skills into your resume and improving alignment with job requirements.
"""

        return summary.strip()