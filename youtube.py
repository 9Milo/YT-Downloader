import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import os

# --------------------------
# FFMPEG suchen
# --------------------------
def find_ffmpeg():
    ffmpeg_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    for root, dirs, files in os.walk(os.getcwd()):
        if ffmpeg_name in files:
            return os.path.join(root, ffmpeg_name)
    return None


# --------------------------
# Download-Ordner auswählen
# --------------------------
def ordner_waehlen():
    pfad = filedialog.askdirectory()
    if pfad:
        ordner_var.set(pfad)


# --------------------------
# Fortschrittsanzeige Handler
# --------------------------
def progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
        downloaded = d.get('downloaded_bytes', 0)

        if total > 0:
            prozent = int(downloaded / total * 100)
            progress_var.set(prozent)
            progress_label.config(text=f"{prozent}%")
            root.update_idletasks()


# --------------------------
# Formate abrufen
# --------------------------
def lade_formate():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Fehler", "Bitte eine YouTube-URL eingeben!")
        return

    try:
        ydl_opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        global formate
        formate = {}

        for f in info['formats']:
            if f.get("height"):
                formate[f"{f['height']}p"] = f["format_id"]

        if not formate:
            messagebox.showinfo("Info", "Keine Video-Formate gefunden.")
            return

        auswahl_box['values'] = sorted(formate.keys(), key=lambda x: int(x.replace("p", "")))
        auswahl_box.current(len(auswahl_box['values']) - 1)

        messagebox.showinfo("Erfolg", "Formate erfolgreich geladen!")

    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Abrufen der Formate:\n{e}")


# --------------------------
# Download starten
# --------------------------
def downloaden():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Fehler", "Bitte eine URL eingeben!")
        return

    qualität = auswahl_box.get()
    if qualität not in formate:
        messagebox.showerror("Fehler", "Bitte eine gültige Qualität auswählen!")
        return

    zielordner = ordner_var.get()
    if not os.path.isdir(zielordner):
        messagebox.showerror("Fehler", "Ungültiger Download-Ordner!")
        return

    ffmpeg_path = find_ffmpeg()
    if ffmpeg_path is None:
        messagebox.showerror("Fehler", "ffmpeg.exe wurde nicht gefunden!\n"
                                       "Bitte in den selben Ordner wie youtube.py legen.")
        return

    format_id = formate[qualität]

    progress_var.set(0)
    progress_label.config(text="0%")

    ydl_opts = {
        'format': format_id + "+bestaudio/best",
        'merge_output_format': 'mp4',
        'ffmpeg_location': ffmpeg_path,
        'progress_hooks': [progress_hook],
        'outtmpl': os.path.join(zielordner, "%(title)s.%(ext)s"),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        messagebox.showinfo("Erfolg", "Download abgeschlossen!")

    except Exception as e:
        messagebox.showerror("Fehler", f"Download fehlgeschlagen:\n{e}")


# --------------------------
# GUI
# --------------------------
root = tk.Tk()
root.title("YouTube Downloader – mit Fortschrittsbalken")
root.geometry("520x350")

# URL Eingabe
tk.Label(root, text="YouTube-URL:").pack(pady=5)
url_entry = tk.Entry(root, width=55)
url_entry.pack(pady=5)

# Format abrufen Button
tk.Button(root, text="Formate abrufen", command=lade_formate).pack(pady=5)

# Qualitäts-Auswahl
tk.Label(root, text="Qualität auswählen:").pack(pady=5)
auswahl_box = ttk.Combobox(root, state="readonly", width=20)
auswahl_box.pack(pady=5)

# Ordner Auswahl
tk.Label(root, text="Download-Ordner:", pady=5).pack()
ordner_var = tk.StringVar()
ordner_entry = tk.Entry(root, textvariable=ordner_var, width=45)
ordner_entry.pack()
tk.Button(root, text="Ordner auswählen", command=ordner_waehlen).pack(pady=5)

# Fortschrittsbalken
progress_var = tk.IntVar()
progress = ttk.Progressbar(root, maximum=100, variable=progress_var, length=400)
progress.pack(pady=10)
progress_label = tk.Label(root, text="0%")
progress_label.pack()

# Download Button
tk.Button(root, text="Download starten", command=downloaden).pack(pady=10)

root.mainloop()
