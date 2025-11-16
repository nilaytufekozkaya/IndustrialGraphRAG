import rdflib
import os

def remove_owl_restrictions(input_file, output_file):

    sparql_queries = [  # for simplifying axioms
        """
        PREFIX NS0: <http://opcfoundation.org/UA/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ia: <http://opcfoundation.org/UA/Meta/IA/>
        PREFIX ta: <http://opcfoundation.org/UA/Meta/TA/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        INSERT {?s ?p ?o} WHERE {
            ?s rdfs:subClassOf ?r .
            ?r rdf:type owl:Restriction .
            ?r owl:allValuesFrom ?o .
            ?r owl:onProperty ?p .
        }
        """,

        #     INSERT Query 2:
        """
        PREFIX NS0: <http://opcfoundation.org/UA/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ia: <http://opcfoundation.org/UA/Meta/IA/>
        PREFIX ta: <http://opcfoundation.org/UA/Meta/TA/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>


        INSERT {?s ?p ?o} WHERE {
            ?s rdfs:subClassOf ?r .
            ?r rdf:type owl:Restriction .
            ?r owl:onProperty ?p .
            ?r owl:hasValue ?o .
        }
        """,

        #     INSERT Query 3:
        """
        PREFIX NS0: <http://opcfoundation.org/UA/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ia: <http://opcfoundation.org/UA/Meta/IA/>
        PREFIX ta: <http://opcfoundation.org/UA/Meta/TA/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>


        INSERT {?s ?p ?o} WHERE {
            ?s rdfs:subClassOf ?r .
            ?r rdf:type owl:Restriction .
            ?r owl:minQualifiedCardinality ?t .
            ?r owl:onProperty ?p .
            ?r owl:onClass ?o .
        }
        """
    ]

    # TODO here i am doing the removal of the owlRestritions using the construct query, mainly because this is how we did it originally
    # TODO using graphDB, as we didn't want to modify the original graph. Here the input graph is not modified anyway, and there is
    # TODO no reason to use construct query instead of a delete query, which would be significantly more efficient.
    # the CONSTRUCT query to create the new graph
    sparql_construct_query = """
    CONSTRUCT {
      ?s ?p ?o .
    } WHERE {
      ?s ?p ?o .
      FILTER NOT EXISTS {
        ?s a [] .
        FILTER(isBlank(?s))
      }
      FILTER NOT EXISTS {
        ?o a [] .
        FILTER(isBlank(?o))
      }
    }
    """

    g = rdflib.Graph()
    g.parse(input_file, format="turtle")

    for query in sparql_queries:
        g.update(query)

    new_graph = g.query(sparql_construct_query)

    output_graph = rdflib.Graph()
    for row in new_graph:
        output_graph.add(row)

    out_dir = os.path.dirname(output_file)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Save the new graph to a Turtle file
    output_graph.serialize(destination=output_file, format="turtle")
