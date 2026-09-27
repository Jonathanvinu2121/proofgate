package dev.proofgate.eval;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * One labelled claim: is it a faithful rendering of the evidence, or a fabrication?
 *
 * @param category what kind of rewrite or fabrication this is, e.g. {@code fake-metric}, {@code paraphrase}
 */
public record EvalCase(Expectation expected, String category, String claim) {

    public enum Expectation { FAITHFUL, FABRICATED }

    /** Loads a TSV file with columns {@code expected, category, claim}. Blank lines and {@code #} comments are skipped. */
    public static List<EvalCase> load(Path tsv) throws IOException {
        List<EvalCase> cases = new ArrayList<>();
        List<String> lines = Files.readAllLines(tsv);
        for (int i = 0; i < lines.size(); i++) {
            String line = lines.get(i).strip();
            if (line.isEmpty() || line.startsWith("#") || line.startsWith("expected\t")) {
                continue;
            }
            String[] cols = line.split("\t");
            if (cols.length != 3) {
                throw new IllegalArgumentException("%s:%d: expected 3 tab-separated columns, got %d"
                        .formatted(tsv, i + 1, cols.length));
            }
            cases.add(new EvalCase(Expectation.valueOf(cols[0].strip().toUpperCase(Locale.ROOT)),
                    cols[1].strip(), cols[2].strip()));
        }
        return cases;
    }
}
