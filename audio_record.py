import queue
import wave
import numpy as np
import sounddevice as sd

# Set to None to automatically select system default microphone.
# If you need a specific hardware index, set it here (e.g., DEVICE_INDEX = 1)
DEVICE_INDEX = None 
SAMPLE_RATE = 16000
CHANNELS = 1
MAX_BAR_LENGTH = 30

# Thread-safe queue to hold raw audio frames in memory
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print(f"Stream status: {status}", flush=True)
    
    # Store audio frames into buffer
    audio_queue.put(indata.copy())
    
    # Visual feedback
    volume_norm = np.linalg.norm(indata) * 10
    bar_length = min(int(volume_norm), MAX_BAR_LENGTH)
    visual_bar = '|' * bar_length
    print(f"Recording... [{visual_bar:<{MAX_BAR_LENGTH}}]", end="\r")

def save_wav(filename, audio_data, sample_rate):
    """Converts floating point audio array to 16-bit PCM WAV file."""
    audio_int16 = (audio_data * 32767).astype(np.int16)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit PCM = 2 bytes per sample
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())

def main():
    # Automatically resolve default input device if DEVICE_INDEX is None
    target_device = DEVICE_INDEX if DEVICE_INDEX is not None else sd.default.device[0]
    dev_info = sd.query_devices(target_device, 'input')
    
    print(f"Using Input Device: {dev_info['name']} (Index {dev_info['index']})")
    print("Recording started. Speak a short sentence...")
    print(">>> Press [ENTER] to stop recording and save 'test_record.wav' <<<\n")
    
    with sd.InputStream(device=target_device, samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback):
        input()
        
    print("\n\nStopping recording and writing to disk...")
    
    # Pull all audio chunks out of the queue
    recorded_chunks = []
    while not audio_queue.empty():
        recorded_chunks.append(audio_queue.get())
    
    if recorded_chunks:
        full_audio = np.concatenate(recorded_chunks, axis=0)
        save_wav("test_record.wav", full_audio, SAMPLE_RATE)
        print("Successfully saved 'test_record.wav' in your project folder!")
    else:
        print("No audio captured.")

if __name__ == "__main__":
    main()