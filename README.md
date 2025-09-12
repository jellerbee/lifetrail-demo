# LifeTrail AI

A full-stack demo AI application for capturing and analyzing moments in time through AI-powered image processing. Features advanced HEIC/HEIF support, GPT-4 Vision analysis, and personalized narrative generation.

---

## Contribute and Shape the Project

This project started as a weekend demo — but we are going to keep building on it. I’m looking for smart, entrepeneurial developers who want to **learn, teach, and build together**.  

Why contribute?  
- **Grow your skills** by working with a real multimodal AI pipeline.  
- **Bring your ideas** — the core pattern (images → metadata → narrative) can be applied to countless real-world problems.  
- **Shape the future** — your contributions can directly influence where this project goes next.  

Check out the [Contributing Guide](CONTRIBUTING.md) to get started, open an issue with your ideas, or fork the repo and submit a PR.  

Let’s see what this can grow into — together.  

---


## Quick Start (Local Development)

### Prerequisites
- **Docker** and **Docker Compose** installed on your system
- **Git** for cloning the repository
- API keys for external services (see Environment Setup below)

### Run Locally
1. **Clone the repository**:
   ```bash
   git clone https://github.com/jellerbee/lifetrail-demo.git
   cd lifemoments-demo
   ```

2. **Set up environment files**:
   ```bash
   # Copy example files
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   
   # Edit with your API keys
   nano backend/.env  # Add your OPENAI_API_KEY, AWS credentials, etc.
   nano frontend/.env # Set NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   ```

3. **Start with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Database: PostgreSQL on localhost:5432

5. **Upload Images**: Start uploading photos with optional captions to see AI analysis in action!

## Deploy to Render
If you want to deploy to render follow these steps: 

### Production Deployment Steps

1. **Deploy to Render**: Connect your forked repository and auto-detect `render.yaml`

2. **Create Environment Groups** in Render Dashboard (recommended):
   - Backend group: `OPENAI_API_KEY`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_BUCKET_NAME`, `LOCATIONIQ_API_KEY`, `ALLOWED_ORIGINS`
   - Frontend group: `NEXT_PUBLIC_BACKEND_URL`
   - Apply groups to services after deployment

3. **Service Configuration**:
   - Custom service names in `render.yaml` for security
   - Uses existing database (no new DB creation needed)
   - Set `NEXT_PUBLIC_DEBUG=false` for production

4. **Optional**: Configure custom domain for professional URLs

5. **Go Live**: Visit your deployed frontend and start building your AI-powered photo timeline!

### Alternative: Manual Development Setup

If you prefer running without Docker, you can set up each service manually:

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
- **Image Upload**: Supports JPEG, PNG, HEIC/HEIF formats with client-side preview conversion
- **AI Narratives**: GPT-4 Vision generates journalist-style timeline descriptions
- **Smart Questions**: AI asks open-ended contextual questions for photos without captions
- **Date Management**: Click dates to edit photo timestamps with native date picker
- **Auto-refresh**: Timeline updates automatically for 2 minutes after uploads (3-second intervals)
- **Caption Priority**: User captions displayed first, AI summaries below with sparkle icons

### Advanced Features
- **HEIC Processing**: Full metadata extraction including GPS and timestamps
- **User Profiles**: Personalized narratives based on user context (demo: Alex Chen profile)
- **Location Awareness**: Reverse geocoding for travel vs. home context
- **Face Recognition**: AWS Rekognition for people identification
- **Debug Mode**: Toggle `NEXT_PUBLIC_DEBUG=true` for detailed technical information

### Data Pipeline
1. **Upload**: Image processed and stored in S3 with HEIC conversion
2. **Analysis**: EXIF metadata extraction, GPS coordinates, face/object detection, OCR text
3. **AI Processing**: GPT-4 Vision analyzes images directly for contextual narratives
4. **Database**: Events stored with separate user_caption and AI summary fields
5. **Timeline**: Real-time display prioritizing user captions, then AI content with sparkle icons

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
- **HEIC conversion** happens server-side (upload) and client-side (preview) with SSR compatibility
- **Auto-refresh** activates for 2 minutes after upload (3-second intervals)
- **Debug mode** shows technical details, AI results, and truncate functionality
- **User profile** is hardcoded for demo (Alex Chen, SF software engineer)
- **Environment groups** recommended for managing secrets in production
- **Custom domains** supported for professional deployment URLs
- **Existing database reuse** prevents data loss during redeployments

## Security Features

- **Custom service names** in `render.yaml` for non-obvious URLs
- **Environment groups** keep API keys out of public repository
- **CORS configuration** restricts frontend access to authorized domains
- **S3 proxy serving** avoids exposing S3 bucket URLs directly

---

