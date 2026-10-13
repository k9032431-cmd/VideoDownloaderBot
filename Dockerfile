FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# YouTube üçin JavaScript runtime (yt-dlp talap edýär)
COPY --from=denoland/deno:bin /deno /usr/local/bin/deno

ENV PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot ./bot
COPY entrypoint.sh .

CMD ["sh", "/app/entrypoint.sh"]
