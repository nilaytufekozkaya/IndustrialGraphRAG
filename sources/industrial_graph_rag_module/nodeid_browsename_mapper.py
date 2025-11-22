import rdflib
import csv
import re
import urllib.parse

VERBOSE = False # Set Verbose to True, if you want to see all the output

def split_uri(uri):
    uri = uri.rstrip('/')
    if '#' in uri:
        ns, local = uri.rsplit('#', 1)
    elif '/' in uri:
        ns, local = uri.rsplit('/', 1)
        ns += '/'
    else:
        ns = ''
        local = uri
    return ns, local

def process_label(label):
    # Remove specific punctuations: , . ; ' " ! ? :
    chars_to_remove = ',.;\'"!?:'
    label = label.translate(str.maketrans('', '', chars_to_remove))
    # Replace whitespaces with '_'
    label = re.sub(r'\s+', '_', label)
    return label

def extract_label_from_uri(uri):
    _, local = split_uri(uri)
    # Unquote any percent-encoded characters
    local = urllib.parse.unquote(local)
    return local

def map_nodeids_to_browsenames(input_file, output_file):

    g = rdflib.Graph()

    g.parse(input_file, format="turtle")

    queries = [
        """
        PREFIX ns1: <http://opcfoundation.org/UA/Meta/TA#>
        PREFIX ns2: <http://opcfoundation.org/UA/Meta/IA#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        SELECT ?s ?nodeid ?browseName ?label ?displayName ?type
        WHERE {
          OPTIONAL { ?s rdf:type ?type . }
          OPTIONAL { ?s ns1:nodeId ?nodeid . }
          OPTIONAL { ?s ns1:browseName ?browseName . }
          OPTIONAL { ?s rdfs:label ?label . }
          OPTIONAL { ?s ns1:displayName ?displayName . }
          OPTIONAL { ?s ns2:displayName ?displayName . }
        }
         """,

        """
        PREFIX ns1: <http://opcfoundation.org/UA/Meta/TA#>
        PREFIX ns2: <http://opcfoundation.org/UA/Meta/IA#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        SELECT ?s ?nodeid ?browseName ?label ?displayName ?type
        WHERE {
          OPTIONAL { ?s rdf:type ?type . }
          OPTIONAL { ?s ns2:nodeId ?nodeid . }
          OPTIONAL { ?s ns2:browseName ?browseName . }
          OPTIONAL { ?s rdfs:label ?label . }
          OPTIONAL { ?s ns1:displayName ?displayName . }
          OPTIONAL { ?s ns2:displayName ?displayName . }
        }
        """,

        """
        PREFIX ns1: <http://opcfoundation.org/UA/Meta/TA#>
        PREFIX ns2: <http://opcfoundation.org/UA/Meta/IA#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        SELECT ?s ?nodeid ?browseName ?label ?displayName ?type
        WHERE {
          OPTIONAL { ?s rdf:type ?type . }
          OPTIONAL { ?s ns1:nodeId ?nodeid . }
          OPTIONAL { ?s ns2:browseName ?browseName . }
          OPTIONAL { ?s rdfs:label ?label . }
          OPTIONAL { ?s ns1:displayName ?displayName . }
          OPTIONAL { ?s ns2:displayName ?displayName . }
        }
        """,
        """
        PREFIX ns1: <http://opcfoundation.org/UA/Meta/TA#>
        PREFIX ns2: <http://opcfoundation.org/UA/Meta/IA#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        SELECT ?s ?nodeid ?browseName ?label ?displayName ?type
        WHERE {
          OPTIONAL { ?s rdf:type ?type . }
          OPTIONAL { ?s ns2:nodeId ?nodeid . }
          OPTIONAL { ?s ns1:browseName ?browseName . }
          OPTIONAL { ?s rdfs:label ?label . }
          OPTIONAL { ?s ns1:displayName ?displayName . }
          OPTIONAL { ?s ns2:displayName ?displayName . }
        }
        """
    ]

    if VERBOSE:
        print("Opening output file")

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(["subject_uri", "subject_name", "nodeid", "browseName", "label", "synonyms", "entity_types"])

        results_dict = {}

        for query in queries:
            results = g.query(query)
            for row in results:
                subject = str(row.s)
                nodeid = str(row.nodeid) if row.nodeid else '<None>'
                browseName = str(row.browseName) if row.browseName else '<None>'
                label = str(row.label) if row.label else None
                displayName = str(row.displayName) if row.displayName else None
                entity_type = str(row.type) if row.type else '<none>'

                if subject not in results_dict:
                    results_dict[subject] = {
                        'nodeid': nodeid,
                        'browseName': browseName,
                        'label': label,
                        'displayName': displayName,
                        'types': set()
                    }
                    if entity_type != '<none>':
                        # Split entity_type by semicolons and add each to the set
                        for et in entity_type.split(';'):
                            et = et.strip()
                            results_dict[subject]['types'].add(et)
                else:
                    # Set nodeid
                    if results_dict[subject]['nodeid'] == '<None>' and nodeid != '<None>':
                        results_dict[subject]['nodeid'] = nodeid
                    # Set browseName
                    if results_dict[subject]['browseName'] == '<None>' and browseName != '<None>':
                        results_dict[subject]['browseName'] = browseName
                    # Set label
                    if not results_dict[subject]['label'] and label:
                        results_dict[subject]['label'] = label
                    # Set displayName
                    if not results_dict[subject]['displayName'] and displayName:
                        results_dict[subject]['displayName'] = displayName
                    # Set entity types
                    if entity_type != '<none>':
                        # Split entity_type by semicolons and add each to the set
                        for et in entity_type.split(';'):
                            et = et.strip()
                            results_dict[subject]['types'].add(et)

        # process the data row by row
        for subject, data in results_dict.items():
            subject_uri = subject
            nodeid = data.get('nodeid') or '<None>'
            browseName = data.get('browseName') or '<None>'
            label = data.get('label')
            displayName = data.get('displayName')
            types = data.get('types', set())

            # Exclude nodes containing 'namespace' in their types
            if any('namespace' in et.lower() for et in types):
                continue

            # Get subject_name and process it (no punctuations and no whitespaces)
            subject_name = extract_label_from_uri(subject_uri)
            subject_name = process_label(subject_name)

            # Handle the label field
            if label:
                label = label
            elif displayName:
                label = displayName
            else:
                if browseName and browseName != '<None>':
                    # Set the label to last part of browseName
                    label = extract_label_from_uri(browseName)
                else:
                    # Use the subject name as label
                    label = subject_name

            # remove punctuations from the label and replace whitespaces with '_'
            label = process_label(label)

            # COMMENT OR UNCOMMENT THIS PART
            # based on whether you want to include URI labels in our mapping.
            #if 'http' in label.lower():
            #    continue

            # we currently always set to none for synonyms
            synonyms = '<None>'

            # for entity types
            if types:
                entity_types = "; ".join(types)
            else:
                entity_types = '<none>'
                print(f"Warning: Node {label} ({nodeid}) has no entity type.")

            if VERBOSE:
                if ';' in entity_types:
                    print(f"Node {label} ({nodeid}) has multiple entity types: {entity_types}.")

            writer.writerow([subject_uri, subject_name, nodeid, browseName, label, synonyms, entity_types])

    print(f"Mapping saved to {output_file} successfully.")
