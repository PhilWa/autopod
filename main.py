import os
from datetime import datetime
from dotenv import load_dotenv
import argparse

from config_parser import (
    load_config,
    get_models,
    get_speakers,
    get_podcast_styles,
    get_prompts,
    get_screenwriter,
    get_directories,
)

from get_information import get_recent_articles
from create_post import create_linkedin_post, get_latest_articles
from create_dialogue import create_dialogue
from create_audio import main as create_audio
from create_episode import (
    load_audio,
    stitch_audio,
    apply_postprocessing,
    add_intro_outro,
    save_audio,
)


def generate_run_id():
    """Generate a unique run ID based on timestamp"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def process_articles(run_id=None, config=None):
    """Fetch articles and create a LinkedIn post"""
    get_recent_articles()
    articles = get_latest_articles()
    if not articles:
        return None, "No articles found"

    print(f"\n=== Creating LinkedIn Post ===")
    article_content = [(article[1], article[2], article[3]) for article in articles]
    linkedin_post = create_linkedin_post(
        article_content, output_file=f"post_{run_id}.txt", config=config
    )
    return linkedin_post, None


def process_text_file(input_text_file):
    """Read content from a provided text file"""
    print(f"\n=== Using Provided Text File: {input_text_file} ===")
    with open(input_text_file, "r") as file:
        return file.read()


def run_pipeline(input_text_file=None, config_path=None):
    """Run the complete content generation pipeline"""
    try:
        run_id = generate_run_id()
        print(f"\n=== Starting Pipeline Run: {run_id} ===")

        # Load configuration
        print(f"Loading config from: {config_path or 'based_config.json'}")
        config = load_config(config_path)
        directories = get_directories(config)

        # Create directories from config
        for dir_path in directories.values():
            if dir_path:  # Only create if path is not None/empty
                os.makedirs(dir_path, exist_ok=True)

        # Determine content source
        if input_text_file:
            content = process_text_file(input_text_file)
            print(f"\n=== Content: {content[:100]} ===")
        else:
            content, error = process_articles(run_id, config=config)
            if error:
                return error

        # Step 2: Create podcast script
        create_dialogue(
            main_content=content,
            output_file=f"podcast_script_{run_id}.txt",
            config=config,  # Pass the whole config
        )
        print("podcast_script_done")

        # Step 3: Generate audio files
        print(f"\n=== Generating Audio Files ===")
        audio_files = create_audio(
            script_path=f"podcast_script_{run_id}.txt",
            output_prefix=f"audio_{run_id}",
            run_id=run_id,
            config=config,  # Pass the whole config
        )
        if not audio_files:
            return "Failed to generate audio files"

        # Step 4: Create final podcast episode
        print(f"\n=== Creating Final Podcast Episode ===")
        segments = load_audio(run_id=run_id, config=config)
        combined_audio = stitch_audio(segments)
        processed_audio = apply_postprocessing(combined_audio)
        final_audio = add_intro_outro(
            processed_audio,
            intro_path="helper/Ready for the Show.mp3",  # Update with your actual paths
            outro_path="helper/Ready for the Show.mp3",
            intro_start=1000,
            intro_end=5000,
            outro_start=2000,
            outro_end=None,
            fade_duration=2000,
        )
        output_filename = f"episode_{run_id}.mp3"
        save_audio(final_audio, output_filename, run_id=run_id, config=config)
        episode_path = os.path.join(directories["episodes"], run_id, output_filename)

        return {
            "status": "success",
            "run_id": run_id,
            "curated_post": content,
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
        help="Path to JSON configuration file. If not provided, uses base config.",
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
