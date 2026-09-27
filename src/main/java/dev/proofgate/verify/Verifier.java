package dev.proofgate.verify;

import dev.proofgate.claims.Claim;
import dev.proofgate.evidence.EvidenceChunk;
import dev.proofgate.facts.Fact;
import dev.proofgate.facts.FactExtractor;
import dev.proofgate.text.Words;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.regex.Pattern;

/**
 * Deterministic claim checker. For each claim it finds the best-matching evidence chunk, then:
 * <ol>
 *   <li>any hard fact found nowhere in the evidence makes the claim UNSUPPORTED;</li>
 *   <li>facts spread across several chunks, weak wording overlap, or leadership language the evidence
 *       does not state make it NEEDS_REVIEW;</li>
 *   <li>otherwise it is SUPPORTED, citing the matched chunk.</li>
 * </ol>
 */
public final class Verifier {

    /** Minimum share of a claim's content words that must appear in its best-matching chunk. */
    static final double MIN_WORD_OVERLAP = 0.4;

    private static final Pattern LEADERSHIP = Pattern.compile(
            "(?i)\\b(led|lead|leading|managed|managing|headed|spearheaded|mentored|mentoring|supervised"
                    + "|directed|oversaw|team of|founded|co-founded)\\b");

    private record IndexedChunk(EvidenceChunk chunk, Set<Fact> facts, Set<String> words) {
    }

    private final FactExtractor factExtractor;
    private final List<IndexedChunk> index;
    private final Set<Fact> allEvidenceFacts = new HashSet<>();

    public Verifier(List<EvidenceChunk> evidence, FactExtractor factExtractor) {
        if (evidence.isEmpty()) {
            throw new IllegalArgumentException("No evidence to verify against");
        }
        this.factExtractor = factExtractor;
        this.index = evidence.stream()
                .map(c -> new IndexedChunk(c, factExtractor.extract(c.text()), Words.contentWords(c.text())))
                .toList();
        index.forEach(c -> allEvidenceFacts.addAll(c.facts()));
    }

    public VerificationReport verify(List<Claim> claims) {
        return new VerificationReport(claims.stream().map(this::check).toList());
    }

    public ClaimResult check(Claim claim) {
        Set<Fact> claimFacts = factExtractor.extract(claim.text());
        Set<String> claimWords = Words.contentWords(claim.text());
        IndexedChunk best = index.stream()
                .max(Comparator.comparingInt(c -> score(claimFacts, claimWords, c)))
                .orElseThrow();

        Set<Fact> missingEverywhere = difference(claimFacts, allEvidenceFacts);
        if (!missingEverywhere.isEmpty()) {
            return result(claim, Verdict.UNSUPPORTED, List.of(best), missingEverywhere,
                    "Not found anywhere in the evidence: " + missingEverywhere);
        }

        Set<Fact> missingFromBest = difference(claimFacts, best.facts());
        if (!missingFromBest.isEmpty()) {
            return result(claim, Verdict.NEEDS_REVIEW, sourcesFor(best, missingFromBest), missingFromBest,
                    "Combines facts from separate evidence entries; the combination itself is unverified");
        }

        double overlap = overlap(claimWords, best.words());
        if (overlap < MIN_WORD_OVERLAP) {
            return result(claim, Verdict.NEEDS_REVIEW, List.of(best), Set.of(),
                    "Weak wording match to the closest evidence (%.0f%% of words)".formatted(overlap * 100));
        }

        if (LEADERSHIP.matcher(claim.text()).find() && !LEADERSHIP.matcher(best.chunk().text()).find()) {
            return result(claim, Verdict.NEEDS_REVIEW, List.of(best), Set.of(),
                    "Claims leadership or ownership that the cited evidence does not state");
        }

        return result(claim, Verdict.SUPPORTED, List.of(best), Set.of(), "All facts found in cited evidence");
    }

    private static int score(Set<Fact> claimFacts, Set<String> claimWords, IndexedChunk chunk) {
        return 100 * intersectionSize(claimFacts, chunk.facts()) + intersectionSize(claimWords, chunk.words());
    }

    private static double overlap(Set<String> claimWords, Set<String> chunkWords) {
        return claimWords.isEmpty() ? 0 : (double) intersectionSize(claimWords, chunkWords) / claimWords.size();
    }

    /** The best chunk, then the first chunk holding each fact the best chunk lacks. */
    private List<IndexedChunk> sourcesFor(IndexedChunk best, Set<Fact> missingFromBest) {
        Set<IndexedChunk> sources = new LinkedHashSet<>();
        sources.add(best);
        for (Fact fact : missingFromBest) {
            index.stream().filter(c -> c.facts().contains(fact)).findFirst().ifPresent(sources::add);
        }
        return new ArrayList<>(sources);
    }

    private static ClaimResult result(Claim claim, Verdict verdict, List<IndexedChunk> cited, Set<Fact> missing,
                                      String reason) {
        return new ClaimResult(claim, verdict, cited.stream().map(c -> c.chunk().id()).toList(), missing, reason);
    }

    private static <T> Set<T> difference(Set<T> a, Set<T> b) {
        Set<T> diff = new LinkedHashSet<>(a);
        diff.removeAll(b);
        return diff;
    }

    private static <T> int intersectionSize(Set<T> a, Set<T> b) {
        int n = 0;
        for (T item : a) {
            if (b.contains(item)) {
                n++;
            }
        }
        return n;
    }
}
