# Welbuk — A Better Way to Care (24 story pages + feature page + covers)

| File | What |
|---|---|
| welbuk-a-better-way-to-care.pdf | Combined comic: front cover, pages 1-25, back cover (27 pages) |
| pages/ | Individual pages at 2048x3072 (covers at their supplied 1055x1491) |
| reader/index.html | Mobile reading edition (one column, lazy loading) |
| manifest.json | SHA-256 of every page and the PDF |

Rebuild: `node works/welbuk-24/tools/build-script.mjs`, then `MANGA_PROJECT=works/welbuk-24/workflow.json node cli/workflow.mjs plan` and `preview`, render the SVGs, then `node works/welbuk-24/tools/assemble.cjs`.

Sources: storyboard v3.0 and the user's revisions (source/original.txt); page art generated with the Higgsfield API (Marketing Studio Image 2.5 Flare), records beside each image in assets/candidates/; page 25 typeset from tools/page25.html; covers supplied by the user (source/cover/), with the back-cover QR replaced by a real code for https://www.welbuk.com (tools/fix-cover-qr.py, record source/cover/back.json).

Status: the pages were inspected by the production agent; the repository's independent stage reviews (script, storyboard, artwork, lettering, final) have not been run on this work yet.
