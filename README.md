# Resume Extractor 🧾📂

A smart **Resume Extractor web application** built with **Python and Flask**. This tool allows recruiters or companies to upload multiple resumes (PDF or DOCX), extract key candidate details, filter the data via checkboxes on the UI, and export everything into a clean CSV file. It simplifies the hiring process by automating resume parsing and structuring.

## 🔍 Key Features

- ✅ Upload **multiple resumes** at once (PDF / DOCX)  
- 🧠 Automatically **extracts key information**:  
  - Full Name  
  - Phone Number  
  - Email Address  
  - Skills  
  - Total Experience  
  - City / Location  
- 📥 One-click **CSV Export** of all parsed data  
- ✅ **Interactive Filter UI**:  
  - Use checkboxes to include/exclude fields (e.g., Name, Phone, Skills, etc.)  
  - Customize the data you want to view or export  
- 🧾 Designed for **bulk resume processing** — saves time and manual effort  

## 🧑‍💼 Ideal For

- HR Professionals & Recruiters  
- Hiring agencies with high resume inflow  
- Startups looking to automate screening  
- Anyone managing candidate pipelines efficiently  

## 🛠 Tech Stack

| Layer    | Technology                     |
| -------- | ----------------------------- |
| Backend  | Python, Flask                 |
| Frontend | HTML, CSS                    |
| Libraries| `pdfminer`, `pdfplumber`, `python-docx`, `docx2txt`, `re`, `spacy`, `PyPDF2`, `Werkzeug`, `csv`, `io` |
| Output   | CSV format                   |

## 🚀 How It Works

1. Upload multiple resumes (PDF or DOCX files)  
2. The app extracts key fields using NLP and pattern matching  
3. Users can select which fields to display/export using checkboxes  
4. All extracted data is shown in a table  
5. Click "Export" to download a structured CSV of the selected fields  

## 📂 Project Structure

```

resume\_app/
│
├── app.py
├── data/
│   └── resume\_data.csv
├── uploads/
├── templates/
│   └── index.html
├── utils/
├── assets/
│   ├── screenshot1.png
│   └── screenshot2.png
├── requirements.txt
├── install\_requirements.bat
├── install\_requirements.sh
├── .gitignore
├── README.md

````

## 💻 Installation & Usage

### 🔸 Option 1: Manual Setup

1. **Clone the repository**:  
   ```bash
   git clone https://github.com/rohit-kr-dev/Resume_Eextractor.git
   cd Resume_Eextractor
````

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Flask server**:

   ```bash
   python app.py
   ```

4. **Open in your browser**:

   ```
   http://localhost:5000
   ```

---

### 🔸 Option 2: Quick Setup for Windows Users

Run the batch script:

```bash
install_requirements.bat
```

This will:

* Create a virtual environment
* Activate it
* Install all required libraries

---

### 🔸 Option 3: Quick Setup for Linux/macOS Users

Make the script executable and run:

```bash
chmod +x install_requirements.sh
./install_requirements.sh
```

---

## 📸 Screenshots

### 🔹 Upload & Filter Interface

![Resume Extractor UI 1](https://github.com/rohit-kr-dev/Resume_Eextractor/blob/master/assets/screenshot1.png)

### 🔹 Extracted Data Display

![Resume Extractor UI 2](https://github.com/rohit-kr-dev/Resume_Eextractor/blob/master/assets/screenshot2.png)

## 📌 Future Enhancements

* ATS Score matching with job descriptions
* Resume preview window
* Experience sorting & filtering
* Dashboard with graphs & analytics
* User login for secure access

## 📬 Contact

**Developer**: Rohit Kumar P Begur
**GitHub**: [@rohit-kr-dev](https://github.com/rohit-kr-dev)
**Email**: [rohitkumarpbegur@gmail.com](mailto:rohitkumarpbegur@gmail.com)

> ⚡ Streamline your recruitment process with Resume Extractor — fast, accurate, and efficient resume data in just a few clicks!

## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

## 🔁 To Push Your Changes

Once you add this README and supporting scripts, commit and push:

```bash
git add README.md requirements.txt install_requirements.bat install_requirements.sh assets/screenshot1.png assets/screenshot2.png
git commit -m "Add README with setup scripts and screenshots"
git push origin master
```
