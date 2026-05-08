# AI-Powered Resume Intelligence & Career Recommendation Platform

An intelligent career support platform that helps students and job seekers improve their resumes, analyze ATS compatibility, identify skill gaps, explore job opportunities, and generate professional portfolio websites.

Built using Python, Streamlit, NLP-based text processing, Selenium automation, and dynamic portfolio generation.

---

# Features

## Resume Analyzer
- Upload resumes in PDF or DOCX format
- Extract and parse resume content
- Detect skills, education, projects, and experience
- Generate ATS compatibility score
- Resume quality evaluation
- Contact information extraction

## AI Resume Analysis
- Strengths and weaknesses analysis
- Resume improvement suggestions
- Content optimization recommendations
- Structured section-wise feedback

## Skill Gap Analysis
- Identify current skills
- Detect missing skills
- Compare skills with industry requirements
- Role-based skill recommendations

## Career Recommendation System
- Suggests suitable career roles
- Role recommendations based on extracted skills
- Guidance for skill improvement

## Resume Enhancer
- Generates optimized resume content
- Improves wording and formatting
- Download enhanced resume

## Portfolio Website Generator
- Convert resume into a portfolio website
- Multiple portfolio templates
- Skills, projects, experience, and contact sections
- Responsive and modern UI
- Editable generated code

## Job Search System
- Multi-platform job search support
- LinkedIn job scraping using Selenium
- Dynamic job search link generation
- Redirect users to official job portals
- Real-time job listings

## Dashboard
- Interactive Streamlit-based UI
- Multi-tab navigation
- Real-time analysis and outputs

---

# Technologies Used

## Frontend
- Streamlit
- HTML
- CSS

## Backend
- Python

## Libraries & Tools
- Pandas
- NumPy
- Selenium
- webdriver-manager
- PyPDF2
- pdfplumber
- python-docx
- Regular Expressions (Regex)
- NLP-based text processing

---

# System Workflow

Resume Upload  
→ Resume Parsing  
→ Information Extraction  
→ ATS Score Calculation  
→ Skill Extraction  
→ Skill Gap Analysis  
→ AI Resume Analysis  
→ Career Recommendation  
→ Resume Optimization  
→ Portfolio Generation  
→ Final Output

---

# ATS Score Calculation

The ATS score is calculated using a weighted scoring system based on:

- Skills relevance
- Resume formatting
- Experience section
- Education section
- Contact details
- Summary section

Formula Used:

ATS Score =
(Contact Score × 0.1) +
(Summary Score × 0.1) +
(Skills Score × 0.3) +
(Experience Score × 0.2) +
(Education Score × 0.1) +
(Formatting Score × 0.2)

---

# LinkedIn Job Search Implementation

The project does not use LinkedIn’s official API because it is restricted.

Instead, Selenium-based browser automation is used to:
- Open LinkedIn job search pages
- Search jobs dynamically
- Scroll and load job listings
- Extract job titles, companies, locations, and descriptions
- Redirect users to LinkedIn for applying

---

# Installation & Setup

## 1. Clone Repository

```bash
git clone https://github.com/tanisha685/AI-resume-analyzer.git
```

---

## 2. Move into Project Folder

```bash
cd AI-resume-analyzer
```

---

## 3. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Install Requirements

```bash
pip install -r requirements.txt
```

---

## 5. Run Application

```bash
streamlit run app.py
```

---

# Deployment

This project can be deployed using:
- Streamlit Cloud
- Render
- Railway

---

# Future Scope

- Integration with real-time job APIs
- AI-based mock interview system
- Advanced NLP models
- Improved portfolio customization
- Cloud deployment and scalability
- Personalized learning recommendations

---

# Project Type

Development cum Research Project

---



# License

This project is developed for academic and educational purposes.
