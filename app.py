import os
from flask import Flask, request, render_template, jsonify, make_response
import openai
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

# Set up Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def extract_text_from_pdf(pdf_path, output_folder="output_images"):
    """
    Converts PDF pages to images and extracts text using OCR.
    """
    os.makedirs(output_folder, exist_ok=True)
    extracted_text = ""

    # The below path is where the 'bin' file in the poppler download would be
    poppler_path = 'INSERT_POPPLER_BIN_FILE_PATH_HERE'
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=300, poppler_path= poppler_path)  # Use 300 DPI for better OCR accuracy
        for i, image in enumerate(images):
            # Save each page as an image
            image_path = os.path.join(output_folder, f"page_{i + 1}.png")
            image.save(image_path, "PNG")
            
            # Perform OCR on the image
            page_text = pytesseract.image_to_string(image)
            extracted_text += f"\n--- Page {i + 1} ---\n{page_text}"

            # Delete Image after use
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
    # Handle uploaded files
    uploaded_files = request.files.getlist('files')
    uploaded_file_names = []
    extracted_texts = []
    for file in uploaded_files:
        if file.filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            uploaded_file_names.append(file.filename)

            # Check if it's a PDF and perform OCR if needed
            if file.filename.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
                if text:
                    extracted_texts.append(f"Content from {file.filename}:\n{text}")
                else:
                    extracted_texts.append(f"Failed to extract text from {file.filename}")

    # Get form inputs
    question_types = request.form.getlist('question_types')
    exam_length = request.form.get('exam_length')
    additional_requests = request.form.get('additional_requests', '')

    # Create a prompt for the AI
    prompt = f"""
    You are a teaching assistant. Create a practice exam with the following parameters:
    - Question Types: {', '.join(question_types)}
    - Exam Length: {exam_length}
    - Additional Requests: {additional_requests}
    """
    if extracted_texts:
        prompt += "\n\nBase the content on these extracted texts:\n" + "\n".join(extracted_texts)

    # Call the OpenAI API
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in creating exams."},
                {"role": "user", "content": prompt},
            ]
        )
        generated_exam = response.choices[0].message.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Create an HTML response for the generated exam
    html_response = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Generated Exam</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                line-height: 1.6;
            }}
            pre {{
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                padding: 10px;
                overflow-x: auto;
            }}
        </style>
    </head>
    <body>
        <h1>Generated Exam</h1>
        <pre>{generated_exam}</pre>
    </body>
    </html>
    """

    # Return the HTML as a response
    response = make_response(html_response)
    response.headers["Content-Type"] = "text/html"
    return response

if __name__ == '__main__':
    app.run(debug=True)
