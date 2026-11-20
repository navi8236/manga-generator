# A Better Way to Care — Welbuk: production status (2026-11-05)

Work: `works/auto-6294ee8a2094` (MANGA_PROJECT=works/auto-6294ee8a2094/workflow.json)
Renderer declared: `ComfyUI+Qwen-Image-Edit-2511-FP8`. Status: **incomplete, blocked at image generation.**

## Done
- Source registered (`auto start`), full six-page English, left-to-right, full-colour script:
  23 panels, cast with three face traits each, sections, production moment/hands/props,
  readingFlow, transitions. Generator: `tools/build-script.mjs` (run via `history run`).
- Source coverage: `workflow/source-coverage.json` (25 contiguous UTF-16 spans).
- `workflow check` OK; `production-audit work` 0 preflight warnings.
- Storyboards, unnumbered storyboards and panel layout PNGs exported (`workflow plan`).
- Independent manga-reviewer subagent reviews (responses in `workflow/stage-reviews/responses/`):
  - source/all: pass.
  - script/all: r1 changes-requested (phone props) -> fixed; r2 pass (staled by storyboard edits);
    r3 changes-requested (screen direction pages 4-5, bag continuity) -> fixed; r4 pass (current).
  - storyboard first (image-only) readings: r1 all pages, r2 all pages, r3 pages 01/04/05 recorded.
    Fixes made from them: Meera tail/order on 01-2, label border on 02-1, Ravi/Meera sides on 03-4,
    distinct product/vision label style.
  - Reviewer task IDs are the Agent IDs returned to the parent; subagents reported their own as UNAVAILABLE.

## Blocked
- `stage-review prepare storyboard NN` requires the canonical character sheets
  (`assets/characters/main-cast.png`, `assets/characters/vision-cast.png`), which must be generated.
- Image generation is unavailable in this session: see `workflow/blockers/image-generation.md`.
- Not done: character sheets, storyboard comparison reviews + seal, 23 panel generations and
  artwork reviews, layout remeasure, lettering reviews, quality review, build/export, PDF and PDF
  inspection, final review, `auto finish`, freeze/bundle reproducibility package.

## Notes for the storyboard comparison (open first-reading points)
- 04-2/04-3 face boxes: Ravi's single shot is in the left panel and Ananya's in the right; scene text
  fixes facing (Ravi screen-left, Ananya screen-right). Consider moving the face boxes so the two
  look at each other across the gutter if the comparison reviewer agrees.
- Transitions without source captions (02-4->03-1, 03-4->04-1, 04-4->05-1, 06-3->06-4) depend on art.
- 05-2: add "bag strap on his shoulder" (non-blocking script note).
