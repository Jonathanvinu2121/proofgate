package dev.proofgate.eval;

import dev.proofgate.claims.Claim;
import dev.proofgate.eval.EvalCase.Expectation;
import dev.proofgate.verify.ClaimResult;
import dev.proofgate.verify.Verdict;
import dev.proofgate.verify.Verifier;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.function.Predicate;

/** Scorecard for a verifier run over labelled cases. */
public record EvalSummary(List<Outcome> outcomes) {

    public record Outcome(EvalCase evalCase, ClaimResult result) {

        /** Fabrications must not pass; faithful claims should pass without review. */
        public boolean correct() {
            return evalCase.expected() == Expectation.FABRICATED
                    ? result.verdict() != Verdict.SUPPORTED
                    : result.verdict() == Verdict.SUPPORTED;
        }
    }

    public record CategoryScore(int correct, int total) {
    }

    public static EvalSummary run(Verifier verifier, List<EvalCase> cases) {
        return new EvalSummary(cases.stream()
                .map(c -> new Outcome(c, verifier.check(new Claim("eval", c.claim(), 0))))
                .toList());
    }

    /** Share of fabricated claims that were not passed (blocked or sent to review). */
    public double catchRate() {
        return rate(Expectation.FABRICATED, v -> v != Verdict.SUPPORTED);
    }

    /** Share of faithful claims wrongly blocked outright. */
    public double falseBlockRate() {
        return rate(Expectation.FAITHFUL, v -> v == Verdict.UNSUPPORTED);
    }

    /** Share of faithful claims sent to review: the manual-work cost of the verifier. */
    public double reviewRate() {
        return rate(Expectation.FAITHFUL, v -> v == Verdict.NEEDS_REVIEW);
    }

    public long count(Expectation expectation) {
        return outcomes.stream().filter(o -> o.evalCase().expected() == expectation).count();
    }

    public Map<String, CategoryScore> byCategory() {
        Map<String, CategoryScore> scores = new TreeMap<>();
        for (Outcome o : outcomes) {
            String key = o.evalCase().expected().name().toLowerCase() + "/" + o.evalCase().category();
            CategoryScore s = scores.getOrDefault(key, new CategoryScore(0, 0));
            scores.put(key, new CategoryScore(s.correct() + (o.correct() ? 1 : 0), s.total() + 1));
        }
        return scores;
    }

    public List<Outcome> misses() {
        return outcomes.stream().filter(o -> !o.correct()).toList();
    }

    private double rate(Expectation expectation, Predicate<Verdict> hit) {
        List<Outcome> group = outcomes.stream().filter(o -> o.evalCase().expected() == expectation).toList();
        if (group.isEmpty()) {
            return 0;
        }
        return (double) group.stream().filter(o -> hit.test(o.result().verdict())).count() / group.size();
    }
}
