package converter;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

import uk.ac.ebi.ontocat.Ontology;
import uk.ac.ebi.ontocat.OntologyService;
import uk.ac.ebi.ontocat.OntologyServiceException;
import uk.ac.ebi.ontocat.OntologyTerm;
import uk.ac.ebi.ontocat.file.FileOntologyService;

public class OntologyConverter {

	static final String INDENT = "_";
	static int node = 0;
	static List<String> tSet = new ArrayList<String>();
	static List<String> keyList = new ArrayList<String>();
	static List<String> visitedTerms = new ArrayList<String>();
	static double allTermsInTree;
	public static void main(String[] args) throws OntologyServiceException,
			URISyntaxException, IOException {
	
		File ontologyFile = new File(
				"C:/Users/crick/workspace/Ontologies/HPO/hp.obo");
		OntologyService os = new FileOntologyService(ontologyFile.toURI());
		Ontology o = os.getOntologies().get(0);
		OntologyTerm hpoRoot = os.getRootTerms(o).get(0);
		
		FileWriter jsonWriter = new FileWriter("hpo.json");
		jsonWriter.append("children: [");
		writeJSONNested(hpoRoot, os, jsonWriter, 0, true);
		jsonWriter.append("]");
		jsonWriter.flush();
		jsonWriter.close();
		
		String rootAccession = os.getRootTerms(o).get(0).getAccession();
		allTermsInTree = os.getAllChildren(o.getOntologyAccession(), rootAccession).size() + 1;
		
		FileWriter labelIDScoreWriter = new FileWriter("labelIDScore.txt");

		writeScoreTDL(o, hpoRoot, os, labelIDScoreWriter);
		labelIDScoreWriter.flush();
		labelIDScoreWriter.close();
		
		FileWriter lineageWriter = new FileWriter("lineage.txt");
		writeLineageTDL(o, hpoRoot, os, lineageWriter);
		lineageWriter.flush();
		lineageWriter.close();
		
		FileWriter parentageWriter = new FileWriter("parentage.txt");
		writeparentageTDL(o, hpoRoot, os, parentageWriter);
		parentageWriter.flush();
		parentageWriter.close();

	}
	

	
	private static void writeparentageTDL(Ontology o, OntologyTerm root, OntologyService os,
			FileWriter writer) throws IOException, OntologyServiceException {
		writer.append(root.getAccession());
		writer.append("\t");
		writer.append("false");
		for (OntologyTerm ot: os.getAllChildren(o.getOntologyAccession(),root.getAccession())){
			for (OntologyTerm parent : os.getParents(o.getOntologyAccession(), ot.getAccession())){
				writer.append("\n");
				writer.append(ot.getAccession());
				writer.append("\t");
				writer.append(parent.getAccession());
			}
			
		}
		
	}

	private static void writeLineageTDL(Ontology o, OntologyTerm root, OntologyService os,
			FileWriter writer) throws IOException, OntologyServiceException {
		writer.append(root.getAccession());
		writer.append("\t");
		writer.append("false");
		for (OntologyTerm ot: os.getAllChildren(o.getOntologyAccession(),root.getAccession())){
			for (OntologyTerm parent : os.getAllParents(o.getOntologyAccession(), ot.getAccession())){
				writer.append("\n");
				writer.append(ot.getAccession());
				writer.append("\t");
				writer.append(parent.getAccession());
			}
			
		}
		
	}

	private static void writeScoreTDL(Ontology o, OntologyTerm root, OntologyService os,
			FileWriter writer) throws IOException, OntologyServiceException {
		writer.append(root.getAccession());
		writer.append("\t");
		writer.append(root.getLabel());
		writer.append("\t");
		writer.append("0");
		for (OntologyTerm ot: os.getAllChildren(o.getOntologyAccession(),root.getAccession())){
			writer.append("\n");
			writer.append(ot.getAccession());
			writer.append("\t");
			writer.append(ot.getLabel());
			writer.append("\t");
			double allDescendants = os.getAllChildren(o.getOntologyAccession(),ot.getAccession()).size() + 1;
			double score = Math.abs(Math.log10(allDescendants/ allTermsInTree));
			writer.append(String.valueOf(score));
		}
		
	}

	private static void writeJSONNested(OntologyTerm ot, OntologyService os,
			FileWriter writer, int depth, Boolean isRoot) throws IOException,
			OntologyServiceException {
		for (int i = 0; i < depth; i++) {
			writer.append("     ");
		}
		writer.append("{");
		writer.append("title:");
		writer.append("\"" + ot.getLabel() + "\", ");
		
		//Derive the key from HPO ID
		String key = ot.getAccession();
		if (keyList.contains(key)){
			int i = 0;
			
			while(true){
				if (!keyList.contains(key+ "." + String.valueOf(i))){
					key = key+ "." + String.valueOf(i);
					break;
				} else{
					i++;
				}
			}
		}
		keyList.add(key);
		writer.append("key:");
		writer.append("\"" + key + "\", ");
		writer.append("hpo_id:");
		writer.append("\"" + ot.getAccession() + "\", ");

		writer.append("icon: false");

		if (!os.getChildren(ot).isEmpty()) {
			writer.append(", ");
			writer.append("\n");
			for (int i = 0; i < depth; i++) {
				writer.append("     ");
			}
			int newDepth = depth + 1;
			writer.append("children: [");

			for (OntologyTerm t : os.getChildren(ot)) {
				writer.append("\n");

				writeJSONNested(t, os, writer, newDepth, false);

			}
			writer.append("\n");
			for (int i = 0; i < depth; i++) {
				writer.append("     ");
			}
			writer.append("]");
		}
		writer.append("},");

	}

	private static void writeJSON(OntologyTerm ot, OntologyService os,
			FileWriter writer, int parent) throws IOException,
			OntologyServiceException {

		writer.append("{");
		writer.append("\"id\":");
		writer.append(String.valueOf(node) + ", ");
		int newParent = node;
		node++;
		writer.append("\"name\":");
		writer.append("\"" + ot.getLabel() + "\", ");
		writer.append("\"parentid\":");
		writer.append(String.valueOf(parent));
		writer.append("},");
		writer.append("\n");
		for (OntologyTerm t : os.getChildren(ot)) {
			if (!t.getLabel().equals("Abnormality of the skeletal system"))
				writeJSON(t, os, writer, newParent);

		}

	}

	private static void writeValuesToCSVFromRoot(OntologyTerm ot,
			OntologyService os, int depth, FileWriter writer, boolean isRoot)
			throws IOException, OntologyServiceException {

		if (isRoot) {
			writer.append('\"' + ot.getLabel() + '\"');
			writer.append(',');
			writer.append('\"' + ot.getAccession() + '\"');
			writer.append(',');
			writer.append('\"' + ot.getURI().toString() + '\"');
			writer.append(',');
			writer.append('\"' + String.valueOf(depth) + '\"');
			writer.append(',');
			writer.append('\"' + String.valueOf(os.getChildren(ot).isEmpty()) + '\"');
		}

		for (OntologyTerm t : os.getChildren(ot)) {
			writer.append('\n');
			writer.append('\"' + t.getLabel() + '\"');
			writer.append(',');
			writer.append('\"' + t.getAccession() + '\"');
			writer.append(',');
			writer.append('\"' + t.getURI().toString() + '\"');
			writer.append(',');
			writer.append('\"' + String.valueOf(depth + 1) + '\"');
			writer.append(',');
			writer.append('\"' + String.valueOf(os.getChildren(t).isEmpty()) + '\"');
			writeValuesToCSVFromRoot(t, os, depth + 1, writer, false);

		}

	}

	public static void writeStructureToCSV(FileWriter writer,
			OntologyService os, Ontology o, OntologyTerm t, int level,
			boolean isFirstChild, boolean isRoot)
			throws OntologyServiceException, IOException {

		int newLevel = level + 1;
		if (!isFirstChild) {
			if (!isRoot)
				writer.append('\n');
			for (int i = 0; i < level; i++) {
				writer.append(',');
			}
			writer.append('\"' + t.getLabel() + '\"');
		}
		if (os.getChildren(t).isEmpty()) {

		} else {
			List<OntologyTerm> children = os.getChildren(t);
			for (int i = 0; i < os.getChildren(t).size(); i++) {
				if (i == 0) {
					writer.append(',');
					writer.append('\"' + children.get(i).getLabel() + '\"');
					writeStructureToCSV(writer, os, o, children.get(i),
							newLevel, true, false);
				} else {

					writeStructureToCSV(writer, os, o, children.get(i),
							newLevel, false, false);
				}

			}
		}

	}

	public static void printAllFromRoot(OntologyTerm ot, OntologyService os,
			int level) {
		int l = level + 1;
		String indent = "";
		boolean unique = true;
		for (int i = 0; i < level; i++)
			indent += INDENT;
		for (String s : tSet) {
			if (s.equals(ot.getAccession())) {
				System.out.println(s);
				unique = false;
				break;
			}
		}
		tSet.add(ot.getAccession());
		try {
			for (OntologyTerm term : os.getChildren(ot)) {
				// System.out.print(indent);
				// System.out.print(level);
				// System.out.print("  ");
				// System.out.println(term);

				printAllFromRoot(term, os, l);
			}
		} catch (OntologyServiceException e) {

			e.printStackTrace();
		}
	}
}