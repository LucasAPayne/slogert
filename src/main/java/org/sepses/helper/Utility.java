package org.sepses.helper;

import org.apache.commons.codec.digest.DigestUtils;
import org.apache.commons.csv.CSVRecord;
import org.sepses.yaml.Config;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashMap;
import java.util.Map;

public class Utility {

    public static final String OTTR_IRI = "ottr:IRI";

    private static final Logger log = LoggerFactory.getLogger(Utility.class);

    /**
     * *** create hash out of content
     *
     * @param templateText
     * @return
     * @throws NoSuchAlgorithmException
     */
    public static String createHash(String templateText) throws NoSuchAlgorithmException {
        final MessageDigest digest = MessageDigest.getInstance("SHA-256");
        final byte[] hashbytes = digest.digest(templateText.getBytes(StandardCharsets.UTF_8));
        return DigestUtils.sha256Hex(hashbytes);
    }

    public static String cleanContent(String inputContent) {

        String cleanContent = inputContent.replace("\\", "|"); // clean up cleanContent
        cleanContent = cleanContent.replaceAll("\"", "|");
        cleanContent = cleanContent.replaceAll("'", "|");

        return cleanContent;
    }

    public static String cleanUriContent(String inputContent) {

        String cleanContent = inputContent.replaceAll("[^a-zA-Z0-9._-]", "_");
        cleanContent = cleanContent.replaceAll("\\.+$", "");

        return cleanContent;
    }

    public static void writeToFile(String string, String filename) throws IOException {
        FileWriter writer = new FileWriter(filename);
        writer.write(string);
        writer.flush();
        writer.close();
    }

    public static Map<String, Template> loadTemplates(Iterable<CSVRecord> existingTemplates, Config config) {

        Map<String, Template> templatesMap = new HashMap<>();
        existingTemplates.forEach(existingTemplate -> {
            Template template = Template.parseExistingTemplate(existingTemplate, config);
            templatesMap.put(template.hash, template);
        });

        return templatesMap;
    }
}
