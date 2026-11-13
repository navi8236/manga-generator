// Shot list for the 60-second Welbuk demo reel (16:9). Each shot animates one comic panel.
// Motion is kept gentle so faces, hands and drawn screens stay stable; no text is generated.
const STYLE =
  'Keep the exact hand-drawn anime/manga illustration style, colours, characters and composition of the image. Gentle, natural motion only; steady camera. Do not add any text, letters, numbers, logos or new objects. Screens keep their simple abstract shapes.';
const P = (motion) => `${motion} ${STYLE}`;

export const shots = [
  { id: 's01', page: '01', panel: 4, prompt: P('Late evening. The tired doctor slowly rubs her forehead and sighs; the receptionist rests her head on the stack of registers and shifts slightly. Slow push-in.') },
  { id: 's02', page: '02', panel: 4, prompt: P('Daytime. The doctor and receptionist smile and welcome the arriving patients; small friendly gestures. Slow push-in.') },
  { id: 's03', page: '05', panel: 1, focus: [0.5, 0.35], prompt: P('The man raises his phone to the pink QR standee and smiles. Subtle movement.') },
  { id: 's04', page: '04', panel: 4, prompt: P('The receptionist calmly reassures two waiting patients with open-hand gestures. Slow push-in.') },
  { id: 's05', page: '06', panel: 2, prompt: P('The nurse checks the blood pressure cuff and looks at her tablet; the patient breathes calmly.') },
  { id: 's06', page: '07', panel: 2, prompt: P('The patient talks, hand at the back of his neck; the doctor nods attentively.') },
  { id: 's07', page: '08', panel: 1, prompt: P('The doctor gestures toward the small device on the desk; the patient nods and opens his palm in agreement.') },
  { id: 's08', page: '09', panel: 4, prompt: P('The dentist points at the monitor; the patient leans in and nods, relieved.') },
  { id: 's09', page: '14', panel: 4, prompt: P('The pharmacist hands the paper bag across the counter with a smile.') },
  { id: 's10', page: '17', panel: 4, prompt: P('The receptionist hands the receipt to the patient; both smile.') },
  { id: 's11', page: '18', panel: 4, prompt: P('Dusk. The doctor locks the glass door and smiles at the receptionist; they turn to leave.') },
  { id: 's12', page: '21', panel: 4, prompt: P('The doctor welcomes the patient back with a warm smile and an open-hand gesture.') },
  { id: 's13', page: '22', panel: 4, prompt: P('A warm family moment: three generations smile and lean together. Soft light, slow push-in.') },
  { id: 's14', page: '24', panel: 4, prompt: P('The doctor welcomes a patient at the clinic entrance; staff and the family smile. Slow pull-back.') },
];
