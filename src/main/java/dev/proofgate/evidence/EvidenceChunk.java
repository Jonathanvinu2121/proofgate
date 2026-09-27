package dev.proofgate.evidence;

/**
 * One citable unit of evidence, e.g. a single CV bullet.
 *
 * @param id         stable citation ID derived from the section, e.g. {@code experience-2}
 * @param section    heading the chunk sits under
 * @param text       the evidence text
 * @param lineNumber 1-based line in the source document
 */
public record EvidenceChunk(String id, String section, String text, int lineNumber) {
}
