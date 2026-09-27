package dev.proofgate.text;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Minimal line-oriented markdown reader: enough structure for CVs, not a full markdown parser. */
public final class MarkdownReader {

    private static final Pattern HEADING = Pattern.compile("^(#{1,6})\\s+(.*)$");
    private static final Pattern LIST_MARKER = Pattern.compile("^(?:[-*+]|\\d+[.)])\\s+");
    private static final Pattern LINK = Pattern.compile("\\[([^\\]]*)]\\([^)]*\\)");
    private static final Pattern EMPHASIS = Pattern.compile("\\*\\*|__|`|(?<!\\w)\\*|\\*(?!\\w)");

    private MarkdownReader() {
    }

    /** Returns content lines tagged with their nearest heading. Headings and rules are not returned. */
    public static List<MarkdownLine> read(String markdown) {
        List<MarkdownLine> lines = new ArrayList<>();
        String section = "";
        String[] raw = markdown.split("\\R", -1);
        for (int i = 0; i < raw.length; i++) {
            String line = raw[i].strip();
            if (line.isEmpty() || line.matches("^(-{3,}|\\*{3,}|_{3,})$")) {
                continue;
            }
            Matcher heading = HEADING.matcher(line);
            if (heading.matches()) {
                section = clean(heading.group(2));
                continue;
            }
            String text = clean(LIST_MARKER.matcher(line).replaceFirst(""));
            if (!text.isEmpty()) {
                lines.add(new MarkdownLine(i + 1, section, text));
            }
        }
        return lines;
    }

    static String clean(String text) {
        String withoutLinks = LINK.matcher(text).replaceAll("$1");
        return EMPHASIS.matcher(withoutLinks).replaceAll("").replaceAll("\\s+", " ").strip();
    }
}
