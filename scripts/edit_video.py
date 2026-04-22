from moviepy import VideoFileClip
import os
from get_video_data import save_video_data
from get_video_data import filter_transcript
from download_video import download_video_smalest_resolution


def cut_video(input_file : str, start_time : float, end_time : float, present_keywords: list[str]):
    filename = os.path.basename(input_file)
    output_file = f"../videos cortados/{filename.replace('.mp4', '')}_cut_{'_'.join(present_keywords)}_{start_time}_{end_time}.mp4"
    c1 = VideoFileClip(input_file)
    c1.subclipped(start_time, end_time).write_videofile(output_file)

def get_clips_from_video(video_id: str, keywords: list[str]):
    transcript = save_video_data(video_id)
    filtered_transcripts, starts = filter_transcript(transcript, keywords)
    download_video_smalest_resolution(video_id)
    for i,second in enumerate(starts):
        start,end = second-5, second + 5 #get_start_end_time(transcript, second)
        present_keywords = filtered_transcripts[i]['contained_keywords']
        cut_video(f"../videos inteiros/l_{video_id}.mp4", start, end,present_keywords)
