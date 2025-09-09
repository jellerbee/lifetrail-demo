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
  - `create_timeline_narrative()` - GPT-4 Vision generates journalist-style narratives
  - `create_first_person_summary()` - Legacy first-person narrative generator (demo)
  - `generate_clarification_questions()` - Creates open-ended contextual questions
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
  - Single image upload form (text upload removed)
  - HEIC/HEIF preview with client-side conversion using heic2any
  - Auto-refresh timeline (3-second intervals for 2 minutes after upload)
  - Clickable date editing with native HTML date picker
  - Debug mode toggle via NEXT_PUBLIC_DEBUG environment variable
  - Clean timeline cards showing user caption first, then AI summary with sparkle icons
  - Interactive pulsing question marks for photos without captions
- `lib/api.ts` - API client with image upload, S3 proxy support, and debug truncate endpoint
- `layout.tsx` - Next.js App Router layout component

**Database**: Event table storing life moments with rich metadata, AI analysis results, and separate user_caption field.

**Key Data Flow**:
1. User uploads image (with optional caption) → POST /api/upload
2. Background processing extracts EXIF metadata, GPS coordinates, faces, labels, OCR text
3. AI generates journalist-style narrative using GPT-4 Vision with user profile context
4. For photos without captions: AI generates open-ended clarification questions
5. Event stored with processing status, AI results, user caption, and personalized summary
6. Frontend displays timeline with user captions first, then AI narratives with sparkle icons

## Environment Variables

Copy `.env.example` files to `.env` in both frontend and backend directories:

**Backend** (`backend/.env`):
- `DATABASE_URL` - Postgres connection string (uses sqlite for local dev)
- `OPENAI_API_KEY` - OpenAI API key for GPT-4 Vision analysis
- `ALLOWED_ORIGINS` - CORS origins (comma-separated)
- `AWS_ACCESS_KEY_ID` - AWS credentials for Rekognition, Textract, and S3
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_BUCKET_NAME` - S3 bucket name for image storage
- `AWS_REGION` - AWS region (default: us-east-1)
- `LOCATIONIQ_API_KEY` - LocationIQ API key for reverse geocoding GPS coordinates

**Frontend** (`frontend/.env`):
- `NEXT_PUBLIC_BACKEND_URL` - Backend API URL
- `NEXT_PUBLIC_DEBUG` - Enable debug features (true/false, requires rebuild for changes)

## Deployment

Configured for Render.com deployment via `render.yaml`:
- Dockerized services with custom service names for security
- Uses existing managed Postgres database (life_moments_db)
- Environment variables managed via Render environment groups
- Custom domain support for production URLs
- Automatic database migrations on backend startup
- SSR-compatible build process with browser API guards

## AI Integration

### Core AI Features
The application includes sophisticated AI analysis for creating personalized life moment narratives:

**User Profile Context** (`backend/app/settings.py`):
- Hardcoded demo profile: Alex Chen (32, San Francisco software engineer)
- Interests: hiking, photography, cooking, travel
- Relationships: partner Sam, pet Luna (cat)
- Used to personalize AI narratives and generate contextual questions

**Timeline Narratives** (`backend/app/ai.py`):
- `create_timeline_narrative()` - GPT-4 Vision analyzes images directly for contextual narratives
- Uses journalist-style third-person descriptions with user profile awareness
- Examples: "Alex stepped away from his desk for a lunchtime walk", "Alex and Sam enjoyed dinner at a neighborhood restaurant"
- Considers timing, location, weather, and user interests for smart context

**Interactive Questions** (`backend/app/ai.py`):
- `generate_clarification_questions()` - Generates up to 2 open-ended contextual questions
- Examples: "What special event is this?", "Who are you with in this photo?", "Where are you hiking?"
- Questions appear as pulsing blue buttons in the UI for photos without captions

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