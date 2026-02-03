from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from test import BusinessEngine
import os
import shutil
import json

app = FastAPI()

# Allow browser communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- THE KEY ADDITION ---
# This serves index.html at http://127.0.0.1:8000/static/index.html
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        engine = BusinessEngine(temp_path)
        engine.load_data()
        engine.standardize_and_clean()
        engine.classify_columns()
        analysis = engine.run_analysis()
        
        report = engine.generate_json_report(analysis)
        return json.loads(report)
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)