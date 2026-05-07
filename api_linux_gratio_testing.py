import mimetypes
import os

import uvicorn
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sanitize_filename import sanitize


app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_GLB_FILENAME = "sample.glb"
SAMPLE_GLB_PATH = os.path.join(BASE_DIR, SAMPLE_GLB_FILENAME)
mimetypes.add_type("model/gltf-binary", ".glb")

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
        "status": "Mock TRELLIS Backend Running",
        "mode": "mock_glb_response",
    }


def get_public_base_url(request: Request):
    forwarded_host = request.headers.get("x-forwarded-host")
    forwarded_proto = request.headers.get("x-forwarded-proto", "https")

    if forwarded_host:
        return f"{forwarded_proto}://{forwarded_host}"

    return str(request.base_url).rstrip("/")


@app.get(f"/models/{SAMPLE_GLB_FILENAME}")
def get_sample_model():
    return FileResponse(
        path=SAMPLE_GLB_PATH,
        media_type="model/gltf-binary",
        filename=SAMPLE_GLB_FILENAME,
    )


# --- MOCK CONVERT ENDPOINT ---
@app.post("/convert")
async def convert_image(request: Request, file: UploadFile = File(...)):
    try:
        original_name = file.filename
        safe_name = sanitize(original_name)

        base_name, _ = os.path.splitext(safe_name)

        if not base_name:
            base_name = "output"

        # Read uploaded image just to simulate processing.
        await file.read()

        # Return a public URL, matching the real backend contract.
        # Native AR viewers need an HTTPS URL; blob/object URLs can drift or fail.
        public_base_url = get_public_base_url(request)
        return JSONResponse(
            content={
                "model_url": f"{public_base_url}/models/{SAMPLE_GLB_FILENAME}",
                "filename": f"{base_name}.glb",
                "mock": True,
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )
