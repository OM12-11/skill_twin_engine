from flask import Flask, render_template, request, jsonify
import os
import PyPDF2
import docx
from werkzeug.utils import secure_filename

# Import modules
import skill_extractor
import job_scraper
import gap_analyzer
import roadmap_generator
import firebase_config

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_path):
    """
    Reads text from .txt, .pdf, or .docx files.
    """
    ext = file_path.rsplit('.', 1)[1].lower()
    text = ""
    
    try:
        if ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
        elif ext == 'pdf':
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                    
        elif ext == 'docx':
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
                
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
        
    return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['resume']
    role = request.form.get('role')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 1. Extract Text from File
        resume_text = extract_text_from_file(filepath)
        if not resume_text:
            return jsonify({'error': 'Could not read file'}), 500
            
        # 2. Extract Skills using spaCy
        resume_skills = skill_extractor.extract_skills(resume_text)
        
        # 3. Get Job Skills
        job_skills = job_scraper.get_job_skills(role)
        
        # 4. Analyze Gap
        analysis_result = gap_analyzer.analyze_gap(resume_skills, job_skills)
        
        # 5. Generate Roadmap
        roadmap = roadmap_generator.generate_roadmap(analysis_result['missing_skills'])
        
        # Prepare final result
        result = {
            'role': role,
            'resume_skills': resume_skills,
            'missing_skills': analysis_result['missing_skills'],
            'match_percent': analysis_result['match_percentage'],
            'roadmap': roadmap
        }
        
        # 6. Save to Firebase
        firebase_config.save_analysis_result(result)
        
        # Clean up uploaded file (optional, keeping it simple)
        # os.remove(filepath)
        
        return jsonify(result)
    
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True)
