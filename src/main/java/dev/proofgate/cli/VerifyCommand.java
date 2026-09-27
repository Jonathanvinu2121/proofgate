package dev.proofgate.cli;

import dev.proofgate.claims.ClaimExtractor;
import dev.proofgate.verify.ClaimResult;
import dev.proofgate.verify.Verdict;
import dev.proofgate.verify.VerificationReport;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.Callable;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

@Command(name = "verify", mixinStandardHelpOptions = true,
        description = "Check every claim in a generated CV or cover letter against your source CV.",
        exitCodeListHeading = "%nExit codes:%n",
        exitCodeList = {"0:all claims pass", "1:unsupported claims found (or claims needing review, with --strict)"})
class VerifyCommand implements Callable<Integer> {

    @Option(names = "--cv", required = true, description = "Source-of-truth CV in markdown.")
    Path cv;

    @Option(names = "--output", required = true, description = "Generated CV or cover letter in markdown.")
    Path output;

    @Option(names = "--strict", description = "Also fail on claims that need review.")
    boolean strict;

    @Override
    public Integer call() throws Exception {
        VerificationReport report = ProofGateCli.verifierFor(cv)
                .verify(ClaimExtractor.extract(Files.readString(output)));

        for (ClaimResult r : report.results()) {
            System.out.printf("[%-6s] line %-3d %s%n", label(r.verdict()), r.claim().lineNumber(), r.claim().text());
            System.out.printf("         cites %s: %s%n%n", String.join(", ", r.citedChunkIds()), r.reason());
        }
        System.out.printf("%d supported, %d need review, %d unsupported%n",
                report.count(Verdict.SUPPORTED), report.count(Verdict.NEEDS_REVIEW), report.count(Verdict.UNSUPPORTED));

        boolean passes = report.passes(strict);
        System.out.println(passes ? "PASS" : "BLOCKED: fix or remove the claims above before sending.");
        return passes ? 0 : 1;
    }

    private static String label(Verdict verdict) {
        return switch (verdict) {
            case SUPPORTED -> "PASS";
            case NEEDS_REVIEW -> "REVIEW";
            case UNSUPPORTED -> "FAIL";
        };
    }
}
