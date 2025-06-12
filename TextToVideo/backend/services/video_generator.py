import os
import torch
from transformers import AutoProcessor, AutoModelForText2Image
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
import cv2
import numpy as np
from typing import List, Dict, Optional
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class VideoGenerator:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = AutoProcessor.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0")
        self.model = AutoModelForText2Image.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0")
        self.model.to(self.device)
        
        # Initialize API keys
        self.runwayml_api_key = os.getenv("RUNWAYML_API_KEY")
        self.pikalabs_api_key = os.getenv("PIKALABS_API_KEY")
        
    def generate_frames(self, prompt: str, num_frames: int = 60) -> List[np.ndarray]:
        """
        Generate video frames using Stable Diffusion
        """
        frames = []
        for _ in range(num_frames):
            inputs = self.processor(prompt, return_tensors="pt").to(self.device)
            with torch.no_grad():
                output = self.model.generate(**inputs)
            frame = output.images[0].numpy()
            frames.append(frame)
        return frames
    
    def create_video_from_frames(self, frames: List[np.ndarray], fps: int = 30) -> str:
        """
        Convert frames to video
        """
        height, width = frames[0].shape[:2]
        output_path = f"output_{hash(str(frames))}.mp4"
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        for frame in frames:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame)
        
        out.release()
        return output_path
    
    def add_audio(self, video_path: str, audio_path: str) -> str:
        """
        Add background audio to video
        """
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)
        
        # Loop audio if it's shorter than video
        if audio.duration < video.duration:
            audio = audio.loop(duration=video.duration)
        else:
            audio = audio.subclip(0, video.duration)
        
        # Combine video and audio
        final_video = video.set_audio(audio)
        output_path = f"final_{os.path.basename(video_path)}"
        final_video.write_videofile(output_path)
        
        return output_path
    
    def generate_with_runwayml(self, prompt: str, duration: int = 120) -> Dict:
        """
        Generate video using RunwayML API
        """
        headers = {
            "Authorization": f"Bearer {self.runwayml_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "prompt": prompt,
            "duration": duration,
            "model": "gen-2"
        }
        
        response = requests.post(
            "https://api.runwayml.com/v1/generate",
            headers=headers,
            json=data
        )
        
        return response.json()
    
    def generate_with_pikalabs(self, prompt: str, duration: int = 120) -> Dict:
        """
        Generate video using Pika Labs API
        """
        headers = {
            "Authorization": f"Bearer {self.pikalabs_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "prompt": prompt,
            "duration": duration,
            "model": "pika-1"
        }
        
        response = requests.post(
            "https://api.pikalabs.ai/v1/generate",
            headers=headers,
            json=data
        )
        
        return response.json()
    
    def process_source_media(self, media_paths: List[str]) -> List[np.ndarray]:
        """
        Process source media (images/videos) for video generation
        """
        processed_frames = []
        
        for path in media_paths:
            if path.lower().endswith(('.png', '.jpg', '.jpeg')):
                frame = cv2.imread(path)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                processed_frames.append(frame)
            elif path.lower().endswith(('.mp4', '.avi', '.mov')):
                cap = cv2.VideoCapture(path)
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    processed_frames.append(frame)
                cap.release()
        
        return processed_frames
    
    def select_best_video(self, video_paths: List[str], criteria: Optional[Dict] = None) -> str:
        """
        Select the best video based on quality metrics
        """
        if not criteria:
            criteria = {
                "resolution": 1080,
                "min_duration": 60,
                "max_duration": 180
            }
        
        best_video = None
        best_score = -1
        
        for path in video_paths:
            cap = cv2.VideoCapture(path)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps
            
            # Calculate quality score
            resolution_score = min(width, height) / criteria["resolution"]
            duration_score = 1.0 if criteria["min_duration"] <= duration <= criteria["max_duration"] else 0.5
            
            total_score = resolution_score * duration_score
            
            if total_score > best_score:
                best_score = total_score
                best_video = path
            
            cap.release()
        
        return best_video 