Brooke Truong, Dante Testini \
LIGN 167 Final Project Write-Up \
&nbsp;&nbsp;&nbsp;&nbsp; The first step of creating the application was to imagine the UI.  We had ideas for the customization of the exams that the application could generate. 
As you can see, we thought about including different question types, varying exam lengths, and additional requests from the user. This process was simple and straightforward until we tried to run the application. 
The first issue that we encountered was not being able to read the files that were in PDF format. This is where we learned that files cannot be directly uploaded to GPT via an API key. 
We still wanted to maintain the functionality of the user uploading PDFs of any sort, whether it be typed or handwritten information. 
So, we decided to utilize Optical Character Recognition (OCR) to solve this problem. We used 2 different 3rd party tools that helped with this process. 
The first tool we went with is pdf2image, which, alongside Poppler,  converts the pdf to images. The second tool we use is Tesseract OCR which is needed for extracting text from the images. 
By going through this process, we were able to read in files. A small issue that we noticed when going about this method was storage. 
The application added the uploaded files to the working tree, but we didn’t want that. So, we told it to delete the uploads after reading them. Our first instance of the application was really simple.
After filling out the customizations, the user would hit generate. The result would be a new tab in the browser that displayed a full exam in simple text format without an answer key yet. \
&nbsp;&nbsp;&nbsp;&nbsp; After some feedback from Professor Bergen, we decided that it was a great idea for our application to create a question-by-question exam instead of a full one all at once. 
 In order to achieve this, we needed to change up the UI and a bit of the backend. 
 We accomplished this by forcing the output of GPT to be a JSON object. 
 By storing each question and answer in pairs, our code can just loop through those pairs and output one pair at a time.  When a user gets to the last question, they have the option to see the full exam and answer sheet with the click of a button. \
&nbsp;&nbsp;&nbsp;&nbsp; Overall, we have implemented a practice exam maker that goes through the exam question by question, controlled by the specifications that are inputted by the user. Despite many hiccups along the way, we found creative solutions to deliver on this final project. We learned how to integrate LLMs into a working application that is able to solve a problem that many students and professors have. 
	
	
	




