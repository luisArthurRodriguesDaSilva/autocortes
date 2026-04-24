from typing import TypedDict, Callable, List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


# ===== Tipos de DictTranscripts =====

class DictTranscript(TypedDict):
    inicio: float
    texto: str


@dataclass
class AmostraDictTranscripts:
    """Amostra de DictTranscripts com contexto (±30s da palavra-chave)"""

    DictTranscripts_antes: List[DictTranscript]
    DictTranscript_principal: DictTranscript
    DictTranscripts_depois: List[DictTranscript]
    palavras_chave: List[str]
    tempo_contexto_antes: float
    tempo_contexto_depois: float

    def duracao_total_contexto(self) -> float:
        """Retorna duração total do contexto (antes + depois)"""
        return self.tempo_contexto_antes + self.tempo_contexto_depois


class QualidadeCorte(str, Enum):
    """Avaliação da qualidade do corte pelo ChatGPT"""

    EXCELENTE = "excelente"
    BOM = "bom"
    MEDIO = "medio"
    RUIM = "ruim"
    INADEQUADO = "inadequado"


class TipoBuscaContext(str, Enum):
    """Tipos de contexto a buscar nas DictTranscripts"""

    ANTES = "antes"
    DEPOIS = "depois"
    AMBOS = "ambos"


# ===== Tipos de Resposta da API =====
class RespostaChatGPT(TypedDict):
    """Resposta estruturada do ChatGPT para avaliação de corte"""

    qualidade: QualidadeCorte
    confianca: float
    justificativa: str
    tempo_inicio_sugerido: Optional[float]
    tempo_fim_sugerido: Optional[float]
    motivo_rejeicao: Optional[str]


# ===== Tipos de Configuração =====
class ConfiguracaoCorte(TypedDict):
    """Configuração para processamento de cortes"""

    palavras_chave: List[str]
    tempo_antes_segundos: float
    tempo_depois_segundos: float
    qualidade_minima: QualidadeCorte
    modelo_gpt: str
    temperatura: float
    max_tokens: int


# ===== Tipos de Funções =====
ProcessadorDictTranscripts = Callable[[List[DictTranscript], List[str]], List[AmostraDictTranscripts]]
ValidadorQualidade = Callable[[AmostraDictTranscripts], bool]
AvaliadorChatGPT = Callable[[AmostraDictTranscripts, str], RespostaChatGPT]
GeradorPrompt = Callable[[AmostraDictTranscripts], str]


class TranscriptItem(TypedDict):
    text: str
    start: float
    duration: float


transcript = List[TranscriptItem]



class VideoInfo(TypedDict):
    title: str
    description: str

class complete_video_info(VideoInfo):
    text_transcript: str

class DictKeywordedItem(DictTranscript):
    keywords: List[str]
    