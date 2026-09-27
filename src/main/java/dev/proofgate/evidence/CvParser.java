package dev.proofgate.evidence;

import dev.proofgate.text.MarkdownLine;
import dev.proofgate.text.MarkdownReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/** Turns a markdown CV (the source of truth) into citable evidence chunks, one per content line. */
public final class CvParser {

    private CvParser() {
    }

    public static List<EvidenceChunk> parse(String markdown) {
        List<EvidenceChunk> chunks = new ArrayList<>();
        Map<String, Integer> perSection = new HashMap<>();
        for (MarkdownLine line : MarkdownReader.read(markdown)) {
            String slug = slug(line.section());
            int n = perSection.merge(slug, 1, Integer::sum);
            chunks.add(new EvidenceChunk(slug + "-" + n, line.section(), line.text(), line.lineNumber()));
        }
        return chunks;
    }

    /** First three words of the heading, e.g. "Backend Developer (Contract), Northwind..." -> "backend-developer-contract". */
    static String slug(String section) {
        String[] words = section.toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9]+", " ").strip().split(" ");
        String slug = String.join("-", Arrays.copyOf(words, Math.min(words.length, 3)));
        return slug.isEmpty() ? "cv" : slug;
    }
}
