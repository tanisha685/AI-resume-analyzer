import streamlit as st
from utils.resume_parser import ResumeParser
from utils.resume_store import ResumeStore


def resume_selector():
    store = ResumeStore()
    saved_resumes = store.get_all_resumes()

    options = ["Upload New"] + [r["name"] for r in saved_resumes]

    selected = st.selectbox("Select Resume", options)

    # --------------------------
    # USE SAVED
    # --------------------------
    if selected != "Upload New":
        for r in saved_resumes:
            if r["name"] == selected:
                st.success(f"Loaded: {selected}")
                return r["text"]

    # --------------------------
    # UPLOAD NEW
    # --------------------------
    if selected == "Upload New":
        file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

        if file:
            parser = ResumeParser()
            text = parser.extract_text(file)

            if text:
                store.save_resume(file.name, text)
                st.success("Uploaded & Saved ✅")
                return text
            else:
                st.error("Extraction failed ❌")

    return None