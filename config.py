import os

# Directory Configuration
DATA_DIR = os.path.join("data")
AUDIO_DIR = os.path.join(DATA_DIR, "audio")
POST_DIR = os.path.join(DATA_DIR, "posts")
SCRIPT_DIR = os.path.join(DATA_DIR, "scripts")
EPISODE_DIR = os.path.join(DATA_DIR, "episodes")

# Create all directories
for dir_path in [DATA_DIR, AUDIO_DIR, POST_DIR, SCRIPT_DIR, EPISODE_DIR]:
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
    "1": {
        "name": "Elly",
        "voice": "shimmer",
        "personality": "energetic and enthusiastic tech expert with vivid descriptions and expressive delivery",
    },
    "2": {
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


PROMPTS = {
    "script": {
        "system": """You are a podcast script writer. Create a natural and engaging conversation between two seasoned podcast hosts.
    
    **Format the output in the following way.**
    <Speaker 1> [Content of speaker 1's line]
    <Speaker 2> [Content of speaker 2's line]
    Remark: It is essential that <Speaker 1> and <Speaker 2> are used exactly as shown above.
    
    **The script should have three parts:**
    1. An introduction
    2. Main content discussion
    3. An outro
    
    Make the conversation flow naturally and maintain the specified style for each section.""",
        "user": """Create a podcast script with the following specifications:
    Use natural fillers like 'mm-hmm' sparingly to simulate authentic interaction during pauses or when someone else is speaking.
    Includes also very short back in forth. Incorporate personal anecdotes to make the content relatable. Add active listening cues such as 'I see' or 'Right' to show engagement in conversation including follow up questions.
    
    **Section styles:**
    Introduction style: {intro_style}
    Main content style: {content_style}
    Outro style: {outro_style}

    ** Content to discuss:**
    Main content to discuss: {main_content}

    **Speaker names:**
    Speaker 1 is called {speaker1_name}
    Speaker 2 is called {speaker2_name}

    **Remark:**
    Make sure the transitions between sections feel natural and maintain engaging dialogue throughout. The main content should be the most important part and should be the longest part of the script.""",
    }
}
