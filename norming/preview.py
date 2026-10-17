"""Render a local/offline norming survey preview for a single allocation slot.

This **does not upload responses**. Do not use it to recruit Prolific participants.
Run: python -m norming.preview --slot 1 --out norming-preview.html
"""
from __future__ import annotations

import argparse
from html import escape
from pathlib import Path
from .allocation import allocate_norming, load_candidates


def render_preview(slot: int, *, candidates_path: Path | None = None) -> str:
    if type(slot) is not int or not (1 <= slot <= 40):
        raise ValueError("preview slot must be between 1 and 40")
    candidates = load_candidates(candidates_path or Path(__file__).with_name("candidates.csv"))
    assignment = allocate_norming(candidates)[slot - 1]
    sections = []
    for order, item in enumerate(assignment.items, start=1):
        word = escape(item.presented_nonce_form)
        concept = escape(item.concept_id)
        definition = escape(item.definition)
        sections.append(f'''
        <fieldset class="item" data-concept="{concept}" data-word="{word}">
          <legend>Item {order} of {len(assignment.items)}</legend>
          <p><strong>{word}</strong> means: {definition}</p>
          <label>In your own words, what does <strong>{word}</strong> mean?
            <textarea name="paraphrase_{order}" required minlength="3"></textarea>
          </label>
          <label>Imagine a neutral report: “Someone used <strong>{word}</strong> yesterday.”
            How negative or positive does the underlying practice seem?</label>
          <div class="scale" role="group" aria-label="Valence: -3 very negative to +3 very positive">
            {''.join(f'<label><input type="radio" name="valence_{order}" value="{v}" required> {v:+d}</label>' for v in range(-3, 4))}
          </div>
          <label>How confident are you that you understand the definition? (0–100)
            <input name="confidence_{order}" type="number" min="0" max="100" step="1" required>
          </label>
          <label><input name="known_{order}" type="checkbox"> I recognise this term from before the survey.</label>
        </fieldset>''')

    return '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nonce-word norming — local preview</title>
<style>
body{font:16px/1.5 system-ui,sans-serif;max-width:800px;margin:2rem auto;padding:0 1rem;color:#222}
header,fieldset{border:1px solid #ccc;border-radius:10px;padding:1rem;margin:1rem 0}
header{background:#fff2d9}.item{margin:1.5rem 0}legend{font-weight:700}
textarea{display:block;width:95%;min-height:4rem;padding:.6rem;margin:.4rem 0 1rem}
label{display:block;margin:.7rem 0}.scale{display:flex;flex-wrap:wrap;gap:1rem}
.scale label{white-space:nowrap}input[type=number]{display:block;width:100px;padding:.4rem}
button{font:inherit;padding:.7rem 1.2rem;cursor:pointer}
</style></head><body><header><h1>Local pilot preview — NOT hosted</h1>
<p>No backend, no central data collection, no Prolific completion integration. Do not recruit participants through this page.
Responses can only be exported to a JSON file on this device.</p></header>
<main><h2>Understanding invented words</h2>
<p>These words have been invented for a study. There are no correct feelings about their meanings.
Explain each practice in your own words, then rate how it seems to you. Focus on the practice rather than its spelling.
Please do not include identifying information in any text field.</p>
<form id="survey">
<fieldset><legend>Preview-only consent acknowledgement</legend>
<label><input type="checkbox" id="consent" required> I understand this is an offline test preview, not an actual research study.</label>
</fieldset>
''' + "\n".join(sections) + f'''
<button type="submit">Export local JSON (preview only)</button></form></main>
<script>
document.getElementById('survey').addEventListener('submit', (event) => {{
  event.preventDefault();
  const form = event.target;
  if (!form.reportValidity()) return;
  const records = [...document.querySelectorAll('.item')].map((fieldset, i) => {{
    const number = i + 1;
    return {{
      concept_id: fieldset.dataset.concept,
      presented_nonce_form: fieldset.dataset.word,
      item_order: number,
      valence_rating: Number(form.elements['valence_' + number].value),
      meaning_paraphrase: form.elements['paraphrase_' + number].value,
      confidence: Number(form.elements['confidence_' + number].value),
      prior_familiarity: form.elements['known_' + number].checked
    }};
  }});
  const data = {{warning:'SYNTHETIC/OFFLINE LOCAL PREVIEW - NOT A RESEARCH SUBMISSION',
                participant_slot:{assignment.participant_slot},responses:records}};
  const blob = new Blob([JSON.stringify(data, null, 2)], {{type:'application/json'}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'norming-preview-slot-{assignment.participant_slot}.json';
  a.click(); URL.revokeObjectURL(url);
}});
</script></body></html>'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", type=int, default=1)
    parser.add_argument("--out", type=Path, default=Path("norming-preview.html"))
    args = parser.parse_args()
    args.out.write_text(render_preview(args.slot), encoding="utf-8")
    print(f"Saved OFFLINE PREVIEW (not a live study) to {args.out}")


if __name__ == "__main__":
    main()
