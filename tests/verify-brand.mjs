// Regression check for the optional brand theme in shared lettering (workflow.json "brand").
import assert from 'node:assert/strict';
import { createLettering } from '../src/lettering.mjs';

const cast = {
  a: {},
  narration: { kind: 'caption' },
  label: { kind: 'caption', variant: 'label' },
};
const panel = {
  id: '01-1',
  rect: [24, 24, 976, 600],
  speakers: { a: { anchor: [500, 400], face: [450, 330, 100, 120] } },
};
const cap = { speaker: 'narration', text: 'A caption.', textColumns: ['A caption.'], textDirection: 'horizontal', x: 20, dy: 20 };
const lab = { speaker: 'label', text: 'STAGING', textColumns: ['STAGING'], textDirection: 'horizontal', x: 600, dy: 20 };

// Without a theme: unchanged teal label and plain caption.
const plain = createLettering(cast);
assert.match(plain.balloon(panel, lab), /fill="#e6f4f3" stroke="#1d6f6a"/);
assert.doesNotMatch(plain.balloon(panel, cap), /#FD006A/);

// With a theme: accent-coloured label and a caption bar.
const theme = { accent: '#FD006A', labelFill: '#FFF0F6', captionBar: true };
const branded = createLettering(cast, theme);
assert.match(branded.balloon(panel, lab), /fill="#FFF0F6" stroke="#FD006A"/);
assert.match(branded.balloon(panel, cap), /width="5" height="\d+" fill="#FD006A"/);
// Speech balloons are not recoloured.
const speech = { speaker: 'a', text: 'Hello.', textColumns: ['Hello.'], textDirection: 'horizontal', x: 300, dy: 20 };
assert.equal(branded.balloon(panel, speech), plain.balloon(panel, speech));
console.log('Brand theme lettering verified');

// Optional fontSize scales the box and the text; the default stays 26.
import { box } from '../src/lettering.mjs';
const big = { speaker: 'narration', text: 'Clinic and hospital operations.', textColumns: ['Clinic and hospital operations.'], textDirection: 'horizontal', x: 20, dy: 20 };
const small = { ...big, fontSize: 20 };
assert.ok(box(panel, small)[2] < box(panel, big)[2] && box(panel, small)[3] < box(panel, big)[3]);
assert.match(plain.balloon(panel, small), /font-size="20"/);
assert.throws(() => box(panel, { ...big, fontSize: 30 }), /fontSize/);
console.log('Caption font size verified');

// Optional fontFamily replaces the default horizontal lettering font.
const fam = createLettering(cast, { ...theme, fontFamily: 'Inter, DejaVu Sans, sans-serif' });
assert.match(fam.balloon(panel, speech), /font-family="Inter, DejaVu Sans, sans-serif"/);
assert.match(plain.balloon(panel, speech), /font-family="Meiryo,MS Gothic,sans-serif"/);
console.log('Lettering font family verified');

// Optional compact padding makes the box smaller; default boxes are unchanged.
const comp = { ...small, compact: true };
assert.ok(box(panel, comp)[3] < box(panel, small)[3] && box(panel, comp)[2] < box(panel, small)[2]);
console.log('Compact balloon verified');
