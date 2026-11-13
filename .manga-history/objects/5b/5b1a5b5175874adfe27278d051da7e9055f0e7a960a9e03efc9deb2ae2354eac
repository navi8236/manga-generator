# A Better Way to Care — Welbuk: production status (2026-11-11)

Work: `works/auto-6294ee8a2094` (MANGA_PROJECT=works/auto-6294ee8a2094/workflow.json)
Status: **complete** (`node cli/auto.mjs finish` passed; see `automation.json`).

## Deliverables
- Six page PNGs: `output/page-01.png` … `output/page-06.png` (SVG alongside).
- HTML reader: `output/reader.html` (left-to-right English reader; `output/index.html`).
- PDF: `output/pdf/manga.pdf` (6 A5 pages; `pdf.mjs verify`: embedded pixels match the PNGs).
- Layers for external editing: `output/layers/`.
- Reproducibility lock: `workflow.lock.json` (sha256 a10bf06b…).
- Release package: `releases/auto-6294ee8a2094-v8-a10bf06b.tar.gz`
  (sha256 a33c6098d8277b504f2a70c65bc0e9e9ca786a54db7f5d493e6c475540c5e6fd, 314 MB).
  It is not in git: `releases/` is gitignored and the file exceeds GitHub's 100 MB limit.
  All its inputs are committed; rebuild it with `node cli/reproduce.mjs bundle --compressed`
  (the lock makes the archive contents verifiable by hash).

## How it was made
- Renderer: Higgsfield `gpt_image_2_6` (ComfyUI was impossible here: no GPU, huggingface.co blocked;
  the user approved Higgsfield). Every generation/edit is saved with its exact request, job ID,
  reference IDs and image hash (`assets/candidates/*/*.run.json`, `workflow/higgsfield-jobs.json`,
  `workflow/generation-log.json`). 23 panels, plus targeted edits recorded in `workflow/edits/`.
- English dialogue is composed by the shared lettering code, never painted into the art.
- Independent manga-reviewer subagent reviews for every stage (`workflow/stage-reviews/responses/`):
  source, script (r16 pass), storyboard first readings + comparisons, artwork for all 23 panels,
  lettering first readings + comparisons, final first reading + final comparison (pass).
  Reviewer task IDs are the Agent IDs returned to the parent; subagents reported none.
- Image-only first readings were recorded before every comparison (two-phase reading protocol).
- Quality review (eight checks + face identity) for every panel: `workflow/quality/*.review.json`.
- PDF inspected page by page after Poppler rendering: `workflow/pdf-inspection.json`.

## Fixes made from reviews (summary)
- Lettering: 03-1 tail rerouted off Ravi's hand; 03-4/05-3 tails made visible; 04-3 caption off
  Ananya's head; 02-1 label/caption cover blank art; 06-2 caption moved so the welcoming hand shows.
- Art edits: 02-3 reframed in the evening office; 02-4 blank corner filled and relit to evening;
  03-1 braid side; 03-2/03-3 bag shoulder and bangle wrist; 03-3 cream counter;
  01-1 clinic exterior matched to the later teal-awning entrance (door opened);
  01-2/01-3 window awning made teal. 05-2 eyeline edit was rejected; the glance is recorded as deliberate.
- Records (scene/hands/props) repeatedly corrected to match the accepted art.

## Known minor, accepted points (reviewers judged non-blocking)
- Waiting-chair style varies on page 1 and page 4; Ananya's bun reads looser in some front views.
- The navy reception phone in 03-1 resembles Ravi's phone.
- Source wording kept verbatim (e.g. "Our time belongs with patients").
- AI image generation is non-deterministic; the reproducible part is composition from the adopted art.

## 2026-11-11 revision in progress (seven pages)
- User requests: self check-in flow, and a page with three check-in routes (front desk always an
  option, Welbuk Health app, QR) all getting slots on the screen. See `source/REVISION-2026-11-11.md`.
- New pages 3 (5 panels) and 4 (3 panels); old pages 4-6 renumbered to 5-7 with the same accepted
  images (`workflow/renumber-2026-11-11.json`). New reference sheets: `assets/characters/nurse.png`,
  `assets/characters/checkin-patients.png`.
- NOTE: `assets/panels/03-*.png` and `04-*.png` currently still hold the OLD page 3/4 art (re-accepted
  by a helper-script mistake while the new panels were not yet generated). They are placeholders and
  will be replaced by the new generations; no review has been or will be recorded against them.
- The previous release (`releases/auto-6294ee8a2094-v8-a10bf06b.tar.gz`) and `automation.json` describe
  the six-page version and are superseded once this revision finishes.
