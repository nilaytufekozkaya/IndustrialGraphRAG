
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import csv
import argparse
from typing import List, Tuple, Dict, Any

from rdflib import Graph, RDF, RDFS, OWL, XSD, URIRef, Literal, BNode

# ---- Optional LLM backends ----
USE_LLAMAINDEX = True  # set True to use llama_index.llms.openai.OpenAI if you prefer

def _init_llm(model: str, temperature: float = 0.0):
    if USE_LLAMAINDEX:
        try:
            from llama_index.llms.openai import OpenAI as LI_OpenAI
        except Exception as e:
            raise RuntimeError("Install llama-index-llms-openai or set USE_LLAMAINDEX=False") from e
        return LI_OpenAI(model=model, temperature=temperature)
    else:
        try:
            from openai import OpenAI
        except Exception as e:
            raise RuntimeError("Install openai>=1.0: pip install -U openai") from e
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Please set OPENAI_API_KEY environment variable")
        client = OpenAI(api_key=api_key)
        return client

def _llm_complete(llm, prompt: str) -> str:
    if USE_LLAMAINDEX:
        # llama-index wrapper
        resp = llm.complete(prompt)
        return resp.text
    else:
        # official OpenAI SDK
        comp = llm.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL_OVERRIDE", "gpt-4o"),
            messages=[
                {"role":"system","content":"You are a careful SPARQL generator over RDF graphs."},
                {"role":"user","content":prompt}
            ],
            temperature=0
        )
        return comp.choices[0].message.content

# ---- Utility ----
def tokens(text: str) -> List[str]:
    return [t for t in re.split(r"[^a-z0-9_]+", text.lower()) if t]

def jaccard(a: List[str], b: List[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 0.0
    return len(sa & sb) / max(1, len(sa | sb))

def qstr(g: Graph, term) -> str:
    try:
        if isinstance(term, (URIRef, BNode, Literal)):
            return g.namespace_manager.normalizeUri(term) if isinstance(term, URIRef) else str(term)
        return str(term)
    except Exception:
        return str(term)

# ---- Build graph-aware context ----
def build_context(g: Graph, nlq: str, k_triples: int = 60, k_schema: int = 40) -> str:
    qtok = tokens(nlq)

    triples_scored: List[Tuple[float,str]] = []
    for s, p, o in g:
        line = f"{qstr(g,s)} {qstr(g,p)} {qstr(g,o)}"
        score = jaccard(tokens(line), qtok)
        if score > 0:
            triples_scored.append((score, line))
    triples_scored.sort(key=lambda x: x[0], reverse=True)
    top_triples = [t for _, t in triples_scored[:k_triples]]

    # schema hints: classes and properties
    classes = set(g.subjects(RDF.type, OWL.Class)) | set(g.subjects(RDF.type, RDFS.Class))
    objprops = set(g.subjects(RDF.type, OWL.ObjectProperty))
    dtprops  = set(g.subjects(RDF.type, OWL.DatatypeProperty))
    annprops = set(g.subjects(RDF.type, OWL.AnnotationProperty))

    def label_of(u):
        for lbl in g.objects(u, RDFS.label):
            return str(lbl)
        return ""

    def score_uri(u):
        return jaccard(tokens(str(u)+" "+label_of(u)), qtok)

    cls_scored = sorted([(score_uri(c), f"CLASS {qstr(g,c)} label:{label_of(c)}") for c in classes], reverse=True)
    op_scored  = sorted([(score_uri(p), f"OPROP {qstr(g,p)} label:{label_of(p)}") for p in objprops], reverse=True)
    dp_scored  = sorted([(score_uri(p), f"DTPROP {qstr(g,p)} label:{label_of(p)}") for p in dtprops],  reverse=True)
    ap_scored  = sorted([(score_uri(p), f"ANNPROP {qstr(g,p)} label:{label_of(p)}") for p in annprops], reverse=True)

    top_schema = []
    top_schema += [s for sc,s in cls_scored if sc>0][:k_schema//2]
    top_schema += [s for sc,s in (op_scored+dp_scored+ap_scored) if sc>0][:k_schema//2]

    ctx = []
    ctx.append("# --- Top triples relevant to NLQ ---")
    ctx += top_triples if top_triples else ["# (no triple hits by keyword)"]
    ctx.append("# --- Schema hints (classes & properties) ---")
    ctx += top_schema if top_schema else ["# (no schema hits by keyword)"]
    return "\n".join(ctx)



def extract_sparql(text: str) -> str:
    m = re.search(r"```sparql\s+(.*?)```", text, flags=re.S|re.I)
    if m:
        return m.group(1).strip()
    m2 = re.search(r"(ASK\\s*\\{.*\\})", text, flags=re.S|re.I)
    if m2:
        return m2.group(1).strip()
    # SELECT fallback
    m3 = re.search(r"(SELECT\\s+.*?\\})", text, flags=re.S|re.I)
    return m3.group(1).strip() if m3 else ""

# ---- Run SPARQL over RDFLib ----
def run_sparql(g: Graph, sparql: str) -> Tuple[str, Any]:
    q = sparql.strip()
    is_ask = q.upper().lstrip().startswith("ASK")
    res = g.query(q)
    if is_ask:
        return ("ASK", bool(res))
    # SELECT
    headers = res.vars
    rows = [[str(v) if v is not None else "" for v in r] for r in res]
    return ("SELECT", (headers, rows))

def save_csv(headers, rows, out_path: str):
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([str(h) for h in headers])
        for r in rows:
            w.writerow(r)
            
            
import pandas as pd
def read_nlqs(nlq_file):
    df = pd.read_excel(nlq_file)
    return df

def save_queries(df, queries):
    # Yeni kolon(lar) ekle
    df["generated queries node2vec"] = queries

    # Yeni dosyaya kaydet
    df.to_excel("../outputs/llamaindex_saref.xlsx", index=False)

def run_batch(ttl_path, nlq_file):
    # 1) Load TTL
    g = Graph()
    g.parse(ttl_path, format="turtle")
    model = "gpt-4o"
    mode = "select"

    # 2) Build context
    
    df = read_nlqs(nlq_file)
    nlq_list = df["NLQ"].tolist()
    queries = []
    for nlq in nlq_list:
    
        context = build_context(g, nlq, k_triples=60, k_schema=40)

        # 3) LLM
        llm = _init_llm(model=model)

        # 4) Compose prompt
        prompt = generate_prompt(nlq, context)
        if mode == "ask":
            prompt = prompt.replace("If the NLQ is a boolean claim, prefer an ASK query; otherwise SELECT.",
                                    "Always produce an ASK query (boolean).")
        elif mode == "select":
            prompt = prompt.replace("If the NLQ is a boolean claim, prefer an ASK query; otherwise SELECT.",
                                    "Always produce a SELECT query (tabular).")

        # 5) Generate SPARQL
        text = _llm_complete(llm, prompt)
        sparql = extract_sparql(text)
        if not sparql:
            print("Failed to extract SPARQL from LLM output:\n", text)
            sys.exit(3)

        #print("=== GENERATED SPARQL ===")
        #print(sparql)
        queries.append(sparql)
    print(queries)
    save_queries(df, queries)



def generate_prompt(nlq, context):
    input_path = "rag_template.txt"

    # read file
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    # replace placeholder
    text = text.replace("{SCHEMA}", context)
    text = text.replace("{NLQ}", nlq)
    prompt = text.replace("{QT}", "SELECT")

    print("prompt:", prompt)
    return prompt

        
        
def run(ttl_path, nlq):
    # 1) Load TTL
    g = Graph()
    g.parse(ttl_path, format="turtle")
    model = "gpt-4o"
    mode = "select"

    # 2) Build context
    context = build_context(g, nlq, k_triples=60, k_schema=40)

    # 3) LLM
    llm = _init_llm(model=model)

    # 4) Compose prompt
    prompt = generate_prompt(nlq, context)
    if mode == "ask":
        prompt = prompt.replace("If the NLQ is a boolean claim, prefer an ASK query; otherwise SELECT.",
                                "Always produce an ASK query (boolean).")
    elif mode == "select":
        prompt = prompt.replace("If the NLQ is a boolean claim, prefer an ASK query; otherwise SELECT.",
                                "Always produce a SELECT query (tabular).")

    # 5) Generate SPARQL
    text = _llm_complete(llm, prompt)
    sparql_query = extract_sparql(text)
    if not sparql_query:
        print("Failed to extract SPARQL from LLM output:\n", text)
        sys.exit(3)
    return sparql_query


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Industrial Graph RAG")

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
    
    
# python llamaindex.py --ttl_file "../inputs/saref_large.ttl" --nlq "what is the instance of the temperature sensor?"
