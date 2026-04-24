from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Dict, Tuple, Callable
import os
import sys
import tipagem as t


def _get_info_video(video_id: str) -> t.VideoInfo:
    """Obtém informações do vídeo do YouTube"""
    youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))
    resp = youtube.videos().list(part="snippet,statistics", id=video_id).execute()

    if "items" not in resp or len(resp["items"]) == 0:
        raise ValueError(f"Vídeo com ID {video_id} não encontrado.")

    item = resp["items"][0]
    return {
        "title": item["snippet"]["title"],
        "description": item["snippet"]["description"],
    }


def get_transcript(video_id: str) -> t.transcript:
    """Obtém transcrição do vídeo"""
    transcript = YouTubeTranscriptApi().fetch(video_id, languages=["pt", "pt-BR", "en"])
    return (
        transcript.to_raw_data() if hasattr(transcript, "to_raw_data") else transcript
    )


def format_to_dict_transcript(transcript: t.transcript) -> List[t.DictTranscript]:
    """Converte transcript em objetos DictTranscript"""
    return [
        {"inicio": float(item["start"]), "texto": item["text"]} for item in transcript
    ]


def format_to_text_trascript(transcript: t.transcript) -> str:
    """Formata transcrição como texto legível"""
    dict_transcript = format_to_dict_transcript(transcript)
    return "\n".join(
        [f"[{item['inicio']:.2f}] {item['texto']}" for item in dict_transcript]
    )


def remove_invalid_caracters(titulo: str) -> str:
    """Remove caracteres inválidos do título"""
    return "".join(c for c in titulo if c not in '\\/:*?"<>|').strip()


def get_completed_video_info(video_id: str) -> t.complete_video_info:
    """Obtém informações completas do vídeo, incluindo título, descrição e transcrição formatada"""
    info = _get_info_video(video_id)
    transcript = get_transcript(video_id)
    transcript_text = format_to_text_trascript(transcript)
    return {
        "title": remove_invalid_caracters(info["title"]),
        "description": remove_invalid_caracters(info["description"]),
        "text_transcript": transcript_text,
    }


def format_to_video_info_file_content(complete_info: t.complete_video_info) -> str:
    """Constrói conteúdo formatado do arquivo"""
    return (
        f"Título: {complete_info['title']}\n"
        f"------------\n"
        f"Descrição:\n{complete_info['description']}\n"
        f"------------\n"
        f"Transcrição:\n{complete_info['text_transcript']}\n"
    )


def save_complete_info(caminho: str, complete_info: t.complete_video_info) -> None:
    """Salva conteúdo em arquivo"""
    file_content = format_to_video_info_file_content(complete_info)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(file_content)


def _contem_palavra_chave(item: t.DictTranscript, keywords: List[str]) -> bool:
    return any(keyword.lower() in item["texto"].lower() for keyword in keywords)


def filter_transcript_by_keywords(
    transcript: t.transcript, keywords: List[str]
) -> Tuple[List[t.DictKeywordedItem], List[float]]:

    dict_transcript = format_to_dict_transcript(transcript)
    filtrados = [
        item for item in dict_transcript if _contem_palavra_chave(item, keywords)
    ]

    filtered_moments_with_keywords = [
        {
            **item,
            "keywords": [
                keyword
                for keyword in keywords
                if keyword.lower() in item["texto"].lower()
            ],
        }
        for item in filtrados
    ]

    return filtered_moments_with_keywords


def remove_next_appearances(
    dictTranscripts: List[t.DictKeywordedItem], tolerance_seconds: float = 30.0
) -> List[t.DictTranscript]:
    dicionario_vigiador = {}
    resultado: List[t.DictKeywordedItem] = []

    for transcript in dictTranscripts:
        keywords = transcript.get("keywords")
        for keyword in keywords:
            last_appear = dicionario_vigiador.get(keyword)
            if last_appear is None or (
                tolerance_seconds <= transcript["inicio"] - last_appear
            ):
                dicionario_vigiador[keyword] = transcript["inicio"]
                resultado.append(transcript)

    return resultado
