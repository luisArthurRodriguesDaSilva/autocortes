# Autocortes

**English** | [Português](#português)

Autocortes is a Python project for finding keyword mentions in a YouTube video's transcript and exporting short video clips around those moments.

## What it does

The current clipping workflow:

1. Fetches the video's transcript in Portuguese or English.
2. Finds transcript entries containing any requested keyword (case-insensitive substring matching).
3. Applies a 30-second per-keyword suppression rule to reduce nearby repeated matches.
4. Downloads the video's lowest available resolution if it is not already present.
5. Exports clips from 5 seconds before each match (not earlier than the start of the video) through 5 seconds after it.

The project also includes helpers for retrieving video metadata, downloading a higher-resolution source, and evaluating transcript excerpts with OpenAI. These helpers are separate from the keyword clipping workflow.

## Requirements

- Python 3.9 or newer
- FFmpeg available on `PATH` for MoviePy video processing
- Dependencies for the clipping workflow:

```bash
python -m pip install moviepy google-api-python-client youtube-transcript-api yt-dlp
```

For the optional OpenAI helper, also install `openai`:

```bash
python -m pip install openai
```

The repository does not currently include a dependency lockfile or package configuration.

## Usage

Run the workflow from the `scripts` directory. This is important because the current implementation uses paths relative to the working directory.

```bash
cd scripts
python -c 'from edit_video import get_clips_from_video; print(get_clips_from_video("YOUTUBE_VIDEO_ID", ["keyword one", "keyword two"]))'
```

Replace `YOUTUBE_VIDEO_ID` with the video's ID and provide one or more keywords. The function returns the paths of the clips it creates; it returns an empty list if no transcript entries match.

### Output and downloads

- Source video: `../videos inteiros/l_<video-id>.mp4`
- Generated clips: `../videos cortados/`

The source is downloaded at the lowest available resolution and reused if it already exists. Clip filenames include the source name, matched keywords, and start/end timestamps.

## API keys

- The clipping workflow uses the YouTube transcript API and `yt-dlp`; it does not require an API key in the current implementation.
- `YOUTUBE_API_KEY` is used by the video metadata helper in `scripts/get_video_data.py`.
- `OPENAI_API_SECRET_KEY` is used by the OpenAI helper in `scripts/send_to_gpt.py`.

Set optional keys in your shell before using the corresponding helpers. Do not commit credentials to the repository.

## Project layout

```text
scripts/
  download_video.py   YouTube video download helpers
  edit_video.py      Keyword matching and clip export workflow
  find_keywords.py   Transcript keyword filtering and context helpers
  get_video_data.py  Transcript and video metadata helpers
  send_to_gpt.py     OpenAI chat-completion helper
  funcoes_core.py    Transcript-context and evaluation utilities
contextos/            Example transcript context files
informacoes dos videos/  Saved video information and transcripts
videos cortados/      Generated clips
```

## Notes

- Transcript availability and language depend on the source video. The transcript helper requests Portuguese, Brazilian Portuguese, and English.
- Keyword matching checks whether a keyword appears anywhere in a transcript entry; it does not match whole words only.
- Generated clip intervals are centered on transcript timestamps. Review the clips, especially near the beginning or end of a source video.
- Only download and reuse videos when you have the right to do so, and follow YouTube's terms and applicable copyright law.

---

# Português

Autocortes é um projeto Python para localizar menções a palavras-chave na transcrição de um vídeo do YouTube e exportar pequenos clipes desses momentos.

## O que faz

O fluxo atual de criação de cortes:

1. Obtém a transcrição do vídeo em português ou inglês.
2. Encontra trechos que contenham qualquer palavra-chave informada (busca sem diferenciar maiúsculas e minúsculas, por substring).
3. Aplica uma regra de supressão de 30 segundos por palavra-chave para reduzir ocorrências repetidas próximas.
4. Baixa o vídeo na menor resolução disponível, caso ele ainda não exista localmente.
5. Exporta clipes começando 5 segundos antes de cada ocorrência (sem ultrapassar o início do vídeo) e terminando 5 segundos depois.

O projeto também contém funções auxiliares para obter metadados do vídeo, baixar uma versão em resolução mais alta e avaliar trechos de transcrição com a OpenAI. Essas funções são separadas do fluxo de cortes por palavra-chave.

## Requisitos

- Python 3.9 ou superior
- FFmpeg disponível no `PATH` para o processamento de vídeo do MoviePy
- Dependências:

```bash
python -m pip install moviepy google-api-python-client youtube-transcript-api yt-dlp
```

Para usar o auxiliar opcional da OpenAI, instale também `openai`:

```bash
python -m pip install openai
```

Atualmente, o repositório não inclui um arquivo de dependências travadas nem configuração de pacote.

## Como usar

Execute o fluxo a partir do diretório `scripts`. Isso é importante porque a implementação atual usa caminhos relativos ao diretório de execução.

```bash
cd scripts
python -c 'from edit_video import get_clips_from_video; print(get_clips_from_video("ID_DO_VIDEO", ["palavra um", "palavra dois"]))'
```

Substitua `ID_DO_VIDEO` pelo ID do vídeo e informe uma ou mais palavras-chave. A função retorna os caminhos dos clipes criados; retorna uma lista vazia se nenhum trecho da transcrição corresponder.

### Saída e downloads

- Vídeo de origem: `../videos inteiros/l_<id-do-video>.mp4`
- Clipes gerados: `../videos cortados/`

O vídeo de origem é baixado na menor resolução disponível e reutilizado se já existir. Os nomes dos clipes incluem o nome do vídeo de origem, as palavras-chave encontradas e os horários inicial e final.

## Chaves de API

- O fluxo de criação de cortes usa a API de transcrições do YouTube e `yt-dlp`; na implementação atual, não exige chave de API.
- `YOUTUBE_API_KEY` é usada pela função auxiliar de metadados em `scripts/get_video_data.py`.
- `OPENAI_API_SECRET_KEY` é usada pelo auxiliar da OpenAI em `scripts/send_to_gpt.py`.

Configure as chaves opcionais no terminal antes de usar as funções correspondentes. Não envie credenciais para o repositório.

## Estrutura do projeto

```text
scripts/
  download_video.py   Funções para baixar vídeos do YouTube
  edit_video.py      Fluxo de busca por palavras-chave e exportação de clipes
  find_keywords.py   Filtragem de palavras-chave e funções de contexto
  get_video_data.py  Funções de transcrição e metadados
  send_to_gpt.py     Auxiliar de chamadas de chat da OpenAI
  funcoes_core.py    Utilitários de contexto e avaliação de transcrições
contextos/              Exemplos de arquivos de contexto de transcrição
informacoes dos videos/  Informações e transcrições salvas
videos cortados/         Clipes gerados
```

## Observações

- A disponibilidade e o idioma da transcrição dependem do vídeo. O auxiliar solicita português, português do Brasil e inglês.
- A busca verifica se a palavra-chave aparece em qualquer parte de um trecho da transcrição; não exige que ela seja uma palavra completa.
- Os intervalos dos clipes são centralizados nos horários da transcrição. Revise os clipes, especialmente os próximos ao início ou ao fim do vídeo.
- Baixe e reutilize vídeos apenas quando tiver direito para isso, respeitando os termos do YouTube e a legislação de direitos autorais aplicável.
