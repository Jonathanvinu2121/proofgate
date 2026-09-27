package dev.proofgate.verify;

import dev.proofgate.claims.Claim;
import dev.proofgate.facts.Fact;
import java.util.List;
import java.util.Set;

/**
 * @param citedChunkIds evidence the claim was matched against, best match first
 * @param missingFacts  facts in the claim that the cited evidence does not contain
 * @param reason        human-readable explanation of the verdict
 */
public record ClaimResult(Claim claim, Verdict verdict, List<String> citedChunkIds, Set<Fact> missingFacts,
                          String reason) {
}
