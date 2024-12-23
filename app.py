from fastapi import FastAPI , APIRouter
from dotenv import load_dotenv
import os
import google.generativeai as genai
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

app.include_router(router)