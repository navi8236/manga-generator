# A Better Way to Care — Welbuk: production status (2026-11-11, seven-page revision)

Work: `works/auto-6294ee8a2094` (MANGA_PROJECT=works/auto-6294ee8a2094/workflow.json)
Status: **all stage reviews pass; built, PDF verified, locked and bundled.**
`node cli/auto.mjs finish` was **not** completed for this revision. It refuses with
"Original changed: start a new automatic work", because the work's source was revised at the
user's request after `auto start`. The check was not bypassed. `automation.json` therefore still
describes the six-page version and is superseded by this file.

## Deliverables (seven pages)
- Page PNGs and SVGs: `output/page-01.png` … `output/page-07.png`.
- HTML reader: `output/reader.html` (left-to-right) and `output/index.html`.
- PDF: `output/pdf/manga.pdf` (7 A5 pages; `pdf.mjs verify`: embedded pixels match the PNGs).
  Poppler renders were inspected (`workflow/pdf-inspection.json`). Pages 3-4 were viewed at 150 dpi
  and the unchanged pages on a 60 dpi contact sheet.
- Layers for external editing: `output/layers/`.
- Reproducibility lock: `workflow.lock.json` (sha256 34995c9f…).
- Release package: `releases/auto-6294ee8a2094-v8-34995c9f.tar.gz`
  (sha256 ac64dc172d92a9ab4eff5a65ad00b6975ae8d5a5ef878da081c1ba685d57877f, 442 MB; "Verified portable
  archive"). It is not in git: `releases/` is gitignored and the file exceeds GitHub's limit. Rebuild
  it with `node cli/reproduce.mjs bundle --compressed`.
- The previous six-page release (`releases/auto-6294ee8a2094-v8-a10bf06b.tar.gz`) was left untouched.

## 2026-11-11 revision (user requests)
- Self check-in flow, and a page with three check-in routes (front desk always an option, Welbuk
  Health app, QR code) that all get slots on the screen. The requests are quoted in
  `source/REVISION-2026-11-11.md` along with the confirmed decisions. The doctor stays Dr. Ananya
  ("her tablet").
- New page 3 (5 panels): front desk (Mr. Raman with Meera), app (Priya, outside), QR scan (Ravi),
  consent form, and all three seated under one TV strip "A-10 · A-11 · A-12".
- New page 4 (3 panels): "NOW · A-12" with Raman's and Priya's chairs empty (they were called
  first), the nurse's vitals check, and Dr. Ananya's tablet showing "RAVI · READY".
- Old pages 4-6 became pages 5-7 with the same accepted images (`workflow/renumber-2026-11-11.json`).
- Wording changes after review (recorded in the revision file): the 03-1 caption became "A later
  morning: patients can always check in at the front desk."; the nurse's line became "Hi, Ravi! Just
  relax your arm for me."
- New reference sheets: `assets/characters/nurse.png`, `assets/characters/checkin-patients.png`.

## How the new art was made
- Higgsfield `gpt_image_2_6`, 8 new panel generations plus 4 targeted edits:
  - 03-1: background patients recoloured;
  - 03-2: an outdoor QR stand removed;
  - 04-1: empty chairs;
  - 04-1: kiosk restyled to match 03-1/03-3.
  Exact requests, job IDs, reference IDs and hashes are in `workflow/generation-inputs/`,
  `workflow/generation-history/`, `assets/candidates/*/*.run.json` and `workflow/edits/`.
  `workflow/generation-log.json` lists 27 panels.
- Each image was inspected before acceptance. Quality records were written for every panel; the new
  face crops are in `workflow/quality/sheets/` (rebuilt by `tools/quality-sheets.py`).

## Reviews (independent manga-reviewer subagents, `workflow/stage-reviews/responses/`)
- Source r6, script r27, storyboard first readings and comparisons (latest r17), artwork for all
  27 panels (r10-r12), lettering first readings and comparisons (r9-r10), and final first reading
  plus comparison (r5). All pass.
- Every change-request was fixed and re-reviewed: the TV strip, queue logic, the chair direction,
  palette, the QR stand, the kiosk style and the tablet label.
- Reviewer task IDs are the Agent IDs returned to the parent; the subagents reported none.

## Known minor points judged acceptable by the reviewers
- The 04-3 "RAVI · READY" label is wrapped after the dot and slightly overlaps the drawn card and the
  tablet's bottom bezel. The shared lettering code sizes the box from the text length.
- Waiting-chair and plant-pot styles vary a little between panels.
- Page 7's "Tomorrow … us" voice and the unintroduced vision figures are verbatim source.
- AI image generation is non-deterministic; what is reproducible is the composition from the adopted art.
