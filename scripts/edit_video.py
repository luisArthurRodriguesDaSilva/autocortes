from pathlib import Path

from moviepy import VideoFileClip
#teste2e
from download_video import download_video_smalest_resolution
from find_keywords import (
    filter_transcript_by_keywords,
    remove_redundant_appearances,
)
from get_video_data import format_to_dict_transcript, get_transcript


def save_video_data(video_id: str):
    """Fetch a transcript for a video id and keep the legacy API name."""
    return get_transcript(video_id)


def filter_transcript(transcript_data, keywords: list[str]):
    """Return filtered transcript entries plus their timestamps."""
    transcript_dict = format_to_dict_transcript(transcript_data)
    filtered_transcripts = remove_redundant_appearances(
        filter_transcript_by_keywords(transcript_dict, keywords),
        tolerance_seconds=30.0,
    )
    starts = [item["inicio"] for item in filtered_transcripts]
    return filtered_transcripts, starts

def cut_video(
    input_file: str,
    start_time: float,
    end_time: float,
    present_keywords: list[str],
) -> str:
    filename = Path(input_file).name
    output_dir = Path("../videos cortados")
    output_dir.mkdir(parents=True, exist_ok=True)

    keywords = "_".join(str(keyword).strip() for keyword in present_keywords if keyword)
    output_file = output_dir / (
        f"{Path(filename).stem}_cut_{keywords}_{start_time}_{end_time}.mp4"
    )

    with VideoFileClip(input_file) as clip:
        clip.subclipped(start_time, end_time).write_videofile(
            str(output_file),
            logger=None,
        )

    return str(output_file)


def get_clips_from_video(video_id: str, keywords: list[str]):
    transcript = save_video_data(video_id)
    filtered_transcripts, starts = filter_transcript(transcript, keywords)

    if not filtered_transcripts:
        return []

    download_video_smalest_resolution(video_id)
    input_file = Path("../videos inteiros") / f"l_{video_id}.mp4"
    created_clips = []

    for item, second in zip(filtered_transcripts, starts):
        start = max(0.0, second - 5)
        end = second + 5
        present_keywords = item.get("keywords", [])
        created_clips.append(cut_video(str(input_file), start, end, present_keywords))

    return created_clips
