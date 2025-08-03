import customtkinter as ctk
import  tkinter.filedialog as filedialog
from yt_dlp import YoutubeDL
from PIL import Image, ImageTk
import urllib.request
import io

# set appearance
def color_mode(mode):
    ctk.set_appearance_mode(mode)

def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_var.set(folder)

def fetch_info():
    video_url = url.get()
    if not video_url:
        title_label.configure(text="Please enter Valid URL.")
        return
    try:
        ydl_opts = {'quite': True}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        title = info.get('title', 'No title found')
        thumbnail_url = info.get('thumbnail', None)

        title_label.configure(text=f"Title: {title}")

        if thumbnail_url:
            with urllib.request.urlopen(thumbnail_url) as u:
                raw_data = u.read()
            image = Image.open(io.BytesIO(raw_data)).resize((300, 180))
            photo = ImageTk.PhotoImage(image)
            thumbnail_label.configure(image=photo, text="")
            thumbnail_label.image = photo  # prevent garbage collection
        else:
            thumbnail_label.configure(text="No thumbnail found.")

    except Exception as e:
        title_label.configure(text=f"Error fetching info: {e}")
        thumbnail_label.configure(image=None, text="Thumbnail will appear here")

def download():
    video_url = url.get()
    download_path = folder_var.get()
    if not video_url or not download_path:
        title_label.configure(text="Enter URL and select folder.")
        return

    progress_bar.set(0) # Reset Progress_bar

    ydl_opts = {
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',
        'format': 'bestvideo[hight<=1080]+bestaudio/best',
        'merge_output_format':'mp4',
        'quiet': False,
        'noplaylist': True,
        'progress_hooks': [progress_hook],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    except Exception as e:
        title_label.configure(text=f"Download failed: {e}")

def progress_hook(d):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        downloaded_bytes = d.get('downloaded_bytes', 0)
        if total_bytes > 0:
            percent = downloaded_bytes / total_bytes
            progress_bar.set(percent)
    elif d['status'] == 'finished':
        progress_bar.set(1.0)
        title_label.configure(text="Download finished!")

# App window
app = ctk.CTk()
app.title("YouTube Downloader")
app.geometry("600x500")

# Variables
url = ctk.StringVar()
folder_var = ctk.StringVar()
switch_var = ctk.StringVar()

# Color mode switch
switch = ctk.CTkSwitch(
    app,
    text="Dark Mode",
    command=lambda: color_mode(switch_var.get()),
    variable=switch_var,
    onvalue="dark",
    offvalue="light"
)
switch.pack(pady=10)

# Link Entry
link_label = ctk.CTkLabel(app, text="YouTube URl:")
link_label.pack(pady=10)

url_entry = ctk.CTkEntry(app, width=300, textvariable=url, placeholder_text="Paste URL Here")
url_entry.pack(pady=5)

folder_btn = ctk.CTkButton(app, text="Select Download Location", command=select_folder)
folder_btn.pack(pady=10)

fetch_button = ctk.CTkButton(app, text="Fetch Video Info", command=fetch_info)
fetch_button.pack(pady=10)

# -------- Preview Labels (empty for now) --------
title_label = ctk.CTkLabel(app, text="Video title will appear here", wraplength=500)
title_label.pack(pady=5)

thumbnail_label = ctk.CTkLabel(app, text="Thumbnail will appear here")
thumbnail_label.pack(pady=5)

download_btn = ctk.CTkButton(app, text="Download Video", command=download)
download_btn.pack(pady=10)

progress_bar = ctk.CTkProgressBar(app, width=400)
progress_bar.set(0)
progress_bar.pack(pady=10)


# start GUI
app.mainloop()