#!/bin/sh
# Her başlananda yt-dlp täzelenýär (saýtlar üýtgände ýalňyşlyk bolmaz ýaly)
pip install --no-cache-dir -q -U "yt-dlp[default]" || echo "yt-dlp täzelenmedi, köne wersiýa bilen dowam edilýär"
exec python -m bot.main
