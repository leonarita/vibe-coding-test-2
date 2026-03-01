# Sorteador de Comentários do YouTube

Ferramenta em Python para coletar autores de comentários de um vídeo do YouTube e sortear vencedores de forma transparente e reproduzível (via seed opcional).

## Requisitos

- Python 3.10+
- Chave da **YouTube Data API v3**

Instalação de dependências:

```bash
pip install -r requirements.txt
```

## Como criar a chave da YouTube Data API

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2. Crie (ou selecione) um projeto.
3. Ative a API **YouTube Data API v3** no projeto.
4. Vá em **APIs e serviços > Credenciais**.
5. Clique em **Criar credenciais > Chave de API**.
6. (Recomendado) Restrinja a chave por API e por origem/uso.

## Como executar

Você pode passar a chave via argumento ou variável de ambiente.

```bash
python -m app.main --url "<URL_DO_VIDEO>" --winners 3 --api-key "SUA_CHAVE"
```

Ou usando variável de ambiente:

```bash
export YOUTUBE_API_KEY="SUA_CHAVE"
python -m app.main --url "<URL_DO_VIDEO>" --winners 3
```

Com seed opcional (resultado reproduzível):

```bash
python -m app.main --url "<URL_DO_VIDEO>" --winners 3 --seed 42
```

## Exemplo de saída

```text
=== Resultado do sorteio ===
Vídeo ID: dQw4w9WgXcQ
Comentários coletados: 153
Participantes únicos: 120
Vencedores (3):
1. João Silva
2. Maria Souza
3. Ana Lima
```

## Limitações

- A YouTube Data API v3 tem limite de quota diária; se exceder, a execução falha.
- Alguns vídeos têm comentários desativados.
- Vídeos removidos/privados ou URLs inválidas não podem ser processados.
