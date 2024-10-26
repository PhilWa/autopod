import os
from datetime import datetime
from dotenv import load_dotenv
from get_information import get_recent_articles
from create_linkedin_post import create_linkedin_post, get_latest_articles
from create_podcast_script import create_podcast_script
from create_podcast_audio import main as create_audio
from create_podcast_episode import create_podcast_episode
from config import (
    DATA_DIR,
    AUDIO_DIR,
    SCRIPT_DIR,
    POST_DIR,
    PODCAST_STYLES,
)


def ensure_directories():
    """Ensure all required directories exist"""
    for dir_path in [DATA_DIR, AUDIO_DIR, SCRIPT_DIR, POST_DIR]:
        os.makedirs(dir_path, exist_ok=True)


def generate_run_id():
    """Generate a unique run ID based on timestamp"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def run_pipeline():
    """Run the complete content generation pipeline"""
    try:
        run_id = generate_run_id()
        print(f"\n=== Starting Pipeline Run: {run_id} ===")

        # Step 1: Fetch and store articles
        get_recent_articles()

        # Step 2: Get latest articles and create LinkedIn post
        articles = get_latest_articles()
        if not articles:
            return "No articles found"

        print(f"\n=== Creating LinkedIn Post ===")
        article_content = [(article[1], article[2], article[3]) for article in articles]
        linkedin_post = create_linkedin_post(
            article_content, output_file=f"linkedin_post_{run_id}.txt"
        )

        # Step 3: Create podcast script using styles from config
        print(f"\n=== Creating Podcast Script ===")
        create_podcast_script(
            main_content=linkedin_post,
            intro_style=PODCAST_STYLES["intro"],
            content_style=PODCAST_STYLES["content"],
            outro_style=PODCAST_STYLES["outro"],
            output_file=f"podcast_script_{run_id}.txt",
        )

        # Step 4: Generate audio files
        print(f"\n=== Generating Audio Files ===")
        audio_files = create_audio(
            script_path=f"podcast_script_{run_id}.txt", output_prefix=f"audio_{run_id}"
        )
        if not audio_files:
            return "Failed to generate audio files"

        # Step 5: Create final podcast episode
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
    ensure_directories()
    result = run_pipeline()

    if isinstance(result, dict):
        print("\n=== Pipeline Completed Successfully ===")
        print(f"Episode created: {result['episode_path']}")
    else:
        print(f"\n=== Pipeline Failed ===\n{result}")


if __name__ == "__main__":
    main()
