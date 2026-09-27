package dev.proofgate.text;

/**
 * A non-empty content line from a markdown document, stripped of list markers and inline formatting.
 *
 * @param lineNumber 1-based line number in the source document
 * @param section    text of the nearest heading above this line, or "" if none
 * @param text       cleaned line text
 */
public record MarkdownLine(int lineNumber, String section, String text) {
}
