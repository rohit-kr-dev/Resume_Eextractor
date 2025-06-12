import pdfplumber
import docx
import re
from datetime import datetime
import os
import json

def read_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = ''
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'
    return text

def read_docx(file):
    doc = docx.Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def extract_name(text):
    """Extract name from text using various patterns"""
    # Load valid names
    valid_names = load_valid_names()
    
    # List of titles and qualifications to exclude
    titles = {'phd', 'ms', 'mba', 'btech', 'b.tech', 'm.tech', 'mtech', 'b.e', 'm.e', 'bsc', 'msc', 'bca', 'mca', 'dr', 'mr', 'mrs', 'miss', 'prof', 'professor'}
    
    # Common name patterns
    patterns = [
        # Full name at start of line
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        # Name: format
        r'(?:name|full name)[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        # Name followed by common separators
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*[-–]',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\(',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*[A-Z]',
        # Name in contact information
        r'(?:contact|email|phone)[:\s]*[^,\n]*,\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        # Name in header
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*$',
    ]
    
    # Try each pattern
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            name = match.group(1).strip()
            # Split into parts and filter out titles
            name_parts = [part for part in name.split() if part.lower() not in titles]
            
            if len(name_parts) >= 1:  # Must have at least first name
                # Basic validation: check if it looks like a name
                if all(part[0].isupper() and len(part) > 1 for part in name_parts):
                    if len(name_parts) >= 2:  # If we have both first and last name
                        return f"{name_parts[0]} {name_parts[-1]}"
                    else:  # If we only have first name
                        return name_parts[0]
    
    # Fallback: Look for capitalized words in first few lines
    lines = text.split('\n')[:10]  # Check first 10 lines
    for line in lines:
        words = line.split()
        for i in range(len(words)):
            # Check for single capitalized word
            if (words[i][0].isupper() and len(words[i]) > 1 and 
                words[i].lower() not in titles):
                # Look ahead for a second name
                if i + 1 < len(words) and words[i+1][0].isupper() and len(words[i+1]) > 1:
                    return f"{words[i]} {words[i+1]}"
                else:
                    return words[i]
    
    return None

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
        'resume', 'cv', 'curriculum', 'vitae', 'objective','qantum','phd' 'profile', 'about','engineer',
    }

    month_map = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }

    def extract_bullet_points(text, start_pos):
        bullet_points = []
        lines = text[start_pos:].split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-'):
                bullet_points.append(line[1:].strip())
            elif line and not any(x in line.lower() for x in ['experience', 'education', 'skills']):
                break
        return bullet_points

    def process_internship_section(text):
        # Find the INTERNSHIPS section
        internship_section = re.search(r'INTERNSHIPS:.*?(?=\n\n|\Z)', text, re.DOTALL | re.IGNORECASE)
        if internship_section:
            section_text = internship_section.group(0)
            # Process each bullet point
            bullet_points = extract_bullet_points(section_text, 0)
            for bullet in bullet_points:
                # Try to extract role and company from bullet point
                role_match = re.search(r"'([A-Za-z\s,/&\-]+)'", bullet)
                company_match = re.search(r"(?:from|in)\s+'([A-Za-z0-9\s,/&\-]+)'", bullet)
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
    process_internship_section(text)

    # Pattern for internship entries
    internship_patterns = [
        # "Internship on 'Role' in 'Company' from Month, Year – Month, Year"
        r"Internship\s+on\s+'([A-Za-z\s,/&\-]+)'\s+in\s+'([A-Za-z0-9\s,/&\-]+)'\s+from\s+([A-Za-z]{3,9}),\s*(\d{4})\s*(?:to|–|-)\s*([A-Za-z]{3,9}|present|current|N)\s*,?\s*(\d{4})?",
        # "Working Intern as a 'Role' in 'Company'"
        r"Working\s+Intern\s+as\s+a\s+'([A-Za-z\s,/&\-]+)'\s+in\s+'([A-Za-z0-9\s,/&\-]+)'",
        # "Did my internship training on 'Role' from Company"
        r"Did\s+my\s+internship\s+training\s+on\s+'([A-Za-z\s,/&\-]+)'\s+from\s+([A-Za-z0-9\s,/&\-]+)",
        # "Company Name Month Year – Month Year"
        r"([A-Za-z0-9\s,/&\-]+)(?:\s+)([A-Za-z]{3,9})\s*(\d{4})\s*(?:to|–|-)\s*([A-Za-z]{3,9}|present|current)\s*(\d{4})?",
        # "Role\nCompany Month Year – Month Year"
        r"([A-Za-z\s,/&\-]+)(?:\n)([A-Za-z0-9\s,/&\-]+)(?:\s+)([A-Za-z]{3,9})\s*(\d{4})\s*(?:to|–|-)\s*([A-Za-z]{3,9}|present|current)\s*(\d{4})?"
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
                bullet_points = extract_bullet_points(text, start_pos)

                experience_entries.append({
                    'type': 'internship',
                    'role': role,
                    'company': company,
                    'duration': years_text,
                    'start_date': start_date.isoformat() if start_month and start_year else None,
                    'end_date': end_date.isoformat() if start_month and start_year else None,
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

    # Save the extracted data
    save_experience_data(unique_entries)

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
    if match:
        return match.group(2)
    return ""

def extract_phone(text):
    match = re.search(r'(\+?\d{1,3}[-.\s]?)?(\d{10})', text)
    if match:
        return match.group()
    return ""

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if match:
        return match.group()
    return ""

def extract_city(text):
    """Extract city from text using various patterns"""
    # Load valid cities
    valid_cities = set()
    try:
        with open('city.txt', 'r', encoding='utf-8') as f:
            valid_cities = {line.strip().lower() for line in f if line.strip()}
    except FileNotFoundError:
        print("Warning: city.txt not found")
    
    # Common city patterns
    patterns = [
        r'Location:\s*([A-Za-z\s]+)',  # Location: format
        r'City:\s*([A-Za-z\s]+)',      # City: format
        r'Address:\s*[^,\n]+,\s*([A-Za-z\s]+)',  # Address format
        r'Based in\s*([A-Za-z\s]+)',   # Based in format
        r'Located in\s*([A-Za-z\s]+)', # Located in format
        r'Residing in\s*([A-Za-z\s]+)', # Residing in format
        r'Current Location:\s*([A-Za-z\s]+)', # Current Location format
    ]
    
    # Try each pattern
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            city = match.group(1).strip()
            # Clean and validate city
            city = re.sub(r'\s+', ' ', city)  # Remove extra spaces
            city = city.strip()
            
            # Check if it's a valid city
            if city.lower() in valid_cities:
                return city
    
    # Fallback: Look for city names in the first few lines
    lines = text.split('\n')[:10]  # Check first 10 lines
    for line in lines:
        words = line.split()
        for word in words:
            word = word.strip('.,;:()[]{}')
            if word.lower() in valid_cities:
                return word
    
    return None

def extract_hobbies(text):
    match = re.search(r'hobbies?[:\s]*([a-zA-Z, \n]+)', text, re.IGNORECASE)
    if match:
        hobbies = match.group(1).replace('\n', ' ').strip()
        return hobbies
    return ""

def load_valid_names(file_path='name.txt'):
    try:
        with open(file_path, 'r') as f:
            return [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError:
        print("⚠️ name.txt not found.")
        return []

def load_skill_list(file_path='skill.txt'):
    try:
        with open(file_path, 'r') as f:
            return [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError:
        print("⚠️ skill.txt not found.")
        return []

def extract_skills(text, skills):
    found_skills = set()
    text = text.lower()
    for skill in skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            found_skills.add(skill)
    return list(found_skills)

def extract_resume_data(file):
    filename = file.filename.lower()
    if filename.endswith('.pdf'):
        text = read_pdf(file)
    elif filename.endswith('.docx'):
        text = read_docx(file)
    else:
        raise ValueError("Unsupported file type. Please upload PDF or DOCX.")

    # Normalize whitespace to avoid parsing issues
    text = re.sub(r'\s+', ' ', text)
    text_lower = text.lower()

    valid_names = load_valid_names()

    first_name, last_name = extract_name(text)

    # Accept empty names if not found in valid names
    if not any([first_name.lower() in valid_names, last_name.lower() in valid_names]):
        first_name, last_name = "", ""

    experience, unique_experience = extract_experience(text)
    dob = extract_dob(text_lower)
    phone = extract_phone(text_lower)
    email = extract_email(text_lower)
    city = extract_city(text_lower)
    hobbies = extract_hobbies(text_lower)

    skill_list = load_skill_list()
    skills = extract_skills(text_lower, skill_list)

    return {
        'first_name': first_name.title(),
        'last_name': last_name.title(),
        'experience': experience,
        'dob': dob,
        'phone': phone,
        'email': email,
        'city': city,
        'hobbies': hobbies,
        'skills': skills
    }

def save_experience_data(experience_data, filename="experience_data.json"):
    """Save experience data to a JSON file"""
    try:
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)
        
        # Load existing data if file exists
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
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