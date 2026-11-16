package designs.struve.freetarget.android;

import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.function.Consumer;

/** Frames fragmented or concatenated Arduino JSON objects. */
final class PacketFramer {
    private static final int LIMIT = 524_288;
    private final ByteArrayOutputStream packet = new ByteArrayOutputStream();
    private int depth;
    private boolean quoted;
    private boolean escaped;

    void feed(byte[] bytes, int length, Consumer<String> accept, Runnable overflow) {
        for (int index = 0; index < length; index++) {
            int value = bytes[index] & 255;
            if (depth == 0 && value != '{') continue;
            packet.write(value);
            if (quoted) {
                if (escaped) escaped = false;
                else if (value == 92) escaped = true;
                else if (value == '"') quoted = false;
            } else if (value == '"') quoted = true;
            else if (value == '{') depth++;
            else if (value == '}') depth--;
            if (packet.size() > LIMIT) {
                reset();
                overflow.run();
            } else if (depth == 0) {
                String text = new String(packet.toByteArray(), StandardCharsets.UTF_8);
                reset();
                accept.accept(clean(text));
            }
        }
    }

    private void reset() {
        packet.reset();
        depth = 0;
        quoted = false;
        escaped = false;
    }

    private static String clean(String text) {
        StringBuilder result = new StringBuilder(text.length());
        boolean inString = false;
        boolean escape = false;
        int previous = -1;
        for (int index = 0; index < text.length(); index++) {
            char value = text.charAt(index);
            if (inString) {
                result.append(value);
                if (escape) escape = false;
                else if (value == 92) escape = true;
                else if (value == '"') { inString = false; previous = result.length() - 1; }
                continue;
            }
            char prior = previous < 0 ? 0 : result.charAt(previous);
            if (value == ',' && (prior == ',' || prior == '{' || prior == '[')) continue;
            if ((value == '}' || value == ']') && prior == ',') result.deleteCharAt(previous);
            result.append(value);
            if (!Character.isWhitespace(value)) previous = result.length() - 1;
            if (value == '"') inString = true;
        }
        return result.toString();
    }
}
