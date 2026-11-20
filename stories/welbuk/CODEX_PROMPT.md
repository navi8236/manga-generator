# Codex task: Produce the Welbuk onboarding comic

Repository: https://github.com/navi8236/manga-generator
Input story: `welbuk-onboarding-story.txt` (place it in or next to the repository and pass its real filesystem path).
Output target: Six-page, full-colour, English, left-to-right comic with reviewed PNG pages, HTML reader, PDF, and reproducibility package.

1. Clone/open the repository safely, without overwriting work. Follow `AGENTS.md`, `README.en.md`, `REPRODUCE.md`, `docs/QUICKSTART.en.md`, `docs/AUTOMATIC.md`, and production-mode instructions.
2. Check Node.js 24, browser, Python PDF libraries, Poppler, and actual image-generation, image-inspection, and independent subagent-review capabilities. Do not claim any unavailable capability works.
3. Run `npm install` if needed, then `npm run check`.
4. Register source with `node cli/auto.mjs start /absolute/path/to/welbuk-onboarding-story.txt --title "A Better Way to Care — Welbuk"`; set `MANGA_PROJECT` to the exact returned workflow.json path for subsequent operations.
5. Adapt the complete story into six pages. Maintain cast identity and the three distinct Welbuk product roles. Keep the future network vision visually and verbally separated from current features. Dialogue is English, concise, and natural. Use left-to-right reading order, varied panel sizes, and text-free panel art.
6. Follow the repository's full workflow for production audit, scripted panels, references, actual image generation, panel inspection/repairs, lettering, reading-order and subagent reviews, source coverage, composition, reader, PDF render and visual inspection, and reproducibility archive. Preserve source prompts, images, choices, and review records.
7. Only mark complete after the repository's actual finish checks succeed. If blocked, save partial work and report which stage and prerequisite remain unfinished, without misrepresenting success.
8. Deliver resulting `reader.html`, six `page-XX.png` files, `manga.pdf`, and the reproducibility package. Include a concise completion report.

Design priority: Trustworthy, friendly healthcare onboarding education for Welbuk. No actual patient data, diagnosis, medical claims or invented live features.
