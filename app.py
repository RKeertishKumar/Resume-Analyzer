from flask import Flask, request, jsonify, render_template
import pdfplumber
import os
from genai_api import gemini_api_response
import re
app = Flask(__name__)
technical_content = None  # Global variable for storing PDF content

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
    # Ensure technical_content is available
    if technical_content is None:
        return jsonify({'error': 'No technical content available'}), 400
    # Use gemini_api_response with the technical content and roadmap
    reply = gemini_api_response(technical_content, roadmap)
    reply = format_text_to_html(reply)
    return jsonify({'reply': reply})

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
