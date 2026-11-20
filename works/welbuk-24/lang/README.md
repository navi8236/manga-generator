# Language versions

One picture per film, an audio track and captions per language (see `../video-kit/`).

Per language (`lang/<code>/`):
- `script.json`: lines for the tour (one per chapter) and the reel (one per cut), each with the time slot the
  picture allows, the text sent to the voice (`say`), the caption (`cap`) and an English back-translation (`en`).
- `clips/`: one voice clip per tour paragraph / reel line group; `jobs.tsv` records the Higgsfield job of each.
- `<film>/`: `voice.wav`, `mix.wav` (voice + ducked music, -14 LUFS), `captions.json`, `fit.json` (speed-up per line).
- `REVIEW.md`: review sheet for a native speaker. `rejected/`: takes that were not used, and why.

Build (repository root):

    python3 -I works/welbuk-24/tools/lang-mix.py ta tour
    python3 -I works/welbuk-24/tools/lang-mix.py ta reel
    python3 -I works/welbuk-24/tools/video-kit.py      # picks up every language with mix.wav + captions.json

Lines may start up to 0.8 s before their cut when the previous line ended early, and may be sped up to x1.22;
anything longer is shortened in the script and re-voiced.
