import os

# Directory Configuration
DATA_DIR = os.path.join("data")
AUDIO_DIR = os.path.join(DATA_DIR, "audio")
POST_DIR = os.path.join(DATA_DIR, "posts")
SCRIPT_DIR = os.path.join(DATA_DIR, "scripts")
POD_DIR = os.path.join(DATA_DIR, "pod")

# Create all directories
for dir_path in [DATA_DIR, AUDIO_DIR, POST_DIR, SCRIPT_DIR, POD_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Model Configuration
MODELS = {
    "linkedin_post": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 2000,
    },
    "podcast_script": {
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 4000,
    },
    "podcast_audio": {
        "model": "gpt-4o-audio-preview",
        "modalities": ["text", "audio"],
        "format": "wav",
    },
}

# Speaker Configuration
SPEAKERS = {
    1: {
        "name": "Elly",
        "voice": "shimmer",
        "personality": "energetic and enthusiastic tech expert with vivid descriptions and expressive delivery",
    },
    2: {
        "name": "Tim",
        "voice": "onyx",
        "personality": "analytical and thoughtful thinker that brings a balanced perspective that encourages deeper exploration of topics",
    },
}

# Style Configuration
PODCAST_STYLES = {
    "intro": "energetic and engaging, with friendly banter between hosts",
    "content": "informative and professional, maintaining audience interest",
    "outro": "warm and inviting, encouraging listener engagement",
}
