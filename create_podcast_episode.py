import os
from datetime import datetime
from pydub import AudioSegment
from config import AUDIO_DIR, POD_DIR


def create_podcast_episode(audio_files=None, output_file=None):
    if not audio_files:
        # Get all wav files in the audio directory
        audio_files = [f for f in os.listdir(AUDIO_DIR) if f.endswith(".wav")]
        if not audio_files:
            return None

        # If no specific files provided, use the latest ones
        files_by_date = {}
        for file in audio_files:
            date_part = file.split("_")[0]
            if date_part in files_by_date:
                files_by_date[date_part].append(file)
            else:
                files_by_date[date_part] = [file]

        latest_date = max(files_by_date.keys())
        audio_files = sorted(files_by_date[latest_date])

    # Create combined episode
    combined = AudioSegment.empty()
    silence = AudioSegment.silent(duration=500)

    # Combine all audio files with silence in between
    for file in audio_files:
        file_path = os.path.join(AUDIO_DIR, file) if not os.path.isabs(file) else file
        audio_segment = AudioSegment.from_wav(file_path)
        combined += audio_segment + silence

    # Save the combined episode
    if output_file:
        output_path = os.path.join(POD_DIR, output_file)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(POD_DIR, f"TheCorner_{timestamp}.wav")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    combined.export(output_path, format="wav")

    return output_path


if __name__ == "__main__":
    output_file = create_podcast_episode()
    if output_file:
        print(f"Created podcast episode: {output_file}")
    else:
        print("No audio files found to process")
