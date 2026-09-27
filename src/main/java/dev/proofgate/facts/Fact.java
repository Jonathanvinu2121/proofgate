package dev.proofgate.facts;

/**
 * A hard, checkable fact inside a sentence: a number or a named technology.
 * Every fact in a claim must appear in the evidence it cites.
 */
public record Fact(Kind kind, String value) {

    public enum Kind { NUMBER, TECHNOLOGY }

    @Override
    public String toString() {
        return value;
    }
}
