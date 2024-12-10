from flask import Flask, request, render_template, jsonify, make_response, redirect, url_for, session
import os
import openai
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import json 
from datetime import timedelta



# Code was assisted by LLMs



# Set up Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = os.urandom(24)  # For session management

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # 30 minutes session expiration

def extract_text_from_pdf(pdf_path, output_folder="output_images"):
    """
    Converts PDF pages to images and extracts text using OCR.
    """
    os.makedirs(output_folder, exist_ok=True)
    extracted_text = ""
    poppler_path = 'Your_Poppler_Path'
    try:
        images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
        for i, image in enumerate(images):
            image_path = os.path.join(output_folder, f"page_{i + 1}.png")
            image.save(image_path, "PNG")
            page_text = pytesseract.image_to_string(image)
            extracted_text += f"\n--- Page {i + 1} ---\n{page_text}"
            os.remove(image_path)
        return extracted_text
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
        return None

@app.route('/')
def index():
    return render_template('exam-maker.html')

@app.route('/generate', methods=['POST'])
def generate_exam():
    session.permanent = True  # Make the session permanent
    uploaded_files = request.files.getlist('files')
    extracted_texts = []
    for file in uploaded_files:
        if file.filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            if file.filename.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
                if text:
                    extracted_texts.append(f"Content from {file.filename}:\n{text}")

    question_types = request.form.getlist('question_types')
    exam_length = request.form.get('exam_length')
    additional_requests = request.form.get('additional_requests', '')

    prompt = f"""
    You are a teaching assistant. Create a practice exam as a STRICT JSON array with these specifications:
    - Use this exact JSON structure: [{{
        "question": "Question text",
        "answer": "Answer text"
    }}]
    - Number of questions: {exam_length}
    - Question Types: {', '.join(question_types)}
    - Additional Requests: {additional_requests}
    
    IMPORTANT: 
    - Return ONLY valid JSON 
    - Do NOT include any text before or after the JSON
    - Ensure test fits THE FOLLOWING LENGTH: {exam_length}
    - Ensure test ONLY has the following types of questions: {', '.join(question_types)}
    - If the question type is multiple-choice:
        - Write the question text so that it includes 3-4 answer options clearly labeled (e.g., A, B, C, D)
        - Have each of the options right after the question, both in "Question Text"
        - Indicate the correct answer in the "answer" field (e.g., "B").
    - If the question type is Fill in the Blank:
        - Write the question text such that there is a ___ in the question
        - Indicate the correct answer that fills in the blank in the "answer" field
    - If the question type is free response:
        - Simply provide a question without answer options and include the correct answer in the "answer" field.
    - Ensure proper JSON formatting
    """
    print(prompt)
    if extracted_texts:
        prompt += "\n\nBase the content on these texts:\n" + "\n".join(extracted_texts)

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are an expert in creating structured exams. Always respond with valid JSON."},
                {"role": "user", "content": prompt},
            ]
        )
        
        full_response = response.choices[0].message.content
        
        try:
            exam_data = json.loads(full_response)
            session['exam'] = exam_data
            return redirect(url_for('show_question', index=0))
        except json.JSONDecodeError as json_err:
            print("JSON Parsing Error:", json_err)
            print("Problematic Response:", full_response)
            return jsonify({
                "error": "Failed to parse JSON", 
                "response": full_response,
                "details": str(json_err)
            }), 500
    
    except Exception as e:
        print("Comprehensive Error:", str(e))
        return jsonify({"error": str(e)}), 500
    


@app.route('/question/<int:index>')
def show_question(index):
    
    # Retrieve exam data from session
    exam = session.get('exam', None)
    
    if not exam:
        return "Exam data is missing or corrupted.", 500  # Handle missing exam data
    
    questions = exam.get('questions', [])  # Retrieve the list of questions from the exam data
    
    if not questions:
        return "No questions found in the exam.", 500  # Handle empty exam data
    # Check if index is valid
    if 0 <= index < len(questions):
        return render_template(
            'question.html',
            question_data=questions[index],  # Pass the question at the given index
            index=index,
            total=len(questions),
        )
    
    return "Invalid question index.", 404  # Handle invalid index

@app.route('/answer/<int:index>')
def show_answer(index):
    exam = session.get('exam', {})  # Get the exam data from the session, default to empty dict
    if 'questions' in exam:  # Check if 'questions' key exists in the exam data
        questions = exam['questions']  # Get the list of questions
        if 0 <= index < len(questions):  # Ensure the index is valid
            return jsonify({"answer": questions[index].get('answer', 'No answer provided')})
    return jsonify({"error": "Invalid question index"}), 404


@app.route('/full_exam')
def full_exam():
    exam = session.get('exam', None)
    if not exam:
        return "Exam data is missing or corrupted.", 500
    return render_template('full_exam.html', exam=exam)

@app.route('/full_answer_sheet')
def full_answer_sheet():
    exam = session.get('exam', None)
    if not exam:
        return "Exam data is missing or corrupted.", 500
    return render_template('full_answer_sheet.html', exam=exam)

if __name__ == '__main__':
    app.run(debug=True)
