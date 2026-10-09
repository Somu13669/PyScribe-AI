from transcriber import transcribe_audio
from llm_test import ask_ollama

def main():
    print("=== PyScribe AI Pipeline ===")
    
    audio_file = "test_record.wav"
    print(f"\n[1/2] Transcribing: {audio_file}")
    transcript = transcribe_audio(audio_file)
    print(f"Recognized Speech: \"{transcript}\"")
    
    if not transcript:
        print("[!] No speech detected. Try recording audio again.")
        return

    print("\n[2/2] Querying Qwen2.5 on GPU 1...")
    response = ask_ollama(transcript)
    print(f"\nLLM Response:\n{response}")

if __name__ == "__main__":
    main()