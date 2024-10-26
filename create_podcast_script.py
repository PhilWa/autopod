import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import datetime
from config import MODELS, SCRIPT_DIR, POST_DIR
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

    # Create the system prompt
    system_prompt = """You are a podcast script writer. Create a natural conversation between two speakers.
    
    **Format the output in the following way.**
    <Speaker 1> [Content of speaker 1's line]
    <Speaker 2> [Content of speaker 2's line]
    Remark: It is essential that <Speaker 1> and <Speaker 2> are used exactly as shown above.
    
    **The script should have three parts:**
    1. An introduction
    2. Main content discussion
    3. An outro
    
    Make the conversation flow naturally and maintain the specified style for each section."""

    # Create the user prompt
    user_prompt = f"""Create a podcast script with the following specifications:
    Use natural fillers like 'mm-hmm' sparingly to simulate authentic interaction during pauses or when someone else is speaking.
    Includes also very short back in forth. Incorporate personal anecdotes to make the content relatable. Add active listening cues such as 'I see' or 'Right' to show engagement in conversation including follow up questions.
    
    Introduction style: {intro_style}
    Main content style: {content_style}
    Outro style: {outro_style}

    Main content to discuss: {main_content}

    Speaker 1 is called Tim
    Speaker 2 is called Elly

    Make sure the transitions between sections feel natural and maintain engaging dialogue throughout. The main content should be the most important part and should be the longest part of the script."""

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
        main_content = "No recent posts found in the post directory."

    # You can customize these styles
    intro_style = "energetic and humorous, with friendly banter between hosts"
    content_style = "informative and professional, but keeping it accessible"
    outro_style = "casual and forward-looking, encouraging listener engagement"

    filepath = create_podcast_script(
        main_content=main_content,
        intro_style=intro_style,
        content_style=content_style,
        outro_style=outro_style,
    )

    print(f"Podcast script has been saved to: {filepath}")


if __name__ == "__main__":
    main()
