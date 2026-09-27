package dev.proofgate.cli;

import dev.proofgate.eval.EvalCase;
import dev.proofgate.eval.EvalCase.Expectation;
import dev.proofgate.eval.EvalSummary;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.Callable;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

@Command(name = "eval", mixinStandardHelpOptions = true,
        description = "Score the verifier on labelled claims and append the result to the history file.")
class EvalCommand implements Callable<Integer> {

    private static final String HISTORY_HEADER = "timestamp,cases,catch_rate,false_block_rate,review_rate,note";

    @Option(names = "--cv", defaultValue = "evals/fixtures/cv.md", description = "Evidence CV. Default: ${DEFAULT-VALUE}")
    Path cv;

    @Option(names = "--cases", defaultValue = "evals/cases.tsv", description = "Labelled cases. Default: ${DEFAULT-VALUE}")
    Path cases;

    @Option(names = "--history", defaultValue = "evals/history.csv", description = "Scorecard log. Default: ${DEFAULT-VALUE}")
    Path history;

    @Option(names = "--note", defaultValue = "", description = "What changed since the last run.")
    String note;

    @Option(names = "--no-record", description = "Print the scorecard without appending to the history file.")
    boolean noRecord;

    @Override
    public Integer call() throws Exception {
        EvalSummary summary = EvalSummary.run(ProofGateCli.verifierFor(cv), EvalCase.load(cases));

        System.out.println("By category (correct / total):");
        summary.byCategory().forEach((category, s) ->
                System.out.printf("  %-34s %2d / %-2d%n", category, s.correct(), s.total()));

        if (!summary.misses().isEmpty()) {
            System.out.println("\nMisses:");
            for (EvalSummary.Outcome o : summary.misses()) {
                System.out.printf("  [%s/%s -> %s] %s%n      %s%n", o.evalCase().expected(), o.evalCase().category(),
                        o.result().verdict(), o.evalCase().claim(), o.result().reason());
            }
        }

        System.out.printf("%nScorecard (%d fabricated, %d faithful):%n",
                summary.count(Expectation.FABRICATED), summary.count(Expectation.FAITHFUL));
        System.out.printf("  Fabrication catch rate  %5.1f%%   (target >= 95%%)%n", summary.catchRate() * 100);
        System.out.printf("  False-block rate        %5.1f%%   (target <= 10%%)%n", summary.falseBlockRate() * 100);
        System.out.printf("  Review rate (faithful)  %5.1f%%   (lower = less manual work)%n", summary.reviewRate() * 100);

        if (!noRecord) {
            record(summary);
        }
        return 0;
    }

    private void record(EvalSummary summary) throws Exception {
        if (!Files.exists(history)) {
            Files.writeString(history, HISTORY_HEADER + System.lineSeparator());
        }
        String row = String.join(",",
                LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME).substring(0, 19),
                String.valueOf(summary.outcomes().size()),
                "%.3f".formatted(summary.catchRate()),
                "%.3f".formatted(summary.falseBlockRate()),
                "%.3f".formatted(summary.reviewRate()),
                "\"" + note.replace("\"", "'") + "\"");
        Files.writeString(history, row + System.lineSeparator(), StandardOpenOption.APPEND);
        System.out.println("\nRecorded in " + history);
    }
}
