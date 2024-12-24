from fastapi import FastAPI , APIRouter , HTTPException 
from fastapi import File , UploadFile
from dotenv import load_dotenv
import os
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
import base64
# from docx import Document
import pandas as pd
load_dotenv()


app = FastAPI()
apiKey = os.getenv('GOOGLE_GEMININI_API_KEY')
genai.configure(api_key=apiKey)
model = genai.GenerativeModel("gemini-1.5-flash")
router = APIRouter()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@router.post("/api/generatecontent/")
def generate_content(prompt: str):
    prompt = f" check given prompt is  general queries or not if it is general queries  then answering general queries  or else do not answering  the question  : {prompt}"
    response = model.generate_content(prompt)
    print(response)
    return {"response": response.text}

@router.post("/api/generatecode/")
def generate_code(prompt: str):
    prompt = f" check given prompt is programming related question or not if it is programming question then generate code for this or else do not generate code and specifies it is not programming question : {prompt}"
    response = model.generate_content(prompt)
    return {"response": response.text}

@router.post("/api/textsummerize/")
def text_summerize(prompt: str , lines : int):
    prompt =f' if it is large text then summerize the  text in { lines } other wise do not summerize  : {prompt}'
    response = model.generate_content(prompt)
    return {"response": response.text}

SUPPORTED_FILE_TYPES = ["pdf", "docx", "txt" , "png" , "jpg" , "jpeg" , "xlsx" , "xls"]

@router.post('/api/documentsummarize/')
async def document_summarize(file: UploadFile = File(...)):
    documenttype = file.filename.split('.')[-1].lower()

    if documenttype not in SUPPORTED_FILE_TYPES:
        return {"response": "Invalid file format"}
    text = ""
    if documenttype == "pdf":
        reader = PdfReader(file.file)  
        for page in reader.pages:
            text += page.extract_text()    
    elif documenttype == "docx":
        document = Document(file.file)
        for para in document.paragraphs:
            text += para.text
    elif documenttype == "txt":
        text = file.file.read().decode("utf-8")
    elif documenttype in ['png', 'jpg', 'jpeg']:
        image_content = await file.read() 
        encoded_image = base64.b64encode(image_content).decode('utf-8')
        prompt = "Describe the image"
        
        response = model.generate_content([{
            'mime_type': f'image/{documenttype}', 
            'data': encoded_image
        }, prompt])
        return {"response": response.text}
    elif documenttype == ['xlsx' , 'xls']:
        excel_content = await file.read() 
        excel_df = pd.read_excel(BytesIO(excel_content), sheet_name=None)  
        for sheet_name, sheet_df in excel_df.items():
            text += sheet_df.to_string(index=False)
        
    response = model.generate_content(text)

    return {"response": response.text}

app.include_router(router)