# Roadmap: Evidence-Grounded Verifier for career-ops

## What this is

A Java tool that plugs into [career-ops](https://github.com/career-ops-hq/career-ops) and makes sure
every claim in a tailored CV / cover letter is backed by real evidence — blocking anything that isn't.

career-ops' own README admits: *"It reformulates your CV; it must never fabricate it. Today that rule
lives in the prompts, not yet in an enforcing gate."* This project is that enforcing gate, plus an
evidence base (your repos, projects, certs) and an upskilling loop that turns skill gaps into citable proof.

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
- [ ] `git init`, `.gitignore`, first commit of current Python prototype (reference only)
- [ ] Build tool: Maven (Java 21 target), JUnit 5
- [ ] Install career-ops locally, run it on 3–5 real SDE JDs, save its tailored CVs as eval inputs
- **Done when:** `mvn test` runs green and there is real career-ops output to test against.

## Step 1 — Standalone verifier (the core)
Input: `cv.md` (source of truth) + a tailored CV / cover letter. Output: per-claim verdict + source line.

- [ ] `evidence`: parse `cv.md` into chunks with stable IDs (e.g. `cv#experience-2`)
- [ ] `claims`: split tailored output into atomic claims (bullets, sentences)
- [ ] `verify`, two layers:
  - Hard-fact check (deterministic): every number, %, technology, company, date in a claim must appear in its supporting evidence
  - Semantic check (LLM judge via Anthropic Java SDK): SUPPORTED / EMBELLISHED / UNSUPPORTED + cited chunk
  - Mock judge for offline tests
- [ ] CLI (picocli): `verify --cv cv.md --output tailored.md` → report, non-zero exit code on any failure
- [ ] Eval set, 50+ cases: faithful rewrites, inflated scope ("led the team"), fake metrics, fake tech, shifted dates
- **Done when:** catch rate ≥ 95% and false-block ≤ 10% on the eval set.

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
