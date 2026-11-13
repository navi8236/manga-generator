// Builds workflow/source-coverage.json: contiguous UTF-16 spans of the saved
// source mapped to the adapted panels, with a concrete adaptation note each.
import fs from 'node:fs';
import crypto from 'node:crypto';

const W = 'works/auto-6294ee8a2094';
const source = fs.readFileSync(`${W}/source/original.txt`, 'utf8');
const at = (needle, from = 0) => {
  const i = source.indexOf(needle, from);
  if (i < 0) throw new Error('Missing source marker: ' + needle);
  return i;
};

const notes = {
  intro: [
    ['01-1', '03-1', '06-2', '06-3', '06-4'],
    'Title, disclaimer and cast list. The cast descriptions became cast.description/faceDesign for Dr. Ananya (teal kurta under white coat), Meera (blue kurta), Ravi (light green shirt) and the Nurse added in the 2026-11-11 revision (lavender scrubs); unstated details are recorded as manga supplements. The disclaimer that future referral-network experiences are vision drives the "WELBUK VISION" labels and vignette styling on 06-2 and 06-3.',
  ],
  '01-1': [['01-1'], 'Wide morning establishing shot of a neighbourhood Tamil Nadu clinic with Dr. Ananya welcoming patients; the source caption is lettered verbatim.'],
  '01-2': [['01-2'], 'Paper registers, ringing phone and queue are drawn as props and background; Meera\'s line is kept verbatim but split into two balloons at the ellipsis so the list and the wish read as two breaths.'],
  '01-3': [['01-3'], 'Ananya looks thoughtfully toward the reception desk; her line is kept verbatim in one balloon.'],
  '02-1': [['02-1'], 'Laptop close-up with a generic, text-free setup form; source caption verbatim. A "WELBUK PRACTICE / for the clinic" label names the product that the source panel describes, so readers learn the first product role.'],
  '02-2': [['02-2'], 'Ananya at the laptop considering team roles; line verbatim.'],
  '02-3': [['02-3'], 'Meera with a staff phone showing an abstract screen; line verbatim plus a "WELBUK CARE / for clinic staff" label naming the source\'s staff app.'],
  '02-4': [['02-4'], 'Friendly two-shot; Ananya\'s line verbatim, Meera answers with a nod.'],
  '03-1': [['03-1'], 'Revised page 3 (2026-11-11, user request). Ravi walks in through the glass entrance holding his phone and notices the abstract QR check-in stand; caption verbatim.'],
  '03-2': [['03-2'], 'Ravi scans the abstract QR pattern with his phone (no real code, no text); caption verbatim.'],
  '03-3': [['03-3'], 'Over-the-shoulder phone close-up: blank form fields and a consent tick-box tapped by his thumb, so no identifying data is shown; caption verbatim.'],
  '03-4': [['03-4'], 'Waiting area: Ravi looks up at the wall TV; the TV screen is drawn blank and the token "TOKEN A-12" is lettered as a label over it; caption verbatim.'],
  '03-5': [['03-5'], 'The new nurse character (cast + nurse sheet) takes Ravi\'s vitals with a cuff and oximeter; the monitor shows no readings; her line is verbatim.'],
  '03-6': [['03-6'], 'Cut to the consultation room: Dr. Ananya reads a notification on her tablet; the screen is drawn blank and "RAVI · READY" is lettered as a label over it; caption verbatim.'],
  '04-1': [['04-1'], 'Consultation-room greeting, laptop closed aside; line verbatim.'],
  '04-2': [['04-2'], 'Ravi states a routine concern; no diagnosis or medical advice is drawn or written. Line verbatim.'],
  '04-3': [['04-3'], 'Ananya listens attentively with the laptop closed aside; the caption is verbatim and the closed laptop shows technology staying in the background.'],
  '04-4': [['04-4'], 'Ananya discusses next steps with a reassuring gesture and no treatment details; line verbatim.'],
  '05-1': [['05-1'], 'Meera introduces the Welbuk Health patient app on a phone; line verbatim.'],
  '05-2': [['05-2'], 'Ravi holds a conceptual, text-free app screen with appointment and health icons; line verbatim plus a "WELBUK HEALTH / for patients" label naming the third product role.'],
  '05-3': [['05-3'], 'Meera\'s line verbatim; the wording "what is available to you" is kept so no unlaunched features are implied.'],
  '05-4': [['05-4'], 'Ravi leaves the clinic waving, reassured; caption verbatim.'],
  '06-1': [['06-1'], 'Train-window transition to another city; the conditional caption ("may") is verbatim.'],
  '06-2': [['06-2'], 'A conceptual connected clinic and specialist inside a pale-blue vignette, with a "WELBUK VISION" label and the source caption verbatim, so it is not read as a current feature.'],
  '06-3': [['06-3'], 'Symbolic family scene with Ravi, his partner and child around an abstract family wellness app. The caption is verbatim; a repeated "WELBUK VISION" label and the same vignette keep it separate from current features (manga supplement).'],
  '06-4': [['06-4'], 'Large closing group panel of Ananya, Meera and Ravi in the present, with the three product labels and the final caption verbatim.'],
  art: [
    ['01-1', '02-1', '03-3', '05-2', '06-2', '06-4'],
    'Art direction applied as config.style, colorMode "color", readingDirection "left-to-right", varied panel rectangles, text-free panel art with separately composed English lettering, and quality.avoid entries against real patient data, medical claims and readable UI text. Vision panels use a distinct vignette.',
  ],
};

const cuts = [{ start: 0, key: 'intro' }];
for (let page = 1; page <= 6; page++) {
  const pageAt = at(`PAGE ${page} —`);
  const panelCount = page === 1 ? 3 : page === 3 ? 6 : 4;
  for (let n = 1; n <= panelCount; n++) {
    const start = n === 1 ? pageAt : at(`Panel ${n}`, pageAt);
    cuts.push({ start, key: `0${page}-${n}` });
  }
}
cuts.push({ start: at('ART DIRECTION'), key: 'art' });
for (let i = 1; i < cuts.length; i++)
  if (cuts[i].start <= cuts[i - 1].start) throw new Error('Unordered markers at ' + cuts[i].key);

const spans = cuts.map((c, i) => ({
  start: c.start,
  end: i + 1 < cuts.length ? cuts[i + 1].start : source.length,
  panels: notes[c.key][0],
  adaptation: notes[c.key][1],
}));
const coverage = {
  sourceHash: crypto.createHash('sha256').update(fs.readFileSync(`${W}/source/original.txt`)).digest('hex'),
  spans,
};
fs.mkdirSync(`${W}/workflow`, { recursive: true });
fs.writeFileSync(`${W}/workflow/source-coverage.json`, JSON.stringify(coverage, null, 2) + '\n');
console.log(`Wrote ${spans.length} spans covering 0..${source.length}`);
