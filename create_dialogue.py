import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import datetime
from config import MODELS, SCRIPT_DIR, POST_DIR, SPEAKERS, PROMPTS
from utils import get_latest_file


def create_podcast_script(
    main_content,
    intro_style="joyful and full of banter",
    content_style="professional",
    outro_style="relaxed and engaging",
    output_file=None,
    models=None,
    speakers=None,
    prompts=None,
):
    # Load environment variables
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Use provided configs or fall back to default
    if models is None or speakers is None or prompts is None:
        from config import MODELS, SPEAKERS, PROMPTS

        # If any parameter is None, use the default from config
        if models is None:
            models = MODELS
        if speakers is None:
            speakers = SPEAKERS
        if prompts is None:
            prompts = PROMPTS

    print(f"\n=== Intro Style: {intro_style} ===")

    # Format the user prompt with dynamic content
    user_prompt = prompts["script"]["user"].format(
        intro_style=intro_style,
        content_style=content_style,
        outro_style=outro_style,
        main_content=main_content,
        speaker1_name=speakers["1"]["name"],
        speaker2_name=speakers["2"]["name"],
    )
    system_prompt = prompts["script"]["system"]
    print(f"\n=== User Prompt: {user_prompt} ===")

    # Create the system prompt

    # Generate the script
    print(f"\n=== System Prompt: {system_prompt} ===")
    response = client.chat.completions.create(
        model=models["podcast_script"]["model"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=models["podcast_script"]["temperature"],
        max_tokens=models["podcast_script"]["max_tokens"],
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
