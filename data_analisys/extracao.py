import re
import time
from collections import Counter
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.util import ngrams
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


def obter_stopwords() -> set[str]:
    """Baixa (se necessário) e retorna o conjunto oficial de stopwords em português."""
    nltk.download("stopwords", quiet=True)
    return set(stopwords.words("portuguese"))


def get_transcript(video_id: str) -> list[dict]:
    """Obtém a transcrição bruta do vídeo em português."""
    try:
        transcript = YouTubeTranscriptApi().fetch(video_id, languages=["pt", "pt-BR"])
        return (
            transcript.to_raw_data() if hasattr(transcript, "to_raw_data") else list(transcript)
        )
    except (TranscriptsDisabled, NoTranscriptFound):
        print(f"[Aviso] Sem legenda em português para o vídeo: {video_id}")
        return []
    except Exception as e:
        print(f"[Erro] Falha ao buscar {video_id}: {e}")
        return []


def gerar_dataframes_analise(
    transcricoes: list[list[dict]], 
    stopwords_set: set[str], 
    top_n: int = 500
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Retorna dois DataFrames para o(s) vídeo(s) passado(s):
    1. Top N palavras individuais (SEM stopwords)
    2. Top N trigramas / conjuntos de 3 palavras (COM stopwords)
    """
    tokens_completos = []

    for lista_trechos in transcricoes:
        texto_video = " ".join(trecho["text"].lower() for trecho in lista_trechos)
        texto_video = re.sub(r"\[.*?\]", " ", texto_video)
        tokens = re.findall(r"\b[a-záàâãéèêíïóôõöúçñ]+\b", texto_video)
        tokens_completos.extend(tokens)

    # --- Análise 1: Palavras individuais (sem stopwords e sem letras soltas) ---
    palavras_filtradas = [
        p for p in tokens_completos if p not in stopwords_set and len(p) >= 2
    ]
    ranking_palavras = Counter(palavras_filtradas).most_common(top_n)
    df_palavras = pd.DataFrame(ranking_palavras, columns=["palavra", "frequencia"])

    # --- Análise 2: Trigramas / 3 palavras seguidas (mantendo stopwords) ---
    lista_trigramas = [" ".join(tri) for tri in ngrams(tokens_completos, 3)]
    ranking_trigramas = Counter(lista_trigramas).most_common(top_n)
    df_trigramas = pd.DataFrame(ranking_trigramas, columns=["trigrama", "frequencia"])

    return df_palavras, df_trigramas


def consolidar_dataframes(
    lista_dfs: list[pd.DataFrame], 
    coluna_chave: str, 
    top_n: int = 500
) -> pd.DataFrame:
    """
    Recebe uma lista de DataFrames individuais, soma as frequências dos itens iguais,
    mantém os itens exclusivos e corta os top_n mais frequentes no total.
    """
    if not lista_dfs:
        return pd.DataFrame(columns=[coluna_chave, "frequencia"])

    df_empilhado = pd.concat(lista_dfs, ignore_index=True)

    df_consolidado = (
        df_empilhado.groupby(coluna_chave, as_index=False)["frequencia"]
        .sum()
        .sort_values(by="frequencia", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    return df_consolidado


if __name__ == "__main__":
    # Lista com os IDs dos vídeos que você deseja analisar e somar
    lista_video_ids = ["NVaELVPF3Ns", "JRWDuQ0eWYk", "0cx24eRlqNE"]

    lista_stopwords = obter_stopwords()
    
    dfs_palavras_por_video = []
    dfs_trigramas_por_video = []

    for video_id in lista_video_ids:
        print(f"Processando vídeo: {video_id}...")
        legenda = get_transcript(video_id)

        if legenda:
            df_pal, df_tri = gerar_dataframes_analise([legenda], lista_stopwords, top_n=500)
            dfs_palavras_por_video.append(df_pal)
            dfs_trigramas_por_video.append(df_tri)

        # Pausa entre requisições para evitar bloqueio de IP pelo YouTube
        time.sleep(2)

    # Consolida todos os vídeos nas duas tabelas finais
    df_final_palavras = consolidar_dataframes(dfs_palavras_por_video, "palavra", top_n=500)
    df_final_trigramas = consolidar_dataframes(dfs_trigramas_por_video, "trigrama", top_n=500)

    print("\n=== TABELA CONSOLIDADA: TOP 500 PALAVRAS ===")
    print(df_final_palavras)

    print("\n=== TABELA CONSOLIDADA: TOP 500 TRIGRAMAS ===")
    print(df_final_trigramas)
    #save on excel
    df_final_palavras.to_excel("top_500_palavras.xlsx", index=False)
    df_final_trigramas.to_excel("top_500_trigramas.xlsx", index=False)