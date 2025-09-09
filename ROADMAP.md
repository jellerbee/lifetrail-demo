# LifeTrail Roadmap

This roadmap outlines the current goals and future direction of the **LifeTrail** project.  
LifeTrail is an open-source, AI-powered application that organizes uploaded images and text into a timeline of meaningful life moments.  

---

## 🎯 Project Goals
- Provide a hands-on example of building a full-stack AI-powered application.
- Serve as a learning playground for developers and product managers working with AI/ML.
- Build a community of contributors experimenting with real-world AI integrations.

---

## ✅ Current (MVP)
- **Frontend (Next.js + Tailwind)**  
  - Multi-file upload (images, text, docs)  
  - Flagging of "key moments"  
  - Basic dashboard & timeline view  

- **Backend (FastAPI)**  
  - File upload handling  
  - Metadata extraction (EXIF, timestamps, GPS)  
  - AI enrichment pipeline  
    - OpenAI (event inference, summarization)  
    - AWS Rekognition (faces, labels)  
    - AWS Textract (text extraction)  
    - LocationIQ (reverse geocoding)  
  - Firestore integration for metadata  
  - S3 integration for media files  

---

## 🚧 Near-Term (Next 1–2 months)
- Improved dashboard UI (search, sort, pagination, event detail view)  
- Unified “Story View” combining dashboard + timeline  
- Contributor-friendly issue templates, PR process ✅ (done!)  
- Basic unit tests for backend APIs  
- CI pipeline (linting + tests on PRs)  
- Docker setup for local dev (frontend + backend)  

---

## 🛠 Mid-Term (3–6 months)
- Mobile-friendly UI  
- AI pipeline enhancements  
  - Better image event inference prompts  
  - Audio transcription (Whisper)  
  - Document OCR improvements  
- Enhanced metadata (faces/emotions, relationships, contextual enrichment)  
- User authentication improvements (roles, privacy controls)  
- Cost monitoring for AI API usage  

---

## 🌐 Long-Term Vision
- Collaborative features (shared timelines, family contributions)  
- Export/import features (PDF/JSON)  
- Plugin architecture for AI modules  
- Historical enrichment: cross-link events with historical/cultural data  
- Marketplace for AI-enhanced “life stories” and add-ons  

---

## 🧑‍💻 How to Get Involved
- Browse open [Issues](../../issues) and look for the `good first issue` label.  
- Join [Discussions](../../discussions) to propose features or ask questions.  
- Submit PRs for bug fixes, documentation improvements, or features.  
- Share your experience in building/using AI features — even small contributions help!

---

✨ *This roadmap is a living document. It will evolve as the project grows and as the community contributes.*  
