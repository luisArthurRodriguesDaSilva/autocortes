import yt_dlp


def download_video(video_id: str):
    ydl_opts = {"outtmpl": f"../videos/{video_id}.mp4"}
    url = f"https://www.youtube.com/watch?v={video_id}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
