#!/usr/bin/env python3
"""
YouTube Uploader — Automated video publishing to YouTube.

This module handles authentication and uploading of generated lesson videos
to YouTube with proper metadata (title, description, tags).

Setup:
1. Enable YouTube Data API v3 in Google Cloud Console
2. Create OAuth 2.0 credentials (Desktop app)
3. Download client_secret.json to project root
4. Run once to authenticate: python youtube_uploader.py --auth
"""

import argparse
import os
import pickle
from pathlib import Path
from typing import Optional

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# OAuth scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Token file location
TOKEN_FILE = Path(__file__).parent / "token.pickle"
CLIENT_SECRET_FILE = Path(__file__).parent / "client_secret.json"


def authenticate_youtube() -> Optional[object]:
    """
    Authenticate with YouTube API using OAuth 2.0.
    
    Returns:
        Authorized YouTube API client, or None if authentication fails.
    """
    creds = None
    
    # Load existing token
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if not CLIENT_SECRET_FILE.exists():
            print(f"Error: {CLIENT_SECRET_FILE} not found.")
            print("Download it from Google Cloud Console after creating OAuth 2.0 credentials.")
            return None
        
        if creds and creds.refresh_token:
            try:
                creds.refresh(None)
            except Exception as e:
                print(f"Token refresh failed: {e}")
                creds = None
        
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        
        # Save token for future use
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)
    
    return build("youtube", "v3", credentials=creds)


def upload_video(
    youtube,
    video_file: str,
    title: str,
    description: str,
    tags: list,
    category_id: str = "27",  # Education
    privacy_status: str = "public"  # public, private, unlisted
) -> Optional[str]:
    """
    Upload a video to YouTube.
    
    Args:
        youtube: Authorized YouTube API client
        video_file: Path to video file
        title: Video title
        description: Video description
        tags: List of tags
        category_id: YouTube category ID (27 = Education)
        privacy_status: public, private, or unlisted
    
    Returns:
        YouTube video URL, or None if upload fails.
    """
    if not Path(video_file).exists():
        print(f"Error: Video file not found: {video_file}")
        return None
    
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status
        }
    }
    
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    
    try:
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%")
        
        video_id = response["id"]
        video_url = f"https://youtu.be/{video_id}"
        print(f"✅ Video uploaded successfully: {video_url}")
        return video_url
        
    except HttpError as e:
        print(f"YouTube API error: {e}")
        if e.resp.status == 403:
            print("Quota exceeded. Check your YouTube API quota in Google Cloud Console.")
        return None


def create_lesson_metadata(lesson: dict) -> dict:
    """
    Create YouTube metadata for a lesson.
    
    Args:
        lesson: Lesson dict with class, subject, chapter
    
    Returns:
        Dict with title, description, tags
    """
    class_level = lesson.get("class", 10)
    subject = lesson.get("subject", "science")
    chapter = lesson.get("chapter", "Introduction")
    
    title = f"Class {class_level} {subject.title()}: {chapter}"
    
    description = f"""📚 Free Educational Lesson by AI Professor

Topic: {chapter}
Class: {class_level}
Subject: {subject.title()}

This lesson is part of our free educational series covering the NCERT curriculum.
Perfect for students preparing for board exams!

🎯 What you'll learn:
- Key concepts explained clearly
- Visual demonstrations
- Exam tips and tricks

📖 Based on NCERT curriculum standards.

#Class{class_level} #{subject.title()} #Education #FreeLearning #NCERT #BoardExams
"""
    
    tags = [
        f"class {class_level}",
        f"class {class_level} {subject}",
        chapter.lower(),
        subject,
        "NCERT",
        "board exams",
        "free education",
        "online learning",
        "India education"
    ]
    
    return {"title": title, "description": description, "tags": tags}


def upload_lesson_video(lesson: dict, video_path: str, test_mode: bool = False) -> Optional[str]:
    """
    Upload a lesson video to YouTube with proper metadata.
    
    Args:
        lesson: Lesson dict
        video_path: Path to video file
        test_mode: If True, upload as unlisted
    
    Returns:
        YouTube URL or None
    """
    youtube = authenticate_youtube()
    if not youtube:
        return None
    
    metadata = create_lesson_metadata(lesson)
    privacy = "unlisted" if test_mode else "public"
    
    return upload_video(
        youtube,
        video_path,
        metadata["title"],
        metadata["description"],
        metadata["tags"],
        privacy_status=privacy
    )


def main():
    parser = argparse.ArgumentParser(description="YouTube Uploader for AI Professor")
    parser.add_argument("--auth", action="store_true", help="Run OAuth authentication flow")
    parser.add_argument("--upload", type=str, help="Upload a video file")
    parser.add_argument("--title", type=str, default="Educational Video", help="Video title")
    parser.add_argument("--test", action="store_true", help="Upload as unlisted (test mode)")
    args = parser.parse_args()
    
    if args.auth:
        print("Starting YouTube OAuth authentication...")
        youtube = authenticate_youtube()
        if youtube:
            print("✅ Authentication successful! Token saved to token.pickle")
        else:
            print("❌ Authentication failed")
        return
    
    if args.upload:
        lesson = {
            "class": 10,
            "subject": "mathematics",
            "chapter": "Sample Chapter"
        }
        url = upload_lesson_video(lesson, args.upload, test_mode=args.test)
        if url:
            print(f"Video uploaded: {url}")
        else:
            print("Upload failed")
        return
    
    print("YouTube Uploader for AI Professor")
    print("=" * 40)
    print("\nUsage:")
    print("  1. First time setup: python youtube_uploader.py --auth")
    print("  2. Upload a video:   python youtube_uploader.py --upload video.mp4 [--test]")
    print("\nThe script integrates automatically with run_ai_professor.py")
    print("when YouTube credentials are configured.")


if __name__ == "__main__":
    main()
