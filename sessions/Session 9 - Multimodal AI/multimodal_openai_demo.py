#!/usr/bin/env python3
"""
multimodal_openai_demo.py

Startup-oriented multimodal AI demo using ONLY OpenAI models/APIs:
1) Image understanding: physical books, whiteboards, handmade notes, screenshots.
2) Image-folder analysis: compare multiple visual inputs.
3) Speech-to-text: transcribe audio, then summarize/action-plan it.
4) Text-to-speech: turn AI output into spoken narration.
5) Video analysis: sample frames with ffmpeg, then analyze frames with OpenAI vision.

Install:
    pip install openai python-dotenv

Set API key:
    export OPENAI_API_KEY="your_key_here"

Examples:
    python multimodal_openai_demo.py image --path "./outputs/01_startup_cv_demo.png"
    python multimodal_openai_demo.py folder --path ./samples/notes
    python multimodal_openai_demo.py audio --path ./samples/meeting.mp3 --speak
    python multimodal_openai_demo.py video --path ./samples/espresso.mp4 --every 5
"""

import argparse
import base64
import json
import mimetypes
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Optional

from openai import OpenAI


VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4.1")
TEXT_MODEL = os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1")
TRANSCRIBE_MODEL = os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-transcribe")
TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

STARTUP_CONTEXT = """
You are helping startup founders understand multimodal AI opportunities.
Focus on practical product ideas, MVP scope, customer value, monetization, risks,
and what can be built quickly with APIs.
Keep explanations clear for students/beginners.
"""


def require_api_key() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Run: export OPENAI_API_KEY='your_key_here'"
        )


def file_to_data_url(path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(path)
    if not mime_type:
        mime_type = "application/octet-stream"

    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def get_image_paths(folder: Path) -> List[Path]:
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    return sorted([p for p in folder.iterdir() if p.suffix.lower() in exts])


def ask_text(prompt: str, model: str = TEXT_MODEL) -> str:
    response = client.responses.create(
        model=model,
        instructions=STARTUP_CONTEXT,
        input=prompt,
    )
    return response.output_text


def analyze_images(
    image_paths: Iterable[Path],
    question: str,
    model: str = VISION_MODEL,
) -> str:
    content = [{"type": "input_text", "text": question}]

    for path in image_paths:
        content.append({
            "type": "input_text",
            "text": f"Image file: {path.name}",
        })
        content.append({
            "type": "input_image",
            "image_url": file_to_data_url(path),
        })

    response = client.responses.create(
        model=model,
        instructions=STARTUP_CONTEXT,
        input=[{
            "role": "user",
            "content": content,
        }],
    )
    return response.output_text


def transcribe_audio(audio_path: Path) -> str:
    with audio_path.open("rb") as f:
        transcription = client.audio.transcriptions.create(
            model=TRANSCRIBE_MODEL,
            file=f,
            prompt=(
                "This audio may be from a startup classroom, product demo, meeting, "
                "or AI lecture. Keep technical terms such as CLIP, OCR, STT, TTS, "
                "RAG, API, MVP, and multimodal AI accurate."
            ),
        )
    return transcription.text


def text_to_speech(text: str, output_path: Path, voice: str = "coral") -> None:
    with client.audio.speech.with_streaming_response.create(
        model=TTS_MODEL,
        voice=voice,
        input=text,
        instructions=(
            "Speak like a clear startup lecturer. Confident, energetic, not too fast."
        ),
    ) as response:
        response.stream_to_file(output_path)


def demo_image(path: Path, out_dir: Path, speak: bool = False) -> None:
    prompt = """
Analyze this visual input as a multimodal AI startup demo.

Return:
1. What the image probably contains.
2. Useful context the AI can extract.
3. Example startup product idea.
4. MVP workflow using OpenAI APIs only.
5. Limitations and risks.
6. A short classroom explanation.
"""

    result = analyze_images([path], prompt)
    print_section("IMAGE ANALYSIS")
    print(result)

    write_text(out_dir / "image_analysis.md", result)

    if speak:
        text_to_speech(result[:3000], out_dir / "image_analysis_narration.mp3")
        print(f"\nSaved narration: {out_dir / 'image_analysis_narration.mp3'}")


def demo_folder(path: Path, out_dir: Path, speak: bool = False) -> None:
    image_paths = get_image_paths(path)
    if not image_paths:
        raise ValueError(f"No images found in {path}")

    prompt = """
You are given multiple visual inputs, possibly books, handwritten notes,
whiteboards, product sketches, screenshots, or physical documents.

Return:
1. Common theme across the images.
2. Key extracted information.
3. How a multimodal AI system could combine the context.
4. 5 startup ideas based on these inputs.
5. Best idea to build first and why.
6. MVP architecture using OpenAI only.
7. A short pitch for investors.
"""

    result = analyze_images(image_paths, prompt)
    print_section("FOLDER / MULTI-IMAGE ANALYSIS")
    print(result)

    write_text(out_dir / "folder_analysis.md", result)

    if speak:
        text_to_speech(result[:3000], out_dir / "folder_analysis_narration.mp3")
        print(f"\nSaved narration: {out_dir / 'folder_analysis_narration.mp3'}")


def demo_audio(path: Path, out_dir: Path, speak: bool = False) -> None:
    transcript = transcribe_audio(path)

    print_section("TRANSCRIPT")
    print(transcript)

    write_text(out_dir / "transcript.txt", transcript)

    summary_prompt = f"""
Here is an audio transcript:

{transcript}

Turn it into a startup-oriented multimodal AI summary.

Return:
1. Main points.
2. Product opportunities.
3. User pain points.
4. MVP idea.
5. Revenue model.
6. Action items for students/founders.
7. 60-second spoken explanation.
"""

    result = ask_text(summary_prompt)

    print_section("AUDIO SUMMARY")
    print(result)

    write_text(out_dir / "audio_summary.md", result)

    if speak:
        text_to_speech(result, out_dir / "audio_summary_narration.mp3")
        print(f"\nSaved narration: {out_dir / 'audio_summary_narration.mp3'}")


def extract_video_frames(video_path: Path, out_frames_dir: Path, every_seconds: int) -> List[Path]:
    """
    Uses ffmpeg CLI to extract frames.
    This does not use other AI models. It only prepares frames for OpenAI vision.
    Install ffmpeg separately if needed:
        macOS: brew install ffmpeg
        Ubuntu: sudo apt install ffmpeg
    """
    out_frames_dir.mkdir(parents=True, exist_ok=True)

    pattern = str(out_frames_dir / "frame_%04d.jpg")
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-vf", f"fps=1/{every_seconds}",
        "-q:v", "3",
        pattern,
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise RuntimeError("ffmpeg is not installed or not found in PATH.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg failed:\n{e.stderr.decode('utf-8', errors='ignore')}")

    frames = sorted(out_frames_dir.glob("frame_*.jpg"))
    if not frames:
        raise RuntimeError("No frames extracted from video.")
    return frames


def demo_video(path: Path, out_dir: Path, every_seconds: int, speak: bool = False) -> None:
    frames_dir = out_dir / "video_frames"
    frames = extract_video_frames(path, frames_dir, every_seconds)

    selected_frames = frames[:12]

    prompt = """
These are sampled frames from a video. Analyze them as a multimodal AI demo.

Return:
1. What seems to happen in the video.
2. Important visual context from frames.
3. How this could become a startup feature.
4. Example product directions: video summarizer, lecture analyzer, meeting whiteboard extractor,
   shopping assistant, industrial visual inspection, or training coach.
5. MVP workflow using OpenAI only.
6. What the system cannot know from frames alone.
7. Suggested next step: combine with transcript from the video's audio.
"""

    result = analyze_images(selected_frames, prompt)

    print_section("VIDEO FRAME ANALYSIS")
    print(result)

    write_text(out_dir / "video_analysis.md", result)

    if speak:
        text_to_speech(result[:3000], out_dir / "video_analysis_narration.mp3")
        print(f"\nSaved narration: {out_dir / 'video_analysis_narration.mp3'}")


def demo_complete(
    images_dir: Optional[Path],
    audio_path: Optional[Path],
    video_path: Optional[Path],
    out_dir: Path,
    every_seconds: int,
    speak: bool,
) -> None:
    pieces = []

    if images_dir:
        image_paths = get_image_paths(images_dir)
        if image_paths:
            image_result = analyze_images(
                image_paths[:8],
                "Analyze these images and extract useful startup/product context.",
            )
            pieces.append(("Image context", image_result))
            write_text(out_dir / "complete_image_context.md", image_result)

    if audio_path:
        transcript = transcribe_audio(audio_path)
        pieces.append(("Audio transcript", transcript))
        write_text(out_dir / "complete_transcript.txt", transcript)

    if video_path:
        frames_dir = out_dir / "complete_video_frames"
        frames = extract_video_frames(video_path, frames_dir, every_seconds)
        video_result = analyze_images(
            frames[:12],
            "Analyze these video frames and extract useful startup/product context.",
        )
        pieces.append(("Video context", video_result))
        write_text(out_dir / "complete_video_context.md", video_result)

    if not pieces:
        raise ValueError("Complete mode needs at least one of --images-dir, --audio-path, --video-path")

    combined_context = "\n\n".join(
        f"## {title}\n{content}" for title, content in pieces
    )

    final_prompt = f"""
Combine the following multimodal inputs into one startup product brief.

{combined_context}

Return:
1. Problem statement.
2. Target users.
3. Product concept.
4. Core multimodal feature.
5. MVP architecture using OpenAI only.
6. User flow.
7. Pricing idea.
8. Competitive advantage.
9. Risks/limitations.
10. 30-day build plan.
11. 45-second demo script for class.
"""

    final = ask_text(final_prompt)

    print_section("COMPLETE MULTIMODAL STARTUP BRIEF")
    print(final)

    write_text(out_dir / "complete_startup_brief.md", final)

    if speak:
        text_to_speech(final[:3500], out_dir / "complete_startup_brief_narration.mp3")
        print(f"\nSaved narration: {out_dir / 'complete_startup_brief_narration.mp3'}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Startup-oriented multimodal AI demo using OpenAI only."
    )
    parser.add_argument(
        "--out",
        default="./outputs",
        help="Output directory for generated markdown/audio/frame files.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    image = subparsers.add_parser("image", help="Analyze one image.")
    image.add_argument("--path", required=True, help="Path to image.")
    image.add_argument("--speak", action="store_true", help="Also create TTS narration.")

    folder = subparsers.add_parser("folder", help="Analyze a folder of images.")
    folder.add_argument("--path", required=True, help="Path to image folder.")
    folder.add_argument("--speak", action="store_true", help="Also create TTS narration.")

    audio = subparsers.add_parser("audio", help="Transcribe and summarize audio.")
    audio.add_argument("--path", required=True, help="Path to audio file.")
    audio.add_argument("--speak", action="store_true", help="Also create TTS narration.")

    video = subparsers.add_parser("video", help="Analyze sampled video frames.")
    video.add_argument("--path", required=True, help="Path to video file.")
    video.add_argument("--every", type=int, default=5, help="Extract one frame every N seconds.")
    video.add_argument("--speak", action="store_true", help="Also create TTS narration.")

    complete = subparsers.add_parser("complete", help="Combine images, audio, and video.")
    complete.add_argument("--images-dir", help="Optional folder with images.")
    complete.add_argument("--audio-path", help="Optional audio file.")
    complete.add_argument("--video-path", help="Optional video file.")
    complete.add_argument("--every", type=int, default=5, help="Extract one frame every N seconds.")
    complete.add_argument("--speak", action="store_true", help="Also create TTS narration.")

    return parser


def main() -> None:
    require_api_key()

    parser = build_parser()
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        if args.command == "image":
            demo_image(Path(args.path), out_dir, args.speak)

        elif args.command == "folder":
            demo_folder(Path(args.path), out_dir, args.speak)

        elif args.command == "audio":
            demo_audio(Path(args.path), out_dir, args.speak)

        elif args.command == "video":
            demo_video(Path(args.path), out_dir, args.every, args.speak)

        elif args.command == "complete":
            demo_complete(
                images_dir=Path(args.images_dir) if args.images_dir else None,
                audio_path=Path(args.audio_path) if args.audio_path else None,
                video_path=Path(args.video_path) if args.video_path else None,
                out_dir=out_dir,
                every_seconds=args.every,
                speak=args.speak,
            )

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
