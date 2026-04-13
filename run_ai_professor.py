#!/usr/bin/env python3
"""
AI Professor — Autonomous Lesson Generation System

This script automates the generation of educational videos from PDF chapters,
following a curriculum planner and publishing to YouTube.

Usage:
    python run_ai_professor.py [--test] [--lesson-index N]
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from dotenv import load_dotenv
load_dotenv()

from ingestion.pdf_processor import process_pdf
from generation.question_forger import generate_questions
from generation.vernacular_narrator import generate_narration
from generation.video_generator import generate_diagram_video
from utils.subject_prompts import get_combined_prompt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("ai_professor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ai_professor")

# Constants
CURRICULUM_FILE = Path(__file__).parent / "curriculum.json"
STATE_FILE = Path(__file__).parent / "state.json"
OUTPUT_DIR = Path(__file__).parent / "output"
PDFS_DIR = Path(__file__).parent / "pdfs"


def ensure_directories():
    """Create necessary directories."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    PDFS_DIR.mkdir(exist_ok=True)


def load_curriculum() -> dict:
    """Load curriculum configuration."""
    if not CURRICULUM_FILE.exists():
        logger.error(f"Curriculum file not found: {CURRICULUM_FILE}")
        raise FileNotFoundError(f"Create {CURRICULUM_FILE} first")
    
    with open(CURRICULUM_FILE, "r") as f:
        return json.load(f)


def load_state() -> dict:
    """Load progress state."""
    default_state = {"published": [], "pending": [], "failed": []}
    if not STATE_FILE.exists():
        return default_state
    
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state: dict):
    """Save progress state."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_next_pending_lesson() -> Optional[dict]:
    """Get the next pending lesson from state."""
    state = load_state()
    if state["pending"]:
        return state["pending"].pop(0)
    return None


def mark_published(lesson: dict, video_url: str = None, youtube_url: str = None):
    """Mark a lesson as published."""
    state = load_state()
    lesson["status"] = "published"
    lesson["video_url"] = video_url
    lesson["youtube_url"] = youtube_url
    lesson["published_at"] = datetime.now().isoformat()
    state["published"].append(lesson)
    save_state(state)
    logger.info(f"Marked lesson as published: {lesson['chapter']}")


def mark_failed(lesson: dict, error: str):
    """Mark a lesson as failed."""
    state = load_state()
    lesson["status"] = "failed"
    lesson["error"] = error
    lesson["failed_at"] = datetime.now().isoformat()
    state["failed"].append(lesson)
    save_state(state)
    logger.error(f"Marked lesson as failed: {lesson['chapter']} - {error}")


def combine_audio_video(video_path: str, audio_path: str, output_dir: Path) -> str:
    """Combine video and audio using ffmpeg."""
    import subprocess
    
    output_path = output_dir / f"final_{Path(video_path).stem}.mp4"
    
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"Combined A/V saved to: {output_path}")
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.warning(f"FFmpeg combine failed: {e.stderr.decode()}")
        return video_path


async def generate_lesson(lesson: dict, subject_prompt: str = None) -> dict:
    """
    Generate a complete lesson from a PDF chapter.
    
    Args:
        lesson: Lesson dict with class, subject, chapter, pdf_path
        subject_prompt: Optional custom system prompt for subject persona
        
    Returns:
        Dict with paths to generated assets
    """
    pdf_path = Path(lesson["pdf_path"])
    if not pdf_path.exists():
        # Try relative to pdfs dir
        pdf_path = PDFS_DIR / lesson["pdf_path"]
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {lesson['pdf_path']}")
    
    session_id = f"{lesson['class']}_{lesson['subject']}_{lesson['chapter'].replace(' ', '_')}"
    output_subdir = OUTPUT_DIR / session_id
    output_subdir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Processing: Class {lesson['class']} {lesson['subject']} - {lesson['chapter']}")
    
    # Step 1: Process PDF with Gemini
    logger.info("Step 1: Processing PDF...")
    chapter_json = await asyncio.get_running_loop().run_in_executor(
        None, process_pdf, str(pdf_path)
    )
    chapter_json["session_id"] = session_id
    chapter_json["subject"] = lesson["subject"]
    
    # Inject subject expert prompt if provided
    if subject_prompt:
        chapter_json["system_prompt"] = subject_prompt
        logger.info(f"Using subject expert prompt for: {lesson['subject']}")
    
    # Step 2: Generate questions
    logger.info("Step 2: Generating questions...")
    board = f"Class {lesson['class']}"
    questions = await asyncio.get_running_loop().run_in_executor(
        None, generate_questions, chapter_json, board, chapter_json.get("language", "en-IN")
    )
    
    # Step 3: Generate audio narration
    logger.info("Step 3: Generating audio narration...")
    audio_url = await asyncio.get_running_loop().run_in_executor(
        None, generate_narration, chapter_json, chapter_json.get("language", "en-IN")
    )
    
    # Download audio to local file if it's a URL
    audio_path = None
    if audio_url.startswith("http"):
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(audio_url)
            audio_path = output_subdir / "narration.wav"
            audio_path.write_bytes(response.content)
            logger.info(f"Audio saved to: {audio_path}")
    else:
        audio_path = Path(audio_url)
    
    # Step 4: Generate Manim video
    logger.info("Step 4: Generating Manim video...")
    video_url = await generate_diagram_video(chapter_json, chapter_json.get("language", "en-IN"), session_id)
    
    # Download video to local file if it's a URL
    video_path = None
    if video_url.startswith("http"):
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(video_url)
            video_path = output_subdir / "diagram.mp4"
            video_path.write_bytes(response.content)
            logger.info(f"Video saved to: {video_path}")
    else:
        video_path = Path(video_url)
    
    # Step 5: Combine audio and video
    final_video = None
    if video_path and audio_path:
        logger.info("Step 5: Combining audio and video...")
        final_video = combine_audio_video(str(video_path), str(audio_path), output_subdir)
    
    result = {
        "session_id": session_id,
        "summary": chapter_json.get("summary_text", "")[:500],
        "questions": questions,
        "audio_path": str(audio_path) if audio_path else audio_url,
        "video_path": str(video_path) if video_path else video_url,
        "final_video": final_video,
        "output_dir": str(output_subdir)
    }
    
    logger.info(f"Lesson generation complete: {session_id}")
    return result


def initialize_curriculum():
    """Create initial curriculum.json if it doesn't exist."""
    if CURRICULUM_FILE.exists():
        logger.info("Curriculum file already exists")
        return
    
    curriculum = {
        "classes": [
            {
                "class": 9,
                "subjects": ["mathematics", "science"],
                "chapters": {
                    "mathematics": ["Number Systems", "Polynomials", "Coordinate Geometry", "Linear Equations"],
                    "science": ["Matter in Our Surroundings", "Atoms and Molecules", "Structure of Atom"]
                }
            },
            {
                "class": 10,
                "subjects": ["mathematics", "science", "social_science"],
                "chapters": {
                    "mathematics": ["Real Numbers", "Polynomials", "Trigonometry", "Quadratic Equations"],
                    "science": ["Chemical Reactions", "Acids Bases Salts", "Electricity"],
                    "social_science": ["Nationalism in India", "Resources and Development"]
                }
            }
        ]
    }
    
    with open(CURRICULUM_FILE, "w") as f:
        json.dump(curriculum, f, indent=2)
    
    logger.info(f"Created curriculum template: {CURRICULUM_FILE}")


def initialize_state():
    """Create initial state.json from curriculum."""
    if STATE_FILE.exists():
        logger.info("State file already exists")
        return
    
    curriculum = load_curriculum()
    pending = []
    
    for cls in curriculum["classes"]:
        class_level = cls["class"]
        for subject in cls["subjects"]:
            chapters = cls["chapters"].get(subject, [])
            for chapter in chapters:
                pdf_filename = f"class{class_level}_{subject}_{chapter.replace(' ', '_')}.pdf"
                pending.append({
                    "class": class_level,
                    "subject": subject,
                    "chapter": chapter,
                    "pdf_path": pdf_filename,
                    "status": "pending"
                })
    
    state = {"published": [], "pending": pending, "failed": []}
    save_state(state)
    logger.info(f"Initialized state with {len(pending)} pending lessons")


async def run_single_lesson(lesson_index: int = None):
    """Run a single lesson generation."""
    ensure_directories()
    
    if lesson_index is not None:
        state = load_state()
        if lesson_index < len(state["pending"]):
            lesson = state["pending"][lesson_index]
        else:
            logger.error(f"Lesson index {lesson_index} out of range")
            return
    else:
        lesson = get_next_pending_lesson()
    
    if not lesson:
        logger.info("No pending lessons. All done!")
        return
    
    try:
        # Get subject-specific prompt
        subject_prompt = get_combined_prompt(lesson["subject"])
        
        # Generate the lesson
        result = await generate_lesson(lesson, subject_prompt)
        
        # Mark as published
        mark_published(lesson, video_url=result.get("final_video"))
        
        logger.info(f"✅ Successfully processed: {lesson['chapter']}")
        logger.info(f"   Output: {result.get('final_video', 'N/A')}")
        
    except Exception as e:
        logger.exception(f"Failed to process lesson: {e}")
        mark_failed(lesson, str(e))


async def run_all_lessons():
    """Process all pending lessons."""
    ensure_directories()
    
    while True:
        lesson = get_next_pending_lesson()
        if not lesson:
            logger.info("All lessons processed!")
            break
        
        try:
            subject_prompt = get_combined_prompt(lesson["subject"])
            result = await generate_lesson(lesson, subject_prompt)
            mark_published(lesson, video_url=result.get("final_video"))
            logger.info(f"✅ Completed: {lesson['chapter']}")
        except Exception as e:
            logger.exception(f"Failed: {e}")
            mark_failed(lesson, str(e))


def main():
    parser = argparse.ArgumentParser(description="AI Professor - Automated Lesson Generator")
    parser.add_argument("--init", action="store_true", help="Initialize curriculum and state files")
    parser.add_argument("--test", action="store_true", help="Test mode with sample PDF")
    parser.add_argument("--lesson-index", type=int, help="Process specific lesson by index")
    parser.add_argument("--all", action="store_true", help="Process all pending lessons")
    args = parser.parse_args()
    
    if args.init:
        initialize_curriculum()
        initialize_state()
        print("Initialization complete. Edit curriculum.json and add PDFs to /pdfs folder.")
        return
    
    if args.test:
        # Create a test lesson
        ensure_directories()
        test_lesson = {
            "class": 10,
            "subject": "mathematics",
            "chapter": "Test Chapter",
            "pdf_path": "test_chapter.pdf"
        }
        # Check if test PDF exists
        if not (PDFS_DIR / "test_chapter.pdf").exists():
            print("No test PDF found. Place a PDF at pdfs/test_chapter.pdf first.")
            return
        asyncio.run(run_single_lesson())
        return
    
    if args.all:
        asyncio.run(run_all_lessons())
        return
    
    if args.lesson_index is not None:
        asyncio.run(run_single_lesson(args.lesson_index))
        return
    
    # Default: process one pending lesson
    asyncio.run(run_single_lesson())


if __name__ == "__main__":
    main()
