# 🎬 VideoDownloaderBot

Telegram boty: **TikTok**, **Instagram** (Reels, postlar, karusel) we **YouTube** (wideolar, Shorts) salgysyny ugradyň — bot wideony **suw belgisiz (водяной знак-syz)** yzyna ugradýar.

- TikTok-yň suw belgili formaty awtomatik aýrylýar, arassa wideo alynýar
- Wideo hemme telefonlarda açylar ýaly H.264 / MP4 görnüşinde ugradylýar
- Wideo uly bolsa, Telegram çägine sygar ýaly hili awtomatik peseldilýär
- Birnäçe adam bir wagtda ulanyp bilýär
- `yt-dlp` her gün awtomatik täzelenýär (saýtlar üýtgände bot döwülmez ýaly)
- Islege görä: 2 GB-a çenli uly wideolar (ýerli Telegram Bot API serweri bilen)

---

## 📋 Ädimme-ädim gurnama

### 1-nji ädim — Telegram-da bot döretmek

1. Telegram-da **[@BotFather](https://t.me/BotFather)**-i açyň.
2. `/newbot` ýazyň.
3. Botuň adyny ýazyň (meselem: `Wideo Ýükleýji`).
4. Botuň ulanyjy adyny ýazyň, `bot` bilen gutarmaly (meselem: `meniň_wideo_bot`).
5. BotFather size **token** berer, şeýle görnüşde:
   `7123456789:AAH...xyz`
   Muny ýazyp goýuň — hiç kime görkezmäň!

### 2-nji ädim — Serwer (VPS) almak

Islendik **Ubuntu 22.04 / 24.04** ýa-da **Debian 12** serwer bolýar (Hetzner, DigitalOcean, Contabo, Aeza we ş.m.).

- Iň az: **1 CPU, 1 GB RAM, 20 GB disk**
- Maslahat: serweri Ýewropada (Germaniýa, Niderlandlar) alyň — YouTube we Instagram şol ýerde has gowy işleýär.

Serweri alanyňyzdan soň size **IP salgy** we **root parol** bererler.

### 3-nji ädim — Serwere birikmek

#### Termius bilen (telefon ýa-da kompýuter)

1. [Termius](https://termius.com) programmasyny guruň (Android, iPhone, Windows, Mac). Hasap açmak hökman däl, "Skip" / "Continue without account" basyp bilersiňiz.
2. **Hosts** bölümine giriň → **+** düwmesi → **New Host**.
3. Doldurmaly ýerler:
   - **Label (Alias)**: islendik at, meselem `Bot serwer`
   - **Address (Hostname)**: serweriň IP salgysy, meselem `185.12.34.56`
   - **Port**: `22`
   - **Username**: `root`
   - **Password**: serweriň paroly
4. **Save** (✓) basyň.
5. Döredilen host-a basyň. "Do you trust this host?" diýip sorasa → **Continue / Add and continue**.
6. Gara ekran (terminal) açylar we `root@...:~#` ýazgysy görner. Bu, serwere birikendigiňizi aňladýar.

**Terminala buýruk goýmak (paste):**
- Telefonda: ekrana barmagyňyzy uzak basyp saklaň → **Paste**
- Kompýuterde: `Ctrl+Shift+V` ýa-da sycanyň sag düwmesi → **Paste**

**Termius-dan faýl ugratmak (meselem `cookies.txt`):** host-uň ýanyndaky **SFTP** bölümini açyň → serwer tarapynda `/opt/videodownloaderbot` papkasyna geçiň → faýly şol ýere süýräp goýuň (telefonda: **⋮ → Upload**).

#### Kompýuterde Termius-syz

**Windows**: `PowerShell` açyň. **Mac / Linux**: `Terminal` açyň. Soňra ýazyň:

```bash
ssh root@SERWERIŇIZIŇ_IP_SALGYSY
```

`yes` ýazyň, soň paroly giriziň (parol ýazylanda görünmeýär — bu kadaly).

### 4-nji ädim — Bir buýruk bilen boty gurnamak

Serwerde şu buýrugy göçürip goýuň we Enter basyň:

```bash
curl -fsSL https://raw.githubusercontent.com/k9032431-cmd/VideoDownloaderBot/main/install.sh | sudo bash
```

Skript özi:
1. Docker-i we gerekli zatlary gurnaýar
2. Kody GitHub-dan alýar
3. Sizden **bot token**-i soraýar (1-nji ädimdäki token)
4. Goşmaça 2 GB rejimi üçin `api_id` soraýar — islemeseňiz diňe **Enter** basyň
5. Boty işledýär we serwer täzeden açylanda hem awtomatik işledýär

Ahyrynda `✅ Taýýar!` ýazgysyny görersiňiz.

### 5-nji ädim — Barlamak

Telegram-da botuňyzy açyň, `/start` ýazyň, soňra islendik TikTok / Instagram / YouTube salgysyny ugradyň. 🎉

---

## 🔧 Dolandyrmak

Ähli buýruklar serwerde, `cd /opt/videodownloaderbot` papkasynda:

| Näme etmeli | Buýruk |
|---|---|
| Loglary görmek | `docker compose logs -f bot` |
| Gaýtadan başlatmak | `docker compose restart bot` |
| Durzmak | `docker compose down` |
| Täzelemek | 4-nji ädimdäki gurnama buýrugyny gaýtadan işlediň |
| Sazlamalary üýtgetmek | `nano .env`, soňra gurnama buýrugyny gaýtadan işlediň |

### Diňe özüňiz ulanmak üçin

`.env` faýlynda `ALLOWED_USERS=` setirine Telegram ID-ňizi ýazyň (ID-ňizi [@userinfobot](https://t.me/userinfobot) arkaly bilip bilersiňiz). Birnäçe adam bolsa otur bilen: `ALLOWED_USERS=123456,789012`

---

## 📦 Uly wideolar (50 MB-dan 2 GB-a çenli) — islege görä

Telegram adaty ýagdaýda botlara diňe **50 MB**-a çenli faýl ugratmaga rugsat berýär. Bot uly wideolaryň hilini awtomatik peseldýär, ýöne doly hilde uly wideo isleseňiz:

1. [my.telegram.org](https://my.telegram.org) sahypasyna telefon belgiňiz bilen giriň.
2. **API development tools** → islendik at ýazyp programma dörediň.
3. `api_id` (san) we `api_hash` (uzyn setir) alyň.
4. Serwerde: `cd /opt/videodownloaderbot && nano .env` — `TELEGRAM_API_ID=` we `TELEGRAM_API_HASH=` setirlerini dolduryň.
5. Gurnama buýrugyny gaýtadan işlediň.

---

## 🍪 Instagram / YouTube "giriş talap edýär" diýse

Käbir Instagram postlary ýa-da YouTube serweriňizi "bot" hasaplap, giriş (login) talap edip biler. Şonda:

1. Kompýuteriňizde Chrome/Firefox-a **[Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)** giňeltmesini guruň.
2. Instagram-a / YouTube-a **goşmaça (esasy däl) hasap** bilen giriň.
3. Giňeltme arkaly `cookies.txt` faýlyny göçürip alyň (Instagram we YouTube üçin birleşdirip bilersiňiz — bir faýla yzly-yzyna goýuň).
4. Faýly serwere `/opt/videodownloaderbot/cookies.txt` ýerine goýuň (Termius-da **SFTP** arkaly, ýa-da kompýuteriňizden):
   ```bash
   scp cookies.txt root@SERWERIŇIZIŇ_IP_SALGYSY:/opt/videodownloaderbot/cookies.txt
   ```
5. `cd /opt/videodownloaderbot && docker compose restart bot`

> ⚠️ Esasy hasabyňyzy ulanmaň — köp ýükleme sebäpli hasap wagtlaýyn petiklenip bilner.

---

## 🧩 Proýektiň gurluşy

```
bot/main.py                   Telegram bot (aiogram 3)
bot/downloader.py             Wideo ýüklemek (yt-dlp + ffmpeg)
Dockerfile                    Python + ffmpeg + deno (YouTube üçin)
docker-compose.yml            Esasy işletmek
docker-compose.local-api.yml  2 GB rejimi üçin ýerli Bot API serweri
install.sh                    Bir buýruk bilen gurnama
.env.example                  Sazlamalaryň nusgasy
```

## ❓ Köp soralýan soraglar

**Bot jogap bermeýär** → `docker compose logs -f bot` bilen loglara serediň. Token nädogry bolsa, `.env`-de düzediň.

**"Wideony ýükläp bolmady"** → Köplenç saýt üýtgände bolýar. `docker compose restart bot` — bu `yt-dlp`-ni iň täze wersiýa täzeleýär.

**Topar (gruppa) içinde işlemeýär** → @BotFather → `/setprivacy` → botuňyzy saýlaň → `Disable`.
