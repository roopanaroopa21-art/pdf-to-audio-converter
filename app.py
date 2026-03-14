import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyttsx3
from gtts import gTTS
import PyPDF2
from threading import Thread
import os

# Initialize engine
engine = pyttsx3.init()

def extract_text(file_path):
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content
    return text

def convert_pdf():
    # 1. Select the PDF
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return

    # 2. Choose where to save the MP3
    save_path = filedialog.asksaveasfilename(defaultextension=".mp3", 
                                            filetypes=[("Audio files", "*.mp3")])
    if not save_path:
        return

    progress.start(10)

    def process(l_combo, v_combo, s_slider, prog):
        try:
            text = extract_text(file_path)
            
            # CHECK: Is the PDF empty?
            if not text.strip():
                prog.stop()
                messagebox.showwarning("Empty PDF", "No text found! This PDF might be an image or scan.")
                return

            selected_lang = l_combo.get()

            if selected_lang == "English (Offline)":
                speed = s_slider.get()
                engine.setProperty('rate', speed)
                
                selected_voice_index = v_combo.current()
                voices = engine.getProperty('voices')
                engine.setProperty('voice', voices[selected_voice_index].id)

                engine.save_to_file(text, save_path)
                engine.runAndWait() 
            else:
                lang_map = {"English": "en", "Hindi": "hi", "Kannada": "kn", "Telugu": "te"}
                code = lang_map.get(selected_lang, "en")
                tts = gTTS(text=text, lang=code)
                tts.save(save_path)

            prog.stop()
            messagebox.showinfo("Success", f"Audiobook saved to:\n{save_path}")
            
            # AUTO-PLAY
            os.startfile(save_path)

        except Exception as e:
            prog.stop()
            messagebox.showerror("Error", f"Something went wrong: {str(e)}")

    Thread(target=process, args=(language_combo, voice_combo, speed_slider, progress)).start()

# --- GUI Setup ---
root = tk.Tk()
root.title("Pro PDF to Audio")
root.geometry("400x500")
root.configure(bg="#1e1e2f")

# Language Selection
tk.Label(root, text="Select Language", bg="#1e1e2f", fg="white").pack(pady=(20, 0))
language_options = ["English (Offline)", "English", "Hindi", "Kannada", "Telugu"]
language_combo = ttk.Combobox(root, values=language_options)
language_combo.current(0)
language_combo.pack(pady=10)

# Voice Selection
tk.Label(root, text="Select Voice (Offline Only)", bg="#1e1e2f", fg="white").pack()
voices = engine.getProperty('voices')
voice_names = [v.name for v in voices]
voice_combo = ttk.Combobox(root, values=voice_names)
voice_combo.current(0)
voice_combo.pack(pady=10)

# Speed Slider
tk.Label(root, text="Speech Speed", bg="#1e1e2f", fg="white").pack()
speed_slider = tk.Scale(root, from_=100, to=300, orient="horizontal", bg="#1e1e2f", fg="white")
speed_slider.set(200)
speed_slider.pack(pady=10)

# Progress
progress = ttk.Progressbar(root, orient="horizontal", length=250, mode='indeterminate')
progress.pack(pady=20)

# Button
tk.Button(root, text="Convert PDF", command=convert_pdf, bg="#4caf50", fg="white", 
          font=("Arial", 12, "bold"), padx=20, pady=10).pack()

root.mainloop()