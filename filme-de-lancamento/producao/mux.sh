#!/bin/sh
# vídeo + trilha → MP4 final. Sonoridade em −16 LUFS integrados, pico verdadeiro −1,5 dBTP.
set -e
cd "$(dirname "$0")"
OUT="$1"
ffmpeg -y -loglevel error -f f32le -ar 48000 -ac 2 -i score.f32 -af "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=summary" -ar 48000 score_norm.wav
ffmpeg -y -loglevel error -i video.mp4 -i score_norm.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest \
  -movflags +faststart -metadata title="Sistema de Processo Seletivo — Cefor | Ifes" "$OUT"
ffprobe -v error -show_entries format=duration,size:stream=codec_name,width,height,r_frame_rate -of compact "$OUT"
