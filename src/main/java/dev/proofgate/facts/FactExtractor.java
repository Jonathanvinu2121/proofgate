package dev.proofgate.facts;

import java.util.LinkedHashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Pulls hard facts (numbers, percentages, years, technologies) out of free text. */
public final class FactExtractor {

    // Not preceded by a letter/digit/dot, so "EC2", "K8s" and version-like "Node.js" never yield numbers.
    private static final Pattern NUMBER =
            Pattern.compile("(?<![\\w.])(\\d{1,3}(?:,\\d{3})+|\\d+(?:\\.\\d+)?)(\\s?%)?");

    private final TechLexicon lexicon;

    public FactExtractor(TechLexicon lexicon) {
        this.lexicon = lexicon;
    }

    public Set<Fact> extract(String text) {
        Set<Fact> facts = new LinkedHashSet<>();
        Matcher m = NUMBER.matcher(text);
        while (m.find()) {
            String value = m.group(1).replace(",", "");
            facts.add(new Fact(Fact.Kind.NUMBER, m.group(2) != null ? value + "%" : value));
        }
        for (String tech : lexicon.find(text)) {
            facts.add(new Fact(Fact.Kind.TECHNOLOGY, tech));
        }
        return facts;
    }
}
