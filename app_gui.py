import os
import queue
import wave
import threading
import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pynput import keyboard
import pyttsx3
import customtkinter as ctk
SAMPLE_RATE = 16000
CHANNELS = 1
OUTPUT_FILENAME = "test_record.wav"
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
class PyScribeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyScribe AI")
        self.root.geometry("600x520")
        self.root.resizable(False,False)

        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.stream = None

        self.key_held = False
        self._create_widgets()
    def _on_key_press(self, key):
        try:
            if key == keyboard.Key.space and not self.key_held:
                self.key_held = True

                self.root.after(0, self.start_recording)
        except AttributeError:
            pass
    def _on_key_release(self, key):
        try:
            if key == keyboard.Key.space and self.key_held:
                self.key_held = False

                self.root.after(0, self.stop_recording)
        except AttributeError:
            pass
    def speak_text(self, text):
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Error occurred while speaking text: {e}")
    def _display_result(self, response_text, status_text, status_color):
        self.txt_response.insert(tk.END, response_text)
        self.lbl_status.configure(text=status_text, foreground=status_color)
        self.btn_send.configure(state=tk.NORMAL)
        self.btn_record.configure(state=tk.NORMAL)
    def _create_widgets(self):
        self.header = ctk.CTkLabel(self.root, text="PyScribe AI", font=("Arial", 24))
        self.header.pack(pady=10)

        self.btn_frame = ctk.CTkButton(self.root, text="start rec", command=self.toggle_recording)
        self.btn_frame.pack(pady=10)
        self.btn_record = ctk.CTkButton(self.root, text="start rec", command=self.toggle_recording)
        self.btn_record.pack(pady=10)
        self.btn_send = ctk.CTkButton(self.root, text="send to LLM", command=self.send_to_llm_thread)
        self.btn_send.pack(pady=10)
        self.lbl_response = ctk.CTkLabel(self.root, text="LLM Response:", font=("Arial", 14))
        self.lbl_response.pack(pady=5)
        self.txt_response = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=70, height=15, font=("Arial", 12))
        self.txt_response.pack(pady=5)
        self.lbl_status = ctk.CTkLabel(self.root, text="status: idle", font=("Arial", 12))
        self.lbl_status.pack(pady=5)

        self.listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.listener.start()


    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.audio_queue.queue.clear()

        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            callback=self._audio_callback
        )
        self.stream.start()

        self.btn_record.configure(text="stop rec")
        self.btn_send.configure(state=ctk.DISABLED)
        self.lbl_status.configure(text="recording...")
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
        self.lbl_status.config(text="recording stopped")
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
    root = ctk.CTk()
    app = PyScribeApp(root)
    root.mainloop()