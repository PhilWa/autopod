import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import datetime
from config import (
    MODELS,
    SCRIPT_DIR,
    POST_DIR,
    SCREENWRITER,
    SPEAKERS,
    PROMPTS,
    PODCAST_STYLES,
)
from utils import get_latest_file


def create_dialogue(
    main_content,
    intro_style=None,
    content_style=None,
    outro_style=None,
    output_file=None,
    models=None,
    speakers=None,
    prompts=None,
    screenwriter=None,
):
    # Load environment variables
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # Use provided configs or fall back to default
    if models is None or speakers is None or prompts is None or screenwriter is None:
        from config import MODELS, SPEAKERS, PROMPTS, SCREENWRITER

        # If any parameter is None, use the default from config
        if models is None:
            models = MODELS
        if speakers is None:
            speakers = SPEAKERS
        if prompts is None:
            prompts = PROMPTS
        if screenwriter is None:
            screenwriter = SCREENWRITER

    # Format input so it's perfect to create a podcast script on.

    # Format the user prompt with dynamic content
    print("user_prompt")
    # here issue
    print(intro_style)
    print(content_style)
    print(outro_style)
    print(main_content)
    print(speakers["1"]["name"])
    print(speakers["2"]["name"])
    print("🥳🥳🥳", prompts["script"]["user"])
    user_prompt = prompts["script"]["user"].format(
        intro_style=intro_style,
        content_style=content_style,
        outro_style=outro_style,
        main_content=main_content,
        speaker1_name=speakers["1"]["name"],
        speaker2_name=speakers["2"]["name"],
    )
    print("😎😎😎", user_prompt)
    system_prompt = prompts["script"]["system"]
    print("system_prompt")
    # Generate the script
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

    print("Lets turn it up a notch!")
    # Add screenwriter transformation
    print("screenwriter_prompt", SCREENWRITER["screenwriter"]["system"])
    screenwriter_prompt = SCREENWRITER["screenwriter"]["system"].format(
        speaker_1=speakers["1"]["personality"], speaker_2=speakers["2"]["personality"]
    )
    print("screenwriter_prompt")
    # Call the API again for the screenwriter transformation
    script = "The script to make a worldclass podcast out of: " + script
    screenwriter_response = client.chat.completions.create(
        model=models["podcast_script"]["model"],
        messages=[
            {"role": "system", "content": screenwriter_prompt},
            {"role": "user", "content": script},
        ],
        temperature=models["podcast_script"]["temperature"],
        max_tokens=models["podcast_script"]["max_tokens"],
    )
    print("screenwriter_response")

    # Get the transformed script
    final_script = screenwriter_response.choices[0].message.content
    print("final_script")
    # Handle file saving with new parameters
    if output_file:
        filepath = os.path.join(SCRIPT_DIR, output_file)
    else:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(SCRIPT_DIR, f"podcast_script_{timestamp}.txt")

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(final_script)

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

    filepath = create_dialogue(
        main_content=main_content,
        intro_style=MODELS["podcast_script"]["intro_style"],
        content_style=MODELS["podcast_script"]["content_style"],
        outro_style=MODELS["podcast_script"]["outro_style"],
    )

    print(f"Podcast script has been saved to: {filepath}")


if __name__ == "__main__":
    main()
