# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (FastAPI)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=sqlite:///./local.db
uvicorn app.main:app --reload
```

### Frontend (Next.js)
```bash
cd frontend
npm install
export NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
npm run dev        # Development server
npm run build      # Production build
npm run start      # Production server
```

## Architecture

This is a full-stack Life Moments AI application with comprehensive image analysis and personalized AI narratives.

**Backend Structure** (`backend/app/`):
- `main.py` - FastAPI application with CORS middleware and main endpoints:
  - `POST /api/upload` - Processes image uploads (JPEG, PNG, HEIC/HEIF) with captions
  - `GET /api/events` - Returns recent events from database
  - `GET /api/image/{s3_key}` - Proxies images from S3 to avoid CORS issues
- `models.py` - SQLAlchemy Event model with fields: id, kind, source, summary, labels, processing_status, ai_results, heic_metadata, original_filename, photo_taken_at, created_at
- `schemas.py` - Pydantic models for request/response validation
- `db.py` - Database session management and SQLAlchemy setup with migrations
- `ai.py` - Advanced AI functions with user profile context:
  - `create_first_person_summary()` - Generates personalized first-person narratives
  - `generate_clarification_questions()` - Creates contextual questions for ambiguous photos
- `settings.py` - Application configuration with hardcoded user profile (Alex Chen demo data)
- `image_processor.py` - Comprehensive image analysis with AWS services:
  - Face detection (AWS Rekognition)
  - Object/scene labeling (AWS Rekognition) 
  - Text extraction (AWS Textract)
  - EXIF GPS coordinates and reverse geocoding
- `heic_processor.py` - HEIC/HEIF image processing with metadata extraction
- `s3.py` - AWS S3 integration for image storage

**Frontend Structure** (`frontend/app/`):
- `page.tsx` - Main React component with:
  - Tabbed interface (Text/Image upload)
  - Clean timeline cards with 3 elements: thumbnail, date, AI summary
  - Interactive pulsing question marks for photos without captions
  - HEIC file preview fallback
- `lib/api.ts` - API client with image upload and S3 proxy support
- `layout.tsx` - Next.js App Router layout component

**Database**: Event table storing life moments with rich metadata, AI analysis results, and first-person narratives.

**Key Data Flow**:
1. User uploads image (with optional caption) → POST /api/upload
2. Background processing extracts EXIF metadata, GPS coordinates, faces, labels, OCR text
3. AI generates first-person narrative using user profile context (Alex Chen - SF software engineer)
4. For photos without captions: AI generates clarification questions based on detected content
5. Event stored with processing status, AI results, and personalized summary
6. Frontend displays timeline with contextual narratives and interactive question UI

## Environment Variables

Copy `.env.example` files to `.env` in both frontend and backend directories:

**Backend** (`backend/.env`):
- `DATABASE_URL` - Postgres connection string (uses sqlite for local dev)
- `OPENAI_API_KEY` - OpenAI API key for event classification and advanced AI features
- `ALLOWED_ORIGINS` - CORS origins (comma-separated)
- `AWS_ACCESS_KEY_ID` - AWS credentials for Rekognition, Textract, and S3
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_BUCKET_NAME` - S3 bucket name for image storage
- `AWS_REGION` - AWS region (default: us-east-1)
- `LOCATIONIQ_API_KEY` - LocationIQ API key for reverse geocoding GPS coordinates

**Frontend** (`frontend/.env`):
- `NEXT_PUBLIC_BACKEND_URL` - Backend API URL

## Deployment

Configured for Render.com deployment via `render.yaml`:
- Dockerized services for both frontend and backend
- Managed Postgres database
- Automatic service discovery between frontend/backend

## AI Integration

### Core AI Features
The application includes sophisticated AI analysis for creating personalized life moment narratives:

**User Profile Context** (`backend/app/settings.py`):
- Hardcoded demo profile: Alex Chen (32, San Francisco software engineer)
- Interests: hiking, photography, cooking, travel
- Relationships: partner Sam, pet Luna (cat)
- Used to personalize AI narratives and generate contextual questions

**First-Person Narratives** (`backend/app/ai.py`):
- `create_first_person_summary()` - Creates personalized stories from image analysis
- Uses user profile, location data, detected objects, and face information
- Examples: "My happy place - away from the screen" (hiking context), "Trip to Austin - good to get away from San Francisco" (travel context)

**Interactive Questions** (`backend/app/ai.py`):
- `generate_clarification_questions()` - Generates up to 2 contextual questions for photos without captions  
- Examples: "Is this with Sam?" (2 faces detected), "Are you visiting Austin for work or pleasure?" (travel detected)
- Questions appear as pulsing blue buttons in the UI

**AWS Services Integration**:
- **Rekognition**: Face detection and object/scene labeling
- **Textract**: OCR text extraction from images
- **S3**: Secure image storage with proxy serving
- **LocationIQ**: Reverse geocoding for GPS coordinates

**Image Processing Pipeline**:
1. HEIC/HEIF conversion and metadata extraction
2. EXIF data parsing (GPS, timestamps, camera settings)
3. AWS analysis (faces, labels, text)
4. Profile-aware narrative generation
5. Contextual question generation for ambiguous photos

### Demo User Profile
The system includes a hardcoded user profile for demonstration:
```python
{
    "name": "Alex Chen",
    "birth_date": "1992-03-15", 
    "age": 32,
    "city": "San Francisco",
    "state": "California",
    "occupation": "Software Engineer",
    "interests": ["hiking", "photography", "cooking", "travel"],
    "relationships": {
        "partner": "Sam",
        "pets": ["Luna (cat)"]
    }
}
```

This profile enables location-aware narratives (travel vs. home), interest-based context (hiking → outdoor language), and relationship awareness (uses partner name in questions).