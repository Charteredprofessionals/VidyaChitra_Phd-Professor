# 📋 AI Professor — Deployment Checklist

Use this checklist to ensure your private desktop deployment is complete and secure.

---

## 🔐 Privacy & Security Setup

### Environment Protection
- [ ] `.env` file created with API key
- [ ] `.env` added to `.gitignore` (verified)
- [ ] `client_secret.json` not committed to Git
- [ ] `token.pickle` not committed to Git
- [ ] Repository set to **private** on GitHub/GitLab

### File Permissions (Linux/macOS)
```bash
chmod 600 .env
chmod 600 client_secret.json
chmod 700 output/
```

### Network Security
- [ ] Firewall configured (if exposing web interface)
- [ ] Using localhost only for web interface
- [ ] No public IP exposure

---

## ✅ Installation Verification

### System Dependencies
- [ ] Python 3.11+ installed: `python --version`
- [ ] Node.js 18+ installed: `node --version`
- [ ] FFmpeg installed: `ffmpeg -version`
- [ ] Git installed: `git --version`

### Python Packages
```bash
python -c "import google.genai; print('✓ Gemini')"
python -c "import manim; print('✓ Manim')"
python -c "import fastapi; print('✓ FastAPI')"
python -c "import uvicorn; print('✓ Uvicorn')"
```

- [ ] All imports successful

### Font Installation (for Indic languages)
- [ ] Windows: Nirmala UI verified (built-in)
- [ ] macOS: `brew install font-noto-sans`
- [ ] Linux: `sudo apt install fonts-noto-extra`

---

## 🧪 Functional Testing

### Initialization
- [ ] `python run_ai_professor.py --init` runs without errors
- [ ] `curriculum.json` created and valid JSON
- [ ] `state.json` created
- [ ] `pdfs/` folder exists
- [ ] `output/` folder exists

### Test Generation
- [ ] Add sample PDF to `pdfs/`
- [ ] `python run_ai_professor.py --test` completes
- [ ] Video file created in `output/`
- [ ] Video plays in media player
- [ ] Audio is clear and audible
- [ ] Animation displays correctly

### Full Pipeline
- [ ] `python run_ai_professor.py` processes one lesson
- [ ] All components generated (video, audio, questions)
- [ ] `final_video.mp4` created
- [ ] Progress tracked in `state.json`

---

## 📤 YouTube Integration (Optional)

### API Setup
- [ ] Google Cloud project created
- [ ] YouTube Data API v3 enabled
- [ ] OAuth 2.0 credentials created (Desktop app)
- [ ] `client_secret.json` downloaded
- [ ] File placed in project root

### Authentication
- [ ] `python youtube_uploader.py --auth` completed
- [ ] Browser OAuth flow successful
- [ ] `token.pickle` created
- [ ] Token saved for future use

### Upload Test
- [ ] `python youtube_uploader.py --upload video.mp4 --test` succeeds
- [ ] Video appears in YouTube Studio as **Unlisted**
- [ ] Title, description, tags are correct
- [ ] Video quality is acceptable

---

## 📊 Performance Baseline

### Timing Tests
Run one lesson generation and record times:

| Component | Expected | Actual |
|-----------|----------|--------|
| PDF Analysis | 15-30 sec | _____ |
| Script Generation | 10-20 sec | _____ |
| Manim Rendering | 60-120 sec | _____ |
| TTS Audio | 20-40 sec | _____ |
| Video Assembly | 10-20 sec | _____ |
| **Total** | **2-4 min** | _____ |

- [ ] Times within expected range
- [ ] No memory errors or crashes
- [ ] Disk space sufficient

---

## 💾 Backup Configuration

### Manual Backup
- [ ] `curriculum.json` backed up
- [ ] `state.json` backed up
- [ ] Important videos copied to external drive

### Automated Backup (Optional)
```bash
# Add to crontab (Linux/macOS) or Task Scheduler (Windows)
0 2 * * * cd /path/to/AI-Professor && ./backup.sh
```

- [ ] Backup script created
- [ ] Scheduled task configured
- [ ] Test restore successful

---

## 🔧 Configuration Customization

### Curriculum
- [ ] `curriculum.json` edited for your needs
- [ ] All required classes added
- [ ] All subjects configured
- [ ] Chapter names match PDF files

### Subject Personas
- [ ] Review `backend/utils/subject_prompts.py`
- [ ] Customize personas if needed
- [ ] Verify pedagogy matches teaching style

### Quality Settings
- [ ] Video resolution set (480p/720p/1080p)
- [ ] Animation quality configured
- [ ] TTS voice selected

---

## 📝 Documentation Review

### Internal Documentation
- [ ] `README.md` reviewed
- [ ] `OFFLINE_DESKTOP_GUIDE.md` reviewed
- [ ] `QUICK_START.md` accessible
- [ ] `IMPLEMENTATION.md` available for reference

### Custom Notes
Create a `NOTES.md` file with:
- [ ] Your API key location (secure note)
- [ ] YouTube channel details
- [ ] Custom curriculum decisions
- [ ] Troubleshooting tips specific to your setup

---

## 🚀 Production Readiness

### Daily Operations
- [ ] Workflow documented for daily use
- [ ] PDF source identified (NCERT, State Board, etc.)
- [ ] Storage plan for videos (local/external/cloud)
- [ ] Sharing method decided (YouTube/local network/USB)

### Monitoring
- [ ] API usage tracked (stay within free tier)
- [ ] Disk space monitored
- [ ] Error logs reviewed periodically
- [ ] Backup integrity verified

### Scaling Plan
- [ ] Estimate monthly video count
- [ ] Calculate API costs
- [ ] Plan storage expansion
- [ ] Consider batch processing schedule

---

## ⚠️ Common Issues & Solutions

### Issue: Out of Disk Space
**Solution:** 
```bash
# Check usage
du -sh output/

# Clean old files
find output/ -mtime +30 -delete
```
- [ ] Solution tested

### Issue: API Rate Limits
**Solution:** Add delays between requests
```python
import time
time.sleep(2)
```
- [ ] Delays implemented if needed

### Issue: Slow Rendering
**Solutions:**
- Reduce resolution to 480p
- Lower animation quality
- Use simpler diagrams
- [ ] Optimizations applied

### Issue: Font Rendering Errors
**Solution:** Install Noto Sans fonts
- [ ] Fonts installed and tested

---

## 📞 Support Resources

### Documentation
- Main Guide: `README.md`
- Desktop Setup: `OFFLINE_DESKTOP_GUIDE.md`
- Quick Start: `QUICK_START.md`
- This Checklist: `DEPLOYMENT_CHECKLIST.md`

### External Resources
- Gemini API: https://ai.google.dev/
- Manim Docs: https://docs.manim.community/
- NCERT Books: https://ncert.nic.in/textbook.php
- YouTube API: https://developers.google.com/youtube/v3

### Community
- GitHub Issues: Report bugs
- Discussions: Share curricula and tips

---

## ✅ Final Sign-Off

Before going live:

- [ ] All tests passed
- [ ] Privacy settings verified
- [ ] Backups configured
- [ ] Documentation reviewed
- [ ] First video generated successfully
- [ ] (Optional) First YouTube upload successful
- [ ] Team/users trained (if applicable)

---

**Deployment Date:** _______________

**Deployed By:** _______________

**Notes:**

_______________________________________

_______________________________________

_______________________________________

---

**🎉 Congratulations! Your AI Professor is ready to educate!**
