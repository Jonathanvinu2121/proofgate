# Roadmap: Evidence-Grounded Verifier for career-ops

## What this is

A Java tool that plugs into [career-ops](https://github.com/career-ops-hq/career-ops) and makes sure
every claim in a tailored CV / cover letter is backed by real evidence — blocking anything that isn't.

career-ops' README says its no-fabrication rule "lives in the prompts, not yet in an enforcing gate",
but the code (v1.34.0) does ship a document-level gate, `verify-cv-facts.mjs`, run before PDF and cover
letter generation. It checks whether each fact exists anywhere in `cv.md`; it does not cite sources,
catch facts mixed across entries, or flag inflated scope. On the same 50 cases it catches 25.0% vs
ProofGate's 96.4% (`evals/compare-career-ops.mjs`, 2026-09-27; cases favour ProofGate).
This project is a per-claim, citation-backed gate, plus an evidence base (your repos, projects, certs)
and an upskilling loop that turns skill gaps into citable proof. A realistic end state is contributing
the checks career-ops lacks upstream, with the benchmark as evidence.

**Why Java:** target is SDE roles; the project doubles as proof of Java / Spring Boot backend skill.

## The rule (anti-aimlessness)

Every change must move a number in the eval scorecard or fix a failing eval case.
If you can't name the number a change will improve, it's not the next thing to do.

## Scorecard (tracked in `evals/history.csv`)

| Metric | Meaning | Target |
|---|---|---|
| Fabrication catch rate | % of fabricated/embellished claims blocked | ≥ 95% |
| False-block rate | % of faithful rewrites wrongly blocked | ≤ 10% |
| Citation accuracy | % of passed claims citing the correct source | ≥ 90% |
| Evidence recall@5 | (Step 3) right evidence found for a JD requirement | ≥ 85% |

---

## Step 0 — Foundation
- [x] `git init`, `.gitignore`, first commit of current Python prototype (moved to `python-prototype/`)
- [x] Build tool: Maven wrapper (3.9.16), Java 21 target, JUnit 6 + AssertJ
- [x] Install career-ops locally (`../career-ops`, v1.34.0) with the master CV, profile and fact-gate config
- [ ] Run it on 3–5 real SDE JDs, save its tailored CVs as eval inputs
- **Done when:** `mvn test` runs green and there is real career-ops output to test against.

## Step 1 — Standalone verifier (the core)
Input: `cv.md` (source of truth) + a tailored CV / cover letter. Output: per-claim verdict + source line.

- [x] `evidence`: parse `cv.md` into chunks with stable IDs (e.g. `backend-developer-contract-2`)
- [x] `claims`: split tailored output into atomic claims (bullets, sentences)
- [ ] `verify`, two layers:
  - [x] Hard-fact check (deterministic): numbers, %, years, technologies must appear in evidence; plus
        wording-overlap and unstated-leadership checks
  - [ ] Company / employer names as hard facts
  - [ ] Section-aware evidence: treat a heading + its bullets as one unit, so a claim combining a role's
        title, dates and bullet facts isn't sent to review (4 of 28 claims on the real resume, all correct)
- [ ] Read `.tex` output directly (career-ops `/latex`, resume builders) instead of needing a markdown copy
- [ ] Prose mode for cover letters / outreach emails (found on real emails, 2026-09-27; career-ops' gate
      has the same false positives):
  - Negation: "I haven't set up CI/CD yet" is a disclosed gap, not a CI/CD claim
  - Quoted requirements: "the role asks for 0–2 years" describes the job, not the candidate
  - Non-claims: greetings, sentences about the employer, and [bracketed notes] should not count as claims
  - [ ] Semantic check (LLM judge via Anthropic Java SDK) for NEEDS_REVIEW claims: SUPPORTED / EMBELLISHED / UNSUPPORTED
  - [ ] Mock judge for offline tests
- [x] CLI (picocli): `verify --cv cv.md --output tailored.md` → report, exit 1 on unsupported claims
- [x] Eval harness + 50 cases (`evals/cases.tsv`), scorecard logged to `evals/history.csv`
- [ ] Eval cases from **real career-ops output**, labelled by hand (the self-written set is not enough, see below)
- **Done when:** catch rate ≥ 95% and false-block ≤ 10% on the eval set **including real career-ops output**.

**Baseline (2026-09-27):** catch 96.4%, false-block 0%, review 13.6% on 50 self-written cases.
Caveat: the cases and the rules were written together, so this number is optimistic. Vague fabrications
and fake employers are only "caught" by being sent to review, and fact-mixing that reuses real numbers
("87% precision … for the POS system") still passes. Real career-ops output is the honest test.

## Step 2 — Plug into career-ops
- [ ] Spring Boot MCP server (Spring AI MCP) exposing `verify_claims`
- [ ] Hook / custom mode so career-ops runs verification before PDF generation
- [ ] No fork: works against a stock career-ops install
- **Done when:** a fabricated claim in a real career-ops run blocks the PDF.

## Step 3 — Evidence base (the RAG part)
- [ ] Ingest GitHub repos (READMEs, key source files), project write-ups, certificates
- [ ] Local embeddings (LangChain4j, all-MiniLM-L6-v2 via ONNX) + pgvector
- [ ] MCP tool `search_evidence(requirement)`; verifier accepts claims backed by evidence, not only `cv.md`
- **Done when:** evidence recall@5 ≥ 85% on a labelled requirement → evidence set.

## Step 4 — Upskilling loop
- [ ] Read career-ops evaluation reports, aggregate gaps weighted by how often they cost a match
- [ ] Turn top gaps into concrete project specs
- [ ] When a project repo exists, ingest it → gap closed → citable in future applications
- **Done when:** one real gap has gone gap → project → evidence → cited in an application.

---

## What happens to the Python prototype
Kept as reference until the Java verifier beats it on the grounding evals, then archived.
Ideas carried over: chunk-ID citations, halt-on-ungrounded guardrail, eval datasets.
