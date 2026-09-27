# ProofGate

Blocks unsupported claims in AI-tailored CVs and cover letters by tracing every claim back to evidence.

AI job-search tools like [career-ops](https://github.com/career-ops-hq/career-ops) rewrite your CV for each role.
Their "never fabricate" rule lives in the prompt; nothing enforces it. ProofGate is the enforcing gate:
it splits generated output into claims, matches each one to a line of your source CV, and blocks the
document if a claim contains a number, date or technology your CV doesn't back.

```
[PASS  ] line 6   Reduced PostgreSQL query latency from ~600ms to under 100ms via targeted indexing.
         cites backend-developer-contract-2: All facts found in cited evidence

[FAIL  ] line 7   Deployed the restaurant POS system on AWS, processing 100+ orders daily.
         cites backend-developer-contract-3: Not found anywhere in the evidence: [AWS]

[REVIEW] line 10  I led backend development for several production systems.
         cites backend-developer-contract-3: Claims leadership or ownership that the cited evidence does not state
```

## Usage

Requires Java 21+. The Maven wrapper downloads Maven on first run.

```bash
./mvnw package                     # build + unit tests -> target/proofgate.jar
java -jar target/proofgate.jar verify --cv cv.md --output tailored-cv.md
java -jar target/proofgate.jar eval --note "what changed"
```

`verify` exits with 1 when any claim is unsupported (`--strict` also fails on claims needing review),
so it can gate a pipeline before PDF generation.

## How it decides

| Verdict | When |
|---|---|
| `UNSUPPORTED` | The claim contains a number, date or technology that appears nowhere in the CV |
| `NEEDS_REVIEW` | Facts exist but come from different CV entries; wording barely matches; or it claims leadership the evidence doesn't state |
| `SUPPORTED` | Every fact is in the best-matching CV line and the wording matches it |

## Measuring it

`evals/cases.tsv` holds labelled faithful rewrites and fabrications (fake metrics, invented tech,
shifted dates, scope inflation, mixed facts, vague claims, fake employers). `eval` scores the verifier
and appends to `evals/history.csv`, so every change is judged by numbers:

- **Fabrication catch rate**: fabrications not passed (target ≥ 95%)
- **False-block rate**: faithful rewrites wrongly blocked (target ≤ 10%)
- **Review rate**: faithful rewrites sent to manual review (lower is better)

See [ROADMAP.md](ROADMAP.md) for what's next. The original Python prototype is kept in `python-prototype/` for reference.
