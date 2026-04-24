from tipagem import AmostraLegendas, GeradorPrompt
from typing import List, Dict, Optional

def _formatar_legendas(legendas: List) -> str:
    """Formata legendas para apresentação no prompt"""
    return "\n".join([
        f"[{leg.tempo_inicio:.1f}s - {leg.tempo_fim:.1f}s]: {leg.texto}"
        for leg in legendas
    ])

def _construir_instrucoes_qualidade(
    criterios_positivos: Optional[List[str]] = None,
    criterios_negativos: Optional[List[str]] = None,
    tipo_plataforma: str = "redes sociais"
) -> str:
    """
    Constrói instruções de qualidade dinamicamente.
    
    Args:
        criterios_positivos: Lista de critérios que fazem um bom corte
        criterios_negativos: Lista de critérios a evitar
        tipo_plataforma: Tipo de plataforma (redes sociais, YouTube, etc)
        
    Returns:
        String com instruções formatadas
    """
    criterios_positivos = criterios_positivos or [
        "Conter momento de pico de interesse",
        "Ter transição suave com contexto narrativo",
        "Manter engajamento com conteúdo surpreendente",
        "Possuir conclusão natural e clara",
        "Ser independente e entendível isoladamente"
    ]
    
    criterios_negativos = criterios_negativos or [
        "Cortes que interrompem frases importantes",
        "Trechos sem conclusão clara",
        "Legendas dependentes de contexto anterior",
        "Momentos de silêncio ou pausa narrativa"
    ]
    
    criterios_pos_formatados = "\n".join([
        f"{i+1}. **{criterio}**" for i, criterio in enumerate(criterios_positivos)
    ])
    
    criterios_neg_formatados = "\n".join([
        f"- {criterio}" for criterio in criterios_negativos
    ])
    
    return f"""
Um BOM CORTE de vídeo para {tipo_plataforma} deve:
{criterios_pos_formatados}

Evitar:
{criterios_neg_formatados}
"""

def gerar_prompt_dinamico(
    amostra: AmostraLegendas,
    tipo_plataforma: str = "redes sociais (TikTok, YouTube Shorts, Reels)",
    criterios_personalizados: Optional[Dict[str, List[str]]] = None
) -> str:
    """
    Gera um prompt dinâmico baseado na amostra de legendas.
    
    Args:
        amostra: AmostraLegendas contendo contexto e palavras-chave
        tipo_plataforma: Tipo de plataforma alvo
        criterios_personalizados: Dict com 'positivos' e 'negativos' personalizados
        
    Returns:
        Prompt formatado para enviar ao ChatGPT
    """
    criterios_personalizados = criterios_personalizados or {}
    
    palavras_chave_str = ", ".join([f'"{p}"' for p in amostra.palavras_chave])
    
    legendas_antes = _formatar_legendas(amostra.legendas_antes)
    legenda_principal = _formatar_legendas([amostra.legenda_principal])
    legendas_depois = _formatar_legendas(amostra.legendas_depois)
    
    instrucoes = _construir_instrucoes_qualidade(
        criterios_positivos=criterios_personalizados.get("positivos"),
        criterios_negativos=criterios_personalizados.get("negativos"),
        tipo_plataforma=tipo_plataforma
    )
    
    prompt = f"""
Você é um especialista em edição de vídeos para {tipo_plataforma}.

Analisando o seguinte trecho de legenda de um vídeo, determine se é um bom momento para fazer um corte.

**CONTEXTO (30s ANTES):**
{legendas_antes if legendas_antes.strip() else "[Sem legendas antes]"}

**TRECHO PRINCIPAL (CONTÉM PALAVRAS-CHAVE: {palavras_chave_str}):**
{legenda_principal}

**CONTEXTO (30s DEPOIS):**
{legendas_depois if legendas_depois.strip() else "[Sem legendas depois]"}

{instrucoes}

Responda em JSON com esta estrutura:
{{
    "qualidade": "excelente" | "bom" | "medio" | "ruim" | "inadequado",
    "confianca": 0.0-1.0,
    "justificativa": "Explicação breve do por quê",
    "tempo_inicio_sugerido": número ou null,
    "tempo_fim_sugerido": número ou null,
    "motivo_rejeicao": null ou "razão se qualidade < bom"
}}

Seja rigoroso e honesto na avaliação. Priorize a experiência do espectador.
"""
    
    return prompt.strip()

# Alias para facilitar uso
gerar_prompt: GeradorPrompt = gerar_prompt_dinamico
