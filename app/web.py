"""Interface web simples para sorteio de comentários do YouTube sem dependências externas."""

from __future__ import annotations

import html
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from app.draw import draw_winners, unique_participants
from app.youtube_comments import (
    CommentsDisabledError,
    InvalidVideoError,
    QuotaExceededError,
    YouTubeAPIError,
    extract_video_id,
    fetch_comment_authors,
)


def _page(form: dict[str, str], winners: list[str], error: str) -> str:
    winner_items = "".join(f"<li>{html.escape(w)}</li>" for w in winners)
    winners_block = (
        "<section class='ok'><strong>Vencedor(es):</strong><ol>"
        f"{winner_items}</ol></section>"
        if winners
        else ""
    )
    error_block = f"<p class='error'>{html.escape(error)}</p>" if error else ""

    return f"""<!doctype html>
<html lang='pt-BR'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Sorteio YouTube</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #f6f8fb; color: #1f2937; }}
    .card {{ max-width: 720px; margin: 48px auto; background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 8px 24px rgba(0,0,0,.08); }}
    h1 {{ margin-top: 0; }}
    label {{ display: block; margin-top: 14px; font-weight: 600; }}
    input {{ width: 100%; box-sizing: border-box; padding: 10px; border: 1px solid #d1d5db; border-radius: 8px; margin-top: 6px; }}
    button {{ margin-top: 18px; background: #2563eb; color: #fff; border: 0; border-radius: 8px; padding: 11px 16px; cursor: pointer; }}
    .error {{ margin-top: 14px; padding: 10px; background: #fee2e2; border-radius: 8px; color: #991b1b; }}
    .ok {{ margin-top: 16px; padding: 12px; background: #dcfce7; border-radius: 8px; color: #166534; }}
    ol {{ margin: 8px 0 0; }}
  </style>
</head>
<body>
  <main class='card'>
    <h1>Sorteador de Comentários do YouTube</h1>
    <form method='post'>
      <label for='url'>URL do vídeo</label>
      <input id='url' name='url' type='url' required value='{html.escape(form['url'])}' placeholder='https://www.youtube.com/watch?v=...' />

      <label for='winners'>Quantidade de vencedores</label>
      <input id='winners' name='winners' type='number' min='1' required value='{html.escape(form['winners'])}' />

      <label for='api_key'>API key (opcional se YOUTUBE_API_KEY estiver definida)</label>
      <input id='api_key' name='api_key' type='text' value='{html.escape(form['api_key'])}' />

      <label for='seed'>Seed (opcional)</label>
      <input id='seed' name='seed' type='number' value='{html.escape(form['seed'])}' />

      <button type='submit'>Sortear</button>
    </form>

    {error_block}
    {winners_block}
  </main>
</body>
</html>"""


class DrawHTTPRequestHandler(BaseHTTPRequestHandler):
    def _send_html(self, body: str, status: int = 200) -> None:
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        form = {"url": "", "winners": "1", "api_key": "", "seed": ""}
        self._send_html(_page(form=form, winners=[], error=""))

    def do_POST(self) -> None:
        form = {"url": "", "winners": "1", "api_key": "", "seed": ""}
        error = ""
        winners: list[str] = []

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length).decode("utf-8")
        data = parse_qs(body)

        form["url"] = data.get("url", [""])[0].strip()
        form["winners"] = data.get("winners", ["1"])[0].strip() or "1"
        form["api_key"] = data.get("api_key", [""])[0].strip()
        form["seed"] = data.get("seed", [""])[0].strip()

        api_key = form["api_key"] or os.getenv("YOUTUBE_API_KEY", "")

        try:
            winners_count = int(form["winners"])
            seed = int(form["seed"]) if form["seed"] else None

            video_id = extract_video_id(form["url"])
            authors = fetch_comment_authors(video_id, api_key)
            participants = unique_participants(authors)
            winners = draw_winners(participants, winners_count=winners_count, seed=seed)
        except (InvalidVideoError, CommentsDisabledError, QuotaExceededError, YouTubeAPIError, ValueError) as exc:
            error = str(exc)

        self._send_html(_page(form=form, winners=winners, error=error))


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = HTTPServer((host, port), DrawHTTPRequestHandler)
    print(f"Servidor web disponível em http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
