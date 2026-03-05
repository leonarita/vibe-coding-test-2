"""CLI para sortear vencedores com base em comentários de um vídeo do YouTube."""

from __future__ import annotations

import argparse
import os

from app.draw import draw_winners, unique_participants
from app.youtube_comments import (
    CommentsDisabledError,
    InvalidVideoError,
    QuotaExceededError,
    YouTubeAPIError,
    extract_video_id,
    fetch_comment_authors,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sorteia vencedores a partir dos autores de comentários de um vídeo YouTube."
    )
    parser.add_argument("--url", required=True, help="URL do vídeo do YouTube")
    parser.add_argument(
        "--winners",
        required=True,
        type=int,
        help="Quantidade de vencedores a sortear",
    )
    parser.add_argument(
        "--api-key",
        dest="api_key",
        default=None,
        help="YouTube Data API key (opcional se YOUTUBE_API_KEY estiver definida)",
    )
    parser.add_argument(
        "--seed",
        default=None,
        type=int,
        help="Seed opcional para sorteio reproduzível",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    api_key = args.api_key or os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("Erro: informe --api-key ou defina YOUTUBE_API_KEY no ambiente.")
        return 1

    try:
        video_id = extract_video_id(args.url)
        authors = fetch_comment_authors(video_id, api_key)
        participants = unique_participants(authors)
        winners = draw_winners(participants, args.winners, seed=args.seed)
    except InvalidVideoError as error:
        print(f"Erro de vídeo: {error}")
        return 1
    except CommentsDisabledError as error:
        print(f"Erro: {error}")
        return 1
    except QuotaExceededError as error:
        print(f"Erro: {error}")
        return 1
    except ValueError as error:
        print(f"Erro de validação: {error}")
        return 1
    except YouTubeAPIError as error:
        print(f"Erro de API: {error}")
        return 1

    print("=== Resultado do sorteio ===")
    print(f"Vídeo ID: {video_id}")
    print(f"Comentários coletados: {len(authors)}")
    print(f"Participantes únicos: {len(participants)}")
    print(f"Vencedores ({len(winners)}):")
    for index, winner in enumerate(winners, start=1):
        print(f"{index}. {winner}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
