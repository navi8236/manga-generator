# PDF history

Every PDF of this comic given to the user, kept so that earlier versions stay available.
The current official PDF is always `output/pdf/manga.pdf`; it is rebuilt by
`node cli/pdf.mjs create` and checked by `node cli/pdf.mjs verify`. These files are
copies, and nothing here is regenerated or edited later. Each new version is added as a new file.

| File | Pages | Status | Source |
|---|---|---|---|
| 2026-11-11-v1-6-pages.pdf | 6 | official, verified | commit 1665f47 (`output/pdf/manga.pdf`) |
| 2026-11-11-v2-7-pages.pdf | 7 | official, verified, released (revisions 1-2: check-in routes) | commit 88e7a9e |
| 2026-11-12-v3-8-pages.pdf | 8 | official, verified (revision 3: doctor's screen, AI voice consent) | commit 4dbd5ea |
| 2026-11-12-draft-8-pages-preview.pdf | 8 | draft preview sent before verification (smaller images) | scratch export |
| 2026-11-12-draft-9-pages-page8-storyboard.pdf | 9 | draft preview; page 8 is still a storyboard sketch (Request 4) | scratch export |

Checksums are in `SHA256SUMS`. Git history also keeps every committed `output/pdf/manga.pdf`.
