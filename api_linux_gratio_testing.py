import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sanitize_filename import sanitize
import uvicorn

app = FastAPI()

# Path to your sample GLB file
SAMPLE_GLB_PATH = "sample.glb"

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "✅ Mock TRELLIS Backend Running",
        "mode": "mock_glb_response"
    }

# --- MOCK CONVERT ENDPOINT ---
@app.post("/convert")
async def convert_image(file: UploadFile = File(...)):
    try:
        original_name = file.filename
        safe_name = sanitize(original_name)

        base_name, _ = os.path.splitext(safe_name)

        if not base_name:
            base_name = "output"

        # OPTIONAL:
        # Read uploaded image just to simulate processing
        await file.read()

        # Return sample GLB
        return FileResponse(
            path=SAMPLE_GLB_PATH,
            media_type="model/gltf-binary",
            filename=f"{base_name}.glb"
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)