// One-shot Welbuk Flare storyboard batch. This file is the workflow trigger.
// Eight requests maximum, one image each, sequential, no retries or extra variants.
import fs from 'node:fs/promises';
import path from 'node:path';
import { higgsfield, config } from '@higgsfield/client/v2';

const credentials = process.env.HIGGSFIELD_API_KEY;
if (!credentials || !/^[^:\s]+:[^:\s]+$/.test(credentials)) {
  throw new Error('HIGGSFIELD_API_KEY is absent or not formatted KEY_ID:KEY_SECRET');
}
config({ credentials });

const base = 'https://raw.githubusercontent.com/navi8236/manga-generator/comic/welbuk-onboarding/works/auto-6294ee8a2094/';
const cast = base + 'assets/characters/';
const classic = base + 'output/';
const main = cast + 'main-cast.png';
const checkin = cast + 'checkin-patients.png';
const nurse = cast + 'nurse.png';

const artDirection = [
  'FULL-COLOR INDIAN SLICE-OF-LIFE MANGA PAGE, premium polished comic illustration,',
  'crisp ink lines, expressive consistent faces, soft cel shading, clear narrative sequence,',
  'professional medical setting in Tamil Nadu. Western LEFT-TO-RIGHT reading order.',
  'Draw FOUR STORY PANELS with black comic borders, one top wide panel, two middle panels, one bottom wide panel.',
  'This is a single PORTRAIT comic page. ALL characters should match the canonical character reference.',
  'Dr. Ananya: South Indian woman doctor with dark hair in a low bun, white coat and teal top.',
  'Meera: South Indian receptionist with a long dark braid, blue printed kurta.',
  'Ravi: South Indian man in his 30s wearing a pale green shirt.',
  'Draw NO text, no page numbers, no speech bubbles, no captions, no watermarks, no fake logos.',
  'Leave a clean safe margin around art. Do not use photorealism or fashion editorial aesthetics.',
  'The reference comics guide style and cast ONLY; follow the NEW scene instructions rather than copying their dialogue.'
].join(' ');

const pages = [
  {page:1,title:'Just Another Busy Day', refs:[main,classic+'page-01.png'],
   dialogue:['NARRATOR: A busy day at Dr. Ananya’s Regular Clinic.',
   'MEERA: Appointments, patient details, follow-ups... so much paperwork!',
   'MEERA: The patients have gone home, but we’re still here.',
   'DR. ANANYA: Our time should belong to patients, not paperwork.'],
   scene:'BEFORE WELBUK. IMPORTANT: Completely generic UNBRANDED Regular Clinic with NO magenta logos, no Welbuk words, no software. Panel 1: exterior waiting patients and ordinary clinic sign area with no written letters. Panel 2: hectic receptionist Meera juggling ringing landline, appointment books, forms, registers. Panel 3: Dr. Ananya checking patient paper records while more files arrive. Panel 4: CLEARLY AFTER HOURS around 8:30 pm, exhausted doctor and receptionist under dim evening clinic lighting with enormous stacks of paper registers, handwritten invoices, prescriptions and files. Emotional contrast, heavy paperwork burden.'},
  {page:2,title:'A Different Kind of Clinic', refs:[main,classic+'page-02.png'],
   dialogue:['NARRATOR: A few weeks later, the same clinic is powered by Welbuk.',
   'DR. ANANYA: I can see my clinic workflows in one place.',
   'MEERA: Our team has role-based tools to work together.',
   'DR. ANANYA: Less chaos. More time for care.'],
   scene:'A FEW WEEKS AFTER PAGE ONE. Same Dr. Ananya and same Meera, SAME CLINIC now transformed into organized Welbuk-powered environment. Panel 1: same reception now clean, bright, calm, computer dashboard with magenta/pink accents. Panel 2: Dr Ananya happily using Welbuk Practice laptop with appointment calendar and patient list. Panel 3: Meera holding tablet/mobile with role-based Welbuk Care staff tasks, no invented functions. Panel 4: doctor and receptionist relaxed, daylight and coordination, subtle brand-magenta accents but NO generated lettering or fake logo; real logo is added later in lettering.'},
  {page:3,title:'Appointments Without Confusion', refs:[main,checkin],
   dialogue:['RAVI: I booked my appointment for this morning.',
   'MEERA: Ravi is booked, and Priya is here as a walk-in.',
   'MEERA: Walk-ins fit the available gaps without disrupting booked slots.',
   'NARRATOR: Prior, Walk-in and Emergency appointments stay organized.'],
   scene:'Panel 1: Ravi on smartphone booking an appointment and approaching clinic; panel 2: Meera managing realistic clinic appointment calendar on computer while Priya arrives as a walk-in; panel 3: clearly distinguish three ordered appointment categories BOOKED, WALK-IN, EMERGENCY using colors/icons rather than words; panel 4: waiting room patients look reassured, computer displays organized schedule. Focus visually on intelligent slot allocation, Indian outpatient reception, without fake interface text.'},
  {page:4,title:'When Every Minute Matters',refs:[main,checkin],
   dialogue:['MEERA: Doctor, an urgent patient has arrived.',
   'NARRATOR: Emergency arrivals can receive priority in the queue.',
   'DR. ANANYA: Let’s assess the patient immediately.',
   'NARRATOR: The waiting room sees updated queue information.'],
   scene:'Panel 1: live clinic waiting-room token TV board visible overhead, patients calmly waiting. Panel 2: a concerned family member arrives with an urgent patient; Meera signals the nurse/doctor. Panel 3: emergency token enters priority queue on organized screen, a small visual red urgency icon; no clinically unsafe delay. Panel 4: the nurse assists urgent patient to evaluation room while Dr Ananya prepares, other patients see updating board. Respect realistic clinical triage; no dramatic ambulance.'},
  {page:5,title:'A Smarter Welcome',refs:[main,checkin],
   dialogue:['RAVI: I can check in using the clinic QR code.',
   'MEERA: I can help you register too, Mr. Raman.',
   'NARRATOR: Consent and registration feed the reception check-in queue.',
   'RAVI: Now I know my token and where to wait.'],
   scene:'Panel 1: Ravi scanning a generic pink-accented QR stand at Welbuk clinic entrance with his phone; panel 2: phone-first onboarding, simple verified form and consent checkbox shapes, no legible fake words; panel 3: Meera warmly assisting older patient Mr Raman at counter while digital records appear; panel 4: a modern waiting room showing token and check-in confirmation on Ravi phone, happy coordinated staff.'},
  {page:6,title:'The Right Task for the Right Team',refs:[main,nurse],
   dialogue:['NURSE: Ravi’s vitals are recorded.',
   'DR. ANANYA: I can see his latest observations.',
   'MEERA: The team knows what needs attention.',
   'NARRATOR: Welbuk Practice and role-based Welbuk Care stay coordinated.'],
   scene:'Panel 1: split scene reception Meera, nurse clinical station, Dr Ananya consultation room; panel 2: nurse with teal uniform taking patient Ravi blood pressure and entering clinical vitals into tablet; panel 3: Dr Ananya reading accurate vitals indicators and next-patient queue on tablet, no false medical values; panel 4: staff coordinate patient hand-off at bright clinic corridor, digital notifications and clear roles, pink Welbuk palette, no drawn dialogue.'},
  {page:7,title:'The Consultation Begins With Context',refs:[main,classic+'page-05.png'],
   dialogue:['DR. ANANYA: Hello, Ravi. What brings you in?',
   'RAVI: I’ve been unusually tired.',
   'NARRATOR: History, allergies and vitals are available for review.',
   'DR. ANANYA: Let’s understand the concerns before deciding next steps.'],
   scene:'Panel 1: Dr Ananya warmly greets Ravi at desk inside private clean consultation room; panel 2: Ravi describes mild tiredness while doctor listens carefully; panel 3: over-the-shoulder electronic medical record screen with medical history cards, allergies, vitals and past visits as legible graphics but NO invented text; panel 4: doctor documents structured SOAP-style clinical note on computer, focused caring expression, no actual diagnosis or treatment.'},
  {page:8,title:'Listening With Care', refs:[main,classic+'page-05.png'],
   dialogue:['DR. ANANYA: May I use a voice assistant to help draft notes?',
   'RAVI: Yes, I consent.',
   'NARRATOR: SpeakADoc creates a draft transcript and summary.',
   'DR. ANANYA: I’ll review the notes before completing the record.'],
   scene:'STAGING DEMONSTRATION, NOT A LIVE DEFAULT FEATURE. Panel 1: Dr Ananya clearly requests Ravi consent before optional recording, Ravi responds positively with hand gesture. Panel 2: doctor listens to patient naturally during consultation, unobtrusive subtle microphone status icon on her device. Panel 3: clinical tablet shows speaker-separated transcript concept and brief summary as gray text-like blocks (do not render fake words). Panel 4: doctor attentively reviews and corrects electronic SOAP notes before completing documentation. Human doctor remains in control, quiet professional tone.'}
];

const out = 'output/welbuk-flare-batch-1';
await fs.mkdir(out,{recursive:true});
const manifest = {title:'Welbuk — A Better Way to Care',model:'marketing-studio/image/flare',quality:'medium',resolution:'1k',pages:pages.map(p=>({...p,status:'pending'}))};
async function save(){await fs.writeFile(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2));}
await save();
console.log('Beginning bounded batch: 8 page image requests, exactly 1 image/page, no retries.');
for(const p of pages) {
  const entry = manifest.pages.find(x=>x.page===p.page);
  const prompt = artDirection + ' STORY CONTENT: ' + p.scene;
  console.log('Submitting page',p.page,'of 8 using Marketing Studio Image 2.5 Flare');
  try {
    const result = await higgsfield.subscribe('marketing-studio/image/flare',{
      input:{
        prompt, image_urls:p.refs, aspect_ratio:'2:3',resolution:'1k',
        quality:'medium', moderation:'auto', enhance_prompt:false
      },
      withPolling:true
    });
    const candidate = result?.images?.[0];
    const url = typeof candidate === 'string'?candidate:candidate?.url||candidate?.image_url||result?.jobs?.[0]?.results?.raw?.url;
    if (!/^https:\/\//.test(url||'')) {
      throw new Error('No HTTPS image URL returned');
    }
    const response = await fetch(url,{signal:AbortSignal.timeout(120000)});
    if(!response.ok)throw new Error('Image download HTTP '+response.status);
    const bytes=Buffer.from(await response.arrayBuffer());
    if(bytes.length<1000 || bytes.length>25000000)throw new Error('Unexpected image size');
    const type=response.headers.get('content-type')||'';
    const ext=type.includes('png')?'png':type.includes('webp')?'webp':'jpg';
    entry.file='raw-page-'+String(p.page).padStart(2,'0')+'.'+ext;
    await fs.writeFile(path.join(out,entry.file),bytes);
    entry.status='completed';
    entry.bytes=bytes.length;
    console.log('Page',p.page,'saved, bytes',bytes.length);
  } catch(err) {
    entry.status='failed';
    entry.error=String(err?.message||err).slice(0,600);
    console.error('Stopping after page',p.page,'error:',entry.error);
    await save();
    process.exitCode=1;
    break;
  }
  await save();
}
console.log('Completed',manifest.pages.filter(p=>p.status==='completed').length,'out of 8 pages');
