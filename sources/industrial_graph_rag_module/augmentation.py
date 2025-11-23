from rdflib import Graph, URIRef, Literal , Namespace, RDF, RDFS
import rdflib
import networkx as nx     
from rdflib.namespace import OWL, RDF
from itertools import chain
from .config import INPUT_KG_FILE, IM_OUTPUT_FOLDER, COMBINED_SUB_GRAPH_FILE, SUB_GRAPH_FILE

from itertools import permutations 
 

def get_graph_from_ttl(ttl_file):
    # Parse the TTL file  
    g = Graph()  
    g.parse(ttl_file)  
    
    # Create a NetworkX graph  
    G = nx.DiGraph()  
    
    for s, p, o in g:  
        G.add_edge(str(s), str(o), name = str(p))
    return G,g

def find_all_paths_astar_all_nodes(nodes,G):
    best_paths = []  
    best_path_length = float('inf')  
     
    for perm in permutations(nodes):  
        total_length = 0  
        path = []  
        try:  
            for i in range(len(perm)-1):  
                current_path = nx.astar_path(G, perm[i], perm[i+1])  
                total_length += len(current_path) - 1  
                path += current_path[:-1]  
            path.append(perm[-1])  
        except nx.NetworkXNoPath:  
            continue  
        if total_length < best_path_length:  
            best_path_length = total_length  
            best_paths = [path]  
        elif total_length == best_path_length:  
            best_paths.append(path)  

    return best_paths 

def find_path_astar_all_nodes(nodes,G):
    # we will store the best path we find in these variables  
    best_path = None  
    best_path_length = float('inf')  
    
    # calculate the shortest path between each permutation of nodes  
    for perm in permutations(nodes):  
        total_length = 0  
        path = []  
        try:  
            for i in range(len(perm)-1):  
                current_path = nx.astar_path(G, perm[i], perm[i+1])  
                total_length += len(current_path) - 1  
                path += current_path[:-1]  
            path.append(perm[-1])  
        except nx.NetworkXNoPath:  
            continue  
        if total_length < best_path_length:  
            best_path_length = total_length  
            best_path = path  

    for i in range(len(best_path) - 1):  
        edge_name = G.edges[path[i], path[i+1]]['name']  

    return best_path 

def find_all_shortest_path(graph, start, end):  
    try:
        paths = list(nx.all_shortest_paths(graph, source=start, target=end))
    except nx.NetworkXNoPath:  
        print("No path between these two nodes.")   
        paths = None

    return paths 

def find_shortest_path(graph, start, end):  
    try:
        path = nx.shortest_path(graph, start, end)
    except nx.NetworkXNoPath:  
        print("No path between these two nodes.")   
        path = None
    return path  

def paths_with_edges(graph, paths):  
    path_with_edges = []  
    paths_with_edges = []
    for path in paths:
        if len(path) == 1:
            return []
        for i in range(len(path) - 1):  
            edge_name = graph.edges[path[i], path[i+1]]['name']  
            path_with_edges.append((path[i], path[i+1], edge_name))  
        paths_with_edges.append(path_with_edges)
    return paths_with_edges

def path_with_edges(graph, path):  
    path_with_edges = []  
    for i in range(len(path) - 1):  
        edge_name = graph.edges[path[i], path[i+1]]['name']  
        path_with_edges.append((path[i], path[i+1], edge_name))  
    return path_with_edges  

def get_all_shortest_paths(G, source, target):

    paths = find_all_shortest_path(G, source, target)  
    if paths == None:
        return []
    paths_w_e = paths_with_edges(G, paths)  
    
    paths_w_e_flattened_list = [item for sublist in paths_w_e for item in sublist]  
    return paths_w_e_flattened_list 

def get_path(G, source, target):

    path = find_shortest_path(G, source, target)  
    if path == None:
        return []
    path_w_e = path_with_edges(G, path)  
    

    return path_w_e 

#v2 
def all_paths_shortest_all_nodes(G,nodes):
    best_candis = []
    if len(nodes) == 1:
        return [nodes]
    for perm in permutations(nodes):

        paths = []
        shortest_path = 1111
        new_perm = True
        for i in range(len(perm)-1):
            if new_perm == True:
                try:
                    new_p = []
                    pair_shortest_paths = list(nx.all_shortest_paths(G, perm[i], perm[i+1])) 
                    if len(pair_shortest_paths) == 0:
                        paths = []
                        new_perm = False
                    else:
                        if len(paths) == 0:
                            for pair in pair_shortest_paths:
                                paths.append(pair)
                             
                        else:
                            for j in range(len(paths)):
                                for pair in pair_shortest_paths:
                                    new_p.append(paths[j] + pair[1:])
                            paths = new_p

                except nx.NetworkXNoPath: 
                    paths = []
                    new_perm = False
                except nx.NodeNotFound:
                    paths = []
                    new_perm = False
        if paths != []:
            best_candis += paths
    if len(best_candis) == 0:
        return best_candis
    min_length = len(min(best_candis, key=len))  
    # Find all the shortest lists  
    best_candis = [l for l in best_candis if len(l) == min_length]

    return best_candis

def all_paths_shortest_all_nodes_v1(G, nodes):
    # we will store the best paths we find in these variables  
    best_paths = []  
    best_path_length = float('inf')  
    
    # calculate the shortest path between each permutation of nodes  
    for perm in permutations(nodes):  
        total_length = 0  
        path = [] 
        path_new = []
        path_arr = [] 
        try:  
            for i in range(len(perm)-1):  
                current_paths = list(nx.all_shortest_paths(G, perm[i], perm[i+1])) 
                # Find the length of the shortest list  
                min_length = len(min(current_paths, key=len))  
                # Find all the shortest lists  
                shortest_lists = [l for l in current_paths if len(l) == min_length]

                total_length += min_length - 1 
                if len(path_arr) == 0: 
                    for c_path in shortest_lists:
                        path_arr.append(c_path[:-1])
                else:
                    path_new = []
                    for p in path_arr:
                        for c_path in shortest_lists:
                            path_new.append(p + c_path[:-1])
            
            for p in path_new:  
                p.append(perm[-1]) 
            path_arr =  path_new
        except nx.NetworkXNoPath:  
            continue  
        if total_length < best_path_length:  
            best_path_length = total_length  
            best_paths = path_arr
        elif total_length == best_path_length:  
            best_paths.append(path_arr)  
    

        pass    
    return best_paths  

def extract_nodes(g, node):  
    # Create a graph  
    # Define the namespaces  
    ns1 = Namespace("http://opcfoundation.org/UA/")  
  
    # Bind the namespaces  
    #g.bind('ns1', ns1)  
  
    # Parse the ontology  
  
    # Define the relationship 
    ns1_relation = "typeDefinitionOf"
    relationship = ns1[ns1_relation]  
  
    # Find all nodes with the specified relationship  
    nodes = [str(o) for s, p, o in g.triples((node, relationship, None))]  
  
    return nodes

def expand_nodes(G, paths):
    # Find the successors (nodes that the chosen node points to)  
    all_extended = []
    for path in paths:
        node =path[0]
        successors = list(G.successors(node))   
        predecessors = list(G.predecessors(node))  
        all_extended += set(successors + predecessors)
    
    return set (all_extended)

def im_expand_node_by_relation(g, relation, node):
    ns1_uri = "http://opcfoundation.org/UA/"
    ns1 = Namespace(ns1_uri)  
    relationship = ns1[relation]
    ns = [str(o) for s, p, o in g.triples((node, relationship, None))]  
    return ns

def extract_related_nodes(g, specific_node):  
    # Create a graph  
    ns1_uri = "http://opcfoundation.org/UA/"  
    ns1 = Namespace(ns1_uri)  
    ns1_relation_list = ["typeDefinitionOf", "hasProperty", "hasTypeDefinition", "hasComponent"]
   
    # Find all nodes related to the specific node via the specified relationship 
    nodes = []
    for ns1_relation in ns1_relation_list:
        relationship = ns1[ns1_relation]
        ns = [str(o) for s, p, o in g.triples((specific_node, relationship, None))]  
        nodes += ns
  
    return list(set(nodes)) 

def expand_node_relations(g, paths):
    all_extended = []
    for path in paths:
            
        if len(path) > 4:
            node =URIRef(path[0])
            all_extended = extract_related_nodes(g, node)
            node =URIRef(path[-1])
            all_extended += extract_related_nodes(g, node)
        else:
            for n in path:
                node =URIRef(n)
                ext_nodes = extract_related_nodes(g, node)
                if len(ext_nodes) != 0:
                    all_extended += ext_nodes
    return list(set(all_extended))

def expand_node_instances(G, paths):
    all_extended = []
    for path in paths:
        node =path[0]
        instances = get_instances_of_class(G, node)
        if len(instances) != 0:
            all_extended += instances
    return set(all_extended)

def get_instances_of_class(graph, class_node):  
    # Check if the node is a class  
    if 'type' in graph.nodes[class_node]: 
        if graph.nodes[class_node]['type'] == 'owl:Class':  
            # Get the instances of the class  
            instances = list(graph.successors(class_node))  
            return instances  
        else:  
            return [] 
    else:
        return []
 

def expand_im(g, paths):
      
    combined_set_list = list(set(chain(*paths)))
    all_nodes = []
    for node in combined_set_list:
        node = URIRef(node)        
        ty = get_type_of_node(g, node)
        if ty == "instance":
            classes = find_classes(g,node)
            all_nodes += classes
            has_comp_nodes1 = im_expand_node_by_relation(g, "hasComponent", node)
            all_nodes += has_comp_nodes1
            for hc_node in has_comp_nodes1:
                all_nodes += im_expand_node_by_relation(g, "hasComponent", hc_node)
        elif ty == "class":
            has_comp_nodes1 = im_expand_node_by_relation(g, "hasComponent", node)
            all_nodes += has_comp_nodes1
            for hc_node in has_comp_nodes1:
                all_nodes += im_expand_node_by_relation(g, "hasComponent", hc_node)
            instances = find_instances(g,node)
            all_nodes += instances
            subclasses = find_subclasses(g, node)
            all_nodes += subclasses
            
    return list(set(all_nodes))
            

def find_subclasses(g, node):
    subclasses = []  
    node = URIRef(node)  
    RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema/") 
    for subclass in g.subjects(RDFS.subClassOf, node):  
        subclasses.append(subclass)  
      
    return subclasses  

def find_classes(g, node):  
    OWL = Namespace("http://www.w3.org/2002/07/owl/")    
    
    # Define the node you are interested in  
    node = node  
    classes = []
    # If the node is a NamedIndividual, find its classes  
    for _, _, o in g.triples((node, RDF.type, None)):  
        if o != OWL.NamedIndividual:  # Exclude the NamedIndividual type itself  
            classes.append(o)

    return classes  

def find_instances(g, node):
    OWL = Namespace("http://www.w3.org/2002/07/owl/")  
  
    node = node
    instances = []
    # If the node is a class, find its instances  
    if (node, RDF.type, OWL.Class) in g:  
        for s, _, _ in g.triples((None, RDF.type, node)):  
            instances.append(s)
    return instances

def get_type_of_node(g, node):
    OWL = Namespace("http://www.w3.org/2002/07/owl/")    
  
    # Check the type of the node  
    if (node, RDF.type, OWL.Class) in g:  
        return "class" 
    elif (node, RDF.type, OWL.NamedIndividual) in g:  
        return "instance"
    else:  
        return "none"

def get_all_shortest_paths_all_nodes_information_model_constraints(G, g, nodes):
    paths = all_paths_shortest_all_nodes(G, nodes) 
    if len(paths) == 0 or len(paths) == 1:
        n_path = [nodes]
        ext_nodes = expand_im(g, n_path)
        ext_nodes += nodes
    else:
        ext_nodes = expand_im(g,paths)
        ext_nodes += nodes
    paths_w_e = paths_with_edges(G, paths)
    paths_w_e_flattened_list = [item for sublist in paths_w_e for item in sublist] 
    return paths_w_e_flattened_list, ext_nodes

def get_all_shortest_paths_all_nodes(G, g, nodes):
    paths = all_paths_shortest_all_nodes(G, nodes) 

    if len(paths) == 0:
         # The above code is a Python script that uses the `print()` function to output a message.
         # However, the message is not provided in the code snippet, as it is represented by the
         # comment symbol `#`. The code snippet seems to be incomplete or missing the actual message
         # to be printed.
         print("no path found")
         ext_nodes = expand_node_relations(g,[nodes])
         ext_nodes += expand_im(g, [nodes])
         ext_nodes += nodes
         ext_nodes = list(set(ext_nodes))
         
    #ext_paths = expand_nodes(G,paths)
    
    else:
        ext_nodes = expand_node_relations(g,paths)
        ext_nodes += expand_im(g, paths)
        ext_nodes = list(set(ext_nodes))
    if len(paths) == 0:
        return paths, ext_nodes
    if len(paths[0]) == 1:
        return paths, ext_nodes
    paths_w_e = paths_with_edges(G, paths)  
    
    paths_w_e_flattened_list = [item for sublist in paths_w_e for item in sublist]  
    return paths_w_e_flattened_list, ext_nodes

def get_relation_nodes(G, paths):
    relation_nodes = []
    for path in paths:
        for i in range(len(path)-1):
            rel_dict = G.get_edge_data(path[i], path[i+1])
            for k, v in rel_dict.items():
               relation_nodes.append(v)             
    return list(set(relation_nodes))

def get_all_shortest_paths_all_nodes_smaller(G, g, nodes):
    #first and last nodes expanded

    paths = all_paths_shortest_all_nodes(G, nodes) 

    if len(paths) == 0:
         print("no path found")
         ext_nodes = expand_node_relations(g,[nodes])
         ext_nodes += nodes
         ext_nodes = list(set(ext_nodes))
         
    #ext_paths = expand_nodes(G,paths)
    else:
        ext_nodes = expand_node_relations(g,paths)
    if len(paths) == 0:
        return paths, ext_nodes, relation_nodes
    if len(paths[0]) == 1:
        return paths, ext_nodes, relation_nodes
    paths_w_e = paths_with_edges(G, paths)  
    

    paths_w_e_flattened_list = [item for sublist in paths_w_e for item in sublist]  

    return paths_w_e_flattened_list, ext_nodes, relation_nodes

def get_all_shortest_paths_all_nodes_small(G, g, nodes):

    paths = all_paths_shortest_all_nodes(G, nodes) 
    relation_nodes = get_relation_nodes(G, paths)

    if len(paths) == 0:
         print("no path found")
         ext_nodes = expand_node_relations(g,[nodes])
         ext_nodes += nodes
         ext_nodes = list(set(ext_nodes))
         
    else:
        ext_nodes = expand_node_relations(g,paths)
    if len(paths) == 0:
        return paths, ext_nodes, relation_nodes
    if len(paths[0]) == 1:
        return paths, ext_nodes, relation_nodes
    paths_w_e = paths_with_edges(G, paths)  
    

    paths_w_e_flattened_list = [item for sublist in paths_w_e for item in sublist]  
    return paths_w_e_flattened_list, ext_nodes, relation_nodes

def get_all_shortest_paths_all_nodes_v2(G, nodes):

    paths = all_paths_shortest_all_nodes(G, nodes)  
    if paths == None:
        return []
    if len(paths) == 1:
        return paths
    paths_w_e = paths_with_edges(G, paths)  

    paths_w_e_flattened_list = [item for sublist in paths_w_e for item in sublist]  
    return paths_w_e_flattened_list 

def get_all_paths_all_nodes(G, nodes):

    paths = find_all_paths_astar_all_nodes(nodes, G)  
    if paths == None:
        return []
    paths_w_e = paths_with_edges(G, paths)  
    
    paths_w_e_flattened_list = [item for sublist in paths_w_e for item in sublist]  
    return paths_w_e_flattened_list  

def get_path_all_nodes(G, nodes):

    path = find_path_astar_all_nodes(nodes, G)  
    if path == None:
       
        return []
    path_w_e = path_with_edges(G, path)  

    return path_w_e 


def save(G, output_file):
    g = Graph()
    g.parse(output_file)  
    for edge in G.edges(data=True):  
        node1 = URIRef(edge[0])  
        node2 = URIRef(edge[1])  
        edge_name = Literal(edge[2]['name'])  
        g.add((node1, edge_name, node2))  
  
    g.serialize(destination=output_file, format='turtle')  

def generate_new_graph(g, path_with_edges):
    node_graph = Graph()

    prefixes = {}
    for prefix, namespace in g.namespaces():  
        prefixes[prefix] = Namespace(namespace)
        node_graph.bind(prefix,Namespace(namespace))
    
    for p in path_with_edges: 

        if len(p) == 1:
            node1 = URIRef(p[0]) 
            node_graph = add_node(node1, g, node_graph) 
        else:
            edge_name = Literal(p[2])
            node_graph = add_node(edge_name, g, node_graph)  
            node1 = URIRef(p[0]) 
            node_graph = add_node(node1, g, node_graph) 
            node2 = URIRef(p[1])
            node_graph = add_node(node2, g, node_graph) 
        
    return node_graph

def node_graph_addition(node1, g, node_graph, rel_nodes):
    triples = []
    triples += list(g.triples((node1, rdflib.term.URIRef("http://opcfoundation.org/UA/Meta/TA/browseName"), None)))
    triples += list(g.triples((node1, rdflib.term.URIRef("http://opcfoundation.org/UA/Meta/IA/browseName"), None)))
    triples += list(g.triples((node1, rdflib.term.URIRef("http://opcfoundation.org/UA/Meta/TA/value"), None)))
    triples += list(g.triples((node1, rdflib.term.URIRef("http://opcfoundation.org/UA/Meta/IA/value"), None)))
    triples += list(g.triples((node1, rdflib.term.URIRef("http://opcfoundation.org/UA/value"), None)))
    triples += list(g.triples((node1, rdflib.term.URIRef("http://www.w3.org/2000/01/rdf-schema/label"), None)))
    triples += list(g.triples((node1, "a", None)))
    triples += list(g.triples((node1, RDF.type, None)))
    triples += list(g.triples((node1, RDFS.label, None)))
    ns1_uri = "http://opcfoundation.org/UA/"  
    ns1 = Namespace(ns1_uri)  
    ns1_relation_list = ["typeDefinitionOf", "hasProperty", "hasTypeDefinition", "hasComponent"]
    ns1_relation_list += rel_nodes
    for ns1_relation in ns1_relation_list:
        relationship = ns1[ns1_relation]
        triples += list(g.triples((node1, relationship, None)))        
    for triple in triples:  
        node_graph.add(triple)
    
    return node_graph

def generate_new_graph_smaller(g, path_with_edges, ext_nodes, rel_nodes):
    node_graph = Graph()

    prefixes = {}
    for prefix, namespace in g.namespaces():  
        prefixes[prefix] = Namespace(namespace)
        node_graph.bind(prefix,Namespace(namespace))
    
    for p in path_with_edges: 
        triples = []
        if len(p) == 1:
            node1 = URIRef(p[0]) 
            node_graph = add_node(node1, g, node_graph) 
        else:
            edge_name = URIRef(p[2])
            node_graph = node_graph_addition(edge_name, g, node_graph, rel_nodes)  
            node1 = URIRef(p[0]) 
            node_graph = node_graph_addition(node1, g, node_graph, rel_nodes)
            node2 = URIRef(p[1])
            node_graph = node_graph_addition(node2, g, node_graph, rel_nodes)
        for triple in triples:  
            node_graph.add(triple)  

    for ext_node in ext_nodes:
        node1 = URIRef(ext_node) 
        node_graph = node_graph_addition(node1, g, node_graph, rel_nodes)
        
    return node_graph

def generate_new_graph_small(g, path_with_edges, ext_nodes, rel_nodes):
    node_graph = Graph()

    prefixes = {}
    for prefix, namespace in g.namespaces():  
        prefixes[prefix] = Namespace(namespace)
        node_graph.bind(prefix,Namespace(namespace))
    
    for p in path_with_edges: 
        triples = []
        if len(p) == 1:
            node1 = URIRef(p[0]) 
            node_graph = add_node(node1, g, node_graph) 
        else:
            edge_name = URIRef(p[2])
            node_graph = node_graph_addition(edge_name, g, node_graph, rel_nodes)  
            node1 = URIRef(p[0]) 
            node_graph = add_node(node1, g, node_graph)
            #node_graph = node_graph_addition(node1, g, node_graph, rel_nodes)
            node2 = URIRef(p[1])
            node_graph = add_node(node2, g, node_graph)
            #node_graph = node_graph_addition(node2, g, node_graph, rel_nodes)
        for triple in triples:  
            node_graph.add(triple)  

    for ext_node in ext_nodes:
        node1 = URIRef(ext_node) 
        node_graph = node_graph_addition(node1, g, node_graph, rel_nodes)
        
    return node_graph

def post_process_combine_with_namespaces(subgraph_ttl):
    graph1 = Graph()
    graph1.parse(subgraph_ttl, format="turtle")  # Another TTL file or dynamically populated graph

    # Create another RDF graph
    graph2 = Graph()
    graph2.parse("opc-ua-copilot/query_generation/requiredNodes.ttl", format="turtle")  # Another TTL file or dynamically populated graph

    # Combine the graphs
    combined = graph1 + graph2

    # Bind namespaces
    combined.bind("owl", "http://www.w3.org/2002/07/owl#")
    combined.bind("xsd", "http://www.w3.org/2001/XMLSchema#")
    combined.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    combined.bind("NS0", "http://opcfoundation.org/UA/")
    combined.bind("NS2", "http://opcfoundation.org/UA/Robotics/")
    combined.bind("ta", "http://opcfoundation.org/UA/Meta/TA/")
    combined.bind("NS1", "http://opcfoundation.org/UA/XML/")
    combined.bind("NS4", "http://siemens.com/robot/demo/")
    combined.bind("NS3", "http://opcfoundation.org/UA/DI/")
    combined.bind("dt", "http://opcfoundation.org/UA/Meta/Types/")
    combined.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    combined.bind("me", "http://opcfoundation.org/UA/Meta/")
    combined.bind("ia", "http://opcfoundation.org/UA/Meta/IA/")
    return combined

def generate_new_graph_im(g, path_with_edges, ext_nodes):
    
    G_original, g_original = get_graph_from_ttl(IM_OUTPUT_FOLDER + INPUT_KG_FILE)
    

    query = """
    CONSTRUCT {
    ?subject ?predicate ?object .
    ?object ?predicate2 ?object2 .
    }
    WHERE {
    {
        ?subject ?predicate ?object .
        FILTER (?subject IN ({nodes}))
    }
    UNION
    {
        ?subject ?predicate ?object .
        ?object ?predicate2 ?object2 .
        FILTER ((?subject IN ({nodes})) && isBlank(?object))
    }
    }
    """

    # Node array'ini SPARQL formatına dönüştür
    nodes_sparql = ", ".join(f"<{node}>" for node in ext_nodes)
    query = query.replace("{nodes}", nodes_sparql)

    # Sorguyu çalıştır
    result = g_original.query(query)
        
    return result

def generate_new_graph_im_old(g, path_with_edges, ext_nodes):
    
    G_original, g_original = get_graph_from_ttl(IM_OUTPUT_FOLDER + INPUT_KG_FILE)
    
    node_graph = Graph()

    prefixes = {}
    for prefix, namespace in g_original.namespaces():  
        prefixes[prefix] = Namespace(namespace)
        node_graph.bind(prefix,Namespace(namespace))
    
    for p in path_with_edges: 

        if len(p) == 1:
            node1 = URIRef(p[0]) 
            node_graph = add_node(node1, g_original, node_graph) 
        else:
            edge_name = Literal(p[2])
            node_graph = add_node(edge_name, g_original, node_graph)  
            node1 = URIRef(p[0]) 
            node_graph = add_node(node1, g_original, node_graph) 
            node2 = URIRef(p[1])
            node_graph = add_node(node2, g_original, node_graph)

    for ext_node in ext_nodes:
        node1 = URIRef(ext_node) 
        node_graph = add_node(node1, g_original, node_graph) 
        
    return node_graph

def generate_new_graph(g, path_with_edges, ext_nodes):
    node_graph = Graph()

    prefixes = {}
    for prefix, namespace in g.namespaces():  
        prefixes[prefix] = Namespace(namespace)
        node_graph.bind(prefix,Namespace(namespace))
    
    for p in path_with_edges: 

        if len(p) == 1:
            node1 = URIRef(p[0]) 
            node_graph = add_node(node1, g, node_graph) 
        else:
            edge_name = Literal(p[2])
            node_graph = add_node(edge_name, g, node_graph)  
            node1 = URIRef(p[0]) 
            node_graph = add_node(node1, g, node_graph) 
            node2 = URIRef(p[1])
            node_graph = add_node(node2, g, node_graph)

    for ext_node in ext_nodes:
        node1 = URIRef(ext_node) 
        node_graph = add_node(node1, g, node_graph) 
           
    return node_graph

def add_node(node_uri, g, node_graph):

    node_data = g.triples((node_uri, None, None))
    for s, p, o in node_data: 
        node_graph.add((s, p, o)) 
    return node_graph

def save_graph(node_graph, output_file):
    node_graph.serialize(destination=output_file, format='turtle') 

def rag(ttl_file, source, target, output_file):
    G,g = get_graph_from_ttl(ttl_file)
    path_with_edges = get_path(G, source, target)
    node_graph = generate_new_graph(g, path_with_edges)
    save_graph(node_graph, output_file)

def rag_all_shortest_paths(ttl_file, source, target, output_file):
    G,g = get_graph_from_ttl(ttl_file)
    paths_with_edges = get_all_shortest_paths(G, source, target)
    node_graph = generate_new_graph(g, paths_with_edges)
    save_graph(node_graph, output_file)

#smaller
def rag_all_shortest_paths_all_nodes_smaller(ttl_file, nodes, output_file):
    G,g = get_graph_from_ttl(ttl_file)
    paths_with_edges, ext_nodes, rel_nodes = get_all_shortest_paths_all_nodes_small(G, g, nodes)
    node_graph = generate_new_graph_smaller(g, paths_with_edges, ext_nodes, rel_nodes)
    save_graph(node_graph, output_file)

#small
def rag_all_shortest_paths_all_nodes_small(ttl_file, nodes, output_file):
    G,g = get_graph_from_ttl(ttl_file)
    paths_with_edges, ext_nodes, rel_nodes = get_all_shortest_paths_all_nodes_small(G, g, nodes)
    node_graph = generate_new_graph_small(g, paths_with_edges, ext_nodes, rel_nodes)
    save_graph(node_graph, output_file)
#org
def rag_all_shortest_paths_all_nodes(ttl_file, nodes, output_file):
    G,g = get_graph_from_ttl(ttl_file)
    paths_with_edges, ext_nodes = get_all_shortest_paths_all_nodes(G, g, nodes)
    node_graph = generate_new_graph(g, paths_with_edges, ext_nodes)
    save_graph(node_graph, output_file)
    
#information model constraints
def rag_all_shortest_paths_all_nodes_information_model_constraints(ttl_file, nodes, output_file):
    G,g = get_graph_from_ttl(ttl_file)
    paths_with_edges, ext_nodes = get_all_shortest_paths_all_nodes_information_model_constraints(G, g, nodes)
    node_graph = generate_new_graph_im(g, paths_with_edges, ext_nodes)
    save_graph(node_graph, IM_OUTPUT_FOLDER + SUB_GRAPH_FILE)
    node_graph_combined = post_process_combine_with_namespaces(IM_OUTPUT_FOLDER + SUB_GRAPH_FILE)
    save_graph(node_graph_combined, IM_OUTPUT_FOLDER + COMBINED_SUB_GRAPH_FILE)

def rag_all_nodes_astar(ttl_file, nodes, output_file):
    G,g = get_graph_from_ttl(ttl_file)
    path_with_edges = get_path_all_nodes(G, nodes)
    node_graph = generate_new_graph(g, path_with_edges)
    save_graph(node_graph, output_file)

def rag_all_nodes_astar_all_paths(ttl_file, nodes, output_file):
    G,g = get_graph_from_ttl(ttl_file)
    path_with_edges = get_all_paths_all_nodes(G, nodes)
    node_graph = generate_new_graph(g, path_with_edges)
    save_graph(node_graph, output_file)
    
def rag_bi(ttl_file, source, target, output_file):
    G,g = get_graph_from_ttl(ttl_file)
    path_with_edges = get_path(G, source, target)
    path_with_edges_reverse = get_path(G, target, source)
    path_with_edges = path_with_edges + path_with_edges_reverse
    node_graph = generate_new_graph(g, path_with_edges)
    save_graph(node_graph, output_file)
