from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from services.storage_service import StorageService
from services.runway_service import RunwayService
import os
import uuid
from typing import List, Optional, Dict
import json
import asyncio

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Video Generation System")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_VISION_KEY = os.getenv("AZURE_VISION_KEY")
AZURE_VISION_ENDPOINT = os.getenv("AZURE_VISION_ENDPOINT")

# Initialize services
storage_service = StorageService(AZURE_STORAGE_CONNECTION_STRING)
vision_client = ComputerVisionClient(
    endpoint=AZURE_VISION_ENDPOINT,
    credentials=AzureKeyCredential(AZURE_VISION_KEY)
)
runway_service = RunwayService()

# Store generation jobs
generation_jobs: Dict[str, Dict] = {}

@app.post("/upload")
async def upload_media(
    file: UploadFile = File(...),
    container_type: str = "media"
):
    """
    Upload media file (image or video) to Azure Blob Storage
    """
    try:
        # Read file content
        content = await file.read()
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Upload to Azure Blob Storage
        upload_result = await storage_service.upload_file(
            file_data=content,
            filename=unique_filename,
            container_type=container_type,
            metadata={
                "original_filename": file.filename,
                "content_type": file.content_type
            }
        )
        
        # If it's an image, analyze it with Computer Vision
        if file_extension.lower() in ['.jpg', '.jpeg', '.png']:
            image_analysis = vision_client.analyze_image_in_stream(
                content,
                visual_features=['Description', 'Tags', 'Categories']
            )
            return {
                **upload_result,
                "analysis": {
                    "description": image_analysis.description.captions[0].text if image_analysis.description.captions else None,
                    "tags": [tag.name for tag in image_analysis.tags],
                    "categories": [category.name for category in image_analysis.categories]
                }
            }
        
        return upload_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files")
async def list_files(
    container_type: str = "media",
    prefix: Optional[str] = None
):
    """
    List files in a container
    """
    try:
        files = await storage_service.list_files(container_type, prefix)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/{filename}")
async def delete_file(
    filename: str,
    container_type: str = "media"
):
    """
    Delete a file from storage
    """
    try:
        success = await storage_service.delete_file(filename, container_type)
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_video_generation(job_id: str, prompt: str, duration: int):
    """
    Background task to process video generation
    """
    try:
        # Update job status
        generation_jobs[job_id] = {
            "status": "processing",
            "progress": 0
        }
        
        # Generate video using RunwayML
        result = runway_service.generate_video(prompt, duration)
        
        # Update job status with result
        generation_jobs[job_id] = {
            "status": "completed",
            "video_url": result["video_url"],
            "job_id": result["job_id"]
        }
    except Exception as e:
        generation_jobs[job_id] = {
            "status": "failed",
            "error": str(e)
        }

@app.post("/generate-video")
async def generate_video(
    background_tasks: BackgroundTasks,
    prompt: str,
    duration: int = 4
):
    """
    Generate video based on text prompt
    """
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job status
        generation_jobs[job_id] = {
            "status": "queued",
            "progress": 0
        }
        
        # Start background task
        background_tasks.add_task(
            process_video_generation,
            job_id,
            prompt,
            duration
        )
        
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Video generation started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/video-status/{job_id}")
async def get_video_status(job_id: str):
    """
    Check status of video generation job
    """
    if job_id not in generation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return generation_jobs[job_id]

@app.get("/runway-credits")
def get_runway_credits():
    """
    Get remaining RunwayML API credits
    """
    try:
        credits = runway_service.get_credits()
        return credits
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 