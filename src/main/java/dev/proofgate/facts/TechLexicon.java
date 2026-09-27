package dev.proofgate.facts;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.regex.Pattern;

/**
 * Named technologies and their aliases, loaded from {@code technologies.txt}.
 * File format: one technology per line, {@code Canonical|alias|alias}. Matching is case-insensitive
 * unless a name is prefixed with {@code =} (for names that are also common English words, e.g. {@code =React}).
 */
public final class TechLexicon {

    private record Entry(String canonical, List<Pattern> patterns) {
    }

    private final List<Entry> entries;

    private TechLexicon(List<Entry> entries) {
        this.entries = entries;
    }

    public static TechLexicon loadDefault() {
        try (InputStream in = TechLexicon.class.getResourceAsStream("/technologies.txt")) {
            if (in == null) {
                throw new IllegalStateException("technologies.txt not found on classpath");
            }
            return parse(new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8)).lines().toList());
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    static TechLexicon parse(List<String> lines) {
        List<Entry> entries = new ArrayList<>();
        for (String line : lines) {
            String trimmed = line.strip();
            if (trimmed.isEmpty() || trimmed.startsWith("#")) {
                continue;
            }
            String[] names = trimmed.split("\\|");
            List<Pattern> patterns = new ArrayList<>();
            for (String name : names) {
                patterns.add(compile(name.strip()));
            }
            entries.add(new Entry(names[0].strip().replaceFirst("^=", ""), patterns));
        }
        return new TechLexicon(entries);
    }

    private static Pattern compile(String name) {
        boolean caseSensitive = name.startsWith("=");
        String literal = caseSensitive ? name.substring(1) : name;
        String regex = "(?<![\\w.])" + Pattern.quote(literal) + "(?![\\w+#])";
        return caseSensitive ? Pattern.compile(regex) : Pattern.compile(regex, Pattern.CASE_INSENSITIVE);
    }

    /** Canonical names of all technologies mentioned in the text. */
    public Set<String> find(String text) {
        Set<String> found = new LinkedHashSet<>();
        for (Entry entry : entries) {
            if (entry.patterns().stream().anyMatch(p -> p.matcher(text).find())) {
                found.add(entry.canonical());
            }
        }
        return found;
    }
}
