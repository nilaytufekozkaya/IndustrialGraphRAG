import networkx as nx
from rdflib import Graph, URIRef
from node2vec import Node2Vec
import numpy as np
from langchain_openai import OpenAIEmbeddings
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from sklearn.metrics.pairwise import cosine_similarity
import argparse

def read_graph(ttl_path):
    
    g = Graph().parse(ttl_path, format="turtle")

    G = nx.DiGraph()
    for s, p, o in g:
        if isinstance(s, URIRef) and isinstance(o, URIRef):
            G.add_edge(str(s), str(o), predicate=str(p))

    return G, g

def node2vec_embedding(G):
    node2vec = Node2Vec(G, dimensions=64, walk_length=10, num_walks=80, workers=1)
    model = node2vec.fit(window=5, min_count=1, batch_words=4)

    node_embeddings = {node: model.wv[node] for node in G.nodes()}

    return node_embeddings

def nlq_embeddings(nlq):

    # 3) NLQ embedding
    emb = OpenAIEmbeddings()
    nlq_vec = emb.embed_query(nlq)
    return nlq_vec

def most_similar_nodes(query_vec, node_embeds, top_k=5):
    names = list(node_embeds.keys())
    X = np.array([node_embeds[n] for n in names])

    qv = np.array(query_vec)
    if qv.shape[0] > X.shape[1]:
        qv = qv[:X.shape[1]]  
    elif qv.shape[0] < X.shape[1]:
        qv = np.pad(qv, (0, X.shape[1] - qv.shape[0])) 

    sims = cosine_similarity([qv], X)[0]
    top_idx = np.argsort(sims)[::-1][:top_k]
    return [(names[i], float(sims[i])) for i in top_idx]

def find_nearest_nodes(nlq_vec, node_embeddings):
    nearest = most_similar_nodes(nlq_vec, node_embeddings)
    print("\n=== Nearest nodes ===")
    for n, s in nearest:
        print(f"{n} ({s:.3f})")
    return nearest

def build_context(nearest,g ):
    context_triples = []
    for node, _ in nearest:
        for s, p, o in g.triples((URIRef(node), None, None)):
            context_triples.append(f"{s} {p} {o}")
        for s, p, o in g.triples((None, None, URIRef(node))):
            context_triples.append(f"{s} {p} {o}")
    context = "\n".join(context_triples[:20])

    return context

def run_llm(context, nlq):


    # file paths
    input_path = "rag_template.txt"

    # read file
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    # replace placeholder
    text = text.replace("{SCHEMA}", context)
    text = text.replace("{NLQ}", nlq)
    prompt = text.replace("{QT}", "SELECT")

    #print("prompt:", prompt)

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    query = llm.invoke([SystemMessage(content="Generate only valid full SPARQL (SELECT form)."),
                        HumanMessage(content=prompt)]).content.strip()

    #print(query)
    return query

def run_query(query,g):
    try:
        res = g.query(query)
        print("\nResult:", bool(res.askAnswer))
    except Exception as e:
        print("SPARQL failed:", e)
        

import pandas as pd
def read_nlqs(nlq_file):
    df = pd.read_excel(nlq_file)
    return df

def save_queries(df, queries):
    df["generated queries node2vec"] = queries

    df.to_excel("../outputs/node2vec_combined_mixed.xlsx", index=False)
    print("written!")
        
def run_batch(ttl_path, nlq_file):
    G, g = read_graph(ttl_path)
    node_embeddings = node2vec_embedding(G)
    queries = []
    results = []
    
    df = read_nlqs(nlq_file)
    nlq_list = df["NLQ"].tolist()
    for nlq in nlq_list:
        nlq_vec = nlq_embeddings(nlq)
        nearest = find_nearest_nodes(nlq_vec, node_embeddings)
        context = build_context(nearest, g)
        sparql_query = run_llm(context, nlq)
        #res = run_query(sparql_query)
        
        queries.append(sparql_query)
        
    save_queries(df, queries)
        
        
def run(ttl_path, nlq):
    G, g = read_graph(ttl_path)
    node_embeddings = node2vec_embedding(G)

    nlq_vec = nlq_embeddings(nlq)
    nearest = find_nearest_nodes(nlq_vec, node_embeddings)
    context = build_context(nearest, g)
    sparql_query = run_llm(context, nlq)

    return sparql_query
    
    
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Node2Vec RAG")

    parser.add_argument(
        "--ttl_file",
        type=str,
        required=True,
        help="TTL knowledge graph file"
    )

    parser.add_argument(
        "--nlq",
        type=str,
        required=True,
        help="Path to the NLQ input"
    )

    args = parser.parse_args()

    sparql_query = run(args.ttl_file, args.nlq)
    print(sparql_query)
    
    #ttl_path = "../inputs/saref/saref_large.ttl"
    #nlq_file = "../inputs/saref/competency_question.xlsx"
    #run_batch(ttl_path, nlq_file)
    
    
# python node2vec_rag.py --ttl_file "../inputs/saref/saref_large.ttl" --nlq "what is the instance of the temperature sensor?"
    
        
    