from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import shutil
import os
import threading
import ai_process
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RESULT_FOLDER = "results"


#upload video to local folder & run the ai process
@app.post("/upload/")
async def upload_video(file: UploadFile = File(...)):
    file_path = f"videos/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    threading.Thread(target=ai_process.run_ai_processing, args=(file_path,)).start()

    return {"filename": file.filename, "message": "Video uploaded successfully"}

#get list video
@app.get("/videos/")
async def list_videos():
    return {"videos": os.listdir("videos")}

#get video by name
@app.get("/videos/{filename}")
async def get_video(filename: str):
    video_path = f"videos/{filename}"
    return FileResponse(video_path, media_type="video/*")

#delete video by name
@app.delete("/videos/{filename}")
async def delete_video(filename: str):
    video_path = f"videos/{filename}"

    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video name not found")

    os.remove(video_path)
    return {"message": f"'{filename}' deleted successfully"}

#Fetch video metadata after processing
@app.get("/videos/{filename}/metadata")
async def get_video_metadata(filename: str):

    metadata_file = os.path.join(RESULT_FOLDER, f"{filename}.json")

    if not os.path.exists(metadata_file):
        return {"error": "Metadata not found. Processing may still be ongoing."}

    with open(metadata_file, "r") as f:
        metadata = json.load(f)

    return metadata
