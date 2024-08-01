from flask import Flask, request, jsonify, render_template
import pdfplumber
import os
from genai_api import gemini_api_response, gemini_api_response_job_role
import re
from jobroles import jobroles
from gtts import gTTS

app = Flask(__name__)
technical_content = None  # Global variable for storing PDF content

def remove_html_tags(text):
    clean_text = re.sub(r'<[^>]+>', '', text)
    return clean_text

def text_to_audio(text, language_code, file_path='output.mp3'):
    # Create gTTS object
    tts = gTTS(text=text, lang=language_code)
    # Save the audio file
    tts.save(file_path)
    
def get_language_code(language_name):
    language_codes = {
        'hindi': 'hi',
        'bengali': 'bn',
        'telugu': 'te',
        'marathi': 'mr',
        'tamil': 'ta',
        'urdu': 'ur',
        'gujarati': 'gu',
        'malayalam': 'ml',
        'kannada': 'kn',
        'odia': 'or',
        'punjabi': 'pa',
        'assamese': 'as',
        'maithili': 'mai',
        'santali': 'sat',
        'konkani': 'kok',
        'nepali': 'ne',
        'sanskrit': 'sa',
        'sindhi': 'sd',
        'kashmiri': 'ks',
        'manipuri': 'mni',
        'bodo': 'brx',
        'dogri': 'doi'
        # Add more languages if needed
    }

def format_text_to_html(text):
    # Replace headers
    html = text.replace('## ', '<h2>').replace('\n', '</h2>\n')
    html = html.replace('### ', '<h3>').replace('\n', '</h3>\n')
    
    # Replace bold text
    while '**' in html:
        html = html.replace('**', '<strong>', 1)
        html = html.replace('**', '</strong>', 1)
    
    # Handle newlines before numbered lists
    lines = html.split('\n')
    formatted_lines = []
    in_list = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Check if the line is a numbered list point
        if stripped and (stripped[0].isdigit() and stripped[1] == '.'):
            # Add a newline before numbered lists if the previous line is not empty
            if formatted_lines and formatted_lines[-1].strip() != '':
                formatted_lines.append('')
            
            # Close previous list if open
            if in_list:
                formatted_lines.append('</ul>' if '<li>' in formatted_lines[-1] else '</ol>')
                in_list = False
            
            formatted_lines.append(f'<ol><li>{stripped[2:].strip()}</li>')
            in_list = True
        
        # Check if the line is a bullet point
        elif stripped.startswith('* '):
            if not in_list:
                formatted_lines.append('<ul>')
                in_list = True
            formatted_lines.append(f'<li>{stripped[2:].strip()}</li>')
        
        else:
            # Close previous list if open
            if in_list:
                formatted_lines.append('</ul>' if '<li>' in formatted_lines[-1] else '</ol>')
                in_list = False
            
            # Add the current line if not empty
            if stripped:
                formatted_lines.append(line)
    
    # Close any remaining open list
    if in_list:
        formatted_lines.append('</ul>' if '<li>' in formatted_lines[-1] else '</ol>')

    html = '\n'.join(formatted_lines)
    html = re.sub(r'(?<!\n)(1\.)', r'<br><br>\1', html)
    return html


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global technical_content  # Declare as global to access the variable
    roadmap = request.json.get('message')
    job_role = request.json.get('jobRole')
    language = request.json.get('language')
    if job_role == "None":
        job_role = False
    if language == "":
        language = False
    if technical_content is None:
        return jsonify({'error': 'No technical content about user available'}), 400
    # Use gemini_api_response with the technical content and roadmap
    if job_role:
        job_role = jobroles[job_role]
        if language:
            roadmap = f"{roadmap} (explain in {language})"
        reply = gemini_api_response_job_role(technical_content, roadmap, job_role)
    else:
        if language:
            roadmap = f"{roadmap} (explain in {language})"
        reply = gemini_api_response(technical_content, roadmap)
    reply = format_text_to_html(reply)
    
    lang_code = get_language_code(language) or 'en'  # Default to English if no language code is found
    audio_file = 'static/output.mp3'
    audio_reply = remove_html_tags(reply)
    text_to_audio(audio_reply, lang_code, audio_file)
    
    return jsonify({'reply': reply, 'audio_file': '/static/output.mp3'})

@app.route('/upload', methods=['POST'])
def upload():
    global technical_content  # Declare as global to modify the variable
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.pdf'):
        # Save file to a temporary location
        temp_path = os.path.join('uploads', file.filename)
        file.save(temp_path)

        # Extract text from the PDF
        technical_content = extract_text_from_pdf(temp_path)

        # Optionally delete the file after processing
        os.remove(temp_path)

        return jsonify({'status': 'File uploaded and processed'})
    
    return jsonify({'error': 'Invalid file type'}), 400

def extract_text_from_pdf(pdf_path):
    text = ''
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + '\n'
    return text

if __name__ == '__main__':
    # Ensure 'uploads' directory exists
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
