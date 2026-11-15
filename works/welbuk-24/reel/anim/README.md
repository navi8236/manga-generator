# Animated demo reel ("the manga comes alive")

Output: `../welbuk-demo-reel-animated.mp4` (61 s, 1280x720, 24 fps, AAC 48 kHz, about -14 LUFS).

1. `refs/`: panel crops (art only, no lettering) from the accepted page candidates, plus the cast
   sheets. Uploaded to Higgsfield; media ids in `refs/media-ids.tsv`.
2. `keys/`: one 16:9 keyframe per story beat, drawn with GPT Image 2.6 from the panel and cast
   references so characters and line style match the comic.
3. `clips/`: each keyframe animated with Seedance 2.0 Mini (image-to-video, start frame), 4-6 s,
   no generated audio. Exact prompts, parameters, job ids and SHA-256 are in `shots.json`, with
   the rejected take and the reason.
4. `works/welbuk-24/tools/reel-anim.py` edits the reel: cover, then camera dives from the real
   lettered page into the panel, which lifts off the page and dissolves into the animated shot
   (pages 01, 02, 21); manga-style slide and white-flash transitions; product and end cards
   animated in time with the voice; captions from `../voiceover.txt`; voice and music from
   `../audio/` (music ducked under the voice). `edit.json` lists every segment, source hash and
   caption time.

Rebuild (repository root):

    python3 -I works/welbuk-24/tools/reel-anim.py works/welbuk-24/reel/audio/vo-2e453c1b.wav works/welbuk-24/reel/audio/music-fbdba503.mp3

The edit is reproducible from the saved clips; the AI generations themselves are not.
