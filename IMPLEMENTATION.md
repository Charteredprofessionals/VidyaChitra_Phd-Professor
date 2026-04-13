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
EOF

# Install dependencies
pip install -r backend/requirements.txt
pip install google-auth-oauthlib google-api-python-client

# Install FFmpeg (required for video processing)
# Ubuntu/Debian:
sudo apt update && sudo apt install ffmpeg
# macOS:
brew install ffmpeg
```

### 2. Initialize the System

```bash
# Initialize curriculum and state files
python run_ai_professor.py --init
```

This creates:
- `curriculum.json` - Your syllabus (already created with Classes 9-10)
- `state.json` - Tracks which lessons are pending/published/failed

### 3. Add PDF Files

Place your NCERT chapter PDFs in the `pdfs/` directory. The filenames should match the pattern in `state.json`:

```
pdfs/
├── class9_mathematics_Number_Systems.pdf
├── class9_mathematics_Polynomials.pdf
├── class9_science_Matter_in_Our_Surroundings.pdf
└── ...
```

**Tip:** Download NCERT PDFs from [ncert.nic.in](https://ncert.nic.in/textbook.php) and rename them to match the expected pattern.

### 4. Run a Test Lesson

```bash
# Process one pending lesson
python run_ai_professor.py

# Or process a specific lesson by index
python run_ai_professor.py --lesson-index 0

# Process ALL pending lessons (may take hours!)
python run_ai_professor.py --all
```

### 5. YouTube Integration (Optional)

#### Step 5a: Set up YouTube API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **YouTube Data API v3**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Choose **Desktop app** as application type
6. Download the JSON file and save as `client_secret.json` in project root

#### Step 5b: Authenticate

```bash
# First-time OAuth authentication
python youtube_uploader.py --auth
```

This opens a browser window. Sign in with your YouTube account and grant permissions.

#### Step 5c: Upload a Video

```bash
# Upload as unlisted (for testing)
python youtube_uploader.py --upload output/class_10_mathematics_test/narration.mp4 --test

# Upload as public
python youtube_uploader.py --upload video.mp4
```

### 6. Automated Daily Publishing (GitHub Actions)

The system includes a GitHub Actions workflow that runs daily at 8 AM UTC.

#### Enable GitHub Actions:

1. Push your code to GitHub
2. Go to your repository → **Settings** → **Secrets and variables** → **Actions**
3. Add these secrets:
   - `GOOGLE_API_KEY` - Your Gemini API key
   - `GOOGLE_CLOUD_BUCKET` - (Optional) GCS bucket name

4. Go to **Actions** tab → Select "AI Professor Daily Lesson" → Click "Run workflow"

The workflow will:
- Install all dependencies
- Initialize the curriculum
- Process one pending lesson
- Upload generated videos as artifacts

---

## Command Reference

### run_ai_professor.py

| Command | Description |
|---------|-------------|
| `--init` | Initialize curriculum.json and state.json |
| `--test` | Run with test PDF (requires pdfs/test_chapter.pdf) |
| `--lesson-index N` | Process lesson at index N |
| `--all` | Process all pending lessons |
| *(no args)* | Process next pending lesson |

### youtube_uploader.py

| Command | Description |
|---------|-------------|
| `--auth` | Run OAuth authentication flow |
| `--upload FILE` | Upload specified video file |
| `--title TEXT` | Set video title (with --upload) |
| `--test` | Upload as unlisted (testing mode) |

---

## Configuration Examples

### Adding More Classes to curriculum.json

```json
{
  "classes": [
    {
      "class": 6,
      "subjects": ["mathematics", "science"],
      "chapters": {
        "mathematics": ["Knowing Our Numbers", "Whole Numbers", "Playing with Numbers"],
        "science": ["Food: Where Does It Come From?", "Components of Food"]
      }
    },
    // ... add more classes
  ]
}
```

### Customizing Subject Personas

Edit `backend/utils/subject_prompts.py`:

```python
SUBJECT_EXPERT_PROMPTS = {
    "mathematics": """Your custom prompt here...""",
    "physics": """Your custom prompt here...""",
}
```

### Changing Schedule (GitHub Actions)

Edit `.github/workflows/ai_professor.yml`:

```yaml
on:
  schedule:
    - cron: '0 14 * * *'  # 2 PM UTC instead of 8 AM
```

---

## Output Structure

After running, you'll find generated files in `output/`:

```
output/
└── 10_mathematics_Real_Numbers/
    ├── chapter_data.json      # Gemini-generated summary
    ├── questions.json         # Generated practice questions
    ├── narration.wav          # TTS audio
    ├── diagram.mp4            # Manim animation
    └── final_*.mp4            # Combined video+audio
```

---

## Troubleshooting

### Error: "PDF not found"
- Ensure PDFs are in the `pdfs/` directory
- Check filename matches exactly what's in `state.json`

### Error: "FFmpeg not found"
- Install FFmpeg: `sudo apt install ffmpeg` (Ubuntu) or `brew install ffmpeg` (macOS)

### Error: "Google API quota exceeded"
- Wait 24 hours for quota reset
- Upgrade quota in Google Cloud Console
- Add retry logic with exponential backoff

### Error: "YouTube upload failed: quotaExceeded"
- YouTube API has daily quota limits (~1,600 units/day for free tier)
- Each upload uses ~1,600 units
- Request quota increase or use unlisted uploads for testing

### Manim rendering is slow
- Reduce animation complexity in prompts
- Use caching for repeated elements
- Consider cloud rendering services

---

## Cost Estimates

| Service | Free Tier | Paid Usage |
|---------|-----------|------------|
| Gemini API | 60 requests/min | ~$0.0007/input token |
| YouTube Upload | 1,600 units/day | Free (quota limits apply) |
| GitHub Actions | 2,000 min/month | $0.008/min over limit |
| Storage (GCS) | 5 GB | $0.02/GB/month |

**Estimated monthly cost for daily videos:** $5-15 USD

---

## Success Metrics

✅ System generates one video per day automatically  
✅ Videos have subject-specific teaching styles  
✅ All lessons tracked in state.json  
✅ Failed lessons logged with error details  
✅ YouTube uploads include proper metadata  

---

## Support

For issues:
1. Check `ai_professor.log` for detailed error messages
2. Verify API keys in `.env`
3. Ensure all dependencies are installed
4. Test with a single lesson before running `--all`
