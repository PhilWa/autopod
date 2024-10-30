from pydub import AudioSegment
from pydub.effects import compress_dynamic_range, normalize
import random
import os
from config import AUDIO_DIR, EPISODE_DIR


def load_audio(run_id=None, file_type="mp3"):
    # List all files in AUDIO_DIR with the given run_id in their name
    audio_files = [
        f
        for f in os.listdir(AUDIO_DIR)
        if f.endswith(f".{file_type}") and (run_id in f if run_id else True)
    ]

    # Sort files by creation time (oldest to latest)
    audio_files = sorted(
        audio_files, key=lambda x: os.path.getctime(os.path.join(AUDIO_DIR, x))
    )

    # Load all sorted audio segments
    return [
        AudioSegment.from_file(os.path.join(AUDIO_DIR, file)) for file in audio_files
    ]


def stitch_audio(segments, pause_range=(500, 2000)):
    combined = AudioSegment.empty()
    for i, segment in enumerate(segments):
        if i > 0:
            # Add a random pause between segments for natural flow
            pause_length = random.randint(*pause_range)
            combined += AudioSegment.silent(duration=pause_length)
        combined += segment
    return combined


def apply_postprocessing(audio, add_ambient=False, ambient_path=None):
    print("🔄 applying postprocessing")
    # Compress and normalize
    audio = compress_dynamic_range(audio)
    print("🔄 normalizing audio")
    audio = normalize(audio)

    # Optional: Add ambient sound for consistency in background tone
    if add_ambient:
        print("🔄 adding ambient sound")
        ambient = AudioSegment.from_file(
            os.path.join(AUDIO_DIR, ambient_path)
        ).apply_gain(-25)
        looped_ambient = (ambient * ((len(audio) // len(ambient)) + 1))[: len(audio)]
        audio = audio.overlay(looped_ambient)
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
    # Load and slice intro and outro segments
    intro = AudioSegment.from_file(os.path.join(AUDIO_DIR, intro_path))[
        intro_start:intro_end
    ].fade_in(fade_duration)
    outro = AudioSegment.from_file(os.path.join(AUDIO_DIR, outro_path))[
        outro_start:outro_end
    ].fade_out(fade_duration)

    return intro + audio + outro


def save_audio(audio, output_path, run_id=None):
    # Define the output path in EPISODE_DIR with run_id if provided
    output_dir = os.path.join(EPISODE_DIR, run_id if run_id else "")
    os.makedirs(output_dir, exist_ok=True)
    full_output_path = os.path.join(output_dir, output_path)
    audio.export(full_output_path, format="mp3")


def main(
    run_id,
    intro_path,
    outro_path,
    output_file_name,
    intro_start=0,
    intro_end=None,
    outro_start=0,
    outro_end=None,
    fade_duration=2000,
    add_ambient=True,
    pause_range=(500, 2000),
):
    # Load and process audio files
    print("🤖 loading audio files  ")
    segments = load_audio(run_id=run_id)
    print("🔄 stitching audio files")
    combined_audio = stitch_audio(segments, pause_range=pause_range)
    print("🥳 applying postprocessing")
    processed_audio = apply_postprocessing(combined_audio)
    print("😎 adding intro and outro")
    final_audio = add_intro_outro(
        processed_audio,
        intro_path,
        outro_path,
        intro_start,
        intro_end,
        outro_start,
        outro_end,
        fade_duration,
    )
    print("💾 saving audio")
    save_audio(final_audio, output_file_name, run_id=run_id)


# Example usage
if __name__ == "__main__":
    main(
        run_id="example_run",
        intro_path="helper/Ready for the Show.mp3",
        outro_path="helper/Ready for the Show.mp3",
        output_file_name=f"episode.mp3",
        intro_start=1000,
        intro_end=5000,
        outro_start=2000,
        outro_end=None,
        fade_duration=2000,
        add_ambient=True,
        pause_range=(500, 2000),
    )
