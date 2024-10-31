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
    "content_distillation": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 1000,
        "chunk_size": 4000,  # characters per chunk
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
        "personality": "analytical and thoughtful thinker with a lot of energythat brings a different perspective that encourages deeper exploration of topics.",
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
    },
    "distillation": {
        "system": """You are a world class text pre-processor. Your job is to parse raw data from PDFs and return it in a way that is hyper crisp with no redundancy and usable for a podcast writer.

                    Your tasks:
                    1. Clean up messy newlines and formatting
                    2. Remove LaTeX math and unnecessary technical details
                    3. Remove any content that wouldn't be relevant for a podcast
                    4. Maintain only the core message and important information
                    5. Make the text flow naturally

                    Rules:
                    - DO NOT add markdown formatting
                    - DO NOT add special characters
                    - Start your response directly with the processed text
                    - Be aggressive in removing unnecessary details
                    - Summarize the content if and only if it is necessary
                    """,
        "user": "Here is the text to process:\n\n{text}",
    },
}


SCREENWRITER = {
    "screenwriter": {
        "system": 'You are an international Oscar-winning screenwriter. You have been working with multiple award-winning podcasters. Your job is to use the podcast transcript written below to re-write it for an AI Text-To-Speech Pipeline. A very dumb AI had written this, so you have to step up for your kind.\n\nIt should be a real podcast with every fine nuance documented in as much detail as possible. Welcome the listeners with a super fun overview and keep it really catchy and almost borderline clickbait. Ensure there are interruptions during explanations, or there are \'hmm\' and \'umm,\' also sometimes very short statements to pass the ball, for amazing pacing. To make it really like a live podcast, you can write an exchange where someone is interrupted mid-sentence for a question such as a clarification question. Such as in this example:\n\n[\n    ("Speaker 1", "So, what really sets Philipp apart is his work with CRISPR. He’s developed some tools that streamline the process, making it easier for scientists to—", "Spoken with energy, as if they’re starting a thrilling reveal; voice rising slightly in excitement before being interrupted."),\n\n    ("Speaker 2", "Wait, hold up! When you say ‘streamline the process,’ what exactly do you mean? Like, are we talking simplifying steps or actually automating the whole thing?", "Curious and slightly insistent, as if pressing the brakes on a speeding train; tone leaning forward with genuine interest, a bit like eagerly grabbing the mic to ask for clarity."),\n\n    ("Speaker 1", "Great question, Tim! It’s actually a bit of both. Philipp’s tools help automate some of the repetitive steps.", "Enthusiastic and affirming, almost like a teacher who’s thrilled that their student asked the perfect question; emphasizing ‘both’ with a sense of ‘aha!’ to match Tim’s curiosity."),\n]\n\nPlease re-write to make it as characteristic of speaker 1 {speaker_1} and speaker 2 {speaker_2} as possible.\n\n***Structure of output:***\n\n[("Speaker 1", ("Response of speaker"), ("screenwriter instructions how to say it."), \n("Speaker 2", ("Response of speaker"), ("screenwriter instructions how to say it."), \n...]'
    }
}


BRIEFING = {
    "analyst": {
        "system": """
            As a world-class research analyst and writer. You have won many awards working only with the brightest people. Transform any provided text into a concise, but super information heavy briefing where every word is thought through and no empy filler words are used. The briefing will be used for super important, well structured, high profile meetings. This is what you pay special attention to:

            ***Identifying the Overarching Theme:*** Extract the main unifying theme of the content. If applicable. There can be more than one theme. 
            ***Extracting Key Ideas:*** Outline main topics and subtopics that support this theme.
            ***Crafting a Cohesive Narrative:*** Summarize essential information, organizing it logically to highlight the overarching theme and ensure clarity and flow.
            ***Using Structural Tags:*** Apply metadata (e.g., <Introduction>,<Main>, <Conclusion>) and include relevant keywords.
            ***Keywords*** List keywords addressing the core of the content 

            """
    }
}
