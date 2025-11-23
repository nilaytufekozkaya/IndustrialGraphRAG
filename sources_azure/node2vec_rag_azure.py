import os
import argparse
import networkx as nx
from rdflib import Graph, URIRef
from node2vec import Node2Vec
import numpy as np
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


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
    # Load environment variables from the specified .env file  
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    env_base = os.path.join(BASE_DIR, ".env") 
    load_dotenv(dotenv_path=env_base, override=True)  

    emb = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )
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


def build_context(nearest, g):
    context_triples = []
    for node, _ in nearest:
        for s, p, o in g.triples((URIRef(node), None, None)):
            context_triples.append(f"{s} {p} {o}")
        for s, p, o in g.triples((None, None, URIRef(node))):
            context_triples.append(f"{s} {p} {o}")
    context = "\n".join(context_triples[:20])
    return context


def run_llm(context, nlq):

    input_path = "rag_template.txt"

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    text = text.replace("{SCHEMA}", context)
    text = text.replace("{NLQ}", nlq)
    prompt = text.replace("{QT}", "SELECT")

    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        temperature=0,
    )

    query = llm.invoke(
        [
            SystemMessage(content="Generate only valid full SPARQL (SELECT form)."),
            HumanMessage(content=prompt),
        ]
    ).content.strip()

    return query


def run_query(query, g):
    try:
        res = g.query(query)
        print("\nQuery executed, number of rows:", len(list(res)))
    except Exception as e:
        print("SPARQL failed:", e)


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

    df = read_nlqs(nlq_file)
    nlq_list = df["NLQ"].tolist()

    for nlq in nlq_list:
        nlq_vec = nlq_embeddings(nlq)
        nearest = find_nearest_nodes(nlq_vec, node_embeddings)
        context = build_context(nearest, g)
        sparql_query = run_llm(context, nlq)
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
    parser = argparse.ArgumentParser(description="Node2Vec RAG (Azure OpenAI)")

    parser.add_argument(
        "--ttl_file",
        type=str,
        required=True,
        help="TTL knowledge graph file",
    )

    parser.add_argument(
        "--nlq",
        type=str,
        required=True,
        help="NLQ input string",
    )

    args = parser.parse_args()

    sparql_query = run(args.ttl_file, args.nlq)
    print(sparql_query)

    # python node2vec_rag_azure.py --ttl_file "../inputs/saref/saref_large.ttl" --nlq "what is the instance of the temperature sensor?"
