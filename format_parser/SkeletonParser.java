import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;
import java.util.Collection;
import java.util.Set;
import java.util.HashSet;

import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.CoreDocument;
import edu.stanford.nlp.pipeline.CoreSentence;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.semgraph.SemanticGraph;
import edu.stanford.nlp.ling.IndexedWord;

public class SkeletonParser {

	static String[] files = new String[] {"filteredexemplars", "6ws-reddit-top2.txt", "6ws-twitter-ernest6words.txt", "6ws-twitter-sixwordstories.txt", "6ws-reddit-top1.txt"};

	//basically tries to replicate SemanticGraph.toString() but adding index.
	//Also a great opportunity to filter/fix bad formats (duplicate words, weird punct, ...what else?)
	private static void strRec(SemanticGraph graph, IndexedWord word, StringBuilder sb, int indent, Set<String> seen) {
		String index_str = Integer.toString(word.index());
		String id = word.toString()+index_str;
		if (seen.contains(id)) {
			return;
		}
		seen.add(id);
		sb.append(Integer.toString(indent));
		sb.append(" -> ");
		sb.append(word.toString()+" ");
		String temp = "() "; //getting this from edges is a pain; formats.py currently only needs "(root)"
		if (indent == 0) {
			temp = "(root) ";
		}
		sb.append(temp+index_str+"\n");
		for (IndexedWord child: graph.getChildList(word)) {
			strRec(graph, child, sb, indent+1, seen);
		}
	}
	
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
					Collection<IndexedWord> roots = dependencyParse.getRoots();
					for (IndexedWord root: roots) {
						strRec(dependencyParse, root, dependencyStr, 0, new HashSet<String>());
					}
				}
				pw.println(document.trim());
				pw.println();
				pw.println(dependencyStr.toString());
				//System.out.println(dependencyStr.toString());
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
			story = story.replaceAll("[\\u2018\\u2019]", "'");
			story = story.replaceAll("[\\u201C\\u201D]", "\"");
			docs.add(story);
		}
		bufferedReader.close();
		
		return docs;
	}

}
