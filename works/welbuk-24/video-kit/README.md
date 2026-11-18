# Welbuk video kit

Per film (`reel/`, `tour/`):
- `<film>-master.mp4`: the picture only (no audio, no burned-in captions), 1280x720, H.264.
- `audio/<film>-<lang>.m4a`: full mix per language (voice + music); `audio/<film>-music.m4a`: music only.
- `captions/<film>-<lang>.vtt|.srt`: captions per language, timed to that language's voice.
- `<film>-all-languages.mp4|.mkv`: picture with every audio language and caption track inside (VLC, QuickTime,
  most players show audio and subtitle menus). Captions are off by default.

`player/index.html`: a static web page (works from disk or any web server) with a film switch, an audio language
menu, a CC on/off button and a separate caption language menu. Copy the whole `player/` folder to host it.

Languages so far: English; Tamil (flyer wording, default) and Tamil (video wording), both voiced with Sarvam AI by the client. The earlier Eleven v4 Tamil take is archived in lang/archive/ta-eleven-v4. Screens in the films are illustrative, with fictional data.
Rebuild: `python3 -I works/welbuk-24/tools/video-kit.py` (repository root).

## Single-language files (play in any player)

Many players (phones, browsers, chat previews) only play the first audio track of a multi-track file. For those,
`tamil/` holds plain files with Tamil as the only audio:
- `<film>-tamil.mp4`: Tamil audio (flyer wording), no captions.
- `<film>-tamil-captions.mp4`: the same with Tamil captions burned in (rendered with Chromium for correct Tamil
  shaping: `tools/burn-captions.py FILM ta OUT.mp4`).
- `<film>-tamil-video-wording.mp4`: Tamil audio following the English narration line by line.
