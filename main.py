import yt_dlp
url = "https://www.youtube.com/watch?v=5uTbulI9LYY"
#do the resthttps://www.youtube.com/watch?v=5uTbulI9LYY and download it using yt_dlp

ydl_opts = {}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

