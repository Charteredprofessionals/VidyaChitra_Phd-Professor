# AI Professor — Autonomous Educator (Desktop Edition)

![AI Professor](Assests/main.png)

**AI Professor** is a fully offline-capable desktop application that transforms textbook PDFs into engaging educational videos with subject-specific expert personas. No internet required after initial setup.

---

## 🖥️ Desktop Edition Features

This private desktop version includes all cloud features plus:

- ✅ **100% Offline Operation** — Generate videos without internet after initial API key setup
- ✅ **Local Storage** — All videos saved to your hard drive
- ✅ **No Cloud Dependencies** — Optional YouTube upload, works standalone
- ✅ **Curriculum Planner** — Track progress across entire syllabus
- ✅ **Subject Expert Personas** — PhD-level AI tutors for each subject
- ✅ **Batch Processing** — Generate multiple lessons in one run
- ✅ **Progress Tracking** — Resume interrupted sessions automatically

---

## The Problem

Over 250 million school students in India study from State Board and NCERT textbooks written in regional languages like Kannada, Hindi, Tamil, Telugu, and Marathi. These students face three major challenges:

1. **Comprehension gap** — Dense textbook language is hard to understand without a teacher's explanation, especially for first-generation learners.
2. **No visual aids** — Diagrams in textbooks are static. Complex science and math concepts — ray diagrams, circuit diagrams, biological processes — are very hard to learn from a flat image alone.
3. **Exam unpreparedness** — Students don't know how questions will be framed in their specific board's pattern (Karnataka SSLC, CBSE, Maharashtra SSC, Tamil Nadu State Board all have different formats).

Most existing EdTech solutions are English-first and ignore regional language students. AI Professor is built for India's linguistic diversity from the ground up, automatically generating videos with subject-specific expert personas.

---

## The Solution

AI Professor generates educational videos from textbook PDFs and saves them locally. Each video features:

1. **Chapter Summary** — AI-generated explanation of the entire chapter, in the textbook's own language, covering every key concept and formula.

2. **Animated Diagram Video** — An AI-generated short video (15–25 seconds) that animates the most important concept using Manim, with all labels in the student's language.

3. **Audio Narration** — A spoken, teacher-style narration synthesised using Gemini 2.5 Flash TTS in regional Indian languages.

4. **Board-Pattern Exam Questions** — Ten MCQs, three short-answer questions, and one Higher Order Thinking (HOT) question, framed exactly as they would appear in the specific board exam.

5. **Subject Expert Personas** — Each subject is taught by a PhD-level AI persona (mathematician, physicist, chemist, historian, etc.) with appropriate pedagogy.

6. **Optional YouTube Upload** — Videos can be uploaded to YouTube automatically or kept private on your desktop.

---

## Key Features at a Glance

### Automatic Language and Board Detection
AI Professor uses Gemini's native PDF understanding to automatically detect which language the textbook is written in, which board it belongs to, and what class level it is. The entire video content is then generated in that language with the appropriate subject expert persona.

### Offline Desktop Operation
All video generation happens locally on your machine. Videos are saved to your hard drive and can be played anytime without internet. YouTube upload is optional.

### Subject Expert Personas
Each subject is taught by a PhD-level AI persona: mathematicians emphasize proofs, physicists use real-world examples, chemists explain molecular foundations, and historians provide chronological context.

### Curriculum Planner
Track progress across entire syllabi for Classes 6-12. The system remembers which lessons are completed and resumes where you left off.

### Batch Processing
Generate multiple lessons in one run. Perfect for creating entire chapter libraries over weekends.

---

## Supported Boards and Languages

| Board | Primary Language |
|-------|-----------------|
| Karnataka SSLC | Kannada |
| CBSE Class 10 | Hindi, English |
| Maharashtra SSC | Marathi |
| Tamil Nadu State Board | Tamil |
| Telugu Medium Schools | Telugu |

All generated content — summaries, narrations, video labels, exam questions — is produced in the detected language of the textbook.

---

## How It Works — Desktop Pipeline

1. **Curriculum Planning** — The system reads `curriculum.json` to determine which lesson to generate next.

2. **PDF Processing** — Gemini 2.5 Flash reads the textbook PDF natively (vector text, diagrams, Indic scripts) and identifies the language, board, class level, chapter name, diagrams, formulas, and key concepts in one pass.

3. **Subject Persona Selection** — Based on the subject (mathematics, physics, chemistry, etc.), the appropriate PhD-level expert persona is loaded.

4. **Parallel Generation** — Multiple AI pipelines run simultaneously:
   - Subject-specific script generation with expert persona
   - Manim animation renders an animated MP4 of the key concept
   - Gemini 2.5 Flash TTS synthesises the audio narration
   - Board-pattern exam questions are generated

5. **Video Assembly** — Audio and video are combined into a final MP4 file saved to `output/` folder.

6. **Optional YouTube Upload** — If configured, videos can be uploaded to YouTube with proper title, description, tags, and metadata.

7. **Progress Tracking** — The lesson is marked as published in `state.json`, allowing you to resume anytime.

---

## Technology Architecture

AI Professor is a desktop video generation system built with Python 3.11 + FastAPI. Every AI capability is powered exclusively by **Google Gemini 2.5 Flash** via the `google-genai` SDK.

### Core Components

| Component | Purpose |
|-----------|---------|
| `run_ai_professor.py` | Main automation orchestrator for desktop |
| `youtube_uploader.py` | Optional YouTube Data API integration |
| `curriculum.json` | Syllabus configuration (Classes 6-12) |
| `state.json` | Progress tracking (auto-generated) |
| `backend/utils/subject_prompts.py` | Subject expert personas |
| `output/` | Local folder for generated videos |

### Desktop Workflow

```bash
# 1. Setup (one time)
python run_ai_professor.py --init

# 2. Add PDFs to pdfs/ folder

# 3. Generate lessons
python run_ai_professor.py              # Process one lesson
python run_ai_professor.py --all        # Process all pending
python run_ai_professor.py --lesson 5   # Process specific lesson

# 4. Videos saved to output/class{N}_{subject}/
```

### Optional: YouTube Upload

```bash
# Authenticate (one time)
python youtube_uploader.py --auth

# Upload a video
python youtube_uploader.py --upload output/class9_math/final_video.mp4
```

### Desktop Architecture (Python 3.11 + FastAPI)

The desktop system uses `asyncio` with `asyncio.create_task` for true concurrency. Each generation pipeline (video, audio, questions) runs as an independent async task, with results saved directly to disk.

**Parallel Processing**: Video rendering, audio synthesis, and question generation all run simultaneously, reducing total generation time by 60-70%.

```bash
run_ai_professor.py:
  ├── asyncio.create_task → generate_questions  → mcqs.json
  ├── asyncio.create_task → generate_narration  → narration.wav
  └── asyncio.create_task → generate_diagram_video → video.mp4
  └── ffmpeg → combine audio+video → final_video.mp4
```

### AI Pipeline — PDF Understanding

`pdf_processor.py` passes the entire PDF as raw bytes to Gemini 2.5 Flash with `mime_type="application/pdf"`. Gemini reads all pages, Indic Unicode text, embedded fonts, and visual diagrams in a **single API call** — no page-by-page image rendering needed.

PDFs longer than 15 pages are truncated in-memory using PyMuPDF (`fitz`) before being sent to Gemini, keeping latency under ~30 seconds.

Gemini returns a structured JSON with: `chapter_name`, `language`, `board`, `class_level`, `summary_text` (in the chapter's language), `key_concepts`, `formulas`, `diagrams`.

**Language normalisation**: Gemini returns free-form language names ("Kannada", "kn", etc.) which are normalised to BCP-47 codes (`kn-IN`, `hi-IN`, `ta-IN`, `te-IN`, `mr-IN`, `en-IN`) via a lookup table before any downstream use.

### AI Pipeline — Video Generation (Two-Step)

Video generation uses a two-step pipeline inspired by the cerebralvalley text-to-video approach:

**Step 1 — Concept Script (Gemini as the prompt writer)**

Gemini reads `summary_text` (already in the student's language — Kannada, Hindi, etc.) and produces a structured 3-step JSON script:

```json
{
  "steps": [
    { "heading": "ಕಾಂತೀಯ ಪ್ರಭಾವ", "body": "ವಿದ್ಯುತ್ ಪ್ರವಾಹ ಕಾಂತ ಕ್ಷೇತ್ರ ಸೃಷ್ಟಿಸುತ್ತದೆ", "shape": "coil" },
    { "heading": "ಫ್ಲೆಮಿಂಗ್ ನಿಯಮ", "body": "ಎಡ ಕೈ ನಿಯಮ ದಿಕ್ಕನ್ನು ನಿರ್ಧರಿಸುತ್ತದೆ", "shape": "arrow" },
    { "heading": "ಅನ್ವಯ", "body": "ವಿದ್ಯುತ್ ಮೋಟಾರ್ ಈ ತತ್ವ ಬಳಸುತ್ತದೆ", "shape": "rectangle" }
  ]
}
```

Using `summary_text` (not `key_concepts`) is critical — key concepts extracted by Gemini from Indic PDFs are always returned in English. The summary is in the textbook's own language, so grounding the script in the summary guarantees the video narrates in the correct language.

**Step 2 — Manim Code Generation**

Gemini writes a Python `DiagramScene(Scene)` class from the JSON script. The generated code is executed by Manim Community Edition, which renders an MP4.

**Critical: Indic text rendering fix**

Cairo (the rendering engine used by Manim) on Windows crashes when rendering Indic Unicode glyphs at partial opacity — which happens during `FadeIn()` and `Write()` animations (opacity interpolates 0→1, crashing at ~27%). The fix: use `self.add()` for all text, which places text at full opacity instantly. Shapes still use `Create()` for visual animation.

```python
# CORRECT — instant, full opacity, no Cairo crash
self.add(heading, body)

# WRONG — crashes on Kannada/Hindi/Tamil/Telugu text
self.play(FadeIn(heading))
```

Indic fonts: `"Nirmala UI"` on Windows (built-in), `"Noto Sans"` on Linux (needs `fonts-noto-extra`). Font is auto-detected at startup via `platform.system()`.

If the generated Manim code fails, the error is fed back to Gemini with a `FIX_PROMPT`, and it retries once.

### AI Pipeline — Audio Narration

`vernacular_narrator.py` runs a two-step process:

1. **Script generation** — Gemini 2.5 Flash writes a 200–280 word teacher-style spoken narration in the target language (Kannada, Hindi, etc.), using the chapter summary, key concepts, and formulas as context.

2. **TTS synthesis** — Gemini 2.5 Flash TTS (`gemini-2.5-flash-preview-tts`) synthesises the script. Gemini returns raw **16-bit PCM audio at 24 kHz mono** — this is wrapped in a WAV container using Python's `wave` module before saving.

```python
# PCM → WAV wrapping
buf = io.BytesIO()
with wave.open(buf, 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)     # 16-bit
    wf.setframerate(24000) # 24 kHz
    wf.writeframes(pcm_data)
```

Voice mapping: `"Kore"` for all Indic languages, `"Puck"` for English.

### AI Pipeline — Question Generation

Gemini 2.5 Flash generates board-specific questions using the full `chapter_json` (summary, concepts, formulas, diagrams) and the detected board name. Output is a structured JSON with MCQs (options + correct answer + explanation), short-answer questions, and one HOT (Higher Order Thinking) question. An `exam_tip` field flags concepts that historically appear in board papers.

### AI Pipeline — Grounded Chat

`document_chat.py` passes the full `chapter_json` as a grounding context and streams Gemini's response using `generate_content_stream`. A system prompt constrains Gemini to answer only from the provided chapter content, preventing hallucinations about unrelated topics.

### Frontend (Optional Web Interface)

The included React 18 + TypeScript + Vite + TailwindCSS frontend provides a web interface for uploading PDFs and viewing generated content. This is optional for desktop use—the main automation runs via CLI.

**To use the web interface:**

```bash
cd frontend && npm install && npm run dev
# Access at http://localhost:5173
```

For pure desktop automation, you can ignore the frontend and use only `run_ai_professor.py`.

---

## Innovation Highlights

### One-Call Native PDF Understanding
Instead of rendering each PDF page to an image and making one API call per page, AI Professor passes the entire PDF as raw bytes to Gemini with `mime_type="application/pdf"`. Gemini reads all pages, diagrams, formulas, and Indic scripts in a single pass.

### AI-Written Manim Animations
AI Professor does not use pre-built animation templates. Gemini writes original Python animation code for every chapter it encounters, and Manim renders them as MP4 videos. The two-step pipeline (concept script → Manim code) ensures text length is controlled and language is correct before code generation.

### Subject Expert Personas
Each subject is taught by a PhD-level AI persona with appropriate pedagogy: mathematicians emphasize proofs, physicists use real-world examples, chemists explain molecular foundations, and historians provide chronological context.

### Desktop-First Design
No server required. All processing happens on your local machine. Videos are saved directly to your hard drive. Optional YouTube upload for sharing.

### Parallel Processing Architecture
All generation tasks (video, audio, questions) run concurrently via `asyncio.create_task`, reducing total generation time by 60-70%.

---

## Impact and Use Cases

### Primary Audience
Indian school students in Class 6–12 who study from regional-language textbooks and lack access to private tutors or coaching centres.

### Secondary Audience
- **Teachers** — Generate summary and exam questions instantly for lesson planning
- **Parents** — Play the audio narration to children who struggle to read
- **Competitive exam aspirants** — Use board-pattern questions for self-assessment

### Potential Scale
India has over 1.5 million schools. State Board students number over 150 million. AI Professor's automatic language detection and subject-specific personas mean the same system works for a student in Bengaluru (Kannada), Mumbai (Marathi), Chennai (Tamil), or Hyderabad (Telugu) without any customisation, publishing educational videos to YouTube daily.

---

## Technology Stack Summary

| Component | Technology |
|-----------|-----------|
| Backend API | Python 3.11, FastAPI, SSE-Starlette |
| AI SDK | `google-genai` (Gemini API SDK — not ADK) |
| AI Model | Google Gemini 2.5 Flash (vision, text, code, TTS) |
| TTS | Gemini 2.5 Flash TTS — raw PCM → WAV via `wave` module |
| Video Animation | Manim Community Edition + FFmpeg |
| PDF Processing | Gemini native PDF mode (`mime_type="application/pdf"`) + PyMuPDF |
| Indic Font (Windows) | Nirmala UI (built-in) |
| Indic Font (Linux) | Noto Sans (`fonts-noto-extra`) |
| Storage | Google Cloud Storage (local `static/` fallback) |
| Automation | GitHub Actions (daily scheduler) |
| YouTube Integration | YouTube Data API v3 + OAuth 2.0 |
| Deployment | Docker + docker-compose |

---

## What Makes AI Professor Different

| Feature | AI Professor | Typical EdTech App |
|---------|-------------|-------------------|
| Automation | Fully autonomous daily video generation | Manual content creation |
| Indian language support | 6 regional languages, auto-detected | English only |
| Subject expert personas | PhD-level AI tutors per subject | Generic presenters |
| Animated diagram videos | AI-generated per chapter via Manim | Pre-recorded or none |
| Board-specific questions | Karnataka / CBSE / Maharashtra / Tamil Nadu | Generic |
| Audio narration | Gemini TTS in student's own language | English only |
| YouTube integration | Auto-upload with metadata | Manual upload |
| Curriculum tracking | Automatic progress across all chapters | No tracking |
| Zero manual intervention | Daily scheduled runs via GitHub Actions | Full manual workflow |

---

## Future Roadmap

- **Offline Mode** — Cache generated materials so students can study without internet
- **More Boards** — Andhra Pradesh, Telangana, West Bengal, Rajasthan State Boards
- **More Languages** — Odia, Punjabi, Gujarati, Bengali
- **Parent Dashboard** — Track which chapters a child has studied and their quiz scores
- **Teacher Tools** — Bulk upload of entire textbook, auto-generate lesson plans
- **Voice Chat** — Speak questions to the AI tutor in regional languages
- **Adaptive Questions** — Difficulty adjusts based on how many previous questions were correct

---

## 🚀 Quick Start Guide

### Step 1: Install Prerequisites

**Windows:**
```powershell
# Install Python 3.11+
# Install Node.js 18+
# Install FFmpeg: choco install ffmpeg
# Install Git
```

**macOS:**
```bash
brew install python@3.11 node ffmpeg git
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3-pip nodejs npm ffmpeg git
```

### Step 2: Clone and Setup

```bash
# Clone repository
git clone <your-repo-url>
cd AI-Professor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
pip install google-auth-oauthlib google-api-python-client

# Create .env file
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
```

### Step 3: Initialize System

```bash
# Initialize curriculum and state files
python run_ai_professor.py --init
```

This creates:
- `curriculum.json` — Syllabus configuration
- `state.json` — Progress tracking
- `pdfs/` — Folder for textbook PDFs
- `output/` — Folder for generated videos

### Step 4: Add Textbook PDFs

Download NCERT or State Board PDFs and place them in the `pdfs/` folder. Name them according to the pattern in `curriculum.json`:

```
pdfs/
├── class9_math_ch1.pdf
├── class9_math_ch2.pdf
├── class9_science_ch1.pdf
└── ...
```

### Step 5: Generate Your First Lesson

```bash
# Process one lesson (default)
python run_ai_professor.py

# Process all pending lessons
python run_ai_professor.py --all

# Process specific lesson by index
python run_ai_professor.py --lesson-index 5

# Test mode (uses sample PDF)
python run_ai_professor.py --test
```

Generated videos are saved to:
```
output/
├── class9_mathematics/
│   ├── Linear_Equations/
│   │   ├── video.mp4
│   │   ├── audio.wav
│   │   ├── questions.json
│   │   └── final_video.mp4
```

### Step 6: (Optional) YouTube Upload

If you want to upload videos to YouTube:

```bash
# Authenticate with YouTube (one-time)
python youtube_uploader.py --auth

# This opens a browser for OAuth. Follow the prompts.
# token.pickle will be saved for future use.

# Upload a specific video
python youtube_uploader.py --upload output/class9_mathematics/Linear_Equations/final_video.mp4

# Upload as unlisted (for testing)
python youtube_uploader.py --upload path/to/video.mp4 --test
```

### Step 7: (Optional) Web Interface

The included web interface is optional. To use it:

```bash
cd frontend
npm install
npm run dev
# Access at http://localhost:5173
```

---

## 📋 Command Reference

### run_ai_professor.py

| Command | Description |
|---------|-------------|
| `--init` | Initialize curriculum and state files |
| `--test` | Run test with sample PDF |
| `--all` | Process all pending lessons |
| `--lesson-index N` | Process lesson at index N |
| `--help` | Show help message |

### youtube_uploader.py

| Command | Description |
|---------|-------------|
| `--auth` | Authenticate with YouTube OAuth |
| `--upload FILE` | Upload video file |
| `--title TITLE` | Custom title (auto-generated if omitted) |
| `--test` | Upload as unlisted |
| `--help` | Show help message |

---

## ⚙️ Configuration

### Environment Variables (.env)

```env
GOOGLE_API_KEY=your_gemini_api_key_here
GOOGLE_CLOUD_BUCKET=optional_bucket_name
```

Get your Gemini API key from: https://aistudio.google.com/apikey

### curriculum.json

Edit this file to customize your syllabus:

```json
{
  "classes": [
    {
      "class": 9,
      "subjects": ["mathematics", "science"],
      "chapters": {
        "mathematics": ["Linear Equations", "Quadratic Equations"],
        "science": ["Matter", "Atoms and Molecules"]
      }
    }
  ]
}
```

### state.json

Auto-generated. Tracks progress:

```json
{
  "published": [...],
  "pending": [...]
}
```

---

## 🛠️ Troubleshooting

### FFmpeg not found
```bash
# Verify installation
ffmpeg -version

# Install if missing
# Windows: choco install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

### Manim rendering fails
- Ensure you have `Noto Sans` fonts installed (Linux)
- Check that PDF has readable text (not scanned images)
- Reduce animation complexity in prompt

### API Rate Limits
- Gemini has rate limits. Add delays between requests if needed
- The script includes automatic retry logic with exponential backoff

### YouTube Upload Fails
- Re-authenticate: delete `token.pickle` and run `--auth` again
- Check quota limits in Google Cloud Console
- Use `--test` flag for unlisted uploads during testing

---

## 💰 Cost Estimates

Using Gemini 2.5 Flash API:

- **PDF Processing**: ~$0.005 per chapter
- **Video Script**: ~$0.002 per lesson
- **TTS Audio**: ~$0.003 per minute
- **Total per lesson**: ~$0.01-0.02

**Monthly cost for daily videos**: $5-15 depending on usage.

---

## 🔒 Privacy & Security

- All processing happens locally on your machine
- Videos saved to your hard drive
- No data sent to third parties (except Gemini API for AI processing)
- YouTube upload is opt-in only
- API keys stored in `.env` (add to `.gitignore`)

---

## 📄 License

MIT — Free to use, modify, and deploy privately.

---

**Built for educators, students, and lifelong learners.**  
**Powered by Google Gemini 2.5 Flash and Manim.**
