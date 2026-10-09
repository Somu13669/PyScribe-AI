import os
import sys

# Find and inject all NVIDIA DLL bin directories into system PATH and DLL search order
venv_base = sys.prefix
nvidia_base = os.path.join(venv_base, "Lib", "site-packages", "nvidia")

if os.path.exists(nvidia_base):
    for root, dirs, files in os.walk(nvidia_base):
        if root.endswith("bin"):
            os.add_dll_directory(root)
            os.environ["PATH"] = root + os.path.pathsep + os.environ["PATH"]

from faster_whisper import WhisperModel

def transcribe_audio(audio_path: str = "test_record.wav") -> str:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    model = WhisperModel(
        "large-v3-turbo", 
        device="cuda", 
        device_index=0, 
        compute_type="float16"
    )

    segments, info = model.transcribe(audio_path, beam_size=5, vad_filter=True)
    return " ".join(segment.text for segment in segments).strip()

if __name__ == "__main__":
    audio_file = "test_record.wav"
    print(f"Transcribing audio file on GPU 0: {audio_file}")
    transcript = transcribe_audio(audio_file)
    print(f"\nTranscript:\n\"{transcript}\"")