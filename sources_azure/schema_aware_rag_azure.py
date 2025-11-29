#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import argparse
from typing import List, Tuple, Any
from dotenv import load_dotenv
from rdflib import Graph, RDF, RDFS, OWL, URIRef, Literal, BNode

USE_LLAMAINDEX = False  # Azure kullanacağımız için False

# ============================================================
#   Azure OpenAI — init
# ============================================================

def _init_llm(model: str, temperature: float = 0.0):
    # Load environment variables from the specified .env file  
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    env_base = os.path.join(BASE_DIR, ".env") 
    load_dotenv(dotenv_path=env_base, override=True)  

    # Fetch the API key, endpoint, API version, and deployment name from the environment variables  
    
    if USE_LLAMAINDEX:
        # Optional llama-index Azure wrapper (KULLANMIYORUZ)
        try:
            from llama_index.llms.azure_openai import AzureOpenAI as LI_AzureOpenAI
        except Exception as e:
            raise RuntimeError("Install llama-index-llms-azure-openai or set USE_LLAMAINDEX=False") from e

        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
        deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", model)

        return LI_AzureOpenAI(
            model=model,
            deployment_name=deployment,
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version,
            temperature=temperature,
        )

    else:
        # Resmi OpenAI SDK — Azure sürümü
        try:
            from openai import AzureOpenAI
        except Exception as e:
            raise RuntimeError("Install openai>=1.0: pip install -U openai") from e

        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        api_version = os.environ.get("AZURE_OPENAI_API_VERSION")

        if not endpoint or not api_key:
            raise RuntimeError("Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY")

        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        return client


# ============================================================
#   Azure OpenAI — Completion
# ============================================================

def _llm_complete(llm, prompt: str) -> str:
    if USE_LLAMAINDEX:
        resp = llm.complete(prompt)
        return resp.text
    else:
        deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
        if not deployment:
            raise RuntimeError("Please set AZURE_OPENAI_DEPLOYMENT_NAME")

        comp = llm.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are a careful SPARQL generator over RDF graphs."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        return comp.choices[0].message.content


# ============================================================
#   Utilities
# ============================================================

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


# ============================================================
#   Build graph context
# ============================================================

def build_context(g: Graph, nlq: str, k_triples: int = 60, k_schema: int = 40) -> str:
    qtok = tokens(nlq)

    triples_scored = []
    for s, p, o in g:
        line = f"{qstr(g,s)} {qstr(g,p)} {qstr(g,o)}"
        score = jaccard(tokens(line), qtok)
        if score > 0:
            triples_scored.append((score, line))

    triples_scored.sort(key=lambda x: x[0], reverse=True)
    top_triples = [t for _, t in triples_scored[:k_triples]]

    # schema
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


# ============================================================
#   SPARQL extraction
# ============================================================

def extract_sparql(text: str) -> str:
    m = re.search(r"```sparql\s+(.*?)```", text, flags=re.S|re.I)
    if m:
        return m.group(1).strip()

    m2 = re.search(r"(ASK\s*\{.*?\})", text, flags=re.S|re.I)
    if m2:
        return m2.group(1).strip()

    m3 = re.search(r"(SELECT\s+.*?\})", text, flags=re.S|re.I)
    if m3:
        return m3.group(1).strip()

    return ""


# ============================================================
#   Prompt
# ============================================================

def generate_prompt(nlq, context):
    with open("rag_template.txt", "r", encoding="utf-8") as f:
        text = f.read()
    text = text.replace("{SCHEMA}", context)
    text = text.replace("{NLQ}", nlq)
    prompt = text.replace("{QT}", "SELECT")
    return prompt


# ============================================================
#   Main SPARQL generation
# ============================================================

def run(ttl_path, nlq):
    g = Graph()
    g.parse(ttl_path, format="turtle")

    context = build_context(g, nlq)
    print("---")
    print(context)
    llm = _init_llm(model="gpt-4o")

    prompt = generate_prompt(nlq, context)
    prompt = prompt.replace(
        "If the NLQ is a boolean claim, prefer an ASK query; otherwise SELECT.",
        "Always produce a SELECT query (tabular)."
    )

    text = _llm_complete(llm, prompt)
    sparql_query = extract_sparql(text)
    if not sparql_query:
        print("Failed to extract SPARQL:\n", text)
        sys.exit(3)

    return sparql_query


# ============================================================
#   CLI
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Azure OpenAI SPARQL Generator")
    parser.add_argument("--ttl_file", type=str, required=True, help="TTL knowledge graph file")
    parser.add_argument("--nlq", type=str, required=True, help="Natural language question")
    args = parser.parse_args()

    sparql_query = run(args.ttl_file, args.nlq)
    print(sparql_query)


# python schema_aware_rag_azure.py --ttl_file "../inputs/saref/saref_large.ttl" --nlq "what is the instance of the temperature sensor?"
