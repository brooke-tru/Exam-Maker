# Exam-Maker


## Required Dependencies

To run the program properly, the following needs to be done first

### Pip installs
```
pip install Flask openai pdf2image pytesseract Pillow
```

### Poppler Installation (Windows)
- Download Poppler binaries from the [Poppler for Windows GitHub page](https://github.com/oschwartz10612/poppler-windows/releases).
- Save where the bin file is in Poppler download
- Put the filepath into system's *PATH*
- Put the filepath in 'poppler_path' in app.py

### Tesseract (OCR) Installation
- **Windows**: Download the Tesseract installer from [Tesseract's GitHub page](https://github.com/tesseract-ocr/tesseract). After installation, add it to your system's PATH.
- **macOS**: Install Tesseract via Homebrew:
```
brew install tesseract
```
 - **Linux**: Install Tesseract using your package manager
```
sudo apt install tesseract-ocr
```
### OpenAI Key
 - Sign up for an OpenAI API key [here](https://beta.openai.com/signup/) if you haven't already
 - Add your OpenAI API key as an environment variable 'OPENAI_API_KEY'

## Running the application
Clone the repository and run the *app.py* file 

## Usage

### Step 1: Upload PDFs
On the homepage, you can upload PDF files by clicking the "Choose Files" button. The app supports both text-based and image-based (scanned) PDFs.

- **Text-based PDFs**: Text is directly extracted from the PDF.
- **Scanned PDFs**: OCR is used to extract the text.

### Step 2: Customize Your Exam
After uploading the PDFs, you can customize the following parameters:

1. **Question Types**: Select from multiple types (e.g., multiple choice, true/false, short answer).
2. **Exam Length**: Define approximately how long you want the exam
3. **Additional Requests**: Add any other specific instructions or requirements

### Step 3: Generate the Exam
Click the "Generate Exam" button. The app will process the PDFs, extract the text, and use OpenAI’s GPT-4o-mini to generate a customized exam based on the content. The generated exam will be displayed in a new tab.

### Step 4: Review and Save the Exam
You can review the generated exam and save it by copying the content or saving it as a PDF.