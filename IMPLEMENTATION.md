# AI Professor: Autonomous Educational Video Generator

## Overview

This system transforms the VidyaChitra codebase into a fully autonomous, multi-class, multi-subject "Professor" that generates and publishes educational videos to YouTube daily.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Professor System                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │  Curriculum  │───▶│   Lesson     │───▶│   YouTube    │   │
│  │   Planner    │    │  Generator   │    │   Uploader   │   │
│  │ curriculum.  │    │ run_ai_      │    │ youtube_     │   │
│  │ json         │    │ professor.py │    │ uploader.py  │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│         │                   │                   │            │
│         ▼                   ▼                   ▼            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │ State Track  │    │ Subject      │    │ GitHub       │   │
│  │ state.json   │    │ Personas     │    │ Actions      │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │     VidyaChitra Core          │
              │  - PDF Processing (Gemini)    │
              │  - Video Generation (Manim)   │
              │  - Audio Narration (TTS)      │
              │  - Question Generation        │
              └───────────────────────────────┘
```

## Files Created

| File | Purpose |
|------|---------|
| `run_ai_professor.py` | Main automation script |
| `youtube_uploader.py` | YouTube API integration |
| `curriculum.json` | Syllabus configuration |
| `state.json` | Progress tracking (auto-generated) |
| `backend/utils/subject_prompts.py` | Subject expert personas |
| `.github/workflows/ai_professor.yml` | CI/CD scheduler |

## Quick Start

### 1. Environment Setup

```bash
# Clone repository
git clone https://github.com/stealthwhizz/VidyaChitra.git
cd VidyaChitra

# Create .env file
cat > .env << EOF
GOOGLE_API_KEY=your_gemini_api_key_here
GOOGLE_CLOUD_BUCKET=optional_bucket_name
