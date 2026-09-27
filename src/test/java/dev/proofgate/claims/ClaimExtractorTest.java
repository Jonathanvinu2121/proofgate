package dev.proofgate.claims;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;
import org.junit.jupiter.api.Test;

class ClaimExtractorTest {

    @Test
    void splitsBulletsAndSentencesAndSkipsHeadingsAndContactLines() {
        String markdown = """
                # Jane Doe
                jane@example.com | github.com/jane

                ## Experience
                - **Optimized** PostgreSQL queries to under 100ms.
                - Built a [rate limiter](https://example.com) in Redis.

                I build backend systems. I shipped Node.js services on Node.js 20.
                """;

        List<Claim> claims = ClaimExtractor.extract(markdown);

        assertThat(claims).extracting(Claim::text).containsExactly(
                "Optimized PostgreSQL queries to under 100ms.",
                "Built a rate limiter in Redis.",
                "I build backend systems.",
                "I shipped Node.js services on Node.js 20.");
        assertThat(claims.get(0).lineNumber()).isEqualTo(5);
    }
}
