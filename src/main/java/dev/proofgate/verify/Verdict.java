package dev.proofgate.verify;

public enum Verdict {
    /** Every hard fact is in the cited evidence and the wording matches it. */
    SUPPORTED,
    /** Not provably false, but not provably backed either: a human or the semantic judge must decide. */
    NEEDS_REVIEW,
    /** Contains a fact that appears nowhere in the evidence. Blocks the document. */
    UNSUPPORTED
}
