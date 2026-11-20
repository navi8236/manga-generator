# Image generation blocker (2026-11-05)

Declared renderer: `ComfyUI+Qwen-Image-Edit-2511-FP8` (docs/COMFYUI.md, docs/CLAUDE-CODE.md).

Observed in the Claude Code cloud container used for this production session:

- `node cli/qwen-comfy.mjs run --prompt-file <smoke prompt> --out <png> --seed 123`
  -> `qwen-comfy: ComfyUI unreachable at http://127.0.0.1:8188: fetch failed`.
  No ComfyUI server is running and none is tunnelled to this container.
- No GPU: `nvidia-smi` is not installed; 4 CPU cores and 15 GB RAM. The setup
  guide records ~48 GB VRAM for the FP8 model used in earlier trials.
- The environment's network policy rejects `huggingface.co:443`
  (proxy `connect_rejected`), so `scripts/comfyui/setup.sh` cannot download
  the pinned Qwen-Image-Edit-2511 FP8 weights here.

Consequences: no character reference sheets, panel images, artwork reviews,
lettering previews, final pages, PDF or reproducibility package were produced.
No placeholder or white test images were registered as production art, and
the renderer was not switched to another tool.

To continue: start ComfyUI on a GPU host (`MANGA_COMFY_HOME=... bash
scripts/comfyui/setup.sh && bash scripts/comfyui/start.sh`), tunnel port 8188
to the production machine (`ssh -N -L 8188:127.0.0.1:8188 ...`), verify with
`curl --fail http://127.0.0.1:8188/system_stats` and the smoke test above,
then continue from `generation prepare` for the character sheets
(`assets/characters/main-cast.png`, `assets/characters/vision-cast.png`) and
the 23 panels, following docs/AUTOMATIC.md steps 5-12.
