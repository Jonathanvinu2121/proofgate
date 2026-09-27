package dev.proofgate.text;

import java.util.LinkedHashSet;
import java.util.Locale;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Content-word extraction with crude suffix stemming, used for textual overlap scoring. */
public final class Words {

    private static final Pattern WORD = Pattern.compile("[a-z]+");
    private static final Set<String> STOPWORDS = Set.of(
            "about", "across", "after", "also", "among", "and", "been", "being", "both", "each", "from",
            "have", "into", "more", "most", "other", "over", "same", "such", "than", "that", "their",
            "them", "then", "there", "these", "they", "this", "those", "through", "under", "using",
            "very", "were", "what", "when", "where", "which", "while", "with", "within", "your");

    private Words() {
    }

    /** Lowercased, stemmed words of length >= 4 that are not stopwords. */
    public static Set<String> contentWords(String text) {
        Set<String> words = new LinkedHashSet<>();
        Matcher m = WORD.matcher(text.toLowerCase(Locale.ROOT));
        while (m.find()) {
            String word = m.group();
            if (word.length() >= 4 && !STOPWORDS.contains(word)) {
                words.add(stem(word));
            }
        }
        return words;
    }

    static String stem(String word) {
        for (String suffix : new String[] {"ing", "ed", "es", "s"}) {
            if (word.endsWith(suffix) && word.length() - suffix.length() >= 4) {
                return word.substring(0, word.length() - suffix.length());
            }
        }
        return word;
    }
}
