import base64
from openai import OpenAI
from dotenv import load_dotenv
import re
import os
from collections import deque
import datetime
from config import AUDIO_DIR, SCRIPT_DIR, SPEAKERS, MODELS
from utils import get_latest_file


def read_podcast_script(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def parse_script(content):
    # Split the content into lines and process each line
    lines = content.strip().split("\n")
    parsed_lines = []

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue

        # Look for speaker pattern with square brackets
        match = re.match(r"<Speaker (\d)> \[(.*)\]", line.strip())
        if match:
            speaker_num, text = match.groups()
            parsed_lines.append(
                {
                    "speaker": int(speaker_num),
                    "text": text.strip(),  # This will remove the square brackets
                }
            )

    return parsed_lines


def generate_audio(
    client, text, speaker_history, speaker_info, voice, file_prefix, index, models=None
):
    # Use provided models config or fall back to default
    models = models or MODELS

    # Print debugging information
    print(f"\n=== Generating Audio for Part {index} ===")
    print(f"Speaker: {speaker_info['name']}")
    print(f"Voice: {voice}")
    print(f"Personality: {speaker_info['personality']}")
    print(f"Text to process: {text[:100]}...")  # Show first 100 chars

    # Show conversation history
    recent_history = (
        speaker_history[-2:] if len(speaker_history) >= 2 else speaker_history
    )
    history_text = " ".join(
        [f"{msg['role']}: {msg['content']}" for msg in recent_history]
    )
    print(f"History text: {history_text}")
    print(f"Text: {text}")
    text = f"Say the following text in the appropriate voice given the previous conversation: {text}"
    try:
        completion = client.chat.completions.create(
            model=models["podcast_audio"]["model"],
            modalities=models["podcast_audio"]["modalities"],
            audio={"voice": voice, "format": models["podcast_audio"]["format"]},
            messages=[
                {
                    "role": "system",
                    "content": f"You are {speaker_info['name']}, {speaker_info['personality']}. Previous conversation: {history_text}",
                },
                {"role": "user", "content": text},
            ],
        )

        wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)
        filename = os.path.join(AUDIO_DIR, f"{file_prefix}_part_{index}.wav")

        with open(filename, "wb") as f:
            f.write(wav_bytes)

        print(f"Successfully generated: {filename}")
        return filename

    except Exception as e:
        print(f"Error generating audio: {str(e)}")
        print(f"Full error details: {e.__dict__}")
        raise


def main(script_path=None, output_prefix=None, run_id=None, models=None, speakers=None):
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Use provided config or fall back to default
    models = models or MODELS
    speakers = speakers or SPEAKERS

    print("\n=== Starting Script Processing ===")
    # Step 1: Process the script
    script_path = "podcast_script_20241029_214055.txt"
    if script_path:
        print(f"Using provided script path: {script_path}")
        script_path = os.path.join(SCRIPT_DIR, script_path)
        content = read_podcast_script(script_path)
    else:
        print("No script path provided, using latest script")
        script_path, content = get_latest_file(SCRIPT_DIR, ".txt")

    # Parse the script
    parsed_lines = parse_script(content)

    # Keep track of conversation history
    speaker_history = deque(maxlen=5)

    # Use run_id for timestamp if provided
    timestamp = run_id or datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Step 2: Generate audio for each line
    audio_files = []
    for i, line in enumerate(parsed_lines):
        print(f"\nProcessing line {i+1} of {len(parsed_lines)}")
        speaker_num = line["speaker"]
        voice = speakers[speaker_num]["voice"]

        try:
            # Use output_prefix if provided, otherwise use timestamp
            file_prefix = output_prefix or f"audio_{timestamp}"
            print(line["text"])
            audio_file = generate_audio(
                client,
                line["text"],
                list(speaker_history),
                speakers[speaker_num],
                voice,
                file_prefix,
                i,
                models=models,
            )
            speaker_history.append(
                {"role": f"Speaker {line['speaker']}", "content": line["text"]}
            )

            audio_files.append(audio_file)

        except Exception as e:
            print(f"Failed to process line {i+1}: {str(e)}")
            break

    return audio_files


if __name__ == "__main__":
    audio_files = main()
    for file in audio_files:
        print(file)
