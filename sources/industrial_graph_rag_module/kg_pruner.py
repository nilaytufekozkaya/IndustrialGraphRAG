import rdflib
import os

def prune_knowledge_graph(input_file, output_file):

    g = rdflib.Graph()
    g.parse(input_file, format='turtle')

    RDF = rdflib.namespace.RDF
    RDFS = rdflib.namespace.RDFS

    # TODO: go over this in another meeting, before slash/hash refactoring
    browseNames_URI = rdflib.URIRef("http://opcfoundation.org/UA/Meta#browseNames")
    objectProperties_URI = rdflib.URIRef("http://opcfoundation.org/UA/Meta#objectProperties")
    aggregates_URI = rdflib.URIRef("http://opcfoundation.org/UA#aggregates")
    nodeType_URI = rdflib.URIRef("http://opcfoundation.org/UA/Meta#nodeType")
    isInstanceDeclaration_URI = rdflib.URIRef("http://opcfoundation.org/UA/Meta#isInstanceDeclaration")


    # 1) remove all nodes which are subproperties of browseNames (for example the definition node for the "axis")
    subproperties_of_browseNames = set()
    for s, p, o in g.triples((None, RDFS.subPropertyOf, None)):
        if browseNames_URI in o:
            subproperties_of_browseNames.add(s)
            g.remove((s, None, None))  # Remove the node entirely

    # 2) remove all statements where the predicate is a subproperty of browseNames (for example statements where "axis" is the predicate)
    for subprop in subproperties_of_browseNames:
        g.remove((None, subprop, None))

    # 3-a) remove all statements where the predicate is browseNames
    g.remove((None, browseNames_URI, None))

    # 3-b) remove all statements where the predicate is the aggregates or objectProperties
    g.remove((None, objectProperties_URI, None))
    g.remove((None, aggregates_URI, None))

    # 3-c) remove all statements where the predicate is the nodeType or isInstanceDeclaration
    g.remove((None, nodeType_URI, None))
    g.remove((None, isInstanceDeclaration_URI, None))

    # 4) remove the browseNames node itself
    g.remove((browseNames_URI, None, None))  # Removes all triples with browseNames as the subject

    # 5) replace any field whose value is larger 1000 characters with empty string.
    for s, p, o in g.triples((None, None, None)):
        if isinstance(o, rdflib.Literal) and len(str(o)) > 1000:
            g.remove((s, p, o))
            # Comment the next line if we just want to remove these fields, and not add any empty strs in place
            g.add((s, p, rdflib.Literal(""))) # replace with plain literals
            # g.add((s, p, rdflib.Literal("", datatype=XSD.string))) # replace with strings

    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    g.serialize(destination=output_file, format='turtle')


