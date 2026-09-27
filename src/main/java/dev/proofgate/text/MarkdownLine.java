package dev.proofgate.text;

/**
 * A non-empty content line from a markdown document, stripped of list markers and inline formatting.
 *
 * @param lineNumber 1-based line number in the source document
 * @param section    text of the nearest heading at or above this line, or "" if none
 * @param text       cleaned line text
 * @param heading    whether the line is itself a heading (headings carry facts too: titles, companies, dates)
 */
public record MarkdownLine(int lineNumber, String section, String text, boolean heading) {
}
