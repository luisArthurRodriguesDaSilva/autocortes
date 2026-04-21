import yt_dlp


def download_video_high_resolution(video_id: str):
    ydl_opts = {"outtmpl": f"../videos inteiros/h_{video_id}.mp4"}
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_video_smalest_resolution(video_id: str):
    ydl_opts = {"outtmpl": f"../videos inteiros/l_{video_id}.mp4", "format": "worst"}
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

