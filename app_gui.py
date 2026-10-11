import os
import queue
import wave
import threading
import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import scrolledtext, messagebox
from pynput import keyboard
import pyttsx3
import customtkinter as ctk

from history_manager import save_entry, load_history

SAMPLE_RATE = 16000
CHANNELS = 1
OUTPUT_FILENAME = "test_record.wav"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class PyScribeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyScribe AI")
        self.root.geometry("600x620")
        self.root.resizable(False, False)

        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.stream = None
        self.key_held = False

        # Variables to store latest response for saving to history
        self.last_transcript = ""
        self.last_response = ""

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

    def _create_widgets(self):
        self.header = ctk.CTkLabel(self.root, text="PyScribe AI", font=("Arial", 24))
        self.header.pack(pady=10)

        # Recording & Action Controls
        self.btn_record = ctk.CTkButton(
            self.root, text="Start Recording", command=self.toggle_recording
        )
        self.btn_record.pack(pady=5)

        self.btn_send = ctk.CTkButton(
            self.root, text="Send to LLM", command=self.send_to_llm_thread
        )
        self.btn_send.pack(pady=5)

        # History Buttons
        self.btn_save_history = ctk.CTkButton(
            self.root, text="Save Entry to History", command=self.save_current_history
        )
        self.btn_save_history.pack(pady=5)

        self.btn_show_history = ctk.CTkButton(
            self.root, text="Show Entry from History", command=self.load_entry
        )
        self.btn_show_history.pack(pady=5)

        # Display Output
        self.lbl_response = ctk.CTkLabel(
            self.root, text="LLM Response:", font=("Arial", 14)
        )
        self.lbl_response.pack(pady=5)

        self.txt_response = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, width=65, height=12, font=("Arial", 12)
        )
        self.txt_response.pack(pady=5)

        self.lbl_status = ctk.CTkLabel(
            self.root, text="Status: idle", font=("Arial", 12)
        )
        self.lbl_status.pack(pady=5)

        # Hotkey listener
        self.listener = keyboard.Listener(
            on_press=self._on_key_press, on_release=self._on_key_release
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
            callback=self._audio_callback,
        )
        self.stream.start()

        self.btn_record.configure(text="Stop Recording")
        self.btn_send.configure(state=ctk.DISABLED)
        self.lbl_status.configure(text="Status: recording...", text_color="yellow")

    def _audio_callback(self, indata, frames, time_info, status):
        if self.is_recording:
            self.audio_queue.put(indata.copy())

    def stop_recording(self):
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self._save_wav_file()
        self.btn_record.configure(text="Start Recording")
        self.btn_send.configure(state=ctk.NORMAL)
        self.lbl_status.configure(text="Status: recording stopped", text_color="white")

    def _save_wav_file(self):
        recorded_chunks = []
        while not self.audio_queue.empty():
            recorded_chunks.append(self.audio_queue.get())

        if recorded_chunks:
            full_audio = np.concatenate(recorded_chunks, axis=0)
            audio_int16 = (full_audio * 32767).astype(np.int16)

            with wave.open(OUTPUT_FILENAME, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio_int16.tobytes())

    def send_to_llm_thread(self):
        self.btn_send.configure(state=ctk.DISABLED)
        self.btn_record.configure(state=ctk.DISABLED)
        self.lbl_status.configure(text="Status: transcribing...", text_color="cyan")

        self.txt_response.delete("1.0", tk.END)

        threading.Thread(target=self._process_llm_request, daemon=True).start()

    def _process_llm_request(self):
        from transcriber import transcribe_audio
        from llm_test import ask_ollama

        try:
            transcript = transcribe_audio(OUTPUT_FILENAME)
            if not transcript:
                self.root.after(
                    0,
                    lambda: self._display_result(
                        "", "No speech detected.", "Status: no speech", "red"
                    ),
                )
                return

            self.root.after(
                0,
                lambda: self.lbl_status.configure(
                    text="Status: querying LLM...", text_color="cyan"
                ),
            )
            response = ask_ollama(transcript)

            self.root.after(
                0,
                lambda: self._display_result(
                    transcript, response, "Status: done", "green"
                ),
            )

        except Exception as e:
            self.root.after(
                0,
                lambda: self._display_result(
                    "", f"Error: {str(e)}", "Status: error", "red"
                ),
            )

    def _display_result(self, transcript, response_text, status_text, status_color):
        self.last_transcript = transcript
        self.last_response = response_text

        self.txt_response.insert(tk.END, response_text)
        self.lbl_status.configure(text=status_text, text_color=status_color)
        self.btn_send.configure(state=ctk.NORMAL)
        self.btn_record.configure(state=ctk.NORMAL)

    def save_current_history(self):
        if not self.last_response:
            self.lbl_status.configure(
                text="Status: no response to save", text_color="orange"
            )
            return

        save_entry(self.last_transcript, self.last_response)
        self.lbl_status.configure(
            text="Status: entry saved to history.json", text_color="green"
        )

    def show_history_window(self):
        history_data = load_history()

        history_window = ctk.CTkToplevel(self.root)
        history_window.title("History")
        history_window.geometry("500x400")

        txt = ctk.CTkTextbox(history_window, wrap=tk.WORD, width=480, height=380)
        txt.pack(padx=10, pady=10)

        if not history_data:
            txt.insert(tk.END, "No history available.")
        else:
            for entry in reversed(history_data):
                timestamp = entry.get("timestamp", "N/A")
                transcript = entry.get("transcript", "N/A")
                response = entry.get("response", "N/A")
                txt.insert(
                    tk.END,
                    f"📅 Date: {timestamp}\n📝 Transcript: {transcript}\n🤖 Response: {response}\n\n"
                    + "=" * 40
                    + "\n\n",
                )

    def load_entry(self):
        history_data = load_history()
        if not history_data:
            messagebox.showinfo("History", "No history available.")
            return

        self.show_history_window()


if __name__ == "__main__":
    root = ctk.CTk()
    app = PyScribeApp(root)
    root.mainloop()