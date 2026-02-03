from fastapi import FastAPI, UploadFile, File
from test import BusinessEngine # Assuming your class is in test.py
import os
import shutil
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your domain
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    # 1. Save uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 2. Run your Business Brain
        engine = BusinessEngine(temp_path)
        engine.load_data()
        engine.standardize_and_clean()
        engine.classify_columns()
        analysis = engine.run_analysis()
        
        # 3. Get the JSON report
        report = engine.generate_json_report(analysis)
        return json.loads(report)
    
    finally:
        # 4. Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)