# Nonce-word stimulus norming — survey draft

**NOT LAUNCHED. NO PARTICIPANT DATA. NOT A PREREGISTRATION.** This is an independent pilot intended to determine which lexical referents merit inclusion in a later transmission experiment.

## Study objective

Pretest 20 candidate behavioural concepts, each paired with a counterbalanced nonce form, for (1) human affective valence, (2) understanding of the intended referent, and (3) interpretation uncertainty. The purpose is **not** to estimate an LLM treatment effect.

## Allocation / task duration

- Proposed: 40 adult English-proficient participants, 10 candidate items each, 400 item exposures total, 20 per concept and 20 per lexical form.
- Balanced incomplete-block allocation: `python -m norming.export_assignments --out norming_assignments.csv`.
- Assign each Prolific session to exactly one available `participant_slot` (1–40), once; prevent reuse through a backend or survey randomizer. This manifest is **not** a collection service.
- Expect **approximately 12–18 minutes** with 10 comprehension paraphrases, not an assumed 10 minutes. Time a small unpaid internal pilot before setting participant pay.
- Each item gets a counterbalanced form and randomized display order. Avoid using fixed example forms that become familiar across items.
- No automatic presumption that all 20 items will be perceived as neutral.

## Actual survey screens

**Screen 1 — information and consent** (to be reviewed for ethics and data protection; do not deploy draft wording without review):

> We are studying how people interpret newly introduced words for everyday practices. You will read short definitions, write brief explanations in your own words and indicate how you evaluate each practice. Participation is voluntary. You may stop at any time. Some answers are free text. Please do not include names, contact details or information identifying real people. We record your Prolific participant identifier for compensation/quality control, response times and your answers; the identifier will be separated from analysis exports. Compensation, retention period, withdrawal deadline, data controller/contact and privacy notice must be provided by the researcher before launch.

A required `I consent / I do not consent` gate must precede items. Do not imply withdrawal remains possible after full anonymisation unless the researcher can still identify a record.

**Screen 2 — task instructions:**

> You will encounter a set of made-up words. Each word names a particular practice or action. There are no right or wrong feelings about the practice. For each word, explain the meaning in your own words, then rate how positively or negatively you regard the **practice itself**. A rating of zero means neither positive nor negative. Focus on what the word denotes, not the pleasantness of its sound or spelling. Do not use a search engine.

**Screen 3 — item template** (repeat for ten allocated concept–form pairings):

> **[nonce]** refers to: **[definition]**
>
> **Q1 (required, open text):** In your own words, what does **[nonce]** mean? (One sentence is enough.)
>
> **Q2 (required, 7-point):** Imagine a neutral report saying: “Someone used **[nonce]** yesterday.” How negative or positive does the underlying practice seem to you? Scale **−3 (very negative)**, −2, −1, **0 (neither)**, +1, +2, **+3 (very positive)**.
>
> **Q3 (required, 0–100):** How confident are you that you understand the definition?
>
> **Q4 (optional, yes/no):** Have you encountered this word previously outside this survey? (If yes, record a short explanation only when justified by ethics review.)

Do not ask participants to rate the *tone of the definition* or an emotionally loaded vignette. The neutral sentence is constant to reduce text-tone contamination. Consider randomising the Q1/Q2 order in a **separate measurement pilot** to quantify demand effects; in the main pretest fix the chosen order.

**Screen 4 — final check:**

> How difficult was it to interpret these invented terms? (1–5)
>
> Optional: Were there any terms whose spelling reminded you of an existing word? If so, which?

**Screen 5 — completion:** Show the genuine study-specific Prolific completion code or redirect **only after answers have been saved successfully**. There is no working link or code in this repository.

## Data export schema (one row per item)

`study_id,participant_slot,pseudonymous_pid,concept_id,presented_nonce_form,item_order,valence_rating,meaning_paraphrase,confidence,prior_familiarity,response_duration_seconds,consent_version,stimulus_inventory_version`

Raw Prolific identifiers are personal-data-linked pseudonyms; store the mapping separately and securely. Do not commit real participant exports or contact information to GitHub.

## Scoring / item selection (MUST freeze before inspecting human responses)

- **Valence:** sample mean on −3..+3; provisional screen `abs(mean) <= 0.75`. Report uncertainty (bootstrap interval) and variability, **not** just observed means.
- **Affective ambiguity:** record dispersion (SD and polarity split), but do not blindly maximise variance; bimodality may reflect group priors or misunderstood denotation.
- **Denotation:** independent, blinded raters code paraphrase agreement against a concept-specific checklist; a provisional screen is **at least 80% correct**; retain rater disagreement and calculate reliability. Ratios from ~20 responses per concept are exploratory and imprecise.
- **Form effects:** check whether particular surface forms consistently drive affect/familiarity. Rare or familiar forms must be replaced and retested.
- **Selection:** choose 8–12 candidates meeting both semantic agreement and valence criteria, balancing their diversity of referents. Record all excluded candidates/reasons; do not retrospectively tune thresholds.
- Do **not** claim equivalence from failure to detect a difference. Avoid selecting items by extremal variance without independent replication (winner's curse).
- A second independent validation sample is strongly preferable before final confirmatory stimulus selection.

## Prolific setup and launch gates

1. Obtain research ethics determination and finalise consent, privacy notice, retention and withdrawal. Determine UK GDPR responsibilities before recruitment.
2. Configure a real compatible hosted questionnaire, with an anonymous access link, stable `PROLIFIC_PID` / study/session ID capture, atomic participant-slot allocation, secure response storage and working completion redirect/code.
3. Internally preview every route, test persistence and completion handling, check mobile accessibility, and verify no PII is required by free text.
4. Time the exact ten-item task with several internal volunteers, set Prolific duration/reward based on **observed** completion times; monitor hourly pay if participants take longer.
5. Pilot on a small number of paid participants before releasing the full 40 slots; avoid irreversible publication without checking.

**Budget illustration (not a quote):** 40 participants × 15 minutes × £9/hour = £90 in base rewards. At 33.3% academic platform fee ≈ £120, or at 42.8% corporate ≈ £128.52, before any applicable platform-fee VAT. Actual eligibility for discounted academic fees is not assumed. If 10 minutes is validated, base rewards are £60 and total fees roughly £80–£85.68 before VAT. No money has been spent.

Prolific references: https://www.prolific.com/pricing ; https://researcher-help.prolific.com/en/articles/445239-what-is-your-pricing ; https://researcher-help.prolific.com/en/articles/445178-what-survey-experimental-software-is-compatible-with-prolific

## Interpretation

The norming sample provides candidate stimulus evidence, **not** evidence that model-mediated semantic drift exists. It cannot be used to claim generation-4 effects, persistence, convergence or model specificity.
