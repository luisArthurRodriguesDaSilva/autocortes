from typing import List, Dict, Tuple, Callable, Optional
from functools import reduce
import json

from tipagem import (
    Legenda,
    AmostraLegendas,
    RespostaChatGPT,
    ConfiguracaoCorte,
    QualidadeCorte,
    ProcessadorLegendas,
)
from scripts.prompts import gerar_prompt_dinamico

# ===== FUNÇÕES PURAS DE PROCESSAMENTO =====


def encontrar_legenda_com_palavra_chave(
    legendas: List[Legenda], palavras_chave: List[str]
) -> List[Tuple[int, Legenda]]:
    """
    Encontra índices de legendas que contêm palavras-chave.

    Args:
        legendas: Lista de legendas do vídeo
        palavras_chave: Palavras a buscar

    Returns:
        Lista de tuplas (índice, legenda)
    """

    def contem_palavra_chave(legenda: Legenda) -> bool:
        texto_lower = legenda.texto.lower()
        return any(palavra.lower() in texto_lower for palavra in palavras_chave)

    return [(i, leg) for i, leg in enumerate(legendas) if contem_palavra_chave(leg)]


def extrair_contexto_legendas(
    legendas: List[Legenda],
    indice_principal: int,
    tempo_antes_s: float = 30.0,
    tempo_depois_s: float = 30.0,
) -> Tuple[List[Legenda], List[Legenda]]:
    """
    Extrai legendas antes e depois do índice principal dentro de um tempo.

    Args:
        legendas: Lista completa de legendas
        indice_principal: Índice da legenda principal
        tempo_antes_s: Segundos de contexto antes
        tempo_depois_s: Segundos de contexto depois

    Returns:
        Tupla (legendas_antes, legendas_depois)
    """
    legenda_principal = legendas[indice_principal]
    tempo_inicio_contexto = legenda_principal.tempo_inicio - tempo_antes_s
    tempo_fim_contexto = legenda_principal.tempo_fim + tempo_depois_s

    legendas_antes = [
        leg
        for leg in legendas[:indice_principal]
        if leg.tempo_inicio >= tempo_inicio_contexto
    ]

    legendas_depois = [
        leg
        for leg in legendas[indice_principal + 1 :]
        if leg.tempo_fim <= tempo_fim_contexto
    ]

    return legendas_antes, legendas_depois


def criar_amostra_legendas(
    legendas: List[Legenda],
    indice_principal: int,
    palavras_chave: List[str],
    tempo_antes_s: float = 30.0,
    tempo_depois_s: float = 30.0,
) -> AmostraLegendas:
    """
    Cria uma amostra de legendas com contexto.

    Args:
        legendas: Lista de todas as legendas
        indice_principal: Índice da legenda que contém palavras-chave
        palavras_chave: Palavras-chave encontradas
        tempo_antes_s: Contexto antes em segundos
        tempo_depois_s: Contexto depois em segundos

    Returns:
        AmostraLegendas com contexto completo
    """
    antes, depois = extrair_contexto_legendas(
        legendas, indice_principal, tempo_antes_s, tempo_depois_s
    )

    return AmostraLegendas(
        legendas_antes=antes,
        legenda_principal=legendas[indice_principal],
        legendas_depois=depois,
        palavras_chave=palavras_chave,
        tempo_contexto_antes=tempo_antes_s,
        tempo_contexto_depois=tempo_depois_s,
    )


def gerar_amostras_para_analise(
    legendas: List[Legenda],
    palavras_chave: List[str],
    tempo_antes_s: float = 30.0,
    tempo_depois_s: float = 30.0,
) -> List[AmostraLegendas]:
    """
    Função principal que processa legendas e gera amostras para análise.

    Args:
        legendas: Lista completa de legendas do vídeo
        palavras_chave: Palavras-chave a buscar
        tempo_antes_s: Contexto antes
        tempo_depois_s: Contexto depois

    Returns:
        Lista de AmostraLegendas prontas para avaliação do ChatGPT
    """
    ocorrencias = encontrar_legenda_com_palavra_chave(legendas, palavras_chave)

    amostras = [
        criar_amostra_legendas(
            legendas, indice, palavras_chave, tempo_antes_s, tempo_depois_s
        )
        for indice, _ in ocorrencias
    ]

    return amostras


# ===== FUNÇÕES DE INTEGRAÇÃO COM CHATGPT =====


def parsear_resposta_gpt(resposta_json: str) -> RespostaChatGPT:
    """
    Converte resposta JSON do ChatGPT para tipo estruturado.

    Args:
        resposta_json: String JSON da resposta

    Returns:
        RespostaChatGPT parseada
    """
    dados = json.loads(resposta_json)
    return RespostaChatGPT(
        qualidade=QualidadeCorte(dados["qualidade"]),
        confianca=float(dados["confianca"]),
        justificativa=dados["justificativa"],
        tempo_inicio_sugerido=dados.get("tempo_inicio_sugerido"),
        tempo_fim_sugerido=dados.get("tempo_fim_sugerido"),
        motivo_rejeicao=dados.get("motivo_rejeicao"),
    )


def avaliar_amostra_com_gpt(
    amostra: AmostraLegendas,
    client_openai,
    config: ConfiguracaoCorte,
) -> RespostaChatGPT:
    """
    Envia amostra para avaliação do ChatGPT.

    Args:
        amostra: AmostraLegendas a avaliar
        client_openai: Cliente OpenAI configurado
        config: Configuração do corte

    Returns:
        RespostaChatGPT com avaliação
    """
    prompt = gerar_prompt_dinamico(amostra)

    resposta = client_openai.chat.completions.create(
        model=config["modelo_gpt"],
        messages=[
            {
                "role": "system",
                "content": "Você é um especialista em edição de vídeos para redes sociais.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=config["temperatura"],
        max_tokens=config["max_tokens"],
        response_format={"type": "json_object"},
    )

    resposta_texto = resposta.choices[0].message.content
    return parsear_resposta_gpt(resposta_texto)


def filtrar_cortes_aprovados(
    avaliacoes: List[Tuple[AmostraLegendas, RespostaChatGPT]],
    qualidade_minima: QualidadeCorte,
) -> List[Tuple[AmostraLegendas, RespostaChatGPT]]:
    """
    Filtra apenas cortes que atendem qualidade mínima.

    Args:
        avaliacoes: Lista de tuplas (amostra, resposta)
        qualidade_minima: Qualidade mínima aceitável

    Returns:
        Lista filtrada apenas com cortes aprovados
    """
    escala_qualidade = {
        QualidadeCorte.EXCELENTE: 5,
        QualidadeCorte.BOM: 4,
        QualidadeCorte.MEDIO: 3,
        QualidadeCorte.RUIM: 2,
        QualidadeCorte.INADEQUADO: 1,
    }

    qualidade_minima_valor = escala_qualidade[qualidade_minima]

    return [
        (amostra, resposta)
        for amostra, resposta in avaliacoes
        if escala_qualidade[resposta["qualidade"]] >= qualidade_minima_valor
    ]
