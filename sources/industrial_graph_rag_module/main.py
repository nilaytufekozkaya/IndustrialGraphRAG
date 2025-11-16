from .preprocess_pipeline import preprocess_pipeline
from .pipeline import pipeline_ext
from .entity_matcher import run_entity_matcher
from .config import NLQ_TYPE, SUB_GRAPH_FILE


import pandas as pd
def read_nlqs(nlq_file):
    df = pd.read_excel(nlq_file)
    return df

def save_queries(df, queries):
    df["generated queries opc ua"] = queries
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    results = os.path.join(BASE_DIR, "./../../outputs/our_rag_saref.xlsx") 
    df.to_excel(results, index=False)

import time
import os

def run_our_rag_batch_single(ttl_path, nlq_file):
    
    df = read_nlqs(nlq_file)
    nlq_list = df["NLQ"].tolist()
    queries = []
    for nlq in nlq_list:
        query = run_our_rag(ttl_path, nlq)
        queries.append(query)
    save_queries(df, queries)

def run_our_rag_batch(ttl_path, nlq_file):
    

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    output_file_path = os.path.join(BASE_DIR, "preprocessed_kg.ttl") 
    node_id_mapping_path = os.path.join(BASE_DIR, "preprocessed_map.csv")  
    intermediate_software_artifacts_directory = os.path.join(BASE_DIR,  "pipeline_artifacts")  
    
    preprocess_pipeline(ttl_path, output_file_path, node_id_mapping_path, intermediate_software_artifacts_directory)
    
    df = read_nlqs(nlq_file)
    nlq_list = df["NLQ"].tolist()
    queries = []
    for nlq in nlq_list:
        el = run_entity_matcher(nlq, node_id_mapping_path)
        nodes = list(el.values())
        query, prompt, df_rdf = pipeline_ext(ttl_path, el, NLQ_TYPE.CQ, nlq, SUB_GRAPH_FILE)
        queries.append(query)
        time.sleep(1)
        
    save_queries(df, queries)

def run_our_rag(ttl_path, nlq):
    

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    output_file_path = os.path.join(BASE_DIR, "preprocessed_kg.ttl") 
    node_id_mapping_path = os.path.join(BASE_DIR, "preprocessed_map.csv")  
    intermediate_software_artifacts_directory = os.path.join(BASE_DIR,  "pipeline_artifacts")  
    
    preprocess_pipeline(ttl_path, output_file_path, node_id_mapping_path, intermediate_software_artifacts_directory)
    
    el = run_entity_matcher(nlq, node_id_mapping_path)
    nodes = list(el.values())
    query, prompt, df_rdf = pipeline_ext(ttl_path, el, NLQ_TYPE.CQ, nlq, SUB_GRAPH_FILE)
    
    return query
        

if __name__ == "__main__":
    
    ttl_path = "../inputs/saref_large.txt"
    nlq_file = "../inputs/competency_question.xlsx"
    run_our_rag_batch_single(ttl_path, nlq_file)
    


    

    