package dev.proofgate.verify;

import java.util.List;

public record VerificationReport(List<ClaimResult> results) {

    public long count(Verdict verdict) {
        return results.stream().filter(r -> r.verdict() == verdict).count();
    }

    /** Whether the document may proceed. In strict mode, claims needing review also block it. */
    public boolean passes(boolean strict) {
        return count(Verdict.UNSUPPORTED) == 0 && (!strict || count(Verdict.NEEDS_REVIEW) == 0);
    }
}
