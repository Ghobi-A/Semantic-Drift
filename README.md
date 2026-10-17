# Semantic Drift

Research software for testing **model-mediated connotational drift**: can LLM rewriting change how human participants evaluate a novel word, and does that effect persist after the model is removed from a transmission chain?

**Status: research infrastructure / protocol draft. No participants have been recruited, no outcome data have been collected, and no effect has been demonstrated.** This repository does **not** yet constitute a preregistered or completed experiment.

## Research question

In controlled iterated-learning chains, does adding a fixed LLM rewriting step change the *affective connotation* of a novel lexical item relative to human-only transmission, while its *denotation* is approximately preserved? Does any difference persist through two subsequent human-only generations?

The original observer-conditioned semantics proposal is the theoretical motivation, not an already validated causal explanation of historical language change. The principal empirical target is much narrower.

## Conditions and generation convention

Both arms start from identical generation-zero (`g0`) vignette seeds. One human participant supplies a valence rating, a denotation paraphrase, a confidence rating and a newly written vignette in each generation `g1`–`g6`.

- **Human-only:** each `g1`–`g6` participant receives the previous text *without* an LLM step.
- **Human editor (active control):** a separately recruited human editor performs the same type of clarity/fluency rewrite on incoming edges to g1–g4; no editor on g5–g6.
- **LLM-mediated:** exactly four edges are mediated: `g0→g1`, `g1→g2`, `g2→g3`, and `g3→g4`.
- **Washout:** `g4→g5` and `g5→g6` transmit human text *without* an LLM step in both arms.

Both editor arms use the **same pinned instruction** (SHA-256-verified in the core protocol). Token-normalised Levenshtein edit magnitude is recorded for each incoming edge and evaluated descriptively, not included automatically as a post-treatment primary covariate. Human editors should be drawn from the same eligible participant pool with separate roles and no same-chain collisions.

The model's operation is a fixed, versioned rewriting instruction intended to improve clarity while preserving intended meaning and the exact target word. Sentiment preservation must **not** be explicitly requested. An LLM rewrite is **not** a substitute for a human observation.

## Start here

- [Protocol draft](docs/study_protocol.md) — hypotheses, estimands, controls and open decisions
- [Data dictionary](docs/data_dictionary.md) — auditable records and data governance
- [Implementation](semantic_drift/protocol.py) — strict, immutable six-generation chain transition
- [Balanced randomisation](semantic_drift/randomization.py) — deterministic chain assignments and counterbalanced nonce forms
- [Example dry run](examples/dry_run.py) — *synthetic only*, never research evidence

Run the dependency-free tests:

```bash
python -m unittest discover -s tests -v
python -m examples.dry_run
```

Requires Python 3.11+. No provider API keys or recruited participants are needed for the core tests. The dry run uses identity rewrites to exercise provenance and washout boundaries; it cannot estimate semantic or connotational drift.

## Scientific boundaries

1. **Unit of independent replication:** transmission chain. The proposed three-arm design includes a human-editor active control to isolate differences between editing protocols. Multiple words judged by one participant are correlated repeated measures.
2. **Main outcomes:** human valence ratings; independent, blinded human ratings of denotational fidelity. Embedding-based scores are supplementary diagnostics.
3. **Primary contrast (draft):** LLM editor minus human editor at generation 4; compare generation 4 and generation 6 contrasts for washout attenuation. The human-only arm is an unedited drift baseline.
4. **Model versioning:** do not silently substitute model versions, prompts, decoding parameters, or failed provider calls.
5. **Causal scope:** a controlled result would establish an effect of the *specified rewriting intervention under the tested conditions*, not that LLMs caused societal semantic change.
6. **Human research:** secure ethics/data-protection review, consent and a registered analysis plan **before** collecting confirmatory participant data.

## Exploratory stimulus norming (not yet launched)

The draft includes **20 candidate concepts** and a **40-slot balanced incomplete-block design** (10 items per participant; 20 observations per concept). These are prospective allocations, **not collected observations**. See [the norming instrument](docs/norming_survey.md) and [candidate inventory](norming/candidates.csv).

```bash
python -m norming.export_assignments --out norming_assignments.csv
python -m norming.preview --slot 1 --out norming-preview.html
# Open norming-preview.html locally; this does not submit to a server.
# After approved human data collection only:
python -m norming.summary path/to/approved_responses.csv
```

Apply the fixed pilot screening rules in [the norming protocol](docs/norming_survey.md): 20 valid ratings, reject if the 95% CI excludes 0 or |mean| > 0.5, plus at least 90% adjudicated denotation agreement and 85% initial two-rater agreement. Passing is **not proof of neutrality**; independent validation remains required.

Do not use the offline preview as a live Prolific questionnaire; it only exports local files. Study launch requires approved consent/privacy materials, persistent capture, stable Prolific session mapping and a completion redirect.

## Roadmap

- [x] Define deterministic three-arm chain/washout invariants, provenance schema and tests
- [x] Document first protocol and candidate analysis plan
- [ ] Screen the 20 candidate concepts using frozen valence / blinded denotation criteria, then independently validate 8–12 retained concepts
- [ ] Implement a privacy-conscious participant interface, backed by durable storage and blinded independent ratings
- [ ] Integrate and pin one LLM rewriting provider with complete request/response logs
- [ ] Pilot measurement reliability and chain-level variance; simulation-based sample-size determination
- [ ] Ethics approval / data protection and preregistration
- [ ] Recruit, run and analyse the confirmatory experiment

MIT licence. Contributions must not fabricate observations or exaggerate empirical conclusions.
