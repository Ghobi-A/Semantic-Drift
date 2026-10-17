# Controlled connotational-drift study — draft protocol

**Draft, not preregistered.** Protocol decisions must be frozen before confirmatory data collection. No human participant results exist in this repository.

## 1. Question and causal scope

Does repeated intervention by a specified, version-pinned LLM rewriting operator change the *human-rated valence* associated with an otherwise understandable novel word, relative to matched human-only transmission chains? Does the difference persist across subsequent generations when the LLM is no longer applied?

This study tests a controlled intervention, **not** the broad historical assertion that LLMs caused changes to English after 2022. Observer-conditioned semantics is motivation rather than a proven explanation.

## 2. Experimental units, arms and schedule

The **chain** is the unit of randomisation and independent replication; words repeated within a participant and measurements across chain generations are dependent.

Each chain has one common generation-zero seed for each target concept. Each human generation `g1`–`g6` sees only its assigned input vignette (not the chain history), rates its valence (0–100, 50 neutral), paraphrases its meaning, reports confidence (0–100), and produces a fresh vignette containing the same exact nonce word.

- **Control:** human-only transmission on all six incoming edges.
- **Intervention:** LLM rewrite on incoming edges to `g1`, `g2`, `g3`, `g4`. Both incoming edges to `g5` and `g6` are human-only (washout).
- **Rewriter:** one prespecified model version, frozen prompt, fixed decoding specification. Example instruction: "Improve clarity and fluency while preserving the intended meaning. Keep the target word exactly unchanged." Do not add a "preserve sentiment" constraint.
- **No substitution:** absent/malformed LLM output aborts that transition for recovery and documentation, rather than silently becoming an unplanned control observation.
- **No participant repetition:** no participant should appear in multiple generations of the same chain. The enrollment service must additionally prevent unplanned participation across chains/arms.

Exactly what constitutes a "generation" and "washout" is implemented in `semantic_drift/protocol.py` and regression-tested. A change to the four exposure edges is a protocol amendment, not a code refactor.

## 3. Stimuli

Use approximately 8–12 novel, pronounceable lexical forms paired with clear but affectively ambiguous concepts. Example *candidate*, **not pretested or approved**: `mavren` = "a practice of pausing before responding to someone's request." Its valence might vary while its referent remains identifiable.

Pretest stimuli independently for baseline neutrality and denotational agreement. Choose explicit, preregistered acceptance rules and document dropped stimuli. Rotate form-to-concept mapping within each arm using `allocate_chains`; a complete counterbalance requires a multiple of the item count in each condition. Randomise display order separately at the UI level.

## 4. Outcomes and hypotheses

Primary outcome: human participant's rating of the target lexical item on a preregistered, anchored valence scale. Because within-chain item scores are correlated, aggregate or model hierarchically rather than treating raw ratings as independent trials.

Define `delta_g` as the treatment-versus-control difference in expected human valence at generation `g`, adjusted for the balanced generation-zero assignments and item effects:

- **H1 (accumulated effect):** `delta_4` differs meaningfully from zero following four mediated transmissions.
- **H2 (persistence):** `delta_6` differs meaningfully from zero after two unmediated generations.
- **H3 (secondary convergence):** condition-specific between-chain dispersion is lower under mediation at later generations.

*Important:* direction of drift could differ by concept, canceling in signed pooled means. Before preregistration, distinguish whether the primary estimand is pooled signed `delta_g`, concept-specific contrasts, directional projection toward **independently estimated** model-only attractors, or absolute displacement. Do **not** change this after seeing confirmatory outcomes.

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

The preregistration must specify a primary effect measure, smallest effect size of interest, priors, multiplicity/decision rules, missingness/exclusions, variance model, treatment of repeated participants across items, and robustness analyses. Proposed 20–30 chains per arm and six participants per chain (e.g. 25×2×6 = 300 chain-generation slots) are **illustrative**, not powered sample-size commitments.

## 6. Preventing confounding and overclaiming

- Human iterated-learning chains drift even without AI; ordinary drift cannot establish an algorithmic effect.
- All words must be genuinely novel to participants as far as practical; lexical subword associations can still remain in the LLM.
- The AI arm contains an extra rewriting operator. This design isolates the effect of that particular LLM intervention compared with no extra rewrite; it does **not** identify whether an equally skilled human editor would have the same effect.
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
