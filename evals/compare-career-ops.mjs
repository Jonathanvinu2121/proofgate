// Runs career-ops' own fact gate (verify-cv-facts.mjs) over ProofGate's labelled cases,
// so both checkers are scored on the same data.
//
// Usage: node evals/compare-career-ops.mjs [path-to-career-ops-checkout]
// Default checkout: ../career-ops (next to this repo).

import { readFileSync } from 'fs';
import { resolve } from 'path';
import { pathToFileURL } from 'url';

const careerOps = resolve(process.argv[2] ?? '../career-ops');
const { verifyFacts } = await import(pathToFileURL(resolve(careerOps, 'verify-cv-facts.mjs')).href);

const source = resolve('evals/fixtures/cv.md');
const cases = readFileSync('evals/cases.tsv', 'utf8').split(/\r?\n/)
  .filter(line => line && !line.startsWith('#') && !line.startsWith('expected\t'))
  .map(line => line.split('\t'));

let fabricated = 0, caught = 0, faithful = 0, blocked = 0;
const byCategory = {};
for (const [expected, category, claim] of cases) {
  // A path that doesn't exist: score the gate itself, not a hand-tuned phrase list.
  const { verdict } = verifyFacts(`- ${claim}\n`, { sourcePaths: [source], configPath: resolve('no-config.json') });
  const key = `${expected.toLowerCase()}/${category}`;
  const score = (byCategory[key] ??= { correct: 0, total: 0 });
  score.total++;
  if (expected === 'FABRICATED') {
    fabricated++;
    if (verdict !== 'pass') { caught++; score.correct++; }
  } else {
    faithful++;
    if (verdict === 'block') blocked++; else score.correct++;
  }
}

for (const [key, { correct, total }] of Object.entries(byCategory).sort()) {
  console.log(`  ${key.padEnd(34)} ${String(correct).padStart(2)} / ${total}`);
}
console.log(`\ncareer-ops verifyFacts: catch ${(100 * caught / fabricated).toFixed(1)}%, `
  + `false-block ${(100 * blocked / faithful).toFixed(1)}%`);
