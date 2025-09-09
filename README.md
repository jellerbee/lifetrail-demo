# Life Moments AI

A comprehensive full-stack application for capturing and analyzing life moments through AI-powered image processing. Features advanced HEIC/HEIF support, GPT-4 Vision analysis, and personalized narrative generation.

## Quick Start

1. **Deploy to Render**: Connect repository and auto-detect `render.yaml`
2. **Configure Environment Variables** in Render Dashboard:
   - Backend: Set `OPENAI_API_KEY`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_BUCKET_NAME`, `LOCATIONIQ_API_KEY`, `ALLOWED_ORIGINS`
   - Frontend: Set `NEXT_PUBLIC_BACKEND_URL`, `NEXT_PUBLIC_DEBUG=false`
3. **Customize service names** in `render.yaml` for security (URLs will be `https://your-service-name.onrender.com`)
4. **Wait for deployment**: Both services and managed database will provision automatically
5. **Upload Images**: Visit frontend URL and upload photos (including HEIC files) with optional captions

## Local Development

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=sqlite:///./local.db
export OPENAI_API_KEY=your_openai_key
export AWS_ACCESS_KEY_ID=your_aws_key
export AWS_SECRET_ACCESS_KEY=your_aws_secret
export AWS_BUCKET_NAME=your_s3_bucket
export LOCATIONIQ_API_KEY=your_locationiq_key
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
export NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
export NEXT_PUBLIC_DEBUG=true  # Enable debug features
npm run dev
```

## Architecture

- **Backend**: FastAPI with comprehensive image processing pipeline
- **Frontend**: Next.js with HEIC support and smart auto-refresh
- **Database**: PostgreSQL with automatic migrations
- **AI Integration**: 
  - **GPT-4 Vision**: Direct image analysis and narrative generation
  - **AWS Rekognition**: Face detection and object labeling
  - **AWS Textract**: OCR text extraction from images
- **Storage**: AWS S3 with proxy serving to avoid CORS issues
- **Image Processing**: HEIC/HEIF conversion and metadata extraction


## Features

### Core Functionality
- **Image Upload**: Supports JPEG, PNG, HEIC/HEIF formats with real-time preview
- **AI Narratives**: GPT-4 Vision generates personalized timeline descriptions
- **Smart Questions**: AI asks contextual clarification questions for photos without captions
- **Date Management**: Click dates to edit photo timestamps
- **Auto-refresh**: Timeline updates automatically after uploads

### Advanced Features
- **HEIC Processing**: Full metadata extraction including GPS and timestamps
- **User Profiles**: Personalized narratives based on user context (demo: Alex Chen profile)
- **Location Awareness**: Reverse geocoding for travel vs. home context
- **Face Recognition**: AWS Rekognition for people identification
- **Debug Mode**: Toggle `NEXT_PUBLIC_DEBUG=true` for detailed technical information

### Data Pipeline
1. **Upload**: Image processed and stored in S3
2. **Analysis**: EXIF metadata extraction, GPS coordinates, face/object detection
3. **AI Processing**: GPT-4 Vision creates contextual narrative using user profile
4. **Timeline**: Real-time display with user captions and AI-generated descriptions

## Environment Setup

**Backend Environment Variables:**
```bash
# Required
OPENAI_API_KEY=sk-...                    # GPT-4 Vision API access
AWS_ACCESS_KEY_ID=AKIA...                # AWS services (Rekognition, Textract, S3)
AWS_SECRET_ACCESS_KEY=...                # AWS secret key
AWS_BUCKET_NAME=your-s3-bucket           # S3 storage bucket
AWS_REGION=us-east-1                     # AWS region

# Optional
LOCATIONIQ_API_KEY=pk.xxx                # Reverse geocoding (LocationIQ)
DATABASE_URL=postgresql://...            # Auto-configured on Render
ALLOWED_ORIGINS=https://yourapp.com      # CORS configuration
```

**Frontend Environment Variables:**
```bash
NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com
NEXT_PUBLIC_DEBUG=false                  # Set to 'true' for debug features
```

## Development Notes

- **Database migrations** run automatically on startup
- **HEIC conversion** happens server-side (upload) and client-side (preview)
- **Auto-refresh** activates for 2 minutes after upload (3-second intervals)
- **Debug mode** shows technical details, AI results, and truncate functionality
- **User profile** is hardcoded for demo (Alex Chen, SF software engineer)

---

