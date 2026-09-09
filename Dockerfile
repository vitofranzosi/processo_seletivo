# Imagem de desenvolvimento do backend.
#
# Ela existe para que "subir o sistema" seja o mesmo ato em macOS, Windows e Linux. O que varia
# entre as três plataformas — de onde vem o PostgreSQL, qual é o superusuário dele, qual locale o
# `initdb` escolheu — deixa de ser problema de quem instala: a imagem é Linux nas três, e o
# `compose.yaml` é quem liga as pontas.
#
# **Não é imagem de produção.** Roda `manage.py runserver`, mantém `DEBUG` ligado e serve os
# estáticos pelo próprio Django. Produção é `config.settings.production`, que se recusa a subir
# com metade do que este arquivo assume.
FROM python:3.13-slim-bookworm

# O uv vem por cópia binária, e não por `pip install uv`: é a forma que a própria Astral publica,
# não mexe no ambiente Python da imagem e fixa a versão da ferramenta junto com a da imagem.
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /bin/

# `make` porque o `Makefile` é a interface documentada do backend, e não uma conveniência: quem
# está dentro do container roda os mesmos alvos que quem está fora (`make lint`, `make test-pg`).
# Sem ele, a documentação teria duas versões de cada comando.
RUN apt-get update \
    && apt-get install --yes --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*

# O ambiente virtual mora **fora** da árvore do código de propósito. O `compose.yaml` monta
# `./backend` por cima de `/app/backend` para que o autoreload enxergue a edição feita no host, e
# um `.venv` dentro dessa árvore seria escondido pela montagem — as dependências instaladas na
# imagem sumiriam no instante em que o container subisse.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app/backend

# Duas camadas, e nesta ordem, para que trocar uma linha de código não reinstale o mundo:
# o manifesto e o lock mudam raramente, o código muda a cada commit. `--no-install-project`
# resolve só as dependências, porque o projeto ainda não foi copiado.
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --extra dev --locked --no-install-project

COPY backend/ ./
RUN uv sync --extra dev --locked

COPY scripts/docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# A raiz privada dos documentos do candidato. É volume no `compose.yaml`; aqui só garantimos que o
# diretório exista e pertença a quem roda o processo.
RUN useradd --create-home --uid 10001 aplicacao \
    && mkdir -p /var/lib/processo-seletivo/arquivos \
    && chown -R aplicacao:aplicacao /var/lib/processo-seletivo /opt/venv

USER aplicacao

EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
