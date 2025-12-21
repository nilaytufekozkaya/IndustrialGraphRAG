from .preprocess_pipeline import preprocess_pipeline
from .pipeline import pipeline_ext
from .entity_matcher import run_entity_matcher
from .config import NLQ_TYPE, SUB_GRAPH_FILE, PREPROCESSED_KG_FILE, PREPROCESSED_CSV_FILE, LLM_ENGINE_TYPES, LLM_ENGINE
from .config_preprocess import INTERMEDIATE_SOFTWARE_ARTIFACTS_PATH
from .my_matchner import call_matchner
from .entity_matcher_router import run_entity_matcher_router

import pandas as pd
import os
import time

def remove_file(file):
    if os.path.isfile(file):
        os.remove(file)

def read_nlqs(nlq_file):
    df = pd.read_excel(nlq_file)
    return df

def save_queries(df, queries):
    df["generated queries opc ua"] = queries
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    results = os.path.join(BASE_DIR, "./../../outputs/our_rag_saref.xlsx") 
    df.to_excel(results, index=False)

def run_our_rag_batch_single(ttl_path, nlq_file, llm_engine):
    
    df = read_nlqs(nlq_file)
    nlq_list = df["NLQ"].tolist()
    queries = []
    for nlq in nlq_list:
        query = run_our_rag(ttl_path, nlq, llm_engine)
        queries.append(query)
    save_queries(df, queries)


def run_our_rag_batch_n_excel(ttl_path, nlq_file, llm_engine, n):
    

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    preprocessed_kg = os.path.join(BASE_DIR, PREPROCESSED_KG_FILE) 
    node_id_mapping_path = os.path.join(BASE_DIR, PREPROCESSED_CSV_FILE)  
    intermediate_software_artifacts_directory = os.path.join(BASE_DIR,  INTERMEDIATE_SOFTWARE_ARTIFACTS_PATH)  
    
    remove_file(preprocessed_kg)
    remove_file(node_id_mapping_path)
    remove_file(intermediate_software_artifacts_directory)
    
    preprocess_pipeline(ttl_path, preprocessed_kg, node_id_mapping_path, intermediate_software_artifacts_directory)
    LLM_ENGINE = llm_engine
    df = read_nlqs(nlq_file)
    nlq_list = df["NLQ"].tolist()
    
    df = read_nlqs(nlq_file)
    nlq_list = df["NLQ"].tolist()
    result_df = [["NLQ", "q1", "q2", "q3", "q4", "q5"]]
    
    for nlq in nlq_list:
        #el = run_entity_matcher(nlq, node_id_mapping_path)
        print(nlq)
        res_tmp = []
        res_tmp.append(nlq)
        for i in range(n):
            el = run_entity_matcher_router(nlq, node_id_mapping_path)
            
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            sg = os.path.join(BASE_DIR, SUB_GRAPH_FILE) 
            remove_file(sg)
            query, prompt, df_rdf = pipeline_ext(ttl_path, el, NLQ_TYPE.CQ, nlq, sg)
            print(query)
            time.sleep(1)
            res_tmp.append(query)
            print("----")
        print(" --- NLQ END ---")
        result_df.append(res_tmp)

        
    print("-- BATCH DONE --")
    df = pd.DataFrame(result_df)
    df.to_excel("../outputs/saref_5_time_our_rag.xlsx", index=False, header=False)


def run_our_rag_batch(ttl_path, nlq_file, llm_engine):
    

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    preprocessed_kg = os.path.join(BASE_DIR, PREPROCESSED_KG_FILE) 
    node_id_mapping_path = os.path.join(BASE_DIR, PREPROCESSED_CSV_FILE)  
    intermediate_software_artifacts_directory = os.path.join(BASE_DIR,  INTERMEDIATE_SOFTWARE_ARTIFACTS_PATH)  
    
    remove_file(preprocessed_kg)
    remove_file(node_id_mapping_path)
    remove_file(intermediate_software_artifacts_directory)
    
    preprocess_pipeline(ttl_path, preprocessed_kg, node_id_mapping_path, intermediate_software_artifacts_directory)
    LLM_ENGINE = llm_engine
    df = read_nlqs(nlq_file)
    nlq_list = df["NLQ"].tolist()
    queries = []
    for nlq in nlq_list:
        #el = run_entity_matcher(nlq, node_id_mapping_path)
        
    
        el = run_entity_matcher_router(nlq, node_id_mapping_path)
        
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        sg = os.path.join(BASE_DIR, SUB_GRAPH_FILE) 
        remove_file(sg)
        query, prompt, df_rdf = pipeline_ext(ttl_path, el, NLQ_TYPE.CQ, nlq, sg)
        queries.append(query)
        time.sleep(1)
        
    save_queries(df, queries)

def run_our_rag(ttl_path, nlq, llm_engine):
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    preprocessed_kg = os.path.join(BASE_DIR, PREPROCESSED_KG_FILE) 
    node_id_mapping_path = os.path.join(BASE_DIR, PREPROCESSED_CSV_FILE)  
    intermediate_software_artifacts_directory = os.path.join(BASE_DIR,  INTERMEDIATE_SOFTWARE_ARTIFACTS_PATH)  
    
    remove_file(preprocessed_kg)
    remove_file(node_id_mapping_path)
    remove_file(intermediate_software_artifacts_directory)
    
    preprocess_pipeline(ttl_path, preprocessed_kg, node_id_mapping_path, intermediate_software_artifacts_directory)
    LLM_ENGINE = llm_engine
    
    el = run_entity_matcher_router(nlq, node_id_mapping_path)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sg = os.path.join(BASE_DIR, SUB_GRAPH_FILE) 
    remove_file(sg)
    query, prompt, df_rdf = pipeline_ext(preprocessed_kg, el, NLQ_TYPE.CQ, nlq, sg, )
    
    return query
        

if __name__ == "__main__":
    
    ttl_path = "../inputs/saref_large.txt"
    nlq_file = "../inputs/competency_question.xlsx"
    run_our_rag_batch_single(ttl_path, nlq_file, LLM_ENGINE_TYPES.OPENAI)
    


    

    