from fastapi import FastAPI, UploadFile, File
import shutil
from analyzer import analyze_text, analyze_image_with_ml
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # for now allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/analyze-text")
async def analyze_text_api(text: str):
    result = analyze_text(text)
    
    

    # Convert classification → fake/real
    if result.classification == "Safe":
        label = "real"
        confidence = max(0.8, 1 - result.risk_score / 100)

    elif result.classification == "Suspicious":
        label = "fake"
        confidence = min(0.8, result.risk_score / 100 + 0.3)

    elif result.classification == "High Risk":
        label = "fake"
        confidence = min(0.95, result.risk_score / 100 + 0.4)

    return {
        "prediction": label,
        "confidence": round(confidence, 3),
        "original_classification": result.classification,
        "risk_score": result.risk_score,
        "summary": result.summary
    }
    
@app.get("/")
def home():
    return {"message": "Backend is running 🚀"}

# Image analysis API
@app.post("/analyze-image")
async def analyze_image_api(file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with open(file_path, "rb") as f:
        image_data = f.read()

    result = analyze_image_with_ml(
        image_path=file_path,
        image_data=image_data,
        filename=file.filename,
        content_type=file.content_type
    )

    return result