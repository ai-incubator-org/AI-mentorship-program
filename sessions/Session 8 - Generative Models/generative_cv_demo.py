"""
Generative Computer Vision Demo for Students
===========================================

What this file demonstrates:
1. Text -> Image generation for startup/product visuals
2. Image -> Text analysis using a vision model
3. Image analysis -> Better prompt -> Generated marketing image
4. Optional image editing: product photo -> e-commerce ad creative

How to run:
-----------
1. Install dependencies:
   pip install openai pillow matplotlib

2. Set your OpenAI API key:
   macOS/Linux:
      export OPENAI_API_KEY="your_key_here"

   Windows PowerShell:
      setx OPENAI_API_KEY "your_key_here"

3. Run examples:
   python generative_cv_demo.py --demo text-to-image
   python generative_cv_demo.py --demo analyze --image path/to/image.png
   python generative_cv_demo.py --demo workflow --image path/to/image.png
   python generative_cv_demo.py --demo edit --image path/to/product.png
"""

import argparse
import base64
import os
from pathlib import Path

from openai import OpenAI
from PIL import Image
import matplotlib.pyplot as plt


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def get_client() -> OpenAI:
    """Create OpenAI client using OPENAI_API_KEY environment variable."""
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Run: export OPENAI_API_KEY='your_key_here'"
        )
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def save_base64_image(base64_data: str, output_path: Path) -> Path:
    """Decode base64 image from API response and save it."""
    image_bytes = base64.b64decode(base64_data)
    output_path.write_bytes(image_bytes)
    return output_path


def show_image(path: Path, title: str = "Generated image") -> None:
    """Display an image with matplotlib."""
    image = Image.open(path)
    plt.figure(figsize=(7, 7))
    plt.imshow(image)
    plt.axis("off")
    plt.title(title)
    plt.show()


def encode_image_to_base64(path: Path) -> str:
    """Encode local image as base64 string for vision input."""
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def guess_mime_type(path: Path) -> str:
    """Simple MIME type helper."""
    suffix = path.suffix.lower()
    if suffix in [".jpg", ".jpeg"]:
        return "image/jpeg"
    if suffix == ".webp":
        return "image/webp"
    return "image/png"


def demo_text_to_image() -> None:
    """
    Demo 1:
    Generate a simple startup/product visual from a text prompt.
    """
    client = get_client()

    prompt = """
    Create a clean marketing image for a startup idea:
    an AI app that turns product photos into professional e-commerce ads.

    Style:
    - modern startup style
    - realistic product photography
    - clean background
    - suitable for a pitch deck slide
    - no text
    """

    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
    )

    output_path = OUTPUT_DIR / "01_startup_cv_demo.png"
    save_base64_image(result.data[0].b64_json, output_path)

    print(f"Saved: {output_path}")
    show_image(output_path, "Text-to-image: startup visual")


def demo_analyze_image(image_path: str) -> str:
    """
    Demo 2:
    Analyze an uploaded/local image using a vision model.
    """
    client = get_client()
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    base64_image = encode_image_to_base64(path)
    mime_type = guess_mime_type(path)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": """
                        Analyze this image for a generative computer vision startup.

                        Return:
                        1. What is in the image?
                        2. What problem could this image relate to?
                        3. What startup idea could be built around it?
                        4. What would the generative AI output be?
                        5. How could the startup monetize it?
                        """
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime_type};base64,{base64_image}",
                    },
                ],
            }
        ],
    )

    print("\n=== IMAGE ANALYSIS ===\n")
    print(response.output_text)
    return response.output_text


def demo_workflow(image_path: str) -> None:
    """
    Demo 3:
    Real startup workflow:
    image -> vision analysis -> improved generation prompt -> generated output.
    """
    client = get_client()

    analysis_text = demo_analyze_image(image_path)

    generation_prompt = f"""
    Based on this image analysis, create a professional marketing visual.

    Analysis:
    {analysis_text}

    Requirements:
    - premium startup pitch deck style
    - realistic but polished
    - clear business use case
    - clean background
    - high-quality lighting
    - no unreadable text
    """

    result = client.images.generate(
        model="gpt-image-1",
        prompt=generation_prompt,
        size="1024x1024",
    )

    output_path = OUTPUT_DIR / "02_workflow_generated_visual.png"
    save_base64_image(result.data[0].b64_json, output_path)

    print(f"\nSaved: {output_path}")
    show_image(output_path, "Vision analysis -> generated marketing visual")


def demo_edit_image(image_path: str) -> None:
    """
    Demo 4:
    Edit an existing product/photo into a marketing creative.
    """
    client = get_client()
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    prompt = """
    Transform this image into a professional e-commerce marketing creative.

    Requirements:
    - preserve the main subject/product as much as possible
    - clean modern background
    - soft realistic lighting
    - premium startup/product photography style
    - suitable for a landing page hero image
    - no fake logos
    - no unreadable text
    """

    with open(path, "rb") as image_file:
        result = client.images.edit(
            model="gpt-image-1",
            image=image_file,
            prompt=prompt,
            size="1024x1024",
        )

    output_path = OUTPUT_DIR / "03_edited_marketing_image.png"
    save_base64_image(result.data[0].b64_json, output_path)

    print(f"Saved: {output_path}")
    show_image(output_path, "Edited product/marketing image")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Small Generative Computer Vision demo for students."
    )

    parser.add_argument(
        "--demo",
        choices=["text-to-image", "analyze", "workflow", "edit"],
        required=True,
        help="Which demo to run.",
    )

    parser.add_argument(
        "--image",
        type=str,
        default=None,
        help="Path to image for analyze/workflow/edit demos.",
    )

    args = parser.parse_args()

    if args.demo == "text-to-image":
        demo_text_to_image()

    elif args.demo == "analyze":
        if not args.image:
            raise ValueError("--image is required for analyze demo")
        demo_analyze_image(args.image)

    elif args.demo == "workflow":
        if not args.image:
            raise ValueError("--image is required for workflow demo")
        demo_workflow(args.image)

    elif args.demo == "edit":
        if not args.image:
            raise ValueError("--image is required for edit demo")
        demo_edit_image(args.image)


if __name__ == "__main__":
    main()
