from flask import Flask, request, render_template, jsonify, send_file, flash, redirect, url_for # Added flash, redirect, url_for
import pdfplumber
import docx
import re
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename
import PyPDF2 # This import seems unused in the provided code, consider removing if not used
import spacy # This import seems unused in the provided code, consider removing if not used
# from utils.parser import extract_name, extract_email, extract_phone, extract_skills, extract_experience, extract_city, extract_dob # These are defined in this file, so no need to import from utils
import csv
import io

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here' # ADDED: Required for flash messages. Change this to a strong, random key!
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx'} # ADDED: Define allowed extensions
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# Create data folder if it doesn't exist (for experience_data.json)
os.makedirs('data', exist_ok=True) # ADDED: Ensure data folder exists

def allowed_file(filename): # ADDED: Helper function to check allowed extensions
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def read_pdf(file_path): # Changed argument to file_path from file
    # Ensure the file is closed properly
    with pdfplumber.open(file_path) as pdf:
        return '\n'.join(page.extract_text() or '' for page in pdf.pages)

def read_docx(file_path): # Changed argument to file_path from file
    doc = docx.Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])

def load_names(file_path='name.txt'):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            names = [line.strip().split() for line in f if line.strip()]
            return [(n[0].lower(), n[1].lower() if len(n) > 1 else '') for n in names]
    except FileNotFoundError:
        return []

def save_name(first_name, last_name, file_path='name.txt'):
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f"{first_name} {last_name}\n")

def extract_name(text):
    # Common name patterns in resumes
    patterns = [
        # Standard formats with better context
        r'(?:^|\n)(?:name|full name|applicant|candidate)[:\s]*([A-Za-z]+(?:\s+[A-Za-z]+)+)(?:\n|$)',
        r'(?:^|\n)(?:name|full name|applicant|candidate)[:\s]*([A-Z]+(?:\s+[A-Z]+)+)(?:\n|$)',
        
        # Name at start of resume (with better validation)
        r'^([A-Za-z]+(?:\s+[A-Za-z]+)+)(?:\n|$)',
        r'^([A-Z]+(?:\s+[A-Z]+)+)(?:\n|$)',
        
        # Name with initials
        r'^([A-Za-z]+\s+[A-Za-z]\.?)(?:\n|$)',
        r'(?:^|\n)(?:name|full name)[:\s]*([A-Za-z]+\s+[A-Za-z]\.?)(?:\n|$)',
        
        # Name of the candidate formats
        r'(?:name of the candidate|candidate name|applicant name)[:\s]*([A-Za-z]+(?:\s+[A-Za-z]+)+)(?:\n|$)',
        r'(?:name of the candidate|candidate name|applicant name)[:\s]*([A-Z]+(?:\s+[A-Z]+)+)(?:\n|$)',
        
        # Personal Information section
        r'(?:personal information|personal details)[:\s]*([A-Za-z]+(?:\s+[A-Za-z]+)+)(?:\n|$)',
        r'(?:personal information|personal details)[:\s]*([A-Z]+(?:\s+[A-Z]+)+)(?:\n|$)',
        
        # Profile section
        r'(?:profile|about)[:\s]*([A-Za-z]+(?:\s+[A-Za-z]+)+)(?:\n|$)',
        r'(?:profile|about)[:\s]*([A-Z]+(?:\s+[A-Z]+)+)(?:\n|$)',
        
        # Contact Information section
        r'(?:contact information|contact details)[:\s]*([A-Za-z]+(?:\s+[A-Za-z]+)+)(?:\n|$)',
        r'(?:contact information|contact details)[:\s]*([A-Z]+(?:\s+[A-Z]+)+)(?:\n|$)',
        
        # Name with middle name/initial
        r'^([A-Za-z]+\s+[A-Za-z]\.?\s+[A-Za-z]+)(?:\n|$)',
        r'(?:^|\n)(?:name|full name)[:\s]*([A-Za-z]+\s+[A-Za-z]\.?\s+[A-Za-z]+)(?:\n|$)',
        
        # Name with prefix/suffix
        r'(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+([A-Za-z]+(?:\s+[A-Za-z]+)+)(?:\n|$)',
        r'(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+([A-Z]+(?:\s+[A-Z]+)+)(?:\n|$)'
    ]

    # Words that should not be considered as names
    invalid_words = {
        'full', 'name', 'first', 'last', 'email', 'phone', 'address', 'resume', 'cv',
        'curriculum', 'vitae', 'experience', 'education', 'skills', 'objective', 'profile',
        'about', 'contact', 'personal', 'details', 'information', 'candidate', 'applicant'
    }

    # First try to find name using patterns
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            full_name = match.group(1).strip()
            # Handle all caps names
            if full_name.isupper():
                full_name = full_name.title()
            
            # Clean up the name
            full_name = re.sub(r'\s+', ' ', full_name)  # Remove extra spaces
            full_name = re.sub(r'[^\w\s]', '', full_name)  # Remove special characters except spaces
            
            parts = full_name.split()
            if len(parts) >= 2:
                first = parts[0]
                last = parts[-1]
                # Skip if parts are invalid words
                if first.lower() in invalid_words or last.lower() in invalid_words:
                    continue
                # Remove any periods from initials
                first = first.replace('.', '')
                last = last.replace('.', '')
                return first.title(), last.title()
            elif len(parts) == 1 and parts[0].lower() not in invalid_words:
                return parts[0].title(), ""

    # If no pattern match, try to find name in first few lines
    lines = text.strip().split('\n')
    for line in lines[:10]:  # Look in first 10 lines
        # Skip lines that are clearly not names
        if any(x in line.lower() for x in invalid_words):
            continue
            
        # Clean the line
        line = re.sub(r'[^\w\s]', '', line)  # Remove special characters
        line = re.sub(r'\s+', ' ', line)  # Remove extra spaces
        
        words = [w for w in line.strip().split() if w.isalpha()]
        if len(words) >= 2:
            # Additional validation for name-like words
            if (all(len(w) > 1 for w in words[:2]) and  # Ensure words are not too short
                words[0].lower() not in invalid_words and  # Check first word
                words[-1].lower() not in invalid_words):  # Check last word
                return words[0].title(), words[-1].title()
        elif len(words) == 1 and len(words[0]) > 1 and words[0].lower() not in invalid_words:
            return words[0].title(), ""

    # Last resort: Look for any two consecutive capitalized words
    for line in lines[:15]:  # Look in first 15 lines
        words = line.strip().split()
        for i in range(len(words) - 1):
            if (words[i][0].isupper() and words[i+1][0].isupper() and 
                len(words[i]) > 1 and len(words[i+1]) > 1 and
                words[i].isalpha() and words[i+1].isalpha() and
                words[i].lower() not in invalid_words and
                words[i+1].lower() not in invalid_words):
                return words[i].title(), words[i+1].title()

    return "Unknown", "Unknown"

def save_experience_data(experience_data, filename="experience_data.json"):
    """Save experience data to a JSON file"""
    try:
        # Create data directory if it doesn't exist (already done at the top)
        # os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)
        
        # Load existing data if file exists
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                try: # Added try-except for JSON decoding issues
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = [] # If file is corrupted, start fresh
        else:
            existing_data = []
        
        # Add timestamp to new entries
        for entry in experience_data:
            entry['extracted_at'] = datetime.now().isoformat()
        
        # Combine existing and new data
        combined_data = existing_data + experience_data
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error saving experience data: {str(e)}")
        return False

def extract_experience(text):
    experience_entries = []

    # Common experience patterns
    patterns = [
        # Standard experience formats
        r'(\d+(?:\+)?(?:\.\d+)?)(?:\s*)(?:years?|yrs?|months?)\s*(?:of)?\s*(?:work|professional)?\s*(?:experience)?\s*(?:in|on|as|with)?\s*([A-Za-z\s,/&\-]+)',
        
        # Work experience formats
        r'(?:worked|interned|training|trainee|experience)\s*(?:for|in|at|as)?\s*(\d+(?:\+)?(?:\.\d+)?)(?:\s*)(?:years?|yrs?|months?)\s*(?:in|on|as)?\s*([A-Za-z\s,/&\-]+)',
        
        # Work Experience section formats
        r'(?:work|professional|technical|industry)\s*(?:experience|exp)[:\s-]*?(\d+(?:\+)?(?:\.\d+)?)(?:\s*)(?:years?|yrs?|months?)\s*(?:in|on|as|with)?\s*([A-Za-z\s,/&\-]+)',
        
        # Internship formats
        r'(?:internship|intern)[:\s-]*?(\d+(?:\+)?(?:\.\d+)?)(?:\s*)(?:months?|yrs?|years?)\s*(?:in|on|with)?\s*([A-Za-z\s,/&\-]+)',
        
        # Experience as role formats
        r'experience\s*(?:as|in|with)\s*([A-Za-z\s,/&\-]+)[:\s-]*?(\d+(?:\+)?(?:\.\d+)?)(?:\s*)(?:years?|yrs?|months?)',
        
        # Worked as role formats
        r'worked\s*(?:as|in|with)\s*([A-Za-z\s,/&\-]+)\s*(?:for|over)?\s*(\d+(?:\+)?(?:\.\d+)?)(?:\s*)(?:years?|yrs?|months?)'
    ]

    # Words that should not be considered as experience domains
    invalid_domains = {
        'phone', 'mobile', 'email', 'address', 'location', 'city', 'state', 'country',
        'pincode', 'pin code', 'postal', 'code', 'contact', 'details', 'information',
        'resume', 'cv', 'curriculum', 'vitae', 'objective','qantum','phd', 'profile', 'about','engineer',
    }

    month_map = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }

    def extract_bullet_points(text_content, start_pos): # Renamed `text` to `text_content` to avoid shadowing
        bullet_points = []
        lines = text_content[start_pos:].split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-'):
                bullet_points.append(line[1:].strip())
            elif line and not any(x in line.lower() for x in ['experience', 'education', 'skills']):
                break
        return bullet_points

    def process_internship_section(text_content): # Renamed `text` to `text_content`
        # Find the INTERNSHIPS section
        internship_section = re.search(r'INTERNSHIPS:.*?(?=\n\n|\Z)', text_content, re.DOTALL | re.IGNORECASE)
        if internship_section:
            section_text = internship_section.group(0)
            # Process each bullet point
            bullet_points = extract_bullet_points(section_text, 0)
            for bullet in bullet_points:
                # Try to extract role and company from bullet point
                role_match = re.search(r'\'([A-Za-z\s,/&\-]+)\'', bullet)
                company_match = re.search(r'(?:from|in)\s+\'([A-Za-z0-9\s,/&\-]+)\'', bullet)
                date_match = re.search(r'from\s+([A-Za-z]{3,9}),\s*(\d{4})\s*(?:to|–|-)\s*([A-Za-z]{3,9}|present|current|N)\s*,?\s*(\d{4})?', bullet)
                
                if role_match and company_match:
                    role = role_match.group(1)
                    company = company_match.group(1)
                    
                    # Calculate duration if dates are available
                    if date_match:
                        start_month, start_year = date_match.group(1), date_match.group(2)
                        end_month = date_match.group(3)
                        end_year = date_match.group(4)
                        
                        try:
                            sm = month_map[start_month.lower()[:3]]
                            sy = int(start_year)
                            em = datetime.now().month if end_month.lower() in ['present', 'current', 'n'] else month_map[end_month.lower()[:3]]
                            ey = datetime.now().year if not end_year or end_month.lower() in ['present', 'current', 'n'] else int(end_year)
                            
                            start_date = datetime(sy, sm, 1)
                            end_date = datetime(ey, em, 1)
                            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                            years = round(months / 12, 1)
                            
                            if years > 0 and years <= 50:
                                years_text = f"{years} years" if years.is_integer() else f"{years} years"
                                experience_entries.append({
                                    'type': 'internship',
                                    'role': role,
                                    'company': company,
                                    'duration': years_text,
                                    'start_date': start_date.isoformat(),
                                    'end_date': end_date.isoformat(),
                                    'is_current': end_month.lower() in ['present', 'current', 'n'],
                                    'description': bullet
                                })
                        except Exception:
                            pass
                    else:
                        # If no dates, add as current internship
                        experience_entries.append({
                            'type': 'internship',
                            'role': role,
                            'company': company,
                            'duration': 'Current',
                            'is_current': True,
                            'description': bullet
                        })

    # Process the INTERNSHIPS section first
    process_internship_section(text) # Passed original `text`

    # Pattern for internship entries
    internship_patterns = [
        # "Internship on 'Role' in 'Company' from Month, Year – Month, Year"
        r'Internship\s+on\s+\'([A-Za-z\s,/&\-]+)\'\s+in\s+\'([A-Za-z0-9\s,/&\-]+)\'\s+from\s+([A-Za-z]{3,9}),\s*(\d{4})\s*(?:to|–|-)\s*([A-Za-z]{3,9}|present|current|N)\s*,?\s*(\d{4})?',
        # "Working Intern as a 'Role' in 'Company'"
        r'Working\s+Intern\s+as\s+a\s+\'([A-Za-z\s,/&\-]+)\'\s+in\s+\'([A-Za-z0-9\s,/&\-]+)\'',
        # "Did my internship training on 'Role' from Company"
        r'Did\s+my\s+internship\s+training\s+on\s+\'([A-Za-z\s,/&\-]+)\'\s+from\s+([A-Za-z0-9\s,/&\-]+)',
        # "Company Name Month Year – Month Year"
        r'([A-Za-z0-9\s,/&\-]+)(?:\s+)([A-Za-z]{3,9})\s*(\d{4})\s*(?:to|–|-)\s*([A-Za-z]{3,9}|present|current)\s*(\d{4})?',
        # "Role\nCompany Month Year – Month Year"
        r'([A-Za-z\s,/&\-]+)(?:\n)([A-Za-z0-9\s,/&\-]+)(?:\s+)([A-Za-z]{3,9})\s*(\d{4})\s*(?:to|–|-)\s*([A-Za-z]{3,9}|present|current)\s*(\d{4})?'
    ]

    # Process internship patterns
    for pattern in internship_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                if len(match) == 5:  # Company name format
                    company, start_month, start_year, end_month, end_year = match
                    role = ""
                elif len(match) == 6:  # Role and company format with dates
                    role, company, start_month, start_year, end_month, end_year = match
                elif len(match) == 2:  # Role and company format without dates
                    role, company = match
                    # Add as current internship
                    experience_entries.append({
                        'type': 'internship',
                        'role': role,
                        'company': company,
                        'duration': 'Current',
                        'is_current': True
                    })
                    continue
                else:
                    continue

                # Process dates if available
                if start_month and start_year:
                    sm = month_map[start_month.lower()[:3]]
                    sy = int(start_year)
                    em = datetime.now().month if end_month.lower() in ['present', 'current', 'n'] else month_map[end_month.lower()[:3]]
                    ey = datetime.now().year if not end_year or end_month.lower() in ['present', 'current', 'n'] else int(end_year)
                    
                    start_date = datetime(sy, sm, 1)
                    end_date = datetime(ey, em, 1)
                    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                    years = round(months / 12, 1)
                    
                    if years <= 0 or years > 50:
                        continue
                    
                    years_text = f"{years} years" if years.is_integer() else f"{years} years"
                else:
                    years_text = "Current"
                    start_date = None # Ensure start_date and end_date are None if not available
                    end_date = None


                # Clean and validate the company and role
                company = company.strip()
                role = role.strip() if role else ""
                
                # Skip if company is invalid
                if (any(word in company.lower() for word in invalid_domains) or
                    len(company) < 2 or
                    company.lower().startswith(('phone', 'mobile', 'email', 'address'))):
                    continue

                # Get bullet points for description
                match_text = match[0] if len(match) == 5 else f"{match[0]}\n{match[1]}"
                start_pos = text.find(match_text) + len(match_text)
                bullet_points = extract_bullet_points(text, start_pos) # Passed original `text`

                experience_entries.append({
                    'type': 'internship',
                    'role': role,
                    'company': company,
                    'duration': years_text,
                    'start_date': start_date.isoformat() if start_date else None, # Use .isoformat() only if not None
                    'end_date': end_date.isoformat() if end_date else None,     # Use .isoformat() only if not None
                    'is_current': end_month.lower() in ['present', 'current', 'n'] if start_month and start_year else True,
                    'description': '\n'.join(bullet_points) if bullet_points else None
                })
            except Exception:
                continue

    # Remove duplicates
    seen = set()
    unique_entries = []
    for exp in experience_entries:
        key = (exp.get('role', ''), exp.get('company', ''), exp.get('start_date'))
        if key not in seen:
            seen.add(key)
            unique_entries.append(exp)

    # Save the extracted data (this will append to the file)
    # save_experience_data(unique_entries) # DEACTIVATED: We will save all data once after processing all files

    # Format for display
    display_entries = []
    for exp in unique_entries:
        display_entries.append({
            'years': exp['duration'],
            
            'domain': f"{exp['role']} at {exp['company']}" if exp['role'] else f"at {exp['company']}"
        })

    return display_entries

def extract_dob(text):
    match = re.search(r'(dob|date of birth)[:\s]*([\d/.-]{6,10})', text, re.IGNORECASE)
    return match.group(2) if match else ""

def extract_phone(text):
    match = re.search(r'(\+?\d{1,3}[-.\s]?)?(\d{10})', text)
    return match.group() if match else ""

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group() if match else ""

def load_skill_list(file_path='skill.txt'):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def extract_skills(text, skills_list_from_file): # Renamed argument to avoid conflict
    found_skills = set()
    text = text.lower()
    for skill in skills_list_from_file: # Used renamed argument
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            found_skills.add(skill)
    return list(found_skills)

def calculate_atc_score(data):
    score = 0
    max_score = 100
    
    # Personal Information (20 points)
    if data.get('first_name') and data.get('last_name'):
        score += 5
    if data.get('email'):
        score += 5
    if data.get('phone'):
        score += 5
    
    # Skills (30 points)
    skills = data.get('skills', [])
    if len(skills) >= 5:
        score += 15
    elif len(skills) >= 3:
        score += 10
    elif len(skills) >= 1:
        score += 5
    
    # Experience (40 points)
    experience = data.get('experience', [])
    if len(experience) >= 3:
        score += 20
    elif len(experience) >= 2:
        score += 15
    elif len(experience) >= 1:
        score += 10
    
    # Additional Information (10 points)
    if data.get('dob'):
        score += 5
    
    # Calculate percentage
    percentage = (score / max_score) * 100
    
    return {
        'score': score,
        'max_score': max_score,
        'percentage': round(percentage, 1),
        'details': {
            'personal_info': 15 if all([data.get('first_name'), data.get('last_name'), data.get('email'), data.get('phone')]) else 0,
            'skills': 30 if len(skills) >= 5 else (20 if len(skills) >= 3 else (10 if len(skills) >= 1 else 0)),
            'experience': 40 if len(experience) >= 3 else (30 if len(experience) >= 2 else (20 if len(experience) >= 1 else 0)),
            'additional': 5 if data.get('dob') else 0
        }
    }

def extract_resume_data(file_path):
    filename = os.path.basename(file_path).lower()
    if filename.endswith('.pdf'):
        text = read_pdf(file_path)
    elif filename.endswith('.docx'):
        text = read_docx(file_path)
    else:
        raise ValueError("Unsupported file type. Please upload PDF or DOCX.")

    text_lower = text.lower()

    first_name, last_name = extract_name(text)
    experience = extract_experience(text)
    dob = extract_dob(text_lower)
    phone = extract_phone(text_lower)
    email = extract_email(text_lower)
    skill_list = load_skill_list()
    skills = extract_skills(text_lower, skill_list)

    data = {
        'filename': os.path.basename(file_path),
        'first_name': first_name.title(),
        'last_name': last_name.title(),
        'experience': experience,
        'dob': dob,
        'phone': phone,
        'email': email,
        'skills': skills
    }

    # Calculate ATC score
    data['atc_score'] = calculate_atc_score(data)

    return data

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', data=None, error=None, all_data=[])

@app.route('/upload', methods=['POST'])
def upload():
    if 'files[]' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))
    
    files = request.files.getlist('files[]')
    
    if not files or all(f.filename == '' for f in files):
        flash('No selected file(s)', 'error')
        return redirect(url_for('index'))

    processed_resumes = []
    all_experience_data = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                file.save(filepath)
                resume_data = extract_resume_data(filepath)
                processed_resumes.append(resume_data)
                
                if resume_data.get('experience'):
                    all_experience_data.extend(resume_data['experience'])

                os.remove(filepath)

            except Exception as e:
                flash(f"Error processing {filename}: {str(e)}", 'error')
                if os.path.exists(filepath):
                    os.remove(filepath)
        else:
            if file.filename:
                flash(f"File '{file.filename}' has an unsupported extension or is malformed.", 'error')
            else:
                flash('An empty file was submitted.', 'error')

    if all_experience_data:
        save_experience_data(all_experience_data)
    
    if processed_resumes:
        flash(f"Successfully processed {len(processed_resumes)} resume(s)!", 'success')
        return render_template('index.html', processed_resumes=processed_resumes, all_data=processed_resumes)
    else:
        flash("No valid resumes were processed.", 'error')
        return redirect(url_for('index'))

@app.route('/experience', methods=['GET'])
def get_experience():
    try:
        filepath = os.path.join('data', 'experience_data.json')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                experience_data = json.load(f)
            return jsonify(experience_data)
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/export-csv', methods=['POST'])
def export_csv():
    try:
        all_resumes_data = request.json
        if not all_resumes_data:
            return jsonify({'error': 'No data provided for export'}), 400

        output = io.StringIO()
        writer = csv.writer(output)

        # Headers without City and Hobbies
        headers = [
            'Filename', 'Name', 'Email', 'Phone', 'DOB', 'Skills', 'Experience', 'ATS Score'
        ]
        writer.writerow(headers)

        for data in all_resumes_data:
            filename = data.get('filename', '')
            name = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
            email = data.get('email', '')
            phone = data.get('phone', '')
            dob = data.get('dob', '')
            skills = ', '.join(data.get('skills', []))
            atc_percentage = data.get('atc_score', {}).get('percentage', '')

            # Combine all experiences into a single string
            experiences = data.get('experience', [])
            if experiences:
                exp_strings = []
                for exp in experiences:
                    years = exp.get('years', '')
                    domain = exp.get('domain', '')
                    if years and domain:
                        exp_strings.append(f"{domain} ({years})")
                    elif domain:
                        exp_strings.append(domain)
                    elif years:
                        exp_strings.append(years)
                experience_str = '; '.join(exp_strings)
            else:
                experience_str = ''

            writer.writerow([
                filename, name, email, phone, dob, skills, experience_str, f"{atc_percentage:.2f}%" if atc_percentage != '' else ''
            ])

        output.seek(0)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'resume_data_{timestamp}.csv'
        )
    except Exception as e:
        print(f"Error during CSV export: {e}")
        return jsonify({'error': f'Error exporting CSV: {str(e)}'}), 500


if __name__ == '__main__':
    print("✅ Flask server running at http://127.0.0.1:5000")
    app.run(debug=True)