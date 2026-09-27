package dev.proofgate.claims;

import dev.proofgate.text.MarkdownLine;
import dev.proofgate.text.MarkdownReader;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;

/** Splits a tailored CV or cover letter into atomic claims: one per bullet, one per prose sentence. */
public final class ClaimExtractor {

    private static final Pattern SENTENCE_BREAK = Pattern.compile("(?<=[.!?])\\s+(?=[A-Z(\"])");
    private static final Pattern CONTACT = Pattern.compile(
            "@|https?://|www\\.|linkedin\\.com|github\\.com|\\+?\\d[\\d\\s()-]{8,}\\d");

    private ClaimExtractor() {
    }

    public static List<Claim> extract(String markdown) {
        List<Claim> claims = new ArrayList<>();
        for (MarkdownLine line : MarkdownReader.read(markdown)) {
            if (CONTACT.matcher(line.text()).find()) {
                continue;
            }
            for (String sentence : SENTENCE_BREAK.split(line.text())) {
                String text = sentence.strip();
                if (text.split("\\s+").length >= 3) {
                    claims.add(new Claim("c" + (claims.size() + 1), text, line.lineNumber()));
                }
            }
        }
        return claims;
    }
}
