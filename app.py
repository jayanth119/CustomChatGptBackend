from fastapi import FastAPI , APIRouter , HTTPException  , Form 
from fastapi import File , UploadFile
from dotenv import load_dotenv
import os
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
import base64
import pandas as pd
from typing import Optional
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request

load_dotenv()


app = FastAPI()
apiKey = os.getenv('GOOGLE_GEMININI_API_KEY')
genai.configure(api_key=apiKey)
model = genai.GenerativeModel("gemini-1.5-flash")
router = APIRouter()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def read_root():
    return {"Hello": "World"}

SUPPORTED_FILE_TYPES = ["pdf", "docx", "txt", "png", "jpg", "jpeg", "xlsx", "xls"]

@router.post("/api/gen-query")
async def generate_content(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")
    if not prompt:
        raise HTTPException(status_code=422, detail="Prompt is required")
    prompt = f"Check if the given prompt is a general query ,  donot say yes or no  and donot mention it is general query or not . If yes, answer it; otherwise, do not answer: {prompt}"
    response = model.generate_content(prompt)
    return {"status": "success", "response": response.text}

@router.post("/api/code-genx")
async def generate_code(request: Request):
    body = await request.json()
    prop = body.get("prompt", "")
    prompt = f"Check if the given prompt is a programming-related question ,donot say yes or no  and donot mention it is  coding content  or not . If yes, generate code; otherwise, indicate it is not programming-related: {prop}"
    response = model.generate_content(prompt)
    return {"status": "success", "response": response.text}

@router.post("/api/textsummarize/")
async def text_summarize(prompt: str, lines: int):
    body = await request.json()
    prop = body.get("prompt", "")
    lines = body.get("lines" , "")
    prompt = f"Summarize the text into {lines} lines if it is long; otherwise, do not summarize: {prop}"
    response = model.generate_content(prompt)
    return {"status": "success", "response": response.text}

@router.post("/api/doc-sumex")
async def document_summarize(
    file: UploadFile = File(...), 
    prompt: str = Form(None)
):
    documenttype = file.filename.split('.')[-1].lower()
    if documenttype not in SUPPORTED_FILE_TYPES:
        return {"status": "error", "message": "Invalid file format"}

    text = ""
    try:
        if documenttype == "pdf":
            reader = PdfReader(file.file)
            for page in reader.pages:
                text += page.extract_text()
        elif documenttype == "docx":
            document = Document(file.file)
            for para in document.paragraphs:
                text += para.text
        elif documenttype == "txt":
            text = await file.read().decode("utf-8")
        elif documenttype in ['png', 'jpg', 'jpeg']:
            image_content = await file.read()
            encoded_image = base64.b64encode(image_content).decode('utf-8')
            image_prompt = prompt if prompt else "Describe the image"
            response = model.generate_content([{
                'mime_type': f'image/{documenttype}',
                'data': encoded_image
            }, image_prompt])
            return {"status": "success", "response": response.text}
        elif documenttype in ['xlsx', 'xls']:
            excel_content = await file.read()
            excel_df = pd.read_excel(BytesIO(excel_content), sheet_name=None)
            for sheet_name, sheet_df in excel_df.items():
                text += sheet_df.to_string(index=False)
        
       
        if prompt:
            text = f"{prompt}\n{text}"

        response = model.generate_content(text)
        return {"status": "success", "response": response.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/api/web-intx")
async def web_content(url: str):
    try:
        if not Web().is_valid_url(url):
            return {"status": "error", "message": "Invalid URL"}
        content = Web().getContent(url)
        response = model.generate_content(content)
        return {"status": "success", "response": response.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}

app.include_router(router)

