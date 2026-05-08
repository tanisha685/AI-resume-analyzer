# ================== TEXT CLEANING PIPELINE ==================

def clean_text(text):
    """Advanced text cleaning pipeline"""
    # Fix common concatenations
    replacements = {
        "includinga": "including a ",
        "includingthe": "including the ",
        "andthe": "and the ",
        "forthe": "for the ",
        "withthe": "with the ",
        "ofthe": "of the ",
        "inthe": "in the ",
        "onthe": "on the ",
        "tothe": "to the ",
        "fromthe": "from the ",
        "bythe": "by the ",
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Fix spacing issues
    import re
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+\.', '.', text)
    text = re.sub(r'\s+,', ',', text)
    
    return text.strip()


# ================== LINK EXTRACTION ==================

def extract_link(text, platform):
    """Extract GitHub or LinkedIn URLs from text"""
    import re
    
    patterns = {
        "github": [
            r'github\.com/([a-zA-Z0-9\-_]+)',
            r'github\.com/([a-zA-Z0-9\-_]+)/?$',
            r'https?://github\.com/([a-zA-Z0-9\-_]+)'
        ],
        "linkedin": [
            r'linkedin\.com/in/([a-zA-Z0-9\-_]+)',
            r'linkedin\.com/in/([a-zA-Z0-9\-_]+)/?$',
            r'https?://linkedin\.com/in/([a-zA-Z0-9\-_]+)'
        ]
    }
    
    for pattern in patterns.get(platform, []):
        match = re.search(pattern, text.lower())
        if match:
            username = match.group(1)
            url = f"https://{platform}.com/{'in/' if platform == 'linkedin' else ''}{username}"
            return url
    
    # Return default/placeholder based on platform
    defaults = {
        "github": "https://github.com",
        "linkedin": "https://linkedin.com"
    }
    return defaults.get(platform, "#")


def ensure_https(url):
    """Ensure URL has https:// prefix"""
    if not url or url == "#":
        return url
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url


# ================== ENHANCED NAME EXTRACTION ==================

def extract_name(text):
    """Extract name from first line or common patterns"""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    if not lines:
        return "Your Name"
    
    # Clean up name
    name = lines[0]
    
    # Remove common prefixes/suffixes
    import re
    name = re.sub(r'^(name:|my name is|i am|profile of)', '', name, flags=re.I)
    name = re.sub(r'(\s+\||\s+-\s+.*$)', '', name)
    
    # Capitalize properly
    name = name.strip().title()
    
    return name if name else "Your Name"


# ================== ENHANCED SKILLS EXTRACTION ==================

def extract_skills(text):
    """Dynamically extract skills from skills section"""
    import re
    
    # Expanded skill keywords
    tech_keywords = {
        "Languages": ["python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "swift", "kotlin", "php", "ruby", "sql"],
        "Frontend": ["react", "vue", "angular", "next.js", "html5", "css3", "tailwind", "bootstrap", "sass", "webpack"],
        "Backend": ["node.js", "express", "django", "flask", "spring", "fastapi", "laravel", "asp.net", "graphql", "rest api"],
        "Database": ["postgresql", "mysql", "mongodb", "redis", "firebase", "dynamodb", "elasticsearch"],
        "Cloud & DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform", "github actions", "gitlab ci"],
        "Data & AI": ["tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "langchain", "openai", "huggingface"],
        "Tools": ["git", "github", "gitlab", "jira", "confluence", "figma", "postman", "vscode"]
    }
    
    all_skills = set()
    text_lower = text.lower()
    
    # First, try to find a dedicated skills section
    lines = text.split("\n")
    in_skills_section = False
    
    for line in lines:
        line_lower = line.lower()
        
        if "skills" in line_lower or "technologies" in line_lower or "tech stack" in line_lower:
            in_skills_section = True
            continue
        
        if in_skills_section:
            if any(section in line_lower for section in ["experience", "projects", "education", "work"]):
                break
            
            # Extract skills from bullet points or comma-separated lists
            if "•" in line or "-" in line or "*" in line:
                parts = line.replace("•", "").replace("-", "").replace("*", "").split(",")
                for part in parts:
                    skill = part.strip()
                    if len(skill) > 1 and len(skill) < 30:
                        all_skills.add(skill.title())
            else:
                # Look for common skill patterns
                for category, skills in tech_keywords.items():
                    for skill in skills:
                        if skill in line_lower:
                            all_skills.add(skill.title())
    
    # If no skills found in section, search entire document
    if not all_skills:
        for category, skills in tech_keywords.items():
            for skill in skills:
                if skill in text_lower:
                    all_skills.add(skill.title())
    
    # Remove duplicates and sort
    skills_list = sorted(list(all_skills))
    
    # Provide fallback
    if not skills_list:
        skills_list = ["Python", "JavaScript", "React", "Node.js", "Git"]
    
    return skills_list[:15]  # Limit to 15 skills


# ================== ENHANCED PROJECT EXTRACTION ==================

def extract_projects(text):
    """Extract structured project data with titles, descriptions, and tech stacks"""
    import re
    
    text = clean_text(text)
    lines = text.split("\n")
    
    projects = []
    in_projects_section = False
    current_project = {}
    project_patterns = [
        r'^•\s*(.+?)(?:[:：\-–—]\s*(.+))?$',  # Bullet points
        r'^\*\s*(.+?)(?:[:：\-–—]\s*(.+))?$',  # Asterisk bullets
        r'^-\s*(.+?)(?:[:：\-–—]\s*(.+))?$',   # Dash bullets
        r'^(\d+\.)\s*(.+?)(?:[:：\-–—]\s*(.+))?$',  # Numbered
        r'^([A-Z][A-Za-z0-9\s]+?)(?:[:：\-–—]\s*(.+))?$'  # Capitalized titles
    ]
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        line_lower = line.lower()
        
        # Detect projects section
        if "project" in line_lower and any(word in line_lower for word in ["work", "portfolio", "showcase", ":" , "—", "-"]):
            in_projects_section = True
            continue
        
        # Stop when next major section starts
        if in_projects_section and any(word in line_lower for word in ["experience", "skills", "education", "work history", "certification"]):
            break
        
        if in_projects_section:
            # Check if line looks like a project title
            is_project_title = False
            project_title = None
            project_desc = None
            
            for pattern in project_patterns:
                match = re.match(pattern, line)
                if match:
                    groups = match.groups()
                    if len(groups) >= 2 and groups[1]:
                        project_title = groups[0].strip()
                        project_desc = groups[1].strip()
                    else:
                        project_title = groups[0].strip() if groups[0] else groups[-1].strip()
                    is_project_title = True
                    break
            
            if is_project_title and project_title and len(project_title) > 2 and len(project_title) < 100:
                # Save previous project
                if current_project:
                    projects.append(current_project)
                
                # Start new project
                current_project = {
                    "title": project_title[:60],
                    "description": project_desc if project_desc else "",
                    "tech": []
                }
            elif current_project and len(line) > 10:
                # This could be project description or tech
                if any(tech_word in line_lower for tech_word in ["react", "python", "javascript", "node", "aws", "docker", "api", "database"]):
                    # Looks like tech stack
                    techs = re.findall(r'\b([A-Z][a-z]+(?:\+[A-Z][a-z]+)?|React|Node\.js|AWS|API|SQL)\b', line)
                    if techs:
                        current_project["tech"].extend(techs)
                else:
                    # Add to description
                    if current_project["description"]:
                        current_project["description"] += " " + line[:120]
                    else:
                        current_project["description"] = line[:120]
    
    # Add last project
    if current_project:
        projects.append(current_project)
    
    # If no structured projects found, create from raw text
    if not projects:
        raw_projects = []
        capture = False
        
        for line in lines:
            line = line.strip()
            if "project" in line.lower():
                capture = True
                continue
            if capture and any(x in line.lower() for x in ["education", "experience", "skills"]):
                break
            if capture and len(line) > 4 and len(line.split()) < 12:
                raw_projects.append(line)
        
        for raw in raw_projects[:5]:
            projects.append({
                "title": raw[:50],
                "description": "A project showcasing my skills and expertise.",
                "tech": []
            })
    
    # Clean up project data
    for project in projects:
        project["title"] = project["title"].replace("including", "").replace("and", "").strip()
        project["tech"] = list(set(project["tech"]))[:4]  # Max 4 techs per project
    
    # Provide fallback
    if not projects:
        projects = [{
            "title": "Featured Project",
            "description": "Exciting project demonstrating technical expertise and problem-solving abilities.",
            "tech": ["Python", "React"]
        }]
    
    return projects[:6]  # Max 6 projects


# ================== ENHANCED EXPERIENCE EXTRACTION ==================

def extract_experience(text):
    """Extract structured experience data with roles and descriptions"""
    import re
    
    text = clean_text(text)
    lines = text.split("\n")
    
    experiences = []
    in_exp_section = False
    current_exp = {}
    
    # Common job title patterns
    title_patterns = [
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:at|@|-|–|—|:)\s+(.+)$',
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[-–—]\s+(.+?)(?:\s+\((\d{4}[-–]\d{4}|\d{4}[-–]present|present)\))?',
        r'^(Senior|Lead|Principal|Junior|Intern|Software|Data|Product|Project|Engineering)\s+.+'
    ]
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        line_lower = line.lower()
        
        # Detect experience section
        if any(word in line_lower for word in ["experience", "work experience", "employment", "work history"]):
            in_exp_section = True
            continue
        
        # Stop when next major section starts
        if in_exp_section and any(word in line_lower for word in ["skills", "projects", "education", "certification"]):
            break
        
        if in_exp_section and len(line) > 5:
            # Check if this looks like a job title
            is_job = False
            job_title = ""
            company = ""
            
            for pattern in title_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    if len(groups) >= 2:
                        job_title = groups[0].strip()
                        company = groups[1].strip()
                    else:
                        job_title = groups[0].strip()
                    is_job = True
                    break
            
            if is_job or (any(word in line_lower for word in ["engineer", "developer", "designer", "manager", "analyst"]) and len(line.split()) < 12):
                # Save previous experience
                if current_exp:
                    experiences.append(current_exp)
                
                # Start new experience
                current_exp = {
                    "title": job_title if job_title else line[:60],
                    "company": company if company else "",
                    "duration": "",
                    "description": []
                }
            elif current_exp:
                # Add to description if it's a bullet point or meaningful line
                if line.startswith(("•", "-", "*", "→", "➜")) or (len(line) > 15 and not any(word in line_lower for word in ["email", "phone", "address"])):
                    clean_line = line.lstrip("•-*→➜ ").strip()
                    if len(clean_line) > 10:
                        current_exp["description"].append(clean_line[:150])
    
    # Add last experience
    if current_exp:
        experiences.append(current_exp)
    
    # If no structured experiences found, create from raw
    if not experiences:
        raw_exp = []
        for line in lines:
            if any(word in line.lower() for word in ["experience", "intern", "work", "job"]):
                if len(line) > 10 and len(line.split()) < 20:
                    raw_exp.append(line)
        
        for raw in raw_exp[:4]:
            experiences.append({
                "title": raw[:50],
                "company": "",
                "duration": "",
                "description": ["Relevant professional experience"]
            })
    
    # Provide fallback
    if not experiences:
        experiences = [{
            "title": "Professional Experience",
            "company": "Previous Company",
            "duration": "",
            "description": ["Demonstrated expertise in software development and team collaboration"]
        }]
    
    return experiences[:4]  # Max 4 experiences


# ================== ENHANCED EDUCATION EXTRACTION ==================

def extract_education(text):
    """Extract structured education data"""
    import re
    
    text = clean_text(text)
    lines = text.split("\n")
    
    education_list = []
    in_edu_section = False
    
    # Education patterns
    edu_patterns = [
        r'(Bachelor|B\.?S\.?|Master|M\.?S\.?|PhD|Associate|Certificate)\s+(?:of\s+)?(.+?)(?:\s+[-–—]\s+(.+))?',
        r'(.+?)\s+(?:University|College|Institute|School)(?:\s+[-–—]\s+(.+))?',
        r'(University|College|Institute|School)\s+of\s+(.+?)(?:\s+[-–—]\s+(.+))?'
    ]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        line_lower = line.lower()
        
        # Detect education section
        if "education" in line_lower:
            in_edu_section = True
            continue
        
        # Stop when other sections start
        if in_edu_section and any(word in line_lower for word in ["experience", "skills", "projects", "certification"]):
            break
        
        if in_edu_section and len(line) > 5 and len(line.split()) < 20:
            education_found = False
            
            for pattern in edu_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    degree = groups[0] if groups[0] else ""
                    institution = groups[1] if len(groups) > 1 and groups[1] else groups[0]
                    
                    edu_entry = {
                        "degree": degree[:40],
                        "institution": institution[:50],
                        "year": groups[2] if len(groups) > 2 and groups[2] else ""
                    }
                    education_list.append(edu_entry)
                    education_found = True
                    break
            
            if not education_found and len(line) > 10:
                education_list.append({
                    "degree": line[:40],
                    "institution": "",
                    "year": ""
                })
    
    # Provide fallback
    if not education_list:
        education_list = [{
            "degree": "Computer Science",
            "institution": "University",
            "year": ""
        }]
    
    return education_list[:3]  # Max 3 education entries


# ================== ABOUT EXTRACTION ==================

def extract_about(text):
    """Extract about/summary section"""
    import re
    
    lines = text.split("\n")
    about_text = []
    in_about = False
    
    for line in lines[:50]:  # Check first 50 lines
        line = line.strip()
        if not line:
            continue
        
        line_lower = line.lower()
        
        if any(word in line_lower for word in ["about", "summary", "profile", "bio"]):
            in_about = True
            continue
        
        if in_about:
            if any(word in line_lower for word in ["skills", "experience", "projects", "education"]):
                break
            if len(line) > 20:
                about_text.append(line)
    
    about = " ".join(about_text)[:250]
    
    if not about:
        about = "Passionate developer creating innovative solutions with modern technologies."
    
    return about


# ================== MAIN FUNCTION ==================

def generate_portfolio(text, template, profile_image="", github="", linkedin=""):
    """Main function to generate portfolio with all extracted data"""
    
    # Clean input text
    text = clean_text(text)
    
    # Extract all data
    name = extract_name(text)
    skills = extract_skills(text)
    projects = extract_projects(text)
    experience = extract_experience(text)
    education = extract_education(text)
    about = extract_about(text)
    
    # Extract links if not provided
    if not github:
        github = extract_link(text, "github")
    if not linkedin:
        linkedin = extract_link(text, "linkedin")
    
    # Ensure HTTPS
    github = ensure_https(github)
    linkedin = ensure_https(linkedin)
    
    # Set default profile image
    if not profile_image:
        profile_image = "https://ui-avatars.com/api/?background=6366f1&color=fff&size=300&bold=true&name=" + name.replace(" ", "+")
    
    # Route to appropriate template
    templates = {
        "Modern": modern_template,
        "Minimal": minimal_template,
        "Creative": creative_template,
        "Developer": developer_template,
        "Professional": professional_template
    }
    
    template_func = templates.get(template, professional_template)
    
    return template_func(name, skills, projects, experience, education,
                        profile_image, github, linkedin, about)


# ================== BACKWARD COMPATIBILITY WRAPPER ==================

def build_template(name, skills, projects, experience, education, template,
                   profile_image="", github="", linkedin="", about=""):
    """
    Legacy wrapper function that maintains compatibility with existing code.
    This converts the old-style parameters to the new generate_portfolio format.
    """
    
    # Convert old-style data to the format expected by generate_portfolio
    
    # If projects are strings, convert them to the new structured format
    structured_projects = []
    for p in projects:
        if isinstance(p, dict):
            structured_projects.append(p)
        elif isinstance(p, str):
            # Convert old string format to new structured format
            structured_projects.append({
                "title": p[:50] if len(p) > 50 else p,
                "description": p,
                "tech": []
            })
        else:
            structured_projects.append({
                "title": "Project",
                "description": str(p),
                "tech": []
            })
    
    # If experience entries are strings, convert them
    structured_experience = []
    for e in experience:
        if isinstance(e, dict):
            structured_experience.append(e)
        elif isinstance(e, str):
            structured_experience.append({
                "title": e[:50],
                "company": "",
                "duration": "",
                "description": [e]
            })
        else:
            structured_experience.append({
                "title": str(e),
                "company": "",
                "duration": "",
                "description": [str(e)]
            })
    
    # If education entries are strings, convert them
    structured_education = []
    for e in education:
        if isinstance(e, dict):
            structured_education.append(e)
        elif isinstance(e, str):
            structured_education.append({
                "degree": e[:40],
                "institution": "",
                "year": ""
            })
        else:
            structured_education.append({
                "degree": str(e),
                "institution": "",
                "year": ""
            })
    
    # Create a mock text from the extracted data (for generate_portfolio)
    # Include the about text in the mock text so generate_portfolio can extract it
    mock_text = f"""{name}
{about}

SKILLS:
{', '.join(skills) if skills else 'Python, JavaScript, React'}

PROJECTS:
{chr(10).join([p.get('title', p) if isinstance(p, dict) else p for p in structured_projects])}

EXPERIENCE:
{chr(10).join([e.get('title', e) if isinstance(e, dict) else e for e in structured_experience])}

EDUCATION:
{chr(10).join([e.get('degree', e) if isinstance(e, dict) else e for e in structured_education])}

GitHub: {github}
LinkedIn: {linkedin}
"""
    
    # Use generate_portfolio to create the HTML
    # IMPORTANT: Do NOT pass 'about' parameter - it's extracted from mock_text
    return generate_portfolio(
        text=mock_text,
        template=template,
        profile_image=profile_image,
        github=github,
        linkedin=linkedin
    )


# ================== MODERN TEMPLATE ==================

def modern_template(name, skills, projects, experience, education, profile_image, github, linkedin, about):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} | Modern Portfolio</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #1a1a2e;
            overflow-x: hidden;
        }}
        
        /* Animated background */
        .bg-animation {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            overflow: hidden;
        }}
        
        .bg-animation::before {{
            content: '';
            position: absolute;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
            background-size: 50px 50px;
            animation: bgMove 20s linear infinite;
        }}
        
        @keyframes bgMove {{
            0% {{ transform: translate(0, 0); }}
            100% {{ transform: translate(50px, 50px); }}
        }}
        
        /* Navigation */
        .navbar {{
            position: fixed;
            top: 0;
            width: 100%;
            padding: 1rem 5%;
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            z-index: 1000;
            animation: slideDown 0.5s ease;
        }}
        
        @keyframes slideDown {{
            from {{ transform: translateY(-100%); }}
            to {{ transform: translateY(0); }}
        }}
        
        .nav-container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .logo {{
            font-size: 1.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .nav-links a {{
            color: #1a1a2e;
            text-decoration: none;
            margin-left: 2rem;
            font-weight: 500;
            transition: all 0.3s;
            position: relative;
        }}
        
        .nav-links a::after {{
            content: '';
            position: absolute;
            bottom: -5px;
            left: 0;
            width: 0;
            height: 2px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            transition: width 0.3s;
        }}
        
        .nav-links a:hover::after {{
            width: 100%;
        }}
        
        /* Sections */
        section {{
            padding: 100px 5%;
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .section-title {{
            font-size: 2.5rem;
            margin-bottom: 3rem;
            text-align: center;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: fadeInUp 0.8s ease;
        }}
        
        /* Hero */
        .hero {{
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 3rem;
            flex-wrap: wrap;
        }}
        
        .hero-content {{
            flex: 1;
            animation: fadeInLeft 0.8s ease;
        }}
        
        @keyframes fadeInLeft {{
            from {{ opacity: 0; transform: translateX(-50px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        
        .hero-content h1 {{
            font-size: 3.5rem;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .hero-content p {{
            font-size: 1.2rem;
            color: #4a5568;
            margin-bottom: 2rem;
            line-height: 1.6;
        }}
        
        .hero-image {{
            flex: 1;
            text-align: center;
            animation: fadeInRight 0.8s ease;
        }}
        
        @keyframes fadeInRight {{
            from {{ opacity: 0; transform: translateX(50px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        
        .hero-image img {{
            width: 300px;
            height: 300px;
            border-radius: 50%;
            object-fit: cover;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            animation: float 3s ease-in-out infinite;
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-20px); }}
        }}
        
        .btn {{
            display: inline-block;
            padding: 12px 30px;
            margin: 0 10px 10px 0;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 4px 15px rgba(102,126,234,0.4);
        }}
        
        .btn-primary:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(102,126,234,0.6);
        }}
        
        .btn-outline {{
            background: transparent;
            color: #667eea;
            border: 2px solid #667eea;
        }}
        
        .btn-outline:hover {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            transform: translateY(-3px);
        }}
        
        /* Skills Grid */
        .skills-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }}
        
        .skill-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: all 0.3s;
            animation: fadeInUp 0.6s ease;
            animation-fill-mode: both;
        }}
        
        .skill-card:hover {{
            transform: translateY(-10px) scale(1.05);
            box-shadow: 0 8px 30px rgba(102,126,234,0.3);
        }}
        
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .skill-card i {{
            font-size: 2.5rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }}
        
        .skill-card h3 {{
            font-size: 1rem;
            color: #4a5568;
        }}
        
        /* Projects Grid */
        .projects-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }}
        
        .project-card {{
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: all 0.3s;
            animation: fadeInUp 0.6s ease;
            animation-fill-mode: both;
        }}
        
        .project-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 15px 40px rgba(102,126,234,0.3);
        }}
        
        .project-content {{
            padding: 1.5rem;
        }}
        
        .project-card h3 {{
            font-size: 1.3rem;
            margin-bottom: 0.5rem;
            color: #2d3748;
        }}
        
        .project-card p {{
            color: #718096;
            margin-bottom: 1rem;
            line-height: 1.5;
        }}
        
        .tech-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }}
        
        .tech-tag {{
            background: linear-gradient(135deg, #667eea20, #764ba220);
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
            color: #667eea;
        }}
        
        /* Experience Timeline */
        .timeline {{
            position: relative;
            padding-left: 2rem;
        }}
        
        .timeline::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 2px;
            background: linear-gradient(135deg, #667eea, #764ba2);
        }}
        
        .timeline-item {{
            position: relative;
            margin-bottom: 2rem;
            padding: 1rem;
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            animation: fadeInUp 0.6s ease;
        }}
        
        .timeline-item::before {{
            content: '';
            position: absolute;
            left: -2rem;
            top: 1.5rem;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea, #764ba2);
        }}
        
        .timeline-item h3 {{
            color: #2d3748;
            margin-bottom: 0.5rem;
        }}
        
        .timeline-item .company {{
            color: #667eea;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        
        .timeline-item ul {{
            list-style: none;
            padding-left: 1rem;
        }}
        
        .timeline-item li {{
            color: #718096;
            margin-bottom: 0.5rem;
            position: relative;
        }}
        
        .timeline-item li::before {{
            content: '▹';
            position: absolute;
            left: -1rem;
            color: #667eea;
        }}
        
        /* Education */
        .education-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }}
        
        .education-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: all 0.3s;
            animation: fadeInUp 0.6s ease;
        }}
        
        .education-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(102,126,234,0.3);
        }}
        
        .education-card i {{
            font-size: 2rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }}
        
        /* Contact Section */
        .contact-section {{
            text-align: center;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 20px;
            margin: 100px auto;
            padding: 3rem;
        }}
        
        .contact-section h2 {{
            color: white;
            -webkit-text-fill-color: white;
        }}
        
        .social-links {{
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            margin-top: 2rem;
        }}
        
        .social-links a {{
            color: white;
            font-size: 1.5rem;
            transition: all 0.3s;
        }}
        
        .social-links a:hover {{
            transform: translateY(-5px);
            color: #1a1a2e;
        }}
        
        /* Footer */
        footer {{
            text-align: center;
            padding: 2rem;
            background: #1a1a2e;
            color: white;
        }}
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .fade-in {{
            animation: fadeIn 1s ease;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .hero {{
                flex-direction: column-reverse;
                text-align: center;
            }}
            
            .nav-links {{
                display: none;
            }}
            
            .section-title {{
                font-size: 2rem;
            }}
            
            .projects-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="bg-animation"></div>
    
    <nav class="navbar">
        <div class="nav-container">
            <div class="logo">{name.split()[0]}</div>
            <div class="nav-links">
                <a href="#home">Home</a>
                <a href="#skills">Skills</a>
                <a href="#projects">Projects</a>
                <a href="#experience">Experience</a>
                <a href="#contact">Contact</a>
            </div>
        </div>
    </nav>
    
    <section id="home" class="hero">
        <div class="hero-content">
            <h1>Hi, I'm {name.split()[0]}</h1>
            <p>{about}</p>
            <a href="{github}" class="btn btn-primary" target="_blank"><i class="fab fa-github"></i> GitHub</a>
            <a href="{linkedin}" class="btn btn-outline" target="_blank"><i class="fab fa-linkedin"></i> LinkedIn</a>
        </div>
        <div class="hero-image">
            <img src="{profile_image}" alt="{name}">
        </div>
    </section>
    
    <section id="skills">
        <h2 class="section-title">Technical Skills</h2>
        <div class="skills-grid">
            {''.join([f'''
            <div class="skill-card" style="animation-delay: {i * 0.05}s">
                <i class="fas fa-code"></i>
                <h3>{skill}</h3>
            </div>
            ''' for i, skill in enumerate(skills[:12])])}
        </div>
    </section>
    
    <section id="projects">
        <h2 class="section-title">Featured Projects</h2>
        <div class="projects-grid">
            {''.join([f'''
            <div class="project-card" style="animation-delay: {i * 0.1}s">
                <div class="project-content">
                    <h3>{p['title']}</h3>
                    <p>{p['description'][:120]}{'...' if len(p['description']) > 120 else ''}</p>
                    <div class="tech-tags">
                        {''.join([f'<span class="tech-tag">{tech}</span>' for tech in p['tech'][:3]])}
                    </div>
                </div>
            </div>
            ''' for i, p in enumerate(projects)])}
        </div>
    </section>
    
    <section id="experience">
        <h2 class="section-title">Work Experience</h2>
        <div class="timeline">
            {''.join([f'''
            <div class="timeline-item">
                <h3>{exp['title']}</h3>
                <div class="company">{exp['company']}</div>
                <ul>
                    {''.join([f'<li>{desc[:100]}</li>' for desc in exp['description'][:3]])}
                </ul>
            </div>
            ''' for exp in experience])}
        </div>
    </section>
    
    <section id="education">
        <h2 class="section-title">Education</h2>
        <div class="education-grid">
            {''.join([f'''
            <div class="education-card">
                <i class="fas fa-graduation-cap"></i>
                <h3>{edu['degree']}</h3>
                <p>{edu['institution']}</p>
                <small>{edu['year']}</small>
            </div>
            ''' for edu in education])}
        </div>
    </section>
    
    <section id="contact" class="contact-section">
        <h2 class="section-title">Let's Connect</h2>
        <p>I'm always open to discussing new projects and opportunities</p>
        <div class="social-links">
            <a href="{github}" target="_blank"><i class="fab fa-github"></i></a>
            <a href="{linkedin}" target="_blank"><i class="fab fa-linkedin"></i></a>
            <a href="mailto:hello@example.com"><i class="fas fa-envelope"></i></a>
        </div>
    </section>
    
    <footer>
        <p>© 2024 {name}. All rights reserved. | Crafted with <i class="fas fa-heart"></i></p>
    </footer>
    
    <script>
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({{
                    behavior: 'smooth'
                }});
            }});
        }});
        
        // Scroll animations
        const observerOptions = {{
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        }};
        
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }}
            }});
        }}, observerOptions);
        
        document.querySelectorAll('.skill-card, .project-card, .timeline-item, .education-card').forEach(el => {{
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'all 0.6s ease';
            observer.observe(el);
        }});
    </script>
</body>
</html>
    """


# ================== MINIMAL TEMPLATE ==================

def minimal_template(name, skills, projects, experience, education, profile_image, github, linkedin, about):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} | Clean Portfolio</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: #fafafa;
            color: #1a1a1a;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }}
        
        /* Header Animation */
        .header {{
            text-align: center;
            margin-bottom: 3rem;
            animation: slideDown 0.6s ease;
        }}
        
        @keyframes slideDown {{
            from {{ opacity: 0; transform: translateY(-30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .avatar {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            object-fit: cover;
            margin-bottom: 1rem;
            border: 3px solid #e0e0e0;
            transition: transform 0.3s;
        }}
        
        .avatar:hover {{
            transform: scale(1.05);
        }}
        
        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .bio {{
            color: #666;
            max-width: 600px;
            margin: 1rem auto;
        }}
        
        .links {{
            margin-top: 1rem;
        }}
        
        .links a {{
            color: #667eea;
            text-decoration: none;
            margin: 0 0.5rem;
            transition: color 0.3s;
        }}
        
        .links a:hover {{
            color: #764ba2;
        }}
        
        /* Section Styles */
        .section {{
            margin-bottom: 3rem;
            animation: fadeInUp 0.6s ease;
            animation-fill-mode: both;
        }}
        
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .section-title {{
            font-size: 1.8rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e0e0e0;
            position: relative;
        }}
        
        .section-title::after {{
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 50px;
            height: 2px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            animation: widthGrow 0.6s ease;
        }}
        
        @keyframes widthGrow {{
            from {{ width: 0; }}
            to {{ width: 50px; }}
        }}
        
        /* Skills */
        .skills-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem;
        }}
        
        .skill-tag {{
            background: white;
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-size: 0.9rem;
            color: #667eea;
            border: 1px solid #e0e0e0;
            transition: all 0.3s;
            cursor: pointer;
        }}
        
        .skill-tag:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102,126,234,0.2);
            border-color: #667eea;
        }}
        
        /* Projects */
        .project-item {{
            background: white;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: all 0.3s;
        }}
        
        .project-item:hover {{
            transform: translateX(10px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        .project-title {{
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #333;
        }}
        
        .project-desc {{
            color: #666;
            margin-bottom: 0.8rem;
        }}
        
        .project-tech {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        
        .project-tech span {{
            font-size: 0.8rem;
            color: #667eea;
            background: #f0f0f0;
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
        }}
        
        /* Experience */
        .exp-item {{
            margin-bottom: 1.5rem;
            padding: 1rem;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: all 0.3s;
        }}
        
        .exp-item:hover {{
            transform: translateX(5px);
        }}
        
        .exp-title {{
            font-weight: 600;
            color: #333;
            margin-bottom: 0.3rem;
        }}
        
        .exp-company {{
            color: #667eea;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }}
        
        .exp-desc {{
            color: #666;
            font-size: 0.9rem;
            padding-left: 1rem;
            border-left: 2px solid #667eea;
        }}
        
        /* Education */
        .edu-item {{
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: all 0.3s;
        }}
        
        .edu-item:hover {{
            transform: scale(1.02);
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding-top: 2rem;
            margin-top: 2rem;
            border-top: 1px solid #e0e0e0;
            color: #999;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 2rem 1rem;
            }}
            
            h1 {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="{profile_image}" alt="{name}" class="avatar">
            <h1>{name}</h1>
            <div class="bio">{about}</div>
            <div class="links">
                <a href="{github}" target="_blank"><i class="fab fa-github"></i> GitHub</a>
                <a href="{linkedin}" target="_blank"><i class="fab fa-linkedin"></i> LinkedIn</a>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">Skills</h2>
            <div class="skills-list">
                {''.join([f'<span class="skill-tag">{skill}</span>' for skill in skills])}
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">Projects</h2>
            {''.join([f'''
            <div class="project-item">
                <div class="project-title">{p['title']}</div>
                <div class="project-desc">{p['description'][:150]}</div>
                <div class="project-tech">
                    {''.join([f'<span>{tech}</span>' for tech in p['tech'][:3]])}
                </div>
            </div>
            ''' for p in projects])}
        </div>
        
        <div class="section">
            <h2 class="section-title">Experience</h2>
            {''.join([f'''
            <div class="exp-item">
                <div class="exp-title">{exp['title']}</div>
                <div class="exp-company">{exp['company']}</div>
                <div class="exp-desc">{exp['description'][0][:100] if exp['description'] else ''}</div>
            </div>
            ''' for exp in experience])}
        </div>
        
        <div class="section">
            <h2 class="section-title">Education</h2>
            {''.join([f'''
            <div class="edu-item">
                <div><strong>{edu['degree']}</strong></div>
                <div>{edu['institution']}</div>
                <small>{edu['year']}</small>
            </div>
            ''' for edu in education])}
        </div>
        
        <div class="footer">
            <p>© 2024 {name}</p>
        </div>
    </div>
</body>
</html>
    """


# ================== CREATIVE TEMPLATE ==================

def creative_template(name, skills, projects, experience, education, profile_image, github, linkedin, about):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} | Creative Portfolio</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Space Grotesk', sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            overflow-x: hidden;
        }}
        
        /* Glitch effect */
        .glitch {{
            position: relative;
            animation: glitch 3s infinite;
        }}
        
        @keyframes glitch {{
            0%, 100% {{ transform: skew(0deg, 0deg); }}
            95% {{ transform: skew(0deg, 0deg); }}
            96% {{ transform: skew(5deg, 2deg); }}
            97% {{ transform: skew(-5deg, -2deg); }}
            98% {{ transform: skew(3deg, 1deg); }}
            99% {{ transform: skew(-3deg, -1deg); }}
        }}
        
        /* Cursor */
        .cursor {{
            width: 20px;
            height: 20px;
            border: 2px solid #ff3366;
            border-radius: 50%;
            position: fixed;
            pointer-events: none;
            z-index: 9999;
            transition: 0.1s;
            transform: translate(-50%, -50%);
        }}
        
        /* Navigation */
        .navbar {{
            position: fixed;
            top: 0;
            width: 100%;
            padding: 1.5rem 5%;
            background: rgba(10,10,10,0.95);
            backdrop-filter: blur(10px);
            z-index: 1000;
            border-bottom: 1px solid rgba(255,51,102,0.3);
        }}
        
        .nav-container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .logo {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #ff3366;
        }}
        
        .nav-links a {{
            color: white;
            text-decoration: none;
            margin-left: 2rem;
            transition: color 0.3s;
            position: relative;
        }}
        
        .nav-links a:hover {{
            color: #ff3366;
        }}
        
        /* Hero */
        .hero {{
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .hero-content {{
            z-index: 2;
        }}
        
        .hero h1 {{
            font-size: 5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #ff3366, #ff6b3d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: fadeInUp 0.8s ease;
        }}
        
        .hero p {{
            font-size: 1.2rem;
            color: #ccc;
            max-width: 600px;
            margin: 0 auto 2rem;
            animation: fadeInUp 0.8s ease 0.2s backwards;
        }}
        
        .btn {{
            display: inline-block;
            padding: 12px 30px;
            margin: 0 10px;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
            animation: fadeInUp 0.8s ease 0.4s backwards;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #ff3366, #ff6b3d);
            color: white;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-3px);
            box-shadow: 0 5px 20px rgba(255,51,102,0.4);
        }}
        
        .btn-outline {{
            border: 2px solid #ff3366;
            color: #ff3366;
        }}
        
        .btn-outline:hover {{
            background: #ff3366;
            color: white;
        }}
        
        /* Sections */
        section {{
            padding: 100px 5%;
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .section-title {{
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 3rem;
            position: relative;
        }}
        
        .section-title::before {{
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 50px;
            height: 3px;
            background: linear-gradient(135deg, #ff3366, #ff6b3d);
        }}
        
        /* Skills */
        .skills-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 1rem;
        }}
        
        .skill-item {{
            text-align: center;
            padding: 1rem;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            transition: all 0.3s;
            cursor: pointer;
        }}
        
        .skill-item:hover {{
            background: rgba(255,51,102,0.2);
            transform: scale(1.05);
        }}
        
        /* Projects 3D Cards */
        .projects-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
            perspective: 1000px;
        }}
        
        .project-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 1.5rem;
            transition: all 0.5s;
            transform-style: preserve-3d;
        }}
        
        .project-card:hover {{
            transform: rotateY(10deg) translateY(-10px);
            background: rgba(255,51,102,0.1);
            box-shadow: 0 10px 30px rgba(255,51,102,0.2);
        }}
        
        .project-card h3 {{
            font-size: 1.3rem;
            margin-bottom: 0.5rem;
            color: #ff3366;
        }}
        
        .tech-stack {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }}
        
        .tech-stack span {{
            font-size: 0.8rem;
            padding: 0.2rem 0.6rem;
            background: rgba(255,51,102,0.2);
            border-radius: 4px;
        }}
        
        /* Timeline */
        .timeline {{
            position: relative;
        }}
        
        .timeline-item {{
            margin-bottom: 2rem;
            padding: 1rem;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            border-left: 3px solid #ff3366;
            transition: all 0.3s;
        }}
        
        .timeline-item:hover {{
            transform: translateX(10px);
            background: rgba(255,51,102,0.1);
        }}
        
        footer {{
            text-align: center;
            padding: 2rem;
            background: rgba(255,51,102,0.1);
        }}
        
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @media (max-width: 768px) {{
            .hero h1 {{
                font-size: 2.5rem;
            }}
            
            .projects-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="cursor"></div>
    
    <nav class="navbar">
        <div class="nav-container">
            <div class="logo glitch">{name.split()[0]}</div>
            <div class="nav-links">
                <a href="#home">Home</a>
                <a href="#skills">Skills</a>
                <a href="#projects">Work</a>
                <a href="#contact">Contact</a>
            </div>
        </div>
    </nav>
    
    <section id="home" class="hero">
        <div class="hero-content">
            <h1 class="glitch">{name}</h1>
            <p>{about}</p>
            <a href="{github}" class="btn btn-primary" target="_blank"><i class="fab fa-github"></i> GitHub</a>
            <a href="{linkedin}" class="btn btn-outline" target="_blank"><i class="fab fa-linkedin"></i> LinkedIn</a>
        </div>
    </section>
    
    <section id="skills">
        <h2 class="section-title">Skills & Technologies</h2>
        <div class="skills-grid">
            {''.join([f'<div class="skill-item">{skill}</div>' for skill in skills])}
        </div>
    </section>
    
    <section id="projects">
        <h2 class="section-title">Featured Work</h2>
        <div class="projects-grid">
            {''.join([f'''
            <div class="project-card">
                <h3>{p['title']}</h3>
                <p>{p['description'][:120]}</p>
                <div class="tech-stack">
                    {''.join([f'<span>{tech}</span>' for tech in p['tech'][:3]])}
                </div>
            </div>
            ''' for p in projects])}
        </div>
    </section>
    
    <section id="experience">
        <h2 class="section-title">Experience</h2>
        <div class="timeline">
            {''.join([f'''
            <div class="timeline-item">
                <h3>{exp['title']}</h3>
                <p style="color:#ff3366">{exp['company']}</p>
                <p>{exp['description'][0][:100] if exp['description'] else ''}</p>
            </div>
            ''' for exp in experience])}
        </div>
    </section>
    
    <footer id="contact">
        <p>© 2024 {name} | <a href="{github}" style="color:#ff3366">GitHub</a> | <a href="{linkedin}" style="color:#ff3366">LinkedIn</a></p>
    </footer>
    
    <script>
        // Custom cursor
        const cursor = document.querySelector('.cursor');
        document.addEventListener('mousemove', (e) => {{
            cursor.style.left = e.clientX + 'px';
            cursor.style.top = e.clientY + 'px';
        }});
        
        // Glitch effect on hover
        document.querySelectorAll('.project-card').forEach(card => {{
            card.addEventListener('mouseenter', () => {{
                card.style.transform = 'rotateY(10deg) translateY(-10px)';
            }});
            card.addEventListener('mouseleave', () => {{
                card.style.transform = 'rotateY(0deg) translateY(0)';
            }});
        }});
    </script>
</body>
</html>
    """


# ================== DEVELOPER TEMPLATE ==================

def developer_template(name, skills, projects, experience, education, profile_image, github, linkedin, about):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} | Dev Portfolio</title>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Fira Code', monospace;
            background: #0d1117;
            color: #c9d1d9;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        /* Terminal animation */
        .terminal {{
            background: #161b22;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 2rem;
            border: 1px solid #30363d;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ border-color: #30363d; }}
            50% {{ border-color: #58a6ff; }}
        }}
        
        .terminal-header {{
            display: flex;
            gap: 8px;
            margin-bottom: 1rem;
        }}
        
        .terminal-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        
        .terminal-dot.red {{ background: #ff5f56; }}
        .terminal-dot.yellow {{ background: #ffbd2e; }}
        .terminal-dot.green {{ background: #27c93f; }}
        
        .terminal-content {{
            font-size: 0.9rem;
        }}
        
        .prompt {{
            color: #58a6ff;
        }}
        
        /* Header */
        .header {{
            text-align: center;
            margin-bottom: 3rem;
        }}
        
        .avatar {{
            width: 150px;
            height: 150px;
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid #58a6ff;
            margin-bottom: 1rem;
        }}
        
        h1 {{
            font-size: 2rem;
            color: #58a6ff;
        }}
        
        .badge {{
            display: inline-block;
            padding: 0.3rem 0.8rem;
            background: #21262d;
            border-radius: 20px;
            font-size: 0.8rem;
            margin: 0.5rem;
        }}
        
        /* Sections */
        .section {{
            margin-bottom: 2rem;
            background: #161b22;
            border-radius: 10px;
            padding: 1.5rem;
            border: 1px solid #30363d;
            transition: all 0.3s;
        }}
        
        .section:hover {{
            border-color: #58a6ff;
            transform: translateX(5px);
        }}
        
        .section-title {{
            color: #58a6ff;
            margin-bottom: 1rem;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        /* Skills */
        .skills-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        
        .skill {{
            background: #21262d;
            padding: 0.3rem 0.8rem;
            border-radius: 4px;
            font-size: 0.8rem;
        }}
        
        /* Project */
        .project {{
            margin-bottom: 1.5rem;
            padding: 1rem;
            background: #21262d;
            border-radius: 8px;
            transition: all 0.3s;
        }}
        
        .project:hover {{
            transform: translateX(5px);
            background: #30363d;
        }}
        
        .project-title {{
            color: #58a6ff;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        
        .tech-badge {{
            display: inline-block;
            background: #0d1117;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.7rem;
            margin-right: 0.5rem;
            margin-top: 0.5rem;
        }}
        
        /* Experience */
        .exp-item {{
            margin-bottom: 1rem;
            padding: 0.5rem;
            border-left: 2px solid #58a6ff;
        }}
        
        /* Typing animation */
        .typing {{
            overflow: hidden;
            border-right: 2px solid #58a6ff;
            white-space: nowrap;
            animation: typing 3s steps(40, end), blink-caret 0.75s step-end infinite;
        }}
        
        @keyframes typing {{
            from {{ width: 0; }}
            to {{ width: 100%; }}
        }}
        
        @keyframes blink-caret {{
            from, to {{ border-color: transparent; }}
            50% {{ border-color: #58a6ff; }}
        }}
        
        @media (max-width: 768px) {{
            .typing {{
                white-space: normal;
                animation: none;
                border-right: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="terminal">
            <div class="terminal-header">
                <div class="terminal-dot red"></div>
                <div class="terminal-dot yellow"></div>
                <div class="terminal-dot green"></div>
            </div>
            <div class="terminal-content">
                <span class="prompt">$</span> cat about.txt<br>
                <span class="prompt">></span> {name} | Developer Portfolio<br>
                <span class="prompt">$</span>_
            </div>
        </div>
        
        <div class="header">
            <img src="{profile_image}" alt="{name}" class="avatar">
            <h1 class="typing">{name}</h1>
            <div>
                <span class="badge"><i class="fab fa-github"></i> GitHub</span>
                <span class="badge"><i class="fab fa-linkedin"></i> LinkedIn</span>
            </div>
            <p style="margin-top: 1rem;">{about}</p>
        </div>
        
        <div class="section">
            <div class="section-title">
                <i class="fas fa-terminal"></i>
                <span>skills.encode()</span>
            </div>
            <div class="skills-list">
                {''.join([f'<span class="skill">{skill}</span>' for skill in skills])}
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">
                <i class="fas fa-folder-open"></i>
                <span>projects.list()</span>
            </div>
            {''.join([f'''
            <div class="project">
                <div class="project-title">▶ {p['title']}</div>
                <div>{p['description'][:120]}</div>
                <div>
                    {''.join([f'<span class="tech-badge">{tech}</span>' for tech in p['tech'][:3]])}
                </div>
            </div>
            ''' for p in projects])}
        </div>
        
        <div class="section">
            <div class="section-title">
                <i class="fas fa-briefcase"></i>
                <span>experience.load()</span>
            </div>
            {''.join([f'''
            <div class="exp-item">
                <strong>{exp['title']}</strong><br>
                <span style="color:#8b949e">{exp['company']}</span><br>
                <span style="font-size:0.8rem">{exp['description'][0][:100] if exp['description'] else ''}</span>
            </div>
            ''' for exp in experience])}
        </div>
        
        <div class="section">
            <div class="section-title">
                <i class="fas fa-graduation-cap"></i>
                <span>education.data</span>
            </div>
            {''.join([f'''
            <div class="exp-item">
                <strong>{edu['degree']}</strong><br>
                <span style="color:#8b949e">{edu['institution']}</span>
            </div>
            ''' for edu in education])}
        </div>
        
        <div class="terminal" style="text-align: center; margin-top: 2rem;">
            <div class="terminal-content">
                <span class="prompt">$</span> <a href="{github}" style="color:#58a6ff; text-decoration:none;">github.com/{name.lower().replace(' ', '')}</a><br>
                <span class="prompt">$</span> <a href="{linkedin}" style="color:#58a6ff; text-decoration:none;">linkedin.com/in/{name.lower().replace(' ', '')}</a><br>
                <span class="prompt">$</span> echo "Let's build something amazing!"<br>
                <span class="prompt">></span> Let's build something amazing!
            </div>
        </div>
    </div>
</body>
</html>
    """


# ================== PROFESSIONAL TEMPLATE ==================

def professional_template(name, skills, projects, experience, education, profile_image, github, linkedin, about):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} | Professional Portfolio</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Source+Sans+Pro:wght@300;400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Source Sans Pro', sans-serif;
            background: #f4f4f4;
            color: #333;
        }}
        
        /* Navigation */
        .navbar {{
            position: fixed;
            top: 0;
            width: 100%;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
            padding: 1rem 0;
        }}
        
        .nav-container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 2rem;
        }}
        
        .logo {{
            font-family: 'Playfair Display', serif;
            font-size: 1.5rem;
            font-weight: 700;
            color: #2c3e50;
        }}
        
        .nav-links a {{
            color: #2c3e50;
            text-decoration: none;
            margin-left: 2rem;
            font-weight: 600;
            transition: color 0.3s;
        }}
        
        .nav-links a:hover {{
            color: #3498db;
        }}
        
        /* Hero */
        .hero {{
            min-height: 100vh;
            display: flex;
            align-items: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            position: relative;
            overflow: hidden;
        }}
        
        .hero::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="rgba(255,255,255,0.1)" fill-opacity="1" d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,122.7C672,117,768,139,864,154.7C960,171,1056,181,1152,165.3C1248,149,1344,107,1392,85.3L1440,64L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>') no-repeat bottom;
            background-size: cover;
            opacity: 0.3;
        }}
        
        .hero-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            position: relative;
            z-index: 1;
            display: flex;
            align-items: center;
            gap: 4rem;
            flex-wrap: wrap;
        }}
        
        .hero-text {{
            flex: 1;
        }}
        
        .hero-text h1 {{
            font-size: 3.5rem;
            font-family: 'Playfair Display', serif;
            margin-bottom: 1rem;
            animation: slideInLeft 0.8s ease;
        }}
        
        .hero-text p {{
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.9;
            animation: slideInLeft 0.8s ease 0.2s backwards;
        }}
        
        .hero-image {{
            flex: 1;
            text-align: center;
            animation: slideInRight 0.8s ease;
        }}
        
        .hero-image img {{
            width: 300px;
            height: 300px;
            border-radius: 50%;
            object-fit: cover;
            border: 5px solid white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        @keyframes slideInLeft {{
            from {{
                opacity: 0;
                transform: translateX(-50px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        
        @keyframes slideInRight {{
            from {{
                opacity: 0;
                transform: translateX(50px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        
        .btn {{
            display: inline-block;
            padding: 12px 30px;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s;
            margin-right: 1rem;
        }}
        
        .btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }}
        
        .btn-outline {{
            background: transparent;
            border: 2px solid white;
            color: white;
        }}
        
        .btn-outline:hover {{
            background: white;
            color: #667eea;
        }}
        
        /* Sections */
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 5rem 2rem;
        }}
        
        .section-title {{
            font-size: 2.5rem;
            font-family: 'Playfair Display', serif;
            text-align: center;
            margin-bottom: 3rem;
            color: #2c3e50;
            position: relative;
        }}
        
        .section-title::after {{
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 3px;
            background: linear-gradient(135deg, #667eea, #764ba2);
        }}
        
        /* Skills */
        .skills-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
        }}
        
        .skill-category {{
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }}
        
        .skill-category:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(102,126,234,0.2);
        }}
        
        .skill-category h3 {{
            color: #667eea;
            margin-bottom: 1rem;
        }}
        
        .skill-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        
        .skill-list span {{
            background: #f0f0f0;
            padding: 0.3rem 0.8rem;
            border-radius: 4px;
            font-size: 0.9rem;
        }}
        
        /* Projects */
        .projects-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
        }}
        
        .project-card {{
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }}
        
        .project-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 15px 40px rgba(102,126,234,0.2);
        }}
        
        .project-content {{
            padding: 1.5rem;
        }}
        
        .project-card h3 {{
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }}
        
        .project-tech {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }}
        
        .project-tech span {{
            font-size: 0.8rem;
            padding: 0.2rem 0.6rem;
            background: #f0f0f0;
            border-radius: 4px;
        }}
        
        /* Experience */
        .exp-item {{
            background: white;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }}
        
        .exp-item:hover {{
            transform: translateX(10px);
        }}
        
        .exp-title {{
            font-size: 1.2rem;
            font-weight: 700;
            color: #2c3e50;
        }}
        
        .exp-company {{
            color: #667eea;
            margin-bottom: 0.5rem;
        }}
        
        /* Education */
        .education-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }}
        
        .edu-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }}
        
        .edu-card:hover {{
            transform: scale(1.05);
        }}
        
        /* Contact */
        .contact-section {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            text-align: center;
            border-radius: 10px;
            padding: 3rem;
        }}
        
        .contact-section .btn {{
            background: white;
            color: #667eea;
        }}
        
        /* Footer */
        footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 2rem;
        }}
        
        @media (max-width: 768px) {{
            .hero-content {{
                flex-direction: column-reverse;
                text-align: center;
            }}
            
            .hero-text h1 {{
                font-size: 2rem;
            }}
            
            .projects-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <div class="logo">{name.split()[0]}</div>
            <div class="nav-links">
                <a href="#home">Home</a>
                <a href="#skills">Skills</a>
                <a href="#projects">Projects</a>
                <a href="#experience">Experience</a>
                <a href="#contact">Contact</a>
            </div>
        </div>
    </nav>
    
    <section id="home" class="hero">
        <div class="hero-content">
            <div class="hero-text">
                <h1>Hello, I'm {name.split()[0]}</h1>
                <p>{about}</p>
                <a href="{github}" class="btn" target="_blank"><i class="fab fa-github"></i> GitHub</a>
                <a href="{linkedin}" class="btn btn-outline" target="_blank"><i class="fab fa-linkedin"></i> LinkedIn</a>
            </div>
            <div class="hero-image">
                <img src="{profile_image}" alt="{name}">
            </div>
        </div>
    </section>
    
    <div class="container" id="skills">
        <h2 class="section-title">Skills & Expertise</h2>
        <div class="skills-grid">
            <div class="skill-category">
                <h3>Technical Skills</h3>
                <div class="skill-list">
                    {''.join([f'<span>{skill}</span>' for skill in skills[:8]])}
                </div>
            </div>
        </div>
    </div>
    
    <div class="container" id="projects">
        <h2 class="section-title">Featured Projects</h2>
        <div class="projects-grid">
            {''.join([f'''
            <div class="project-card">
                <div class="project-content">
                    <h3>{p['title']}</h3>
                    <p>{p['description'][:120]}</p>
                    <div class="project-tech">
                        {''.join([f'<span>{tech}</span>' for tech in p['tech'][:3]])}
                    </div>
                </div>
            </div>
            ''' for p in projects])}
        </div>
    </div>
    
    <div class="container" id="experience">
        <h2 class="section-title">Professional Experience</h2>
        {''.join([f'''
        <div class="exp-item">
            <div class="exp-title">{exp['title']}</div>
            <div class="exp-company">{exp['company']}</div>
            <p>{exp['description'][0][:150] if exp['description'] else ''}</p>
        </div>
        ''' for exp in experience])}
    </div>
    
    <div class="container" id="education">
        <h2 class="section-title">Education</h2>
        <div class="education-grid">
            {''.join([f'''
            <div class="edu-card">
                <i class="fas fa-graduation-cap" style="font-size: 2rem; color: #667eea;"></i>
                <h3>{edu['degree']}</h3>
                <p>{edu['institution']}</p>
                <small>{edu['year']}</small>
            </div>
            ''' for edu in education])}
        </div>
    </div>
    
    <div class="container" id="contact">
        <div class="contact-section">
            <h2 style="margin-bottom: 1rem;">Let's Work Together</h2>
            <p style="margin-bottom: 2rem;">I'm always interested in hearing about new opportunities</p>
            <a href="{github}" class="btn" target="_blank"><i class="fab fa-github"></i> GitHub</a>
            <a href="{linkedin}" class="btn" style="margin-left: 1rem;" target="_blank"><i class="fab fa-linkedin"></i> LinkedIn</a>
        </div>
    </div>
    
    <footer>
        <p>© 2024 {name}. All rights reserved.</p>
    </footer>
</body>
</html>
    """


# Export all public functions
__all__ = [
    'generate_portfolio',
    'build_template',
    'extract_name',
    'extract_skills',
    'extract_projects',
    'extract_experience',
    'extract_education',
    'extract_link',
    'extract_about'
]