from moviepy import VideoFileClip
def cut_video(input_file : str, start_time : float, end_time : float):
    output_file = f"{input_file.replace('.mp4', '')}_cut_{start_time}_{end_time}.mp4"
    c1 = VideoFileClip(input_file)
    c1.subclipped(start_time, end_time).write_videofile(output_file)
