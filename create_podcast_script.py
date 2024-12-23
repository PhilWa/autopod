import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import datetime
from config import MODELS, SCRIPT_DIR, POST_DIR, SPEAKERS, PROMPTS, PODCAST_STYLES
from utils import get_latest_file


def create_podcast_script(
    main_content,
    intro_style="joyful and full of banter",
    content_style="professional",
    outro_style="relaxed and engaging",
    output_file=None,
):
    # Load environment variables
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Format the user prompt with dynamic content
    user_prompt = PROMPTS["script"]["user"].format(
        intro_style=intro_style,
        content_style=content_style,
        outro_style=outro_style,
        main_content=main_content,
        speaker1_name=SPEAKERS[1]["name"],
        speaker2_name=SPEAKERS[2]["name"],
    )
    system_prompt = PROMPTS["script"]["system"]

    # Create the system prompt

    # Generate the script
    response = client.chat.completions.create(
        model=MODELS["podcast_script"]["model"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=MODELS["podcast_script"]["temperature"],
        max_tokens=MODELS["podcast_script"]["max_tokens"],
    )

    # Get the generated script
    script = response.choices[0].message.content

    # Handle file saving with new parameters
    if output_file:
        filepath = os.path.join(SCRIPT_DIR, output_file)
    else:
        # Fallback to timestamp if no output_file provided
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(SCRIPT_DIR, f"podcast_script_{timestamp}.txt")

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(script)

    return filepath


def main():
    # Get the latest post from the post directory
    file_path, post_content = get_latest_file(POST_DIR, ".txt")
    if post_content:
        content_lines = post_content.split("\n")
        main_content = "\n".join(
            line for line in content_lines if line.startswith("**")
        )
    else:
        raise ValueError("No recent posts found in the post directory.")

    filepath = create_podcast_script(
        main_content=main_content,
        intro_style=MODELS["podcast_script"]["intro_style"],
        content_style=MODELS["podcast_script"]["content_style"],
        outro_style=MODELS["podcast_script"]["outro_style"],
    )

    print(f"Podcast script has been saved to: {filepath}")


if __name__ == "__main__":
    main()
