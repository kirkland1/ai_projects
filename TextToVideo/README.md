# AI Video Generation System

A comprehensive AI-powered video generation system built on Azure cloud infrastructure with Flutter frontend.

## Features

- User input processing (images/video snippets)
- Text-to-video generation with personalized prompts
- High-quality 10-seconds video output
- Multiple video generation and selection mechanism
- Integration with Azure AI services and HuggingFace models
- Pre-existing media asset library integration
- Background audio processing
- Video generation pipeline integration
- Computer vision and media processing capabilities

## Tech Stack

### Backend
- Azure Cloud Services
- Python
- PyTorch
- OpenCV
- FFmpeg
- Transformers
- Azure AI Services
- HuggingFace Models

### Frontend
- Flutter
- Dart

### Video Generation: This program has RunwayML. You can replace it with other ones with a little bit of efforts.
- RunwayML 
- Pika Labs
- Sora
- Kaiber

## Project Structure

```
.
├── backend/
│   ├── api/
│   ├── models/
│   ├── services/
│   └── utils/
├── frontend/
│   ├── lib/
│   ├── assets/
│   └── test/
├── media_assets/
├── pipelines/
└── docs/
```

## Setup Instructions

1. Clone the repository
2. Install backend dependencies:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Install frontend dependencies:
   ```bash
   cd frontend
   flutter pub get
   ```
4. Configure environment variables:
   - In the `backend` directory, copy the example environment file and fill in all required keys:
     ```bash
     cp .env.copy .env
     ```
   - Open `.env` in a text editor and fill in all the required secrets and keys.
   - **Important:** You must add your RunwayML API key to the `.env` file as `RUNWAYML_API_SECRET=your_runwayml_api_key`.
     - To get your RunwayML API key, go to [dev.runwayml.com](https://dev.runwayml.com/) and generate/copy your API key.
5. Configure Azure credentials
6. Get RunwayML API secret
7. Make a copy of .env.copy to .env
8. Add all the necessary keys and secrets, otherwise, the next step will fail
9. Run the application:
   ```bash
   # Backend: cd backend
   python main.py
   # Go to http://localhost:8000/docs for the APIs that this app supports, which you can test them out without the frontend
   
   # Frontend: cd frontend
   flutter run
   ```

## Azure Services Used

- Azure Cognitive Services
- Azure Video Indexer
- Azure Media Services
- Azure Blob Storage
- Azure Functions
- Azure App Service

## RUNWAY ML Used

- Go to dev.Runwayml.com to get the API key

## License

MIT License 