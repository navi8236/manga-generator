# Welbuk video kit

Per film (`reel/`, `tour/`):
- `<film>-master.mp4`: the picture only (no audio, no burned-in captions), 1280x720, H.264.
- `audio/<film>-<lang>.m4a`: full mix per language (voice + music); `audio/<film>-music.m4a`: music only.
- `captions/<film>-<lang>.vtt|.srt`: captions per language, timed to that language's voice.
- `<film>-all-languages.mp4|.mkv`: picture with every audio language and caption track inside (VLC, QuickTime,
  most players show audio and subtitle menus). Captions are off by default.

`player/index.html`: a static web page (works from disk or any web server) with a film switch, an audio language
menu, a CC on/off button and a separate caption language menu. Copy the whole `player/` folder to host it.

Languages so far: English, Tamil. Screens in the films are illustrative, with fictional data.
Rebuild: `python3 -I works/welbuk-24/tools/video-kit.py` (repository root).
