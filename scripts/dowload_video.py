import yt_dlp
import os

def verify_file_exist(file_path: str) -> bool:
    return os.path.isfile(file_path)
    

def download_video_high_resolution(video_id: str):
    output_file = f"../videos inteiros/h_{video_id}.mp4"
    if verify_file_exist(output_file):
        print(f"Arquivo {output_file} já existe. Pulando download.")
        return 0
    ydl_opts = {"outtmpl": output_file, "format": "bestvideo+bestaudio/best"}
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_video_smalest_resolution(video_id: str):
    output_file = f"../videos inteiros/l_{video_id}.mp4"
    if verify_file_exist(output_file):
        print(f"Arquivo {output_file} já existe. Pulando download.")
        return 0
    ydl_opts = {"outtmpl": output_file, "format": "worst"}
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

