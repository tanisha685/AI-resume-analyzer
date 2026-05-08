import streamlit as st
import re

from utils.resume_parser import ResumeParser
from utils.jd_analyzer import JDAnalyzer
from utils.resume_optimizer import ResumeOptimizer
from utils.text_generator import TextGenerator
from utils.resume_builder import ResumeBuilder
from utils.ats_score import ATSScorer
from utils.skill_gap import SkillGapAnalyzer
from utils.resume_store import ResumeStore


# --------------------------
# CLEAN TEXT
# --------------------------
def clean_resume_text(text):
    lines = text.split("\n")
    cleaned = []
    seen = set()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        line = line.replace("", "-").replace("•", "-")

        if line not in seen:
            cleaned.append(line)
            seen.add(line)

    return "\n".join(cleaned)


# --------------------------
# PARSER (FIXED + LINK EXTRACTION)
# --------------------------
def convert_text_to_data(resume_text, template):

    resume_text = clean_resume_text(resume_text)
    lines = [l.strip() for l in resume_text.split("\n") if l.strip()]

    # -------- CONTACT EXTRACTION --------
    email = ""
    phone = ""
    linkedin = ""
    portfolio = ""

    for line in lines[:5]:

        if "@" in line:
            email = line

        if any(char.isdigit() for char in line) and len(line) >= 10:
            phone = line

        if "linkedin.com" in line.lower():
            linkedin = line

        if "http" in line.lower() and "linkedin" not in line.lower():
            portfolio = line

    # -------- DATA STRUCTURE --------
    data = {
        "template": template,
        "personal_info": {
            "full_name": lines[0] if lines else "Candidate",
            "email": email,
            "phone": phone,
            "location": "",
            "linkedin": linkedin,
            "portfolio": portfolio
        },
        "summary": "",
        "experience": [],
        "projects": [],
        "education": [],
        "skills": {"technical": []}
    }

    section = None
    current_exp = None
    current_proj = None

    for line in lines[1:]:
        lower = line.lower()

        if "summary" in lower:
            section = "summary"
            continue
        elif "experience" in lower:
            section = "experience"
            continue
        elif "project" in lower:
            section = "projects"
            continue
        elif "education" in lower:
            section = "education"
            continue
        elif "skill" in lower:
            section = "skills"
            continue

        # -------- SUMMARY --------
        if section == "summary":
            data["summary"] += line + " "

        # -------- EXPERIENCE --------
        elif section == "experience":
            if not line.startswith("-"):
                current_exp = {
                    "position": line,
                    "company": "",
                    "start_date": "",
                    "end_date": "",
                    "description": "",
                    "responsibilities": []
                }
                data["experience"].append(current_exp)
            else:
                if current_exp:
                    current_exp["responsibilities"].append(line[1:].strip())

        # -------- PROJECTS --------
        elif section == "projects":
            if not line.startswith("-"):
                current_proj = {
                    "name": line,
                    "description": [],
                    "technologies": ""
                }
                data["projects"].append(current_proj)
            else:
                if current_proj:
                    current_proj["description"].append(line[1:].strip())

        # -------- EDUCATION --------
        elif section == "education":
            data["education"].append({
                "school": line,
                "degree": "B.Tech",
                "field": "Computer Science",
                "graduation_date": ""
            })

        # -------- SKILLS --------
        elif section == "skills":
            skills = re.split(r"[•,]", line)
            data["skills"]["technical"].extend(
                [s.strip() for s in skills if s.strip()]
            )

    return data


# --------------------------
# SCHEMA FIX
# --------------------------
def ensure_complete_schema(data):

    for edu in data.get("education", []):
        edu.setdefault("school", "")
        edu.setdefault("degree", "")
        edu.setdefault("field", "")
        edu.setdefault("graduation_date", "")

    for exp in data.get("experience", []):
        exp.setdefault("position", "")
        exp.setdefault("company", "")
        exp.setdefault("start_date", "")
        exp.setdefault("end_date", "")
        exp.setdefault("description", "")
        exp.setdefault("responsibilities", [])

    for proj in data.get("projects", []):
        proj.setdefault("name", "")
        proj.setdefault("description", [])
        proj.setdefault("technologies", "")

    if "skills" not in data:
        data["skills"] = {"technical": []}
    else:
        data["skills"].setdefault("technical", [])

    return data


# --------------------------
# MAIN FUNCTION
# --------------------------
def render_resume_enhancer():

    st.title("🚀 Resume Enhancer")

    # --------------------------
    # SESSION STATE INIT
    # --------------------------
    for key in [
        "resume_text", "jd_text", "optimized_resume",
        "cover_letter", "outreach", "jd_summary", "match_data"
    ]:
        if key not in st.session_state:
            st.session_state[key] = None if key != "jd_text" else ""

    for key in ["ats_score", "ats_grade", "ats_suggestions"]:
        if key not in st.session_state:
            st.session_state[key] = 0 if key == "ats_score" else []

    # --------------------------
    # STEP 1
    # --------------------------
    st.subheader("Step 1: Upload Resume + Job Description")

    col1, col2 = st.columns(2)

    with col1:
        store = ResumeStore()
        saved_resumes = store.get_all_resumes()

        options = ["Upload New"] + [r["name"] for r in saved_resumes]
        selected = st.selectbox("Select Resume", options)

        if selected != "Upload New":
            for r in saved_resumes:
                if r["name"] == selected:
                    st.session_state.resume_text = r["text"]
                    st.success(f"Loaded: {selected}")

        if selected == "Upload New":
            resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

            if resume_file:
                parser = ResumeParser()
                text = parser.extract_text(resume_file)

                if text:
                    st.session_state.resume_text = text
                    store.save_resume(resume_file.name, text)
                    st.success("Resume Uploaded & Saved ✅")
                else:
                    st.error("Extraction failed ❌")

    with col2:
        st.session_state.jd_text = st.text_area("Paste Job Description")

    # --------------------------
    # PROCESS
    # --------------------------
    if st.session_state.resume_text and st.session_state.jd_text:

        if st.button("Analyze & Optimize"):

            analyzer = JDAnalyzer()
            jd_data = analyzer.analyze(st.session_state.jd_text)

            match_data = analyzer.keyword_match(
                st.session_state.resume_text,
                jd_data["keywords"]
            )

            optimizer = ResumeOptimizer()
            result = optimizer.optimize_resume(
                st.session_state.resume_text,
                jd_data
            )

            generator = TextGenerator()

            st.session_state.optimized_resume = result["optimized_resume"]
            st.session_state.cover_letter = generator.generate_cover_letter(
                result["optimized_resume"], jd_data
            )
            st.session_state.outreach = generator.generate_outreach_mail(jd_data)
            st.session_state.jd_summary = generator.generate_jd_match_summary(match_data)
            st.session_state.match_data = match_data

            scorer = ATSScorer()

            ats_score = scorer.calculate_score(
                match_data,
                st.session_state.optimized_resume
            )

            st.session_state.ats_score = ats_score
            st.session_state.ats_grade = scorer.get_grade(ats_score)
            st.session_state.ats_suggestions = scorer.get_suggestions(match_data)

            gap = SkillGapAnalyzer().analyze(match_data)
            st.session_state.skill_gap = gap

    # --------------------------
    # RESULTS
    # --------------------------
    if st.session_state.optimized_resume:

        st.subheader("Results")

        tab1, tab2, tab3, tab4 = st.tabs([
            "📄 Resume",
            "✉️ Cover Letter",
            "📩 Outreach",
            "📊 JD Match"
        ])

        with tab1:

            template = st.selectbox(
                "Choose Template",
                ["Modern", "Professional", "Minimal", "Creative"]
            )

            edited_resume = st.text_area(
                "Edit Resume",
                st.session_state.optimized_resume,
                height=400
            )

            st.success(f"✨ Using {template} Template")

            builder = ResumeBuilder()

            if st.button("Generate Styled Resume"):

                data = convert_text_to_data(edited_resume, template)
                data = ensure_complete_schema(data)

                buffer = builder.generate_resume(data)

                st.download_button(
                    "Download Styled Resume",
                    data=buffer,
                    file_name="styled_resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        with tab2:
            st.text_area("Cover Letter", st.session_state.cover_letter, height=300)

        with tab3:
            st.text_area("Outreach", st.session_state.outreach, height=200)

        with tab4:

            ats_score = st.session_state.get("ats_score", 0)
            grade = st.session_state.get("ats_grade", "N/A")
            suggestions = st.session_state.get("ats_suggestions", [])
            percent = st.session_state.match_data.get("match_percent", 0)

            st.subheader("ATS Score")

            st.metric("ATS Score", f"{ats_score}/100")
            st.progress(ats_score / 100)

            if grade == "Excellent":
                st.success(f"Grade: {grade}")
            elif grade == "Good":
                st.warning(f"Grade: {grade}")
            else:
                st.error(f"Grade: {grade}")

            st.divider()

            st.subheader("JD Match")

            st.metric("JD Match %", f"{percent}%")
            st.progress(percent / 100)

            st.success("Matched Skills")
            st.write(", ".join(st.session_state.match_data.get("matched", [])))

            st.error("Missing Skills")
            st.write(", ".join(st.session_state.match_data.get("missing", [])))

            st.text_area("Summary", st.session_state.jd_summary)

            st.divider()

            st.subheader("Suggestions")

            for s in suggestions:
                st.write(f"• {s}")

            st.divider()

            st.subheader("Skill Gap Analysis")

            gap = st.session_state.get("skill_gap", {})

            missing_skills = gap.get("missing_skills", [])
            recommendations = gap.get("recommendations", [])
            priority = gap.get("priority", "Low")

            if priority == "High":
                st.error(f"Priority: {priority}")
            elif priority == "Medium":
                st.warning(f"Priority: {priority}")
            else:
                st.success(f"Priority: {priority}")

            st.write("### Missing Skills")
            st.write(", ".join(missing_skills) if missing_skills else "None")

            st.write("### Learning Recommendations")
            for r in recommendations:
                st.write(f"• {r}")