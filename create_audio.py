import base64
from openai import OpenAI
from dotenv import load_dotenv
import os
from collections import deque
import datetime
from utils import get_latest_file

from config_parser import (
    load_config,
    get_models,
    get_speakers,
    get_directories,
    format_audio_generation_prompt,
)


def read_podcast_script(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def parse_script(content):
    """Parse the screenplay format script"""
    try:
        # Evaluate the string as a Python list of tuples
        script_data = eval(content)
        parsed_lines = []

        for speaker_tuple in script_data:
            if len(speaker_tuple) >= 3:  # ("Speaker X", "text", "expression")
                speaker, text, voice_expression = speaker_tuple[:3]
                # Extract speaker number from "Speaker X"
                speaker_num = speaker.split()[1]
                parsed_lines.append(
                    {
                        "speaker": speaker_num,
                        "text": text.strip(),
                        "voice_expression": voice_expression.strip(),
                    }
                )

        return parsed_lines
    except Exception as e:
        print(f"Error parsing script: {e}")
        return []


def generate_audio(
    client,
    text,
    speaker_history,
    speaker_info,
    voice,
    file_prefix,
    index,
    voice_expression,
    config,
):
    models = get_models(config)

    # Get the last two messages from history
    recent_history = (
        speaker_history[-2:] if len(speaker_history) >= 2 else speaker_history
    )

    # Format the messages using config_parser
    messages = format_audio_generation_prompt(
        config,
        speaker_info,
        voice_expression,
        recent_history,
        text,
    )

    try:
        completion = client.chat.completions.create(
            model=models["podcast_audio"]["model"],
            modalities=models["podcast_audio"]["modalities"],
            audio={"voice": voice, "format": models["podcast_audio"]["format"]},
            messages=messages,
        )

        wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)
        filename = os.path.join(file_prefix + f"_part_{index+1}.wav")

        with open(filename, "wb") as f:
            f.write(wav_bytes)

        print(f"Successfully generated: {filename}")
        return filename

    except Exception as e:
        print(f"Error generating audio: {str(e)}")
        print(f"Full error details: {e.__dict__}")
        raise


def main(
    script_path=None,
    output_prefix=None,
    run_id=None,
    config=None,
):
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    if config is None:
        raise ValueError("Config must be provided")

    models = get_models(config)
    speakers = get_speakers(config)
    directories = get_directories(config)
    audio_dir = directories.get("audio", "data/audio")
    script_dir = directories.get("scripts", "data/scripts")

    print("\n=== Starting Script Processing ===")
    if script_path:
        print(f"Using provided script path: {script_path}")
        script_path = os.path.join(script_dir, script_path)
        content = read_podcast_script(script_path)
    else:
        print("No script path provided, using latest script")
        script_path, content = get_latest_file(script_dir, ".txt")

    # Parse the script
    parsed_lines = parse_script(content)
    if not parsed_lines:
        print("Failed to parse script")
        return []

    speaker_history = deque(maxlen=5)
    timestamp = run_id or datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    audio_files = []
    for i, line in enumerate(parsed_lines):
        print(f"\nProcessing line {i+1} of {len(parsed_lines)}")
        speaker_num = line["speaker"]
        voice = speakers[speaker_num]["voice"]

        try:
            file_prefix = output_prefix or f"audio_{timestamp}"
            file_prefix = os.path.join(audio_dir, file_prefix)
            audio_file = generate_audio(
                client,
                line["text"],
                list(speaker_history),
                speakers[speaker_num],
                voice,
                file_prefix,
                i,
                line["voice_expression"],
                config,
            )
            speaker_history.append(
                {"role": f"Speaker {speaker_num}", "content": line["text"]}
            )
            audio_files.append(audio_file)

        except Exception as e:
            print(f"Failed to process line {i+1}: {str(e)}")
            break

    return audio_files


if __name__ == "__main__":
    config = load_config()
    audio_files = main(config=config)
    for file in audio_files:
        print(file)
