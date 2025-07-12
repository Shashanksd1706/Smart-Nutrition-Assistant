from fastapi import FastAPI, UploadFile, File, Form, Depends
from .services.image_captioner import generate_caption_with_gemini
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .auth import auth_router, get_db
from .services.gpt_planner import generate_with_gemini
from .services.nutrition_lookup import get_nutrition_facts
from .services.image_captioner import generate_caption_with_gemini
from .services.voice_transcriber import convert_audio
from .utils.pdf_exporter import generate_pdf
from .models import MealHistory, User
from .database import SessionLocal
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import os

app = FastAPI()
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def get_current_user(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        return db.query(User).filter(User.username == username).first()
    except JWTError:
        return None

@app.post("/text")
async def text_meal_plan(token: str = Form(...), text: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        return {"error": "Unauthorized"}
    plan = generate_with_gemini(f"Suggest a meal plan for: {text}")
    history = MealHistory(input_text=text, meal_plan=plan, user_id=user.id)
    db.add(history)
    db.commit()
    return {"plan": plan}

@app.post("/history")
async def get_user_history(token: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        return {"error": "Unauthorized"}
    history = db.query(MealHistory).filter(MealHistory.user_id == user.id).all()
    return {"history": [{"input": h.input_text, "plan": h.meal_plan, "created_at": h.created_at} for h in history]}

@app.post("/nutrition")
async def nutrition_lookup(text: str = Form(...)):
    try:
        print(f"Nutrition lookup request for: '{text}'")
        facts = get_nutrition_facts(text)
        print(f"Nutrition facts result: {facts}")
        
        if not facts:
            return {"facts": [], "message": f"No nutrition information found for '{text}'"}
        
        return {"facts": facts}
    except Exception as e:
        print(f"Nutrition lookup error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Failed to fetch nutrition information: {str(e)}", "facts": []}

# Replace your existing /analyze-image endpoint in app.py with this:

@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        if not contents:
            return JSONResponse(status_code=400, content={"error": "Empty file"})
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            return JSONResponse(status_code=400, content={"error": "File must be an image"})
        
        # Use Gemini Vision to analyze the image
        result = generate_caption_with_gemini(contents)
        
        return {"food_items": result}
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to analyze image: {str(e)}"})

@app.post("/voice")
async def voice_transcription(file: UploadFile = File(...)):
    audio_path = convert_audio(file.file)
    transcript = "This is a placeholder. Use frontend speech API."
    plan = generate_with_gemini(f"Suggest meal plan for: {transcript}")
    return {"transcript": transcript, "plan": plan}

@app.post("/pdf")
async def export_pdf(text: str = Form(...)):
    filename = generate_pdf(text)
    return {"pdf_file": filename}