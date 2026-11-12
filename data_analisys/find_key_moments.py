import re
import pandas as pd
from extracao import get_transcript


def formatar_tempo(segundos_totais: float) -> tuple[int, int, str]:
    """Converte segundos (float) para (minuto, segundo, 'MM:SS')."""
    total_int = int(segundos_totais)
    minutos, segundos = divmod(total_int, 60)
    tempo_formatado = f"{minutos:02d}:{segundos:02d}"
    return minutos, segundos, tempo_formatado


def localizar_top_trigramas(
    transcricao_video: list[dict],
    df_trigramas_consolidado: pd.DataFrame,
    top_k: int = 5
) -> pd.DataFrame:
    """
    Busca na transcrição de um vídeo específico todos os momentos (minuto e segundo)
    em que os top_k trigramas mais frequentes aparecem.
    """
    # 1. Extrai a lista com os 5 trigramas mais utilizados da tabela consolidada
    top_trigramas = set(df_trigramas_consolidado["trigrama"].head(top_k))

    # 2. Cria uma lista sequencial de tuplas: (palavra, start_em_segundos)
    palavras_com_tempo: list[tuple[str, float]] = []

    for trecho in transcricao_video:
        texto = trecho["text"].lower()
        texto = re.sub(r"\[.*?\]", " ", texto)
        tokens = re.findall(r"\b[a-záàâãéèêíïóôõöúçñ]+\b", texto)

        for token in tokens:
            palavras_com_tempo.append((token, trecho["start"]))

    # 3. Percorre as palavras em janelas de 3 (trigramas) e verifica se estão no Top 5
    ocorrencias = []
    total_palavras = len(palavras_com_tempo)

    for i in range(total_palavras - 2):
        p1, tempo_inicio = palavras_com_tempo[i]
        p2, _ = palavras_com_tempo[i + 1]
        p3, _ = palavras_com_tempo[i + 2]

        trigrama_atual = f"{p1} {p2} {p3}"

        if trigrama_atual in top_trigramas:
            minuto, segundo, timestamp_str = formatar_tempo(tempo_inicio)
            ocorrencias.append({
                "trigrama": trigrama_atual,
                "minuto": minuto,
                "segundo": segundo,
                "tempo_formatado": timestamp_str,
                "segundos_brutos": round(tempo_inicio, 2)
            })

    return pd.DataFrame(ocorrencias)


# ==========================================
# EXEMPLO DE EXECUÇÃO NO SEGUNDO ARQUIVO
# ==========================================
if __name__ == "__main__":
    # ID do vídeo específico onde você quer buscar os momentos
    video_alvo_id = "ID_DO_VIDEO_ALVO"

    # Exemplo simulando o df_final_trigramas vindo do primeiro arquivo
    # (Na prática, você pode importar a função do arquivo 1 ou carregar o DataFrame)
    df_final_trigramas = pd.DataFrame({
        "trigrama": [
            "a gente vai",
            "o que eu",
            "por causa de",
            "como fazer isso",
            "muito mais fácil",
            "outro trigrama qualquer"
        ],
        "frequencia": [45, 38, 30, 25, 19, 10]
    })

    # 1. Obtém a legenda do vídeo específico usando a mesma get_transcript
    legenda_alvo = get_transcript(video_alvo_id)

    # 2. Localiza os minutos e segundos dos 5 principais trigramas
    if legenda_alvo:
        df_momentos = localizar_top_trigramas(
            transcricao_video=legenda_alvo,
            df_trigramas_consolidado=df_final_trigramas,
            top_k=5
        )

        if not df_momentos.empty:
            print("=== MOMENTOS ENCONTRADOS NO VÍDEO ===")
            print(df_momentos.to_string(index=False))
        else:
            print("Nenhum dos 5 trigramas principais apareceu neste vídeo.")