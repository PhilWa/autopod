import os
from datetime import datetime
from pydub import AudioSegment
from config import AUDIO_DIR, EPISODE_DIR


def add_audio_effects(audio_segment, fade_duration_ms=5000):
    """Add fade effects to an audio segment"""
    return audio_segment.fade_in(fade_duration_ms).fade_out(fade_duration_ms)


def create_podcast_episode(audio_files=None, output_file=None):
    # Load and prepare intro/outro music
    music_path = os.path.join(AUDIO_DIR, "helper", "Ready for the Show.mp3")
    if os.path.exists(music_path):
        # Prepare intro music
        intro_music = AudioSegment.from_mp3(music_path)
        intro_music = intro_music[:15000]  # First 15 seconds
        intro_music = add_audio_effects(intro_music, fade_duration_ms=5000)
        intro_music = intro_music - 15  # Reduce volume by 15 dB

        # Prepare outro music
        outro_music = AudioSegment.from_mp3(music_path)
        outro_music = outro_music[:15000]  # First 15 seconds
        outro_music = add_audio_effects(outro_music, fade_duration_ms=5000)
        outro_music = outro_music - 15  # Reduce volume by 15 dB
    else:
        intro_music = AudioSegment.empty()
        outro_music = AudioSegment.empty()
        print("Warning: Music file not found")

    # Handle main content
    if not audio_files:
        audio_files = [f for f in os.listdir(AUDIO_DIR) if f.endswith(".wav")]
        if not audio_files:
            return None

        files_by_date = {}
        for file in audio_files:
            date_part = file.split("_")[0]
            if date_part in files_by_date:
                files_by_date[date_part].append(file)
            else:
                files_by_date[date_part] = [file]

        latest_date = max(files_by_date.keys())
        audio_files = sorted(files_by_date[latest_date])

    # Combine main content first
    combined = AudioSegment.empty()
    silence = AudioSegment.silent(duration=500)

    # Add main content
    for file in audio_files:
        file_path = os.path.join(AUDIO_DIR, file) if not os.path.isabs(file) else file
        audio_segment = AudioSegment.from_wav(file_path)
        combined += audio_segment + silence

    # Overlay intro music with the beginning of the podcast
    if len(intro_music) > 0:
        start_segment = combined[:15000]
        overlay_segment = start_segment.overlay(intro_music)
        combined = overlay_segment + combined[15000:]

    # Overlay outro music with the end of the podcast
    if len(outro_music) > 0:
        end_segment = combined[-15000:]  # Last 15 seconds
        overlay_segment = end_segment.overlay(outro_music)
        combined = combined[:-15000] + overlay_segment

    # Add final fade out
    combined = combined.fade_out(5000)  # 5-second fade out at the end

    # Save the combined episode
    if output_file:
        output_path = os.path.join(EPISODE_DIR, output_file)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(EPISODE_DIR, f"TheCorner_{timestamp}.wav")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    combined.export(output_path, format="wav")

    return output_path


if __name__ == "__main__":
    output_file = create_podcast_episode()
    if output_file:
        print(f"Created podcast episode: {output_file}")
    else:
        print("No audio files found to process")
