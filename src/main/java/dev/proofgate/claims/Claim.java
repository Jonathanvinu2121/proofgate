package dev.proofgate.claims;

/**
 * One atomic statement from generated output that must be backed by evidence.
 *
 * @param id         sequential ID within the document, e.g. {@code c3}
 * @param text       the claim text
 * @param lineNumber 1-based line in the generated document (0 if not from a document)
 */
public record Claim(String id, String text, int lineNumber) {
}
