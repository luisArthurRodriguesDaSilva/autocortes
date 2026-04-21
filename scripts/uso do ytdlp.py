import yt_dlp

url = "https://www.youtube.com/watch?v=5uTbulI9LYY"

ydl_opts = {}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
