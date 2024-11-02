from pydub import AudioSegment
from pydub.effects import compress_dynamic_range, normalize
import os
import json

# Load base configuration
with open("based_config.json", "r") as f:
    config = json.load(f)
    AUDIO_DIR = config["directories"]["audio"]
    EPISODE_DIR = config["directories"]["episodes"]


def load_audio(run_id=None, directories=None):
    directories = directories or {"audio": AUDIO_DIR}
    audio_dir = directories["audio"]

    # Load all audio files for the given run_id
    audio_files = [
        os.path.join(audio_dir, f)
        for f in os.listdir(audio_dir)
        if f.startswith(f"audio_{run_id}_part_") and f.endswith(".wav")
    ]
    audio_files.sort()
    segments = [AudioSegment.from_wav(file) for file in audio_files]
    return segments


def stitch_audio(segments):
    combined = AudioSegment.empty()
    for segment in segments:
        combined += segment
    return combined


def apply_postprocessing(audio):
    # Apply normalization and compression
    audio = normalize(audio)
    audio = compress_dynamic_range(audio)
    return audio


def add_intro_outro(
    audio,
    intro_path,
    outro_path,
    intro_start=0,
    intro_end=None,
    outro_start=0,
    outro_end=None,
    fade_duration=2000,
):
    intro = AudioSegment.from_file(intro_path)
    outro = AudioSegment.from_file(outro_path)

    if intro_end:
        intro = intro[intro_start:intro_end]
    else:
        intro = intro[intro_start:]

    if outro_end:
        outro = outro[outro_start:outro_end]
    else:
        outro = outro[outro_start:]

    # Fade in and out
    intro = intro.fade_in(fade_duration).fade_out(fade_duration)
    outro = outro.fade_in(fade_duration).fade_out(fade_duration)

    final_audio = intro + audio + outro
    return final_audio


def save_audio(audio, output_filename, run_id=None, directories=None):
    directories = directories or {"episodes": EPISODE_DIR}
    episode_dir = directories["episodes"]

    if run_id:
        episode_dir = os.path.join(episode_dir, run_id)
        os.makedirs(episode_dir, exist_ok=True)

    output_path = os.path.join(episode_dir, output_filename)
    audio.export(output_path, format="mp3")
    print(f"Episode saved to {output_path}")
