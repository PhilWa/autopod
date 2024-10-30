import os
from datetime import datetime
from dotenv import load_dotenv
from get_information import get_recent_articles
from create_post import create_linkedin_post, get_latest_articles
from create_dialogue import create_podcast_script
from create_audio import main as create_audio
from create_episode import create_podcast_episode
import argparse
import json


def generate_run_id():
    """Generate a unique run ID based on timestamp"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def process_articles(run_id=None, models=None):
    """Fetch articles and create a LinkedIn post"""
    get_recent_articles()
    articles = get_latest_articles()
    if not articles:
        return None, "No articles found"

    print(f"\n=== Creating LinkedIn Post ===")
    article_content = [(article[1], article[2], article[3]) for article in articles]
    linkedin_post = create_linkedin_post(
        article_content, output_file=f"post_{run_id}.txt", models=models
    )
    return linkedin_post, None


def process_text_file(input_text_file):
    """Read content from a provided text file"""
    print(f"\n=== Using Provided Text File: {input_text_file} ===")
    with open(input_text_file, "r") as file:
        return file.read()


def load_config(config_path=None):
    """Load configuration from either JSON file or default Python config"""
    if config_path and config_path.endswith(".json"):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            return (
                config.get("models", {}),
                config.get("speakers", {}),
                config.get("podcast_styles", {}),
                config.get("prompts", {}),
            )
        except Exception as e:
            print(f"Error loading JSON config: {e}")
            print("Falling back to Python config...")

    # Fall back to Python config
    from config import MODELS, SPEAKERS, PODCAST_STYLES, PROMPTS

    return MODELS, SPEAKERS, PODCAST_STYLES, PROMPTS


def run_pipeline(input_text_file=None, config_path=None):
    """Run the complete content generation pipeline"""
    try:
        run_id = generate_run_id()
        print(f"\n=== Starting Pipeline Run: {run_id} ===")

        # Load configuration
        MODELS, SPEAKERS, PODCAST_STYLES, PROMPTS = load_config(config_path)

        # Determine content source
        if input_text_file:
            linkedin_post = process_text_file(input_text_file)
        else:
            linkedin_post, error = process_articles(run_id, models=MODELS)
            if error:
                return error

        # Step 2: Create podcast script
        create_podcast_script(
            main_content=linkedin_post,
            intro_style=PODCAST_STYLES["intro"],
            content_style=PODCAST_STYLES["content"],
            outro_style=PODCAST_STYLES["outro"],
            output_file=f"podcast_script_{run_id}.txt",
        )

        # Step 3: Generate audio files
        print(f"\n=== Generating Audio Files ===")
        audio_files = create_audio(
            script_path=f"podcast_script_{run_id}.txt",
            output_prefix=f"audio_{run_id}",
            run_id=run_id,
            models=MODELS,
            speakers=SPEAKERS,
        )
        if not audio_files:
            return "Failed to generate audio files"

        # Step 4: Create final podcast episode
        print(f"\n=== Creating Final Podcast Episode ===")
        episode_path = create_podcast_episode(
            audio_files=audio_files, output_file=f"episode_{run_id}.mp3"
        )

        return {
            "status": "success",
            "run_id": run_id,
            "linkedin_post": linkedin_post,
            "audio_files": audio_files,
            "episode_path": episode_path,
        }

    except Exception as e:
        return f"Pipeline failed: {str(e)}"


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run the content generation pipeline.")
    parser.add_argument(
        "--input-file",
        type=str,
        help="Path to the input text file to be used for the podcast script.",
    )
    parser.add_argument(
        "--config-file",
        type=str,
        help="Path to JSON configuration file. If not provided, uses Python config.",
    )
    args = parser.parse_args()

    result = run_pipeline(args.input_file, args.config_file)

    if isinstance(result, dict):
        print("\n=== Pipeline Completed Successfully ===")
        print(f"Episode created: {result['episode_path']}")
    else:
        print(f"\n=== Pipeline Failed ===\n{result}")


if __name__ == "__main__":
    main()
