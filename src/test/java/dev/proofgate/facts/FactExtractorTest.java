package dev.proofgate.facts;

import static org.assertj.core.api.Assertions.assertThat;

import dev.proofgate.facts.Fact.Kind;
import java.util.List;
import org.junit.jupiter.api.Test;

class FactExtractorTest {

    private final FactExtractor extractor = new FactExtractor(TechLexicon.loadDefault());

    private List<String> values(String text, Kind kind) {
        return extractor.extract(text).stream().filter(f -> f.kind() == kind).map(Fact::value).toList();
    }

    @Test
    void extractsNumbersPercentagesAndYears() {
        assertThat(values("Cut latency from ~600ms to under 100ms for 44,000+ users, 87% precision (2023)", Kind.NUMBER))
                .containsExactly("600", "100", "44000", "87%", "2023");
    }

    @Test
    void ignoresDigitsInsideNames() {
        assertThat(values("Deployed on EC2 with K8s and OAuth2 via Node.js", Kind.NUMBER)).isEmpty();
    }

    @Test
    void normalisesTechnologyAliases() {
        assertThat(values("Used Postgres, NodeJS and k8s", Kind.TECHNOLOGY))
                .containsExactlyInAnyOrder("PostgreSQL", "Node.js", "Kubernetes");
    }

    @Test
    void distinguishesJavaFromJavaScriptAndGitFromGitHub() {
        assertThat(values("JavaScript on GitHub", Kind.TECHNOLOGY)).containsExactlyInAnyOrder("JavaScript", "GitHub");
    }

    @Test
    void caseSensitiveNamesDoNotMatchEnglishWords() {
        assertThat(values("Able to react quickly and express ideas", Kind.TECHNOLOGY)).isEmpty();
        assertThat(values("Built UIs in React", Kind.TECHNOLOGY)).containsExactly("React");
    }
}
