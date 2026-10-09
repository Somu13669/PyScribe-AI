import os
import queue
import wave
import threading
import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

SAMPLE_RATE = 16000
CHANNELS = 1
OUTPUT_FILENAME = "test_record.wav"

class PyScribeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyScribe AI")
        self.root.geometry("600x520")
        self.root.resizable(False,False)

        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.stream = None

        self._create_widgets()

    def _create_widgets(self):

        header = ttk.Label(self.root, text="pyscribeAIAss", font=("helvetica",16))
        header.pack(pady=10)

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.btn_record = ttk.Button(btn_frame, text="start rec",command=self.toggle_recording)
        self.btn_record.grid(row=0, column=0, padx=10)

        self.btn_send = ttk.Button(btn_frame, text="send to LLM", command=self.send_to_llm_thread, state=tk.DISABLED)
        self.btn_send.grid(row=0, column=1, padx=10)

        self.lbl_status = ttk.Label(self.root, text='Status: ready')
        self.lbl_status.pack(pady=5)

        lbl_response = ttk.Label(self.root, text="LLMresponse:")
        lbl_response.pack(anchor="w", padx=20, pady=(10,2))

        self.txt_response = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=65, height=15)
        self.txt_response.pack(padx=20, pady=5)

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.audio_queue = queue.Queue()

        self.btn_record.config(text="stop rec")
        self.btn_send.config(state=tk.DISABLED)
        self.lbl_status.config(text="status: recording")
        target_device = sd.default.device[0]
        self.stream = sd.InputStream(
            device=target_device,
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            callback=self._audio_callback
        )
        self.stream.start()

    def _audio_callback(self, indata, frames, time, status):
        if self.is_recording:
            self.audio_queue.put(indata.copy())

    def stop_recording(self):
        self.is_recording = False

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        self._save_wav_file()


        self.btn_record.config(text="start rec")

        self.btn_send.config(state=tk.NORMAL)
        self.lbl_status.config(text="recording saved")
    def _save_wav_file(self):
        recorded_chunks =[]
        while not self.audio_queue.empty():
            recorded_chunks.append(self.audio_queue.get())

        if recorded_chunks:
            full_audio = np.concatenate(recorded_chunks, axis=0)
            audio_int16 = (full_audio *32767).astype(np.int16)

            with wave.open(OUTPUT_FILENAME, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio_int16.tobytes())


    def send_to_llm_thread(self):
        self.btn_send.config(state=tk.DISABLED)
        self.btn_record.config(state=tk.DISABLED)
        self.lbl_status.config(text="transcribing")

        self.txt_response.delete("1.0", tk.END)

        threading.Thread(target=self._process_llm_request, daemon=True).start()

    def _process_llm_request(self):
        from transcriber import transcribe_audio
        from llm_test import ask_ollama

        try:
            transcript = transcribe_audio(OUTPUT_FILENAME)
            if not transcript:
                self._display_result("No speech detected.", "status: no speech", "red")
                return

            self.lbl_status.config(text="querying LLM")
            response = ask_ollama(transcript)

            self._display_result(response, "status: done", "green")

        except Exception as e:
            self._display_result(f"Error: {str(e)}", "status: error", "red")


    def _display_result(self, response_text, status_text, status_color):
        self.txt_response.insert(tk.END, response_text)
        self.lbl_status.config(text=status_text, foreground=status_color)
        self.btn_send.config(state=tk.NORMAL)
        self.btn_record.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = PyScribeApp(root)
    root.mainloop()