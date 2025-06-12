import os
import time
from runwayml import RunwayML
from dotenv import load_dotenv

class RunwayService:
    def __init__(self):
        load_dotenv()
        # Get API key from environment variable
        self.api_key = os.getenv("RUNWAYML_API_SECRET")
        if not self.api_key:
            raise ValueError("RUNWAYML_API_SECRET not found in environment variables")
        
        # Initialize client with API key
        self.client = RunwayML(api_key=self.api_key)
        
    def get_credits(self):
        """Get credit balance and available models from RunwayML."""
        try:
            account = self.client.organization.retrieve()
            return {
                "creditBalance": account.credit_balance,
                "tier": {
                    "maxMonthlyCreditSpend": account.tier.max_monthly_credit_spend,
                    "models": {
                        "gen4_turbo": {
                            "maxConcurrentGenerations": account.tier.models.gen4_turbo.max_concurrent_generations,
                            "maxDailyGenerations": account.tier.models.gen4_turbo.max_daily_generations
                        },
                        "upscale_v1": {
                            "maxConcurrentGenerations": account.tier.models.upscale_v1.max_concurrent_generations,
                            "maxDailyGenerations": account.tier.models.upscale_v1.max_daily_generations
                        },
                        "gen3a_turbo": {
                            "maxConcurrentGenerations": account.tier.models.gen3a_turbo.max_concurrent_generations,
                            "maxDailyGenerations": account.tier.models.gen3a_turbo.max_daily_generations
                        },
                        "gen4_image": {
                            "maxConcurrentGenerations": account.tier.models.gen4_image.max_concurrent_generations,
                            "maxDailyGenerations": account.tier.models.gen4_image.max_daily_generations
                        }
                    }
                },
                "usage": {
                    "models": {
                        "gen4_turbo": {
                            "dailyGenerations": account.usage.models.gen4_turbo.daily_generations
                        },
                        "upscale_v1": {
                            "dailyGenerations": account.usage.models.upscale_v1.daily_generations
                        },
                        "gen3a_turbo": {
                            "dailyGenerations": account.usage.models.gen3a_turbo.daily_generations
                        },
                        "gen4_image": {
                            "dailyGenerations": account.usage.models.gen4_image.daily_generations
                        }
                    }
                }
            }
        except Exception as e:
            raise Exception(f"Error getting credits: {str(e)}")

    def generate_video(self, prompt: str, duration: int = 4):
        """Generate a video from text using RunwayML's two-step process:
        1. Generate an image from text
        2. Generate a video from the image
        Input JSON: {prompt: "A beautiful sunset over the ocean with waves crashing on the shore"
        duration: 4}
        """
        try:
            print(f"[DEBUG] Starting video generation with prompt: {prompt}")
            
            # Step 1: Generate image from text
            print("[DEBUG] Step 1: Generating image from text...")
            image_task = self.client.text_to_image.create(
                model='gen4_image',
                prompt_text=prompt,
                ratio='1360:768'  # Using the exact ratio from the sample code
            )
            print(f"[DEBUG] Image generation task created with ID: {image_task.id}")
            
            # Poll for image generation completion
            print("[DEBUG] Polling for image generation completion...")
            while True:
                image_status = self.client.tasks.retrieve(image_task.id)
                print(f"[DEBUG] Image generation status: {image_status.status}")
                if image_status.status in ['completed', 'SUCCEEDED']:
                    print("[DEBUG] Image generation completed successfully")
                    break
                elif image_status.status in ['failed', 'FAILED']:
                    print(f"[DEBUG] Image generation failed: {image_status.error}")
                    raise Exception(f"Image generation failed: {image_status.error}")
                time.sleep(5)
            
            # Get the generated image URL
            print(f"[DEBUG] Task output: {image_status.output}")
            image_url = image_status.output[0] if isinstance(image_status.output, list) else image_status.output
            print(f"[DEBUG] Generated image URL: {image_url}")
            
            # Step 2: Generate video from image
            print("[DEBUG] Step 2: Generating video from image...")
            video_task = self.client.image_to_video.create(
                model='gen4_turbo',
                prompt_image=image_url,
                prompt_text=prompt,
                ratio='1280:720'  # Using the ratio from the sample code
            )
            print(f"[DEBUG] Video generation task created with ID: {video_task.id}")
            
            # Poll for video generation completion
            print("[DEBUG] Polling for video generation completion...")
            while True:
                video_status = self.client.tasks.retrieve(video_task.id)
                print(f"[DEBUG] Video generation status: {video_status.status}")
                if video_status.status in ['completed', 'SUCCEEDED']:
                    print("[DEBUG] Video generation completed successfully")
                    break
                elif video_status.status in ['failed', 'FAILED']:
                    print(f"[DEBUG] Video generation failed: {video_status.error}")
                    raise Exception(f"Video generation failed: {video_status.error}")
                time.sleep(5)
            
            # Get the generated video URL
            video_url = video_status.output[0] if isinstance(video_status.output, list) else video_status.output
            print(f"[DEBUG] Generated video URL: {video_url}")
            
            return {
                "job_id": video_task.id,
                "status": "completed",
                "video_url": video_url,
                "image_url": image_url
            }
        except Exception as e:
            print(f"[DEBUG] Error in generate_video: {str(e)}")
            raise Exception(f"Error generating video: {str(e)}")

    def get_video_status(self, job_id: str):
        """Get the status of a video generation job"""
        try:
            status = self.client.tasks.retrieve(job_id)
            return {
                "job_id": job_id,
                "status": status.status,
                "video_url": status.output.video_url if status.status == "completed" else None,
                "error": status.error if status.status == "failed" else None
            }
        except Exception as e:
            raise Exception(f"Error getting video status: {str(e)}") 