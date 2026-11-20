# Welbuk feature tour (long version)

Output: `welbuk-feature-tour.mp4`, about 3 min 16 s, 1280x720, 24 fps, AAC 48 kHz, about -14 LUFS.

A features-only walkthrough of every "Product focus" line in the 24-page storyboard
(`../source/original.txt`), in storyboard order, one chapter per feature:

| Chapter | Storyboard page | Screen(s) | Device |
|---|---|---|---|
| Intro: Practice, Care, Health | 2 | dashboard, careteam, healthrec | laptop, tablet, phone |
| Appointments | 3 | schedule | laptop |
| Live queue | 4 | queue | laptop |
| QR registration & consent | 5 | consent | phone |
| Role-based workflows | 6 | vitals, careteam | tablet |
| Patient record | 7 | emr | laptop |
| Care Scribe | 8 | scribe | laptop |
| Dental | 9 | odonto | laptop |
| Ophthalmology | 10 | ophtho | laptop |
| Dermatology | 11 | derm | laptop |
| Paediatrics | 12 | paeds | tablet |
| Prescriptions | 13 | rxhist | laptop |
| Pharmacy | 14 | stock | laptop |
| Laboratory | 15 | labresult | laptop |
| Referrals | 16 | referral | laptop |
| Billing | 17 | invoice | laptop |
| Day-end | 18 | dayend | laptop |
| Multi-facility & deployment | 19 | facilities | laptop |
| HRMS | 20 | hrms | laptop |
| Patient app | 21 | healthrec | phone |
| Family | 22 | child | phone |
| Looking ahead | 23-24 | network (full screen) | - |

Deployment wording follows the user's corrections: Welbuk Cloud AVAILABLE; on-premises, hybrid and
air-gapped AI "LET'S TALK" (air-gapped AI shown separately). The network chapter is labelled
LOOKING AHEAD and worded as a goal. No staging labels.

Screens are illustrative (`../reel/ui/screens.html`, fictional data) and labelled on screen.
Scenes are the animated clips in `../reel/anim/clips/` (provenance in `../reel/anim/shots.json`);
the dermatology clip was animated through the Higgsfield API (Seedance 2.5) after the MCP credits ran out. Referrals, multi-facility and HRMS open with a dive into the comic page.

Audio: `script.txt` read in two halves by Seed Audio, cloned from the short reel's narrator
(`audio/sources.json`); `tools/tour-vo.py` shortens pauses and joins the halves
(`audio/vo-tight.wav`, paragraph times in `audio/vo-tight.json`). Music: ElevenLabs Music,
stretched by about 3% to the length and ducked under the voice.

Rebuild (repository root):

    node works/welbuk-24/tools/render-ui.cjs
    python3 -I works/welbuk-24/tools/tour-vo.py
    python3 -I works/welbuk-24/tools/tour-edit.py
