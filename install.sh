#!/usr/bin/env bash
# VideoDownloaderBot — bir buýruk bilen gurnamak / täzelemek.
# Ulanylyşy (Ubuntu/Debian serwerde):
#   curl -fsSL https://raw.githubusercontent.com/k9032431-cmd/VideoDownloaderBot/main/install.sh | sudo bash
# Täzelemek üçin hem şol buýrugy gaýtadan işlediň.
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/k9032431-cmd/VideoDownloaderBot.git}"
BRANCH="${BRANCH:-}"
INSTALL_DIR="${INSTALL_DIR:-/opt/videodownloaderbot}"

green() { printf '\033[1;32m%s\033[0m\n' "$*"; }
red()   { printf '\033[1;31m%s\033[0m\n' "$*" >&2; }
ask() {  # ask "Sorag" VAR  — curl | bash ýagdaýynda hem klawiaturadan okaýar
  local prompt="$1" var="$2" value=""
  read -r -p "$prompt" value < /dev/tty || true
  printf -v "$var" '%s' "$value"
}

if [ "$(id -u)" -ne 0 ]; then
  red "Bu skripti root bilen işlediň: ... | sudo bash"
  exit 1
fi

green "==> 1/5 Gerekli programmalar gurnalýar"
if command -v apt-get >/dev/null; then
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq git curl ca-certificates >/dev/null
fi
if ! command -v docker >/dev/null; then
  curl -fsSL https://get.docker.com | sh
fi
systemctl enable --now docker >/dev/null 2>&1 || true
if ! docker compose version >/dev/null 2>&1; then
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq docker-compose-plugin
fi

green "==> 2/5 Kod GitHub-dan alynýar: $INSTALL_DIR"
if [ -d "$INSTALL_DIR/.git" ]; then
  git -C "$INSTALL_DIR" fetch --quiet origin
  git -C "$INSTALL_DIR" reset --quiet --hard "origin/${BRANCH:-$(git -C "$INSTALL_DIR" rev-parse --abbrev-ref HEAD)}"
else
  git clone --quiet ${BRANCH:+-b "$BRANCH"} "$REPO_URL" "$INSTALL_DIR"
fi
cd "$INSTALL_DIR"

green "==> 3/5 Sazlamalar (.env)"
[ -f .env ] || cp .env.example .env
set_env() {  # set_env KEY VALUE
  if grep -q "^$1=" .env; then
    sed -i "s|^$1=.*|$1=$2|" .env
  else
    echo "$1=$2" >> .env
  fi
}
get_env() { grep -E "^$1=" .env | head -n1 | cut -d= -f2- || true; }

TOKEN="${BOT_TOKEN:-$(get_env BOT_TOKEN)}"
while true; do
  if [ -z "$TOKEN" ]; then
    ask "@BotFather-dan alnan BOT TOKEN-i giriziň: " TOKEN
  fi
  if curl -fsS "https://api.telegram.org/bot${TOKEN}/getMe" >/dev/null 2>&1; then
    break
  fi
  red "Token nädogry ýa-da Telegram-a birigip bolmady. Gaýtadan synanyşyň."
  TOKEN=""
done
set_env BOT_TOKEN "$TOKEN"

API_ID="${TELEGRAM_API_ID:-$(get_env TELEGRAM_API_ID)}"
API_HASH="${TELEGRAM_API_HASH:-$(get_env TELEGRAM_API_HASH)}"
if [ -z "$API_ID" ] && [ ! -f .asked_api ]; then
  echo
  echo "Goşmaça: 50 MB-dan uly (2 GB-a çenli) wideolary ugratmak isleseňiz,"
  echo "https://my.telegram.org -> API development tools sahypasyndan api_id we api_hash alyň."
  ask "api_id (geçmek üçin Enter basyň): " API_ID
  if [ -n "$API_ID" ]; then
    ask "api_hash: " API_HASH
  fi
  touch .asked_api
fi
set_env TELEGRAM_API_ID "$API_ID"
set_env TELEGRAM_API_HASH "$API_HASH"
chmod 600 .env

# docker cookies.txt-ny faýl hökmünde birikdirmeli (bolmasa papka döreder)
[ -f cookies.txt ] || touch cookies.txt

COMPOSE=(docker compose -f docker-compose.yml)
if [ -n "$API_ID" ] && [ -n "$API_HASH" ]; then
  COMPOSE+=(-f docker-compose.local-api.yml)
  green "    2 GB rejimi açyk (ýerli Telegram Bot API serweri)"
else
  green "    Adaty rejim: wideolar 50 MB-a çenli"
fi

green "==> 4/5 Bot gurulýar we işledilýär"
"${COMPOSE[@]}" up -d --build --remove-orphans

green "==> 5/5 Her gün 04:00-da gaýtadan başlatmak (yt-dlp täzelenmesi)"
cat > /etc/cron.d/videodownloaderbot <<EOF
0 4 * * * root cd $INSTALL_DIR && ${COMPOSE[*]} restart bot >/dev/null 2>&1
EOF
chmod 644 /etc/cron.d/videodownloaderbot

echo
green "✅ Taýýar! Bot işleýär. Telegram-da bota /start ýazyň."
echo "Loglary görmek:   cd $INSTALL_DIR && docker compose logs -f bot"
echo "Täzelemek:        şol gurnama buýrugyny gaýtadan işlediň"
echo "Durzmak:          cd $INSTALL_DIR && ${COMPOSE[*]} down"
