# Ethics review and recruitment — operational gate

**Status: advice, not ethical approval. No Prolific recruitment is authorised by this file.**

## What is verified (17 October 2026)

- [City St George's research ethics policy](https://www.citystgeorges.ac.uk/research/support/integrity-and-ethics/ethics) states that projects conducted within or under the auspices of the university need approval **before** research starts; retrospective approvals are not offered.
- The [research ethics approval process](https://www.citystgeorges.ac.uk/research/support/integrity-and-ethics/ethics/approval) gives local committee contacts and advises planning for **at least four weeks** for departmental processing, potentially longer.
- [Nikos Komninos' public staff profile](https://www.citystgeorges.ac.uk/about/people/academics/nikos-komninos) lists `Nikos.Komninos.1@citystgeorges.ac.uk`. His suitability or willingness to supervise/collaborate is **not confirmed**.
- [University policy on external researchers recruiting City students/staff](https://www.citystgeorges.ac.uk/research/support/integrity-and-ethics/guidance-and-resources/recruitment) is a **separate recruitment-access process** and **not** an alternative to ethical approval.

## Immediate outreach

Ask whether independent alumni research can be hosted under a genuine staff collaborator / university auspices or whether another independent-research ethics route is more appropriate; enquire who serves as sponsor/data controller and whether the pilot requires approval. Do not assume the university offers alumni sponsorship.

### Draft email to Dr Komninos (not sent)

**To:** Nikos.Komninos.1@citystgeorges.ac.uk  
**Subject:** Research ethics route for an independent human–AI language study

Hello Dr Komninos,

I completed my MSc in Data Science at City and I'm developing an independent research project on how LLM-assisted rewriting might influence the connotation of novel words as they pass through successive human participants.

I've drafted a controlled experiment comparing human-only, human-editor and LLM-editor transmission chains, with a small initial norming study of around 40 participants through Prolific. Before recruiting anybody, I want to establish the correct research ethics and data-protection route.

Would an alumni-led study like this be eligible for review through City St George's with an academic collaborator, or is there a different route you would recommend? I'd also appreciate any guidance on possible departmental sponsorship and whether you would be willing to point me toward the appropriate person.

The working protocol and instruments are in [Ghobi-A/Semantic-Drift](https://github.com/Ghobi-A/Semantic-Drift). I can send a concise protocol and participant information sheet if useful.

Best regards,  
Ghobikan Aravindan

## Gates before any external pilot

1. Written clarification of ethics review/oversight and determination for the proposed pilot; any required approval issued in advance.
2. Identify research data controller, lawful basis, retention, consent/withdrawal arrangements and secure hosting location.
3. Review and finalise consent and participant information; test language accessibility.
4. Then conduct 2–3 consented timing/UX dry runs; do not treat them as norming data without an appropriate protocol.
5. Use a compatible hosted survey with secure, atomic participant-slot allocation; map Prolific identifiers separately and send completion redirect only on confirmed save.
6. Set payment from measured duration and monitor effective hourly compensation. Do not describe a local browser preview as a hosted live study.

## Hosting follow-up

[jsPsych's Prolific integration documentation](https://www.jspsych.org/latest/overview/prolific/) describes capturing `PROLIFIC_PID`, `STUDY_ID` and `SESSION_ID` from query parameters plus redirecting to Prolific's completion URL. JATOS and equivalent secure jsPsych hosting are candidate engineering options, not verified deployed infrastructure for this repository. No survey is live; no participant IDs are captured.
