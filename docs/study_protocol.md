# Controlled connotational-drift study — draft protocol

**Draft, not preregistered.** Protocol decisions must be frozen before confirmatory data collection. No human participant results exist in this repository.

## 1. Question and causal scope

Does repeated intervention by a specified, version-pinned LLM rewriting operator change the *human-rated valence* associated with an otherwise understandable novel word, relative to matched human-only transmission chains? Does the difference persist across subsequent generations when the LLM is no longer applied?

This study tests a controlled intervention, **not** the broad historical assertion that LLMs caused changes to English after 2022. Observer-conditioned semantics is motivation rather than a proven explanation.

## 2. Experimental units, arms and schedule

The **chain** is the unit of randomisation and independent replication; words repeated within a participant and measurements across chain generations are dependent.

Each chain has one common generation-zero seed for each target concept. Each human generation `g1`–`g6` sees only its assigned input vignette (not the chain history), paraphrases its meaning, rates the word in a constant neutral probe sentence (−3..+3, 0 = neither; primary outcome), separately rates the tone of the received vignette (−3..+3), reports confidence (0–100), and produces a fresh vignette containing the same nonce word. This question order is fixed.

- **Arm A:** human-only transmission for all six incoming edges.
- **Arm B:** a separately recruited human editor rewrites the incoming text on edges to g1–g4; edges to g5–g6 are unedited washout.
- **Arm C:** a fixed LLM rewrites the incoming text on edges to g1–g4; edges to g5–g6 are unedited washout.
- **Both editing arms:** match editing objectives, input constraints and exposure counts as closely as practical. Log human-editor eligibility and editor identifiers separately from transmission participants.
- **Matched editor instruction:** exactly the same text is versioned in `semantic_drift/protocol.py` as `SHARED_EDITOR_INSTRUCTION` and presented to **both human and LLM editors**. The word and vignette must be presented as corresponding separate inputs; no arm-specific rewording. The protocol validates its SHA-256 in either editor's provenance. Do not add a "preserve sentiment" constraint.
- **Human editor selection:** recruit editors from the same *eligible sampling frame* as transmission participants. Randomise roles, ensure editor and human transmission identities do not overlap within a chain, and record qualifications/familiarity. Shared sampling eligibility reduces selection differences; it cannot equalise ability or internal model priors.
- **Rewriter:** one prespecified model version, frozen decoding specification, full raw API request/response log including any separate system instructions. A matching SHA-256 **alone** does not verify prompt delivery; an integration-level audit is required.
- **Request binding:** each rewrite or human edit carries `request_sha256`, the hash of the complete canonical request (shared instruction, target word, source passage; see `editor_request_sha256`). `advance_chain` rejects an edit whose hash does not match the edge's actual source text. An adapter must hash what it sends: every LLM call is a fresh context containing those three inputs only, with no chain history, concept definition, arm label or earlier rewrite.
- **Decoding parameters:** `decoding_parameters_json` must be a JSON object stating `temperature` and `seed` (`null` only if the provider offers none). Model, version and all decoding settings other than the per-call seed must be identical on every mediated edge of a chain; the code enforces this within a chain and the preregistration must fix them across chains. **Open decision:** temperature 0 (one deterministic operator) versus a fixed temperature above 0 (sampling noise enters arm C). This choice changes the meaning of H3 and must be frozen before data collection.
- **Target-word form:** seeds contain the exact lower-case nonce form. Transmitted and participant-produced text may use the lower-case form or its initial-capital form (e.g. sentence-initial "Mavren"); any other variant (all capitals, inflections, respellings) fails. This avoids aborting ordinary fluent edits at different rates in different arms.
- **No substitution:** absent/malformed human-editor or LLM output aborts the affected transition; do not silently fall back to another arm.
- **Attempt budget and attrition:** an editing step may be attempted at most three times (`MAX_EDITOR_ATTEMPTS`), each with the identical request and its own archived `run_id`. Failed attempts are stored on the step (`failed_editor_attempts`) with a reason. With deterministic decoding, retry only transport/provider failures; a content failure (e.g. target word missing) will recur. If the budget is exhausted the chain ends at that generation and is **not** replaced after outcomes are seen. Report, by arm and generation, the number of failed attempts and of terminated chains; the primary analysis is intention-to-treat on allocated chains, with a prespecified sensitivity analysis for terminated chains.
- **No participant repetition:** no participant should appear in multiple generations of the same chain. The enrollment service must additionally prevent unplanned participation across chains/arms.

Exactly what constitutes a "generation" and "washout" is implemented in `semantic_drift/protocol.py` and regression-tested. A change to the four exposure edges is a protocol amendment, not a code refactor.

## 3. Stimuli

Use approximately 8–12 novel, pronounceable lexical forms paired with clear but affectively ambiguous concepts. Example *candidate*, **not pretested or approved**: `mavren` = "a practice of pausing before responding to someone's request." Its valence might vary while its referent remains identifiable.

Pretest stimuli independently for baseline neutrality and denotational agreement. Choose explicit, preregistered acceptance rules and document dropped stimuli. Rotate form-to-concept mapping within each arm using `allocate_chains`; a complete counterbalance requires a multiple of the item count in each condition. Randomise display order separately at the UI level.

## 4. Outcomes and hypotheses

Primary outcome: `valence_rating`, the participant's rating of the target word in the constant neutral probe sentence `NEUTRAL_PROBE_TEMPLATE` ("Someone used [word] yesterday."), on the same integer −3..+3 scale and wording as the norming survey. `passage_tone_rating` (tone of the received vignette, same scale) is a secondary diagnostic and never substitutes for the primary outcome. Using one scale means the norming neutrality bounds and the smallest effect size of interest are expressed in the same units. Because within-chain item scores are correlated, aggregate or model hierarchically rather than treating raw ratings as independent trials.

Let delta_g(C,B) = E[V_g | LLM editor] − E[V_g | human editor], with prespecified item and chain adjustment.

- **H1 (primary, provisional):** positive delta_4(C,B), if independently motivated by pilot observations; freeze sign and smallest effect size of interest before confirmatory data.
- **H2 (washout):** report delta_4(C,B), delta_6(C,B) and their discrete change delta_6(C,B)−delta_4(C,B). Two post-mediation generations do not identify a defensible continuous decay constant; interpretation needs sensitivity analysis and attention to g4 effect sizes.
- **H3 (secondary):** between-chain variance in the model-editor arm differs from human-editor arm, especially at g4 and g6. A one-sided reduction must be specified before outcomes are inspected.

**Do not claim that C−B alone identifies a special semantic mechanism.** It identifies an operationally specified LLM-vs-human-editing intervention; editor competence, style, timing and compliance remain relevant.

**Measurement contamination:** immediately rating the tone of the received vignette is not the same as word-level valence, which is why the two are separate required fields. The probe is still answered after reading the vignette, so carry-over is reduced, not removed: pretest the separation (probe–tone correlation) and add independent blinded ratings of vignette tone.

**Directional caution:** positive valence and neutrality are not interchangeable. For negatively seeded items, motion toward 0 can be positive; for positively seeded items, movement toward 0 is negative. Pretest the expected direction.
**Denotational fidelity is a guardrail, not a post-hoc excuse.** Recruit independent raters blinded to arm and generation to compare transmitted uses against seeded referents. Define a meaningful equivalence/non-inferiority margin and rater reliability checks **before** confirmatory analysis. Non-significant differences do **not** establish equivalence.

Additional diagnostic: independent LLM-only rewrites may estimate item-specific attractor tendencies, frozen before inspecting human outcomes. This is descriptive support, not an independently established human causal mechanism.

## 5. Analysis plan (to be preregistered)

Candidate hierarchical model (for approximately continuous ratings):

```text
rating ~ StudentT(nu, mu, sigma)
mu = intercept + item_effect + chain_effect + participant_effect
     + generation_fixed_effect + condition_by_generation_effect
```

Required amendments to this sketch (to be frozen at preregistration):

1. **Likelihood.** The outcome is a 7-point integer scale; use a cumulative ordinal likelihood. The StudentT form above is a sensitivity analysis only.
2. **Editor effect.** Add a random effect for the human editor in arm B. Arm C has a single operator, so C−B compares a population of editors with **one** model instance. State the estimand as "this model versus the editor population"; it does not generalise to LLMs as a class without further models.
3. **Item slopes.** Include by-item random slopes for condition (and condition × generation where estimable). With 8–12 items, an intercept-only item effect overstates generalisation across items.
4. **Within-chain dependence.** Drift accumulates, so between-chain variance grows with generation; a chain intercept alone is misspecified. Either analyse H1 on the g4 cross-section (one chain-by-item observation) or model generation-specific chain deviations (random walk / AR(1)).
5. **Arm-specific variance for H3.** H3 requires a distributional model with a separate between-chain SD per arm and generation. One operator versus many editors lowers between-chain variance mechanically, so a C < B variance result is **not** evidence of a semantic attractor unless it exceeds what the editor variance component alone predicts. Report H3 as exploratory unless a design that removes this asymmetry is added.
6. **One primary contrast, fixed order.** The single confirmatory test is H1: C−B at g4 on `valence_rating`. H2 (δ6−δ4) is tested only if H1 meets its decision rule; H3 follows H2. C−A, B−A, g1–g3 and g5 contrasts, `passage_tone_rating`, edit distance and per-item effects are secondary and reported with intervals and no confirmatory claim. Denotational fidelity is a separate guardrail with its own equivalence margin.
7. **Baseline check.** Report g1 arm-A valence per item against the norming bounds; items selected for near-zero pilot means will regress away from zero.
8. **Power.** Commit the simulation code and its seed. H2 is a difference of two noisy contrasts and will have much lower power than H1; state its achieved power explicitly rather than interpreting a null as washout.

The generation interaction is categorical, avoiding unsupported linear/exponential assumptions. Chain assignment is the treatment level; participant/item repeated measurements need appropriate nesting or crossed effects and within-chain dependence. If the scale is ordinal rather than continuous, use an ordinal likelihood. Inspect posterior predictive checks and conduct simulation-based recovery/power analysis.

The preregistration must specify a primary effect measure, smallest effect size of interest, priors, multiplicity/decision rules, missingness/exclusions, variance model, treatment of repeated participants across items, and robustness analyses. Proposed 20–30 chains per arm and six participants per chain (e.g. 25×3×6 = 450 chain-generation participant slots, plus up to 100 human-editor assignments for arm B) are **illustrative**, not powered commitments. Simulate chain- and editor-level variance before choosing sample size.

## 6. Preventing confounding and overclaiming

- Human iterated-learning chains drift even without AI; ordinary drift cannot establish an algorithmic effect.
- All words must be genuinely novel to participants as far as practical; lexical subword associations can still remain in the LLM.
- Both editing arms contain an extra operator. The principal C−B contrast tests the specified human-versus-LLM editing procedures, not a uniquely intrinsic property of AI.
- **Edit magnitude (recorded on every edge):** token-level normalised Levenshtein edit distance = edit operations / max(source tokens, edited tokens). Report the distribution by stage and arm; also consider changes in text length and topical content. Edit magnitude is **post-treatment**, so including it as a covariate in the primary model would change the estimand and could introduce collider bias. Use it for a preregistered *descriptive diagnostic* or explicitly labelled sensitivity/mediation analyses, not as an automatic correction for treatment imbalance.
- Keep pre- and post-model text, exact provenance and any failed attempts; never infer semantic change solely from embedding cosine distance.
- A one-model, nonce-word experiment cannot establish universal behaviour across models, languages or real-world social discourse.
- Treat null washout effects as substantive evidence about the boundary of persistence, not a failed project.

## 7. Ethical and operational gates

Recruitment, consent, compensation, data-retention period, storage location, ethics review status, withdrawal procedures and UK GDPR lawful basis must be resolved before starting human sessions. Publish only de-identified data subject to participant consent and confidentiality constraints. Separate participant contact data from transmission observations.

## 8. Next concrete milestones

1. Create a first stimulus inventory and independent pretest instrument.
2. Build provider-specific rewrite adapter with immutable prompt/version configuration and typed failure logging.
3. Build participant-only input UI and a server-side chain allocation/orchestration layer; do not leak condition labels or history to participants.
4. Pilot blind denotation-rater reliability and chain-level variance; run simulation-based sample-size analysis.
5. Freeze protocol and preregister **before** the confirmatory experiment.
