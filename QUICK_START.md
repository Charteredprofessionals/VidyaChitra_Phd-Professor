# 🚀 AI Professor — Quick Start

## 3-Minute Setup

### 1. Install Dependencies (2 min)

```bash
# macOS
brew install python@3.11 node ffmpeg git

# Linux
sudo apt install python3.11 python3-pip nodejs npm ffmpeg git

# Windows (PowerShell as Admin)
winget install Python.Python.3.11 OpenJS.NodeJS.LTS Gyan.FFmpeg Git.Git
```

### 2. Setup Project (1 min)

```bash
cd AI-Professor
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
pip install google-auth-oauthlib google-api-python-client

# Create .env file
echo "GOOGLE_API_KEY=your_key_here" > .env
```

**Get API key:** https://aistudio.google.com/apikey

### 3. Initialize & Run

```bash
# Initialize
python run_ai_professor.py --init

# Add a PDF to pdfs/ folder, then:
python run_ai_professor.py
```

**Done!** Video saved to `output/` folder.

---

## Next Steps

- **Add more PDFs:** Download from https://ncert.nic.in/textbook.php
- **Generate all:** `python run_ai_professor.py --all`
- **Upload to YouTube:** `python youtube_uploader.py --auth` then `--upload video.mp4`
- **Full guide:** See `OFFLINE_DESKTOP_GUIDE.md`

---

## Commands Cheat Sheet

```bash
python run_ai_professor.py --init      # Initialize system
python run_ai_professor.py             # Generate one lesson
python run_ai_professor.py --all       # Generate all pending
python run_ai_professor.py --test      # Test mode

python youtube_uploader.py --auth      # Authenticate YouTube
python youtube_uploader.py --upload file.mp4  # Upload video
python youtube_uploader.py --upload file.mp4 --test  # Upload unlisted
```

---

**Need help?** See `README.md` or `OFFLINE_DESKTOP_GUIDE.md`
