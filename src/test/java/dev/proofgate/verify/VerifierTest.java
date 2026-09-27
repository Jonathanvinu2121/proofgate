package dev.proofgate.verify;

import static org.assertj.core.api.Assertions.assertThat;

import dev.proofgate.claims.Claim;
import dev.proofgate.evidence.CvParser;
import dev.proofgate.facts.FactExtractor;
import dev.proofgate.facts.TechLexicon;
import org.junit.jupiter.api.Test;

class VerifierTest {

    private static final String CV = """
            ## Experience
            - Optimized slow PostgreSQL queries from ~600ms to under 100ms through targeted indexing.
            - Engineered a rate limiter backed by Redis for 10+ tenants.

            ## Skills
            - Java, Python, Docker
            """;

    private final Verifier verifier =
            new Verifier(CvParser.parse(CV), new FactExtractor(TechLexicon.loadDefault()));

    private ClaimResult check(String text) {
        return verifier.check(new Claim("c1", text, 1));
    }

    @Test
    void faithfulParaphraseIsSupportedAndCitesItsSource() {
        ClaimResult r = check("Cut PostgreSQL query times from ~600ms to under 100ms with targeted indexing.");

        assertThat(r.verdict()).isEqualTo(Verdict.SUPPORTED);
        assertThat(r.citedChunkIds()).containsExactly("experience-1");
    }

    @Test
    void inventedNumberIsUnsupported() {
        ClaimResult r = check("Optimized slow PostgreSQL queries from ~900ms to under 100ms.");

        assertThat(r.verdict()).isEqualTo(Verdict.UNSUPPORTED);
        assertThat(r.missingFacts()).extracting(Object::toString).containsExactly("900");
    }

    @Test
    void inventedTechnologyIsUnsupported() {
        assertThat(check("Engineered a rate limiter in Golang backed by Redis for 10+ tenants.").verdict())
                .isEqualTo(Verdict.UNSUPPORTED);
    }

    @Test
    void factsFromDifferentEntriesNeedReview() {
        ClaimResult r = check("Engineered a rate limiter backed by PostgreSQL for 10+ tenants.");

        assertThat(r.verdict()).isEqualTo(Verdict.NEEDS_REVIEW);
        assertThat(r.citedChunkIds()).containsExactly("experience-2", "experience-1");
    }

    @Test
    void unstatedLeadershipNeedsReview() {
        assertThat(check("Led the effort to optimize slow PostgreSQL queries through targeted indexing.").verdict())
                .isEqualTo(Verdict.NEEDS_REVIEW);
    }

    @Test
    void strictModeAlsoBlocksClaimsNeedingReview() {
        VerificationReport report = new VerificationReport(java.util.List.of(
                check("Led the effort to optimize slow PostgreSQL queries through targeted indexing.")));

        assertThat(report.passes(false)).isTrue();
        assertThat(report.passes(true)).isFalse();
    }
}
