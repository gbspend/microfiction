import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.CoreDocument;
import edu.stanford.nlp.pipeline.CoreSentence;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.semgraph.SemanticGraph;

public class SkeletonParser {

	static String[] files = new String[] {"6ws-reddit-top2.txt", "6ws-twitter-ernest6words.txt", "6ws-twitter-sixwordstories.txt", "6ws-reddit-top1.txt"};

	
  public static void main(String[] args) throws IOException {
    // set up pipeline properties
    Properties props = new Properties();
	props.put("threads", 16);
    // set the list of annotators to run
    props.setProperty("annotators", "tokenize,ssplit,pos,depparse");
    // build pipeline
    StanfordCoreNLP pipeline = new StanfordCoreNLP(props);
    // create a document object
    for (String filename : files) {
    	System.out.println(filename);
    	List<String> documents = loadDocument(filename);
    	PrintWriter pw = new PrintWriter(filename + ".depparse.txt");
    	for (String document : documents) {
	    	// annnotate the document
	    	final CoreDocument coreDocument = new CoreDocument(document.replaceAll("(?<=[a-zA-Z0-9])\\. ", "; "));// replace periods with semi-colons
			pipeline.annotate(coreDocument);
	    	
	    	final List<CoreSentence> sentences = coreDocument.sentences();
	    	StringBuilder dependencyStr = new StringBuilder();
	    	int i = 0;
	    	for (CoreSentence sentence: sentences) {
	    		// dependency parse for the second sentence
	    		SemanticGraph dependencyParse = sentence.dependencyParse();
	    		for (String line : dependencyParse.toString().split("\n")) {
	    			final int numSpaces = line.indexOf('-');
	    			dependencyStr.append((numSpaces/2)+i);
	    			dependencyStr.append(' ');
	    			dependencyStr.append(line.substring(numSpaces));
	    			dependencyStr.append('\n');
	    		}
	    		i++;
	    	}
	    	pw.println(document.trim());
	    	pw.println();
	    	pw.println(dependencyStr.toString());
    	}
    	pw.close();
	}
  }

	private static List<String> loadDocument(String filename) throws IOException {
		List<String> docs = new ArrayList<String>();
		final BufferedReader bufferedReader = new BufferedReader(new FileReader(filename));
		String line;
		while ((line = bufferedReader.readLine()) != null) {
			String story = line.trim();
			story = story.replaceAll("\\\\\"", "\""); // get rid of \"
			story = story.replaceAll("\\.\\.+", "…"); // replace multiple periods with ellipses
			docs.add(story);
		}
		bufferedReader.close();
		
		return docs;
	}

}
