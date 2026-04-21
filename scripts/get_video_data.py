from googleapiclient.discovery import build
import os
from youtube_transcript_api import YouTubeTranscriptApi

def get_video_info(video_id):
    youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))
    resp = youtube.videos().list(part="snippet,statistics", id=video_id).execute()
    if "items" not in resp or len(resp["items"]) == 0:
        raise ValueError(f"Vídeo com ID {video_id} não encontrado.")
    item = resp["items"][0]
    return {
        "title": item["snippet"]["title"],
        "description": item["snippet"]["description"],
        "views": item["statistics"].get("viewCount"),
        "likes": item["statistics"].get("likeCount"),
    }


def get_transcript(video_id):
    transcript = YouTubeTranscriptApi().fetch(video_id, languages=["pt", "pt-BR", "en"])
    transcript = (
        transcript.to_raw_data() if hasattr(transcript, "to_raw_data") else transcript
    )
    return transcript


def formatar_legenda(transcript):
    legenda = "\n".join(
        [f"[{item['start']:.2f}] {item['text']}" for item in transcript]
    )
    return legenda


def save_txt_legivel(dados, filename):
    conteudo = (
        f"Título: {dados['titulo']}\n------------\n"
        f"Descrição:\n{dados['descricao']}\n------------\n"
        f"Legenda:\n{dados['legenda']}\n"
    )
    with open(filename, "w", encoding="utf-8") as f:
        f.write(conteudo)


def save_video_data(video_id):
    info = get_video_info(video_id)
    titulo_limpo = "".join(
        c for c in info["title"] if c not in "\\/:*?\"<>|"
    ).strip()
    filename = f"{titulo_limpo}.txt"
    dados = {
        "titulo": info["title"],
        "descricao": info["description"],
        "legenda": formatar_legenda(get_transcript(video_id)),
    }
    save_txt_legivel(dados, f"./legendas/{filename}")