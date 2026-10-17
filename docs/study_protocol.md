# Controlled connotational-drift study — draft protocol

**Draft, not preregistered.** Protocol decisions must be frozen before confirmatory data collection. No human participant results exist in this repository.

## 1. Question and causal scope

Does repeated intervention by a specified, version-pinned LLM rewriting operator change the *human-rated valence* associated with an otherwise understandable novel word, relative to matched human-only transmission chains? Does the difference persist across subsequent generations when the LLM is no longer applied?

This study tests a controlled intervention, **not** the broad historical assertion that LLMs caused changes to English after 2022. Observer-conditioned semantics is motivation rather than a proven explanation.

## 2. Experimental units, arms and schedule

The **chain** is the unit of randomisation and independent replication; words repeated within a participant and measurements across chain generations are dependent.

Each chain has one common generation-zero seed for each target concept. Each human generation `g1`–`g6` sees only its assigned input vignette (not the chain history), rates its valence (0–100, 50 neutral), paraphrases its meaning, reports confidence (0–100), and produces a fresh vignette containing the same exact nonce word.

- **Arm A:** human-only transmission for all six incoming edges.
- **Arm B:** a separately recruited human editor rewrites the incoming text on edges to g1–g4; edges to g5–g6 are unedited washout.
- **Arm C:** a fixed LLM rewrites the incoming text on edges to g1–g4; edges to g5–g6 are unedited washout.
- **Both editing arms:** match editing objectives, input constraints and exposure counts as closely as practical. Log human-editor eligibility and editor identifiers separately from transmission participants.
- **Matched editor instruction:** exactly the same text is versioned in `semantic_drift/protocol.py` as `SHARED_EDITOR_INSTRUCTION` and presented to **both human and LLM editors**. The word and vignette must be presented as corresponding separate inputs; no arm-specific rewording. The protocol validates its SHA-256 in either editor's provenance. Do not add a "preserve sentiment" constraint.
- **Human editor selection:** recruit editors from the same *eligible sampling frame* as transmission participants. Randomise roles, ensure editor and human transmission identities do not overlap within a chain, and record qualifications/familiarity. Shared sampling eligibility reduces selection differences; it cannot equalise ability or internal model priors.
- **Rewriter:** one prespecified model version, frozen decoding specification, full raw API request/response log including any separate system instructions. A matching SHA-256 **alone** does not verify prompt delivery; an integration-level audit is required.
- **No substitution:** absent/malformed human-editor or LLM output aborts the affected transition; do not silently fall back to another arm.
- **No participant repetition:** no participant should appear in multiple generations of the same chain. The enrollment service must additionally prevent unplanned participation across chains/arms.

Exactly what constitutes a "generation" and "washout" is implemented in `semantic_drift/protocol.py` and regression-tested. A change to the four exposure edges is a protocol amendment, not a code refactor.

## 3. Stimuli

Use approximately 8–12 novel, pronounceable lexical forms paired with clear but affectively ambiguous concepts. Example *candidate*, **not pretested or approved**: `mavren` = "a practice of pausing before responding to someone's request." Its valence might vary while its referent remains identifiable.

Pretest stimuli independently for baseline neutrality and denotational agreement. Choose explicit, preregistered acceptance rules and document dropped stimuli. Rotate form-to-concept mapping within each arm using `allocate_chains`; a complete counterbalance requires a multiple of the item count in each condition. Randomise display order separately at the UI level.

## 4. Outcomes and hypotheses

Primary outcome: human participant's rating of the target lexical item on a preregistered, anchored valence scale. Because within-chain item scores are correlated, aggregate or model hierarchically rather than treating raw ratings as independent trials.

Let delta_g(C,B) = E[V_g | LLM editor] − E[V_g | human editor], with prespecified item and chain adjustment.

- **H1 (primary, provisional):** positive delta_4(C,B), if independently motivated by pilot observations; freeze sign and smallest effect size of interest before confirmatory data.
- **H2 (washout):** report delta_4(C,B), delta_6(C,B) and their discrete change delta_6(C,B)−delta_4(C,B). Two post-mediation generations do not identify a defensible continuous decay constant; interpretation needs sensitivity analysis and attention to g4 effect sizes.
- **H3 (secondary):** between-chain variance in the model-editor arm differs from human-editor arm, especially at g4 and g6. A one-sided reduction must be specified before outcomes are inspected.

**Do not claim that C−B alone identifies a special semantic mechanism.** It identifies an operationally specified LLM-vs-human-editing intervention; editor competence, style, timing and compliance remain relevant.

**Measurement contamination:** immediately rating the tone of the received vignette is not the same as word-level valence. Use a fresh standardised neutral-context probe and independently rated vignette tone; pretest the separation.

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
