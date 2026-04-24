
from typing import List, Tuple
import tipagem as t
import get_video_data as gvd


def _contem_palavra_chave(item: t.DictTranscript, keywords: List[str]) -> bool:
    return any(keyword.lower() in item["texto"].lower() for keyword in keywords)


def filter_transcript_by_keywords(
    dict_transcript: List[t.DictTranscript], keywords: List[str]
) -> Tuple[List[t.DictKeywordedItem], List[float]]:

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

def format_to_context_trascript(dict_transcript: List[t.DictTranscript]) -> str:
    """Formata transcrição como texto legível"""
    return "\n".join(
        [f"[{item['inicio']:.2f}] {item['texto']}" for item in dict_transcript]
    )

def get_context(completed_dict_transcript: List[t.DictKeywordedItem],
                keyword_transcript_item : t.DictKeywordedItem,
                seconds_before : int,
                seconds_after:int) -> List[t.DictKeywordedItem]: 
    new_transcript = completed_dict_transcript.copy()
    reference_time = keyword_transcript_item["inicio"]
    filtered_transcript = list(filter(
        lambda item: (reference_time - seconds_before) <= item["inicio"] <= (reference_time + seconds_after),
        new_transcript
    ))
    text_transcript = format_to_context_trascript(filtered_transcript)
    return text_transcript

    