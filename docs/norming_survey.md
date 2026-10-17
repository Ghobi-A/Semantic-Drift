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

- **Valence exclusion rule (frozen here prior to data collection):** exclude a concept if **either** its two-sided 95% one-sample Student-t confidence interval for the mean **excludes 0**, **or** `abs(unrounded_sample_mean) > 0.5` on the −3..+3 scale. Exactly 20 valid ratings per concept are required for an automatic screening decision; otherwise flag **insufficient data**, do not silently accept. At n=20, use t critical 2.093024 (19 df); do not switch to normal-approximation CI after seeing data. This is **screening, not equivalence testing or certification of neutrality**; even a retained concept needs independent validation.
- **Valence uncertainty:** report the unrounded mean, sample SD, CI endpoints, number of positive/negative responses and deviations from planned missingness. Do not optimise for large variance; heterogeneity may reflect contradictory or misunderstood interpretations.
- **Affective ambiguity:** record dispersion (SD and polarity split), but do not blindly maximise variance; bimodality may reflect group priors or misunderstood denotation.
- **Denotation exclusion rule (strict screening):** two independently blinded raters score each paraphrase against a **prewritten concept-specific checklist**; record their independent binary codes and a documented adjudication where they disagree. Retain a concept only when **at least 18 of 20 (90%)** paraphrases are adjudicated correct, **and at least 17 of 20 (85%)** receive concordant initial rater codes. A failure is a rejection; missing rater codes or fewer than 20 unique linked responses make the item **insufficient**, never accepted. Report raw rater agreement and a chance-corrected agreement coefficient (including prevalence limitations) as a diagnostic; 90% from 20 remains imprecise.
- **Form effects:** check whether particular surface forms consistently drive affect/familiarity. Rare or familiar forms must be replaced and retested.
- **Selection:** keep only candidates that pass **both** independently specified valence and denotation screens. Choose up to 12 from the passing set using a concept diversity rationale recorded before looking at main-study outcomes; **do not fill a minimum quota of eight by relaxing criteria**. If fewer than eight pass, create and norm a new batch rather than redefining neutrality. Preserve every excluded candidate and reason, including insufficient observations.
- Do **not** claim equivalence from failure to detect a difference. Avoid selecting items by extremal variance without independent replication (winner's curse).
- A **second independent validation sample is required** before final confirmatory stimulus selection: 20 pilot ratings per candidate can efficiently reject implausible items, but cannot establish tight neutrality bounds. Freeze that validation analysis and sample size separately.

## Machine-readable screening

Run `python -m norming.screen responses.csv blinded_denotation_codes.csv` **only after** real approved responses exist. It reports **retain_for_validation**, **reject**, or **insufficient**, along with explicit criteria and confidence intervals. The expected blinded code CSV columns are `participant_slot,concept_id,rater_a_correct,rater_b_correct,adjudicated_correct` with binary 0/1 values, one row per actual paraphrase. A pilot item is not a validated neutral stimulus merely because it passes screening.

The candidate definitions include deliberately competing social interpretations, but a few may still be valenced by construction. They remain **unvalidated**, including revised `maruni`, `sevlin` and `veluni`. A second pilot inventory is preferable to retaining an obviously biased item. Keep failed candidates documented rather than silently editing definitions after inspecting ratings.

## Prolific setup and launch gates

1. **Obtain an applicable ethics determination before recruitment**, including even a small external participant timing pilot. Finalise consent, privacy notice, retention and withdrawal and determine UK GDPR responsibilities. See [ethics route](ethics_route.md).
2. Configure a real compatible hosted questionnaire, with an anonymous access link, stable `PROLIFIC_PID` / study/session ID capture, atomic participant-slot allocation, secure response storage and working completion redirect/code.
3. Internally preview every route, test persistence and completion handling, check mobile accessibility, and verify no PII is required by free text.
4. After the appropriate ethics determination, run 2–3 consented dry-run participants to measure actual time and UX, then set Prolific duration/reward based on **observed** completion times; monitor hourly pay if participants take longer.
5. Pilot on a small number of paid participants before releasing the full 40 slots; avoid irreversible publication without checking.

**Budget illustration (not a quote):** 40 participants × 15 minutes × £9/hour = £90 in base rewards. At 33.3% academic platform fee ≈ £120, or at 42.8% corporate ≈ £128.52, before any applicable platform-fee VAT. Actual eligibility for discounted academic fees is not assumed. If 10 minutes is validated, base rewards are £60 and total fees roughly £80–£85.68 before VAT. No money has been spent.

Prolific references: https://www.prolific.com/pricing ; https://researcher-help.prolific.com/en/articles/445239-what-is-your-pricing ; https://researcher-help.prolific.com/en/articles/445178-what-survey-experimental-software-is-compatible-with-prolific

## Interpretation

The norming sample provides candidate stimulus evidence, **not** evidence that model-mediated semantic drift exists. It cannot be used to claim generation-4 effects, persistence, convergence or model specificity.
