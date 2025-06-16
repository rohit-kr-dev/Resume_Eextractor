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
| Libraries| `pdfminer`, `docx2txt`, `re`, `pandas` |
| Output   | CSV format                   |

## 🚀 How It Works

1. Upload multiple resumes (PDF or DOCX files)  
2. The app extracts key fields using NLP and pattern matching  
3. Users can select which fields to display/export using checkboxes  
4. All extracted data is shown in a table  
5. Click "Export" to download a structured CSV of the selected fields  

## 📂 Project Structure

```
resume_app/
│
├── app.py
├── data/
│   └── resume_data.csv
├── uploads/
├── templates/
│   └── index.html
├── utils/
├── assets/
│   ├── screenshot1.png
│   └── screenshot2.png
├── .gitignore
├── requirements.txt
├── README.md
```

## 💻 Installation & Usage

1. **Clone the repository**:  
   ```bash
   git clone https://github.com/rohit-kr-dev/Resume_Eextractor.git
   cd Resume_Eextractor
   ```

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

## 📸 Screenshots

### 🔹 Upload & Filter Interface

![Resume Extractor UI 1](https://github.com/rohit-kr-dev/Resume_Eextractor/blob/master/assets/screenshot1.png)

### 🔹 Extracted Data Display

![Resume Extractor UI 2](https://github.com/rohit-kr-dev/Resume_Eextractor/blob/master/assets/screenshot1.png)

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

If you want, I can help generate a `LICENSE` file for you too.

Once you add this README, remember to commit and push:

```bash
git add README.md assets/screenshot1.png assets/screenshot2.png
git commit -m "Add detailed README with screenshots and license"
git push origin master
```

