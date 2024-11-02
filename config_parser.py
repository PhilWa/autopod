import json
import os


def load_config(config_path=None):
    """
    Load the configuration from a JSON file.
    Args:
        config_path: Path to config file. If None, uses default "based_config.json"
    """
    # Use default path if none provided
    config_path = config_path or "based_config.json"

    # Get absolute path relative to the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, config_path)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file {config_path} not found.")

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {str(e)}")
    except Exception as e:
        raise Exception(f"Error loading config: {str(e)}")


def get_directories(config):
    return config.get("directories", {})


def get_models(config):
    return config.get("models", {})


def get_speakers(config):
    return config.get("speakers", {})


def get_podcast_styles(config):
    return config.get("podcast_styles", {})


def get_prompts(config):
    return config.get("prompts", {})


def get_screenwriter(config):
    return config.get("screenwriter", {})


def get_briefing(config):
    return config.get("briefing", {})


def get_data_dir(config):
    directories = get_directories(config)
    return directories.get("data", ".")


# Formatting functions for prompts
def format_script_prompt(config, main_content):
    prompts = get_prompts(config)
    podcast_styles = get_podcast_styles(config)
    speakers = get_speakers(config)
    script_prompt = prompts["script"]

    user_prompt = script_prompt["user"].format(
        intro_style=podcast_styles["intro"],
        content_style=podcast_styles["content"],
        outro_style=podcast_styles["outro"],
        main_content=main_content,
        speaker1_name=speakers["1"]["name"],
        speaker2_name=speakers["2"]["name"],
    )

    return {
        "system": script_prompt["system"],
        "user": user_prompt,
    }


def format_screenwriter_prompt(config, raw_script):
    screenwriter = get_screenwriter(config)
    speakers = get_speakers(config)
    screenwriter_prompt = screenwriter["screenwriter"]

    system_prompt = screenwriter_prompt["system"].format(
        speaker_1=speakers["1"]["personality"],
        speaker_2=speakers["2"]["personality"],
    )

    user_prompt = f"Here is the podcast transcript:\n\n{raw_script}"

    return {
        "system": system_prompt,
        "user": user_prompt,
    }


def format_linkedin_post_prompt(config, article_content):
    models = get_models(config)
    content = "\n".join(
        [f"{title}\n{excerpt}\n{url}" for title, excerpt, url in article_content]
    )

    messages = [
        {
            "role": "system",
            "content": "You are a professional content writer specializing in social media posts.",
        },
        {
            "role": "user",
            "content": f"Create a LinkedIn post summarizing the following articles:\n{content}",
        },
    ]

    return messages


def format_distillation_prompt(config, chunk):
    models = get_models(config)
    prompts = get_prompts(config)

    messages = [
        {"role": "system", "content": prompts["distillation"]["system"]},
        {"role": "user", "content": prompts["distillation"]["user"].format(text=chunk)},
    ]

    return messages


def format_briefing_prompt(config, content):
    briefing = get_briefing(config)
    messages = [
        {"role": "system", "content": briefing["analyst"]["system"]},
        {"role": "user", "content": content},
    ]
    return messages


def format_audio_generation_prompt(
    config, speaker_info, voice_expression, recent_history, text
):
    history_text = " ".join(
        [f"{msg['role']}: {msg['content']}" for msg in recent_history]
    )
    system_prompt = f"You are {speaker_info['name']}, {speaker_info['personality']}. Previous conversation: {history_text}. This is how you say it based on voice coaching: {voice_expression}"

    user_prompt = f"Say exactly the following text in the appropriate voice given the previous conversation and what you have learned from the voice coaching. *Text to say:* {text}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    return messages


# Add any other helper functions as needed
