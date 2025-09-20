import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;

public class _CharacterLocAdder {

    // Keys to skip for localization
    private static final Set<String> SKIP_KEYS = new HashSet<>(Arrays.asList(
        "traits", "ai_will_do", "modifier", "visible", "available", "allowed", "civilian", "army", "portraits", "NOT", "OR", "AND"
    ));

    public static void main(String[] args) {
        Map<String, LinkedHashMap<String, String>> allCharNames = new LinkedHashMap<>();

        try {
            Path currentDir = Paths.get(".");
            DirectoryStream<Path> stream = Files.newDirectoryStream(currentDir, "*.txt");

            for (Path filePath : stream) {
                LinkedHashMap<String, String> charNames = processFile(filePath);
                if (!charNames.isEmpty()) {
                    String fileKey = filePath.getFileName().toString().replaceFirst("\\.txt$", "");
                    allCharNames.put(fileKey, charNames);
                }
            }

            // Write combined _CharacterLocAdderOutput.yml
            List<String> outputLines = new ArrayList<>();
            outputLines.add("l_english:");
            for (Map.Entry<String, LinkedHashMap<String, String>> entry : allCharNames.entrySet()) {
                String fileName = entry.getKey();
                LinkedHashMap<String, String> charMap = entry.getValue();

                outputLines.add(""); // empty line
                outputLines.add("#" + fileName); // comment with file name
                for (Map.Entry<String, String> charEntry : charMap.entrySet()) {
                    outputLines.add(" " + charEntry.getKey() + ":0 \"" + charEntry.getValue() + "\"");
                }
            }

            Files.write(Paths.get("_CharacterLocAdderOutput.yml"), outputLines);
            System.out.println("All .txt files processed. Combined output: _CharacterLocAdderOutput.yml");

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static LinkedHashMap<String, String> processFile(Path filePath) {
        LinkedHashMap<String, String> charNames = new LinkedHashMap<>();
        String outputFilePath = filePath.toString();

        try {
            List<String> lines = Files.readAllLines(filePath);
            List<String> newLines = new ArrayList<>();

            String currentKey = null;
            Pattern keyPattern = Pattern.compile("^\\s*(\\w+)\\s*=\\s*\\{");
            Pattern namePattern = Pattern.compile("^\\s*name\\s*=\\s*\"([^\"]+)\"");

            for (String line : lines) {
                Matcher keyMatcher = keyPattern.matcher(line);
                Matcher nameMatcher = namePattern.matcher(line);

                if (keyMatcher.find()) {
                    currentKey = keyMatcher.group(1);
                    newLines.add(line);
                } else if (nameMatcher.find() && currentKey != null) {
                    // Skip if currentKey is in the skip list
                    if (!SKIP_KEYS.contains(currentKey)) {
                        String originalName = nameMatcher.group(1);
                        charNames.put(currentKey, originalName);
                    }
                    String newLine = line.replaceAll("\"[^\"]+\"", currentKey);
                    newLines.add(newLine);
                } else {
                    newLines.add(line);
                }
            }

            // Overwrite the original .txt file
            Files.write(Paths.get(outputFilePath), newLines);
            System.out.println("Processed: " + filePath.getFileName());

        } catch (IOException e) {
            System.err.println("Error processing file: " + filePath.getFileName());
            e.printStackTrace();
        }

        return charNames;
    }
}
