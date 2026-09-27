package dev.proofgate.cli;

import dev.proofgate.evidence.CvParser;
import dev.proofgate.facts.FactExtractor;
import dev.proofgate.facts.TechLexicon;
import dev.proofgate.verify.Verifier;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import picocli.CommandLine;
import picocli.CommandLine.Command;

@Command(name = "proofgate", mixinStandardHelpOptions = true, version = "proofgate 0.1.0",
        description = "Blocks unsupported claims in tailored CVs by tracing each one to evidence.",
        subcommands = {VerifyCommand.class, EvalCommand.class})
public class ProofGateCli implements Runnable {

    public static void main(String[] args) {
        System.exit(new CommandLine(new ProofGateCli()).execute(args));
    }

    @Override
    public void run() {
        new CommandLine(this).usage(System.out);
    }

    static Verifier verifierFor(Path cv) throws IOException {
        return new Verifier(CvParser.parse(Files.readString(cv)), new FactExtractor(TechLexicon.loadDefault()));
    }
}
