package dev.proofgate.evidence;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;
import org.junit.jupiter.api.Test;

class CvParserTest {

    @Test
    void givesEachLineAStableIdFromItsHeading() {
        String markdown = """
                Intro line before any heading.
                ## Backend Developer (Contract), Northwind Labs, Oct 2025
                - First bullet.
                - Second bullet.
                ## Skills
                - Java, Python
                """;

        List<EvidenceChunk> chunks = CvParser.parse(markdown);

        assertThat(chunks).extracting(EvidenceChunk::id)
                .containsExactly("cv-1", "backend-developer-contract-1", "backend-developer-contract-2", "skills-1");
        assertThat(chunks.get(2).lineNumber()).isEqualTo(4);
    }
}
