# This is a dummy API server for translation services for testing purposes.
# To run this server:
# $ pip3 install -r requirements.txt
# $ uvicorn translate_api:app --reload 

# You must set up dptran to use this API server:
# $ dptran api -t http://localhost:8000/pro/v2/translate
# $ dptran api -u http://localhost:8000/pro/v2/usage
# $ dptran api -l http://localhost:8000/pro/v2/languages

from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import llm_translate

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Access Successful"}

class TranslationResponseText(BaseModel):
    text: str

class TranslationResponse(BaseModel):
    translations: list[TranslationResponseText]

class TranslationDummyData(BaseModel):
    source_lang: str
    target_lang: str
    request: str
    reponse: str

LangCodes = {
    "AR": "Arabic",
    "BG": "Bulgarian",
    "CS": "Czech",
    "DA": "Danish",
    "DE": "German",
    "EL": "Greek",
    "EN": "English",
    "EN-GB": "English (British)",
    "EN-US": "English (American)",
    "ES": "Spanish",
    "ET": "Estonian",
    "FI": "Finnish",
    "FR": "French",
    "HU": "Hungarian",
    "ID": "Indonesian",
    "IT": "Italian",
    "JA": "Japanese",
    "KO": "Korean",
    "LT": "Lithuanian",
    "LV": "Latvian",
    "NB": "Norwegian",
    "NL": "Dutch",
    "PL": "Polish",
    "PT": "Portuguese",
    "PT-BR": "Portuguese (Brazilian)",
    "PT-PT": "Portuguese (European)",
    "RO": "Romanian",
    "RU": "Russian",
    "SK": "Slovak",
    "SL": "Slovenian",
    "SV": "Swedish",
    "TR": "Turkish",
    "UK": "Ukrainian",
    "ZH": "Chinese (simplified)",
    "ZH-HANS": "Chinese (simplified)",
    "ZH-HANT": "Chinese (traditional)"
}

def get_lang_code(lang: str) -> str:
    lang = lang.lower()
    for code, name in LangCodes.items():
        if lang in code.lower():
            return name
    return None

def translate_texts(source_lang: str, target_lang: str, texts: List[str]) -> JSONResponse:
    source_lang = source_lang.lower() if source_lang else None
    target_lang = target_lang.lower()
    
    # convert to lang codes
    source_lang = get_lang_code(source_lang) if source_lang else None
    target_lang = get_lang_code(target_lang)
    if not target_lang:
        return JSONResponse(
            content={"error": "Invalid target language code."},
            status_code=400
        )

    # prepare langchain
    chain = llm_translate.init_langchain("llama3.1")

    # Simulate translation by looking up dummy data
    results = []
    answers = llm_translate.translate_text(
        chain=chain,
        texts=texts,
        source_lang=source_lang,
        target_lang=target_lang
    )
    print(f"Query: {texts} Source: {source_lang}, Target: {target_lang}\n=> Answers: {answers}")
    for answer in answers:
        results.append({"text": answer})
    
    return JSONResponse(content={"translations": results})

def usage_response(character_count: int, character_limit: int, type: str) -> JSONResponse:
    return JSONResponse(
        content={
            "character_count": character_count,
            "character_limit": 1000000000000,  # DeepL Pro API has no character limit, but the API returns a character limit of 1000000000000 characters as a default value.
        }
    )

def languages_response(type: str) -> JSONResponse:
    content = []
    if type not in ["source", "target"]:
        return JSONResponse(
            content={
                "error": "Invalid type. Must be 'source' or 'target'."
            },
            status_code=400
        )
    
    for code, name in LangCodes.items():
        content.append({
            "language": code,
            "name": name
        })

    return JSONResponse(
        content=content,
    )

@app.post("/free/v2/translate")
async def translate_for_free(auth_key: str = Form(...), target_lang: str = Form(...), texts: List[str] = Form(...), source_lang: Optional[str] = Form(None)):
    print(f"Received request: auth_key={auth_key}, target_lang={target_lang}, texts={texts}, source_lang={source_lang}")
    if auth_key == "":
        return JSONResponse(content={"error": "auth_key is required"}, status_code=400)
    return translate_texts(source_lang, target_lang, texts)

@app.post("/pro/v2/translate")
async def translate_for_pro(auth_key: str = Form(...), target_lang: str = Form(...), text: List[str] = Form(...), source_lang: Optional[str] = Form(None)):
    print(f"Received request: auth_key={auth_key}, target_lang={target_lang}, source_lang={source_lang}, text={text}")
    if auth_key == "":
        return JSONResponse(content={"error": "auth_key is required"}, status_code=400)
    return translate_texts(source_lang, target_lang, text)

@app.post("/free/v2/usage")
async def usage_for_free(auth_key: str = Form(...)):
    print(f"Received request: auth_key={auth_key}")
    if auth_key == "":
        return JSONResponse(content={"error": "auth_key is required"}, status_code=400)
    return usage_response(
        character_count=1000,
        character_limit=1000000,
        type="free"
    )

@app.post("/pro/v2/usage")
async def usage_for_pro(auth_key: str = Form(...)):
    print(f"Received request: auth_key={auth_key}")
    if auth_key == "":
        return JSONResponse(content={"error": "auth_key is required"}, status_code=400)
    return usage_response(
        character_count=10000,
        character_limit=1000000000000,
        type="pro"
    )

class LanguagesResponseElement(BaseModel):
    language: str
    name: str

@app.post("/free/v2/languages")
async def languages_for_free(type: str = Form(...), auth_key: str = Form(...)):
    print(f"Received request: type={type}, auth_key={auth_key}")
    if auth_key == "":
        return JSONResponse(content={"error": "auth_key is required"}, status_code=400)
    return languages_response(type)

@app.post("/pro/v2/languages")
async def languages_for_pro(type: str = Form(...), auth_key: str = Form(...)):
    print(f"Received request: type={type}, auth_key={auth_key}")
    if auth_key == "":
        return JSONResponse(content={"error": "auth_key is required"}, status_code=400)
    return languages_response(type)
