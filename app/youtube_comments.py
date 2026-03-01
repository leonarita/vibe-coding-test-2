"""Integração com a YouTube Data API para leitura de autores de comentários."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse


class YouTubeCommentsError(Exception):
    """Erro base para falhas ao buscar comentários no YouTube."""


class InvalidVideoError(YouTubeCommentsError):
    """Vídeo inválido, inexistente ou URL não reconhecida."""


class CommentsDisabledError(YouTubeCommentsError):
    """Comentários estão desativados para este vídeo."""


class QuotaExceededError(YouTubeCommentsError):
    """Quota da API excedida para a chave informada."""


class YouTubeAPIError(YouTubeCommentsError):
    """Erro genérico da API do YouTube."""


def extract_video_id(url: str) -> str:
    """Extrai o ID de vídeo de URLs comuns do YouTube.

    Suporta formatos:
    - https://www.youtube.com/watch?v=<VIDEO_ID>
    - https://youtu.be/<VIDEO_ID>
    - https://www.youtube.com/shorts/<VIDEO_ID>
    """

    parsed = urlparse(url.strip())
    hostname = (parsed.hostname or "").lower()

    if hostname in {"youtu.be", "www.youtu.be"}:
        video_id = parsed.path.strip("/").split("/")[0]
        if video_id:
            return video_id

    if hostname in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
            if video_id:
                return video_id
        if parsed.path.startswith("/shorts/"):
            video_id = parsed.path.split("/shorts/", maxsplit=1)[1].split("/")[0]
            if video_id:
                return video_id

    raise InvalidVideoError("Não foi possível extrair o video_id da URL informada.")


def _raise_mapped_http_error(error: Exception) -> None:
    body = ""
    response = getattr(error, "resp", None)
    try:
        content = getattr(error, "content", b"")
        body = content.decode("utf-8", errors="ignore").lower()
    except Exception:
        body = str(error).lower()

    status = getattr(response, "status", None)

    if "commentsdisabled" in body or "disabled comments" in body:
        raise CommentsDisabledError("Comentários desativados para este vídeo.") from error
    if "quotaexceeded" in body or "dailylimitexceeded" in body:
        raise QuotaExceededError("Quota da YouTube Data API excedida.") from error
    if "video_not_found" in body or "video not found" in body or status == 404:
        raise InvalidVideoError("Vídeo inválido ou não encontrado.") from error

    raise YouTubeAPIError(f"Falha ao consultar API do YouTube: {error}") from error


def fetch_comment_authors(video_id: str, api_key: str) -> list[str]:
    """Coleta todos os autores de comentários (top-level) de um vídeo."""

    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    if not video_id:
        raise InvalidVideoError("video_id vazio.")
    if not api_key:
        raise YouTubeAPIError("API key não informada.")

    youtube = build("youtube", "v3", developerKey=api_key)
    authors: list[str] = []
    next_page_token: str | None = None

    while True:
        try:
            response = (
                youtube.commentThreads()
                .list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=100,
                    pageToken=next_page_token,
                    textFormat="plainText",
                )
                .execute()
            )
        except HttpError as error:
            _raise_mapped_http_error(error)

        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            top_level = snippet.get("topLevelComment", {}).get("snippet", {})
            author_name = top_level.get("authorDisplayName")
            if author_name:
                authors.append(author_name)

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return authors
