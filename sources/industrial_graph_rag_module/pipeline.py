from . import augmentation 
#generate prompt
from . import call_llm 
import pandas as pd
from .config import RAG_TEMPLATE_FILE, NLQ_TYPE, QUERY_TYPE



#run the SPARQL on the large graph
def run_query(queries, ttl_file):
    print("... SPARQL query is running ...")
    results = call_llm.call_queries(queries, ttl_file)
    # results[0]
    return results[0]


#send prompt to llm
def run_llm_prompt(prompt):
    print("... LLM is running ...")
    queries = call_llm.run_prompt(prompt)
    return queries

#send prompt to llm
def run_llm(template, nlqs):
    print("... LLM is running ...")
    queries, prompt = call_llm.run_nlqs(template, nlqs)
    return queries, prompt

import os


#generate prompt
def generate_prompt(output_file):
    print("... prepare the prompt ...")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    template_file = os.path.join(BASE_DIR, RAG_TEMPLATE_FILE)
    #template_file =  RAG_TEMPLATE_FILE
    f = open(template_file, "r")
    template = f.read()
    f.close()
    f = open(output_file, "r")
    ontology = f.read()
    f.close()
    template = template.replace("{SCHEMA}", ontology) 
    return template

#extract the sub-graph
def extract_sub_graph_information_model_constraints(ttl_file, nodes, output_file):
    print("... extracting sub-graph im ...")
    #augmentation.rag_all_shortest_paths_all_nodes_small(ttl_file, nodes, output_file)
    augmentation.rag_all_shortest_paths_all_nodes_information_model_constraints(ttl_file, nodes, output_file)

def pipeline_ext(ttl_file, el, nlq_type, nlq, output_file):
    nodes = list(el.values())
    if nlq_type == NLQ_TYPE.IM:
        pipeline_extr_sub_graph_im_constraints(ttl_file, nodes, output_file)
        df = pd.DataFrame(data=[""], columns=["Result"]) 
        return [""] ,"", df
    else:
        extract_sub_graph(ttl_file, nodes, output_file)
        prompt = generate_prompt_nlq(output_file, nlq_type, nlq, el)
        if check_prompt_size(prompt, 127000 ) == False:#128000 
            extract_sub_graph_small(ttl_file, nodes, output_file)
            prompt = generate_prompt_nlq(output_file, nlq_type, nlq, el)
            if check_prompt_size(prompt, 127000 ) == False:
                extract_sub_graph_smaller(ttl_file, nodes, output_file)
                prompt = generate_prompt_nlq(output_file, nlq_type, nlq, el)
        queries = generate_sparql_prompt(prompt)
        df = generate_sparql_result_df_nlq(queries, ttl_file, nlq_type)
        
        return queries[0], prompt, df
 
 
def pipeline_extr_sub_graph_im_constraints(ttl_file, nodes, output_file):

    extract_sub_graph_information_model_constraints(ttl_file, nodes, output_file)  

    return True
    
#generate prompt
def generate_prompt_nlq(output_file, nlq_type, nlq, el):
    print("... prepare the prompt ...")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    template_file = os.path.join(BASE_DIR, RAG_TEMPLATE_FILE)
    #template_file =  RAG_TEMPLATE_FILE
    f = open(template_file, "r")
    template = f.read()
    f.close()
    f = open(output_file, "r")
    ontology = f.read()
    f.close()
    template = template.replace("{SCHEMA}", ontology) 
    template = template.replace("{QT}", QUERY_TYPE[nlq_type])
    template = template.replace("{entities}", str(el))
    prompt = template.replace("{NLQ}", nlq)
    return prompt


#extract the sub-graph
def extract_sub_graph(ttl_file, nodes, output_file):
    print("... extracting sub-graph ...")
    augmentation.rag_all_shortest_paths_all_nodes(ttl_file, nodes, output_file)
    
def check_prompt_size(prompt, limit_token):
    
    token_count = call_llm.num_tokens_from_string(prompt)
    if token_count > limit_token:
        print("----------------------limit exceeded", token_count)
        return False
    else:
        return True

def generate_subsequent_im_prompt(latest_xml, user_instructions):
    template_file =  RAG_TEMPLATE_FILE_XML
    f = open(template_file, "r")
    template = f.read()
    f.close()
    template = template.replace("{XML}", latest_xml) 
    final_prompt = template.replace("{NLQ}", user_instructions)
    
    return final_prompt

def show_table_form(result):
    if isinstance(result, str):
        return pd.DataFrame()
    col_names = result.vars
    data = [ {str(v): res[i] for i, v in enumerate(col_names)} for res in result]  

    df = pd.DataFrame(data)  

    return df 

def generate_sparql_result_df_nlq(queries, ttl_file, nlq_type):
    result = run_query(queries, ttl_file)
    if nlq_type == NLQ_TYPE.CQ:
        df = show_table_form(result)
    else:
        for res in result:
            df = pd.DataFrame(data=[str(res)], columns=["Result"])  
            return df
    return df

#extract the sub-graph
def extract_sub_graph_small(ttl_file, nodes, output_file):
    print("... extracting sub-graph small...")
    augmentation.rag_all_shortest_paths_all_nodes_small(ttl_file, nodes, output_file)
    
def generate_sparql_prompt(prompt):
    queries = run_llm_prompt(prompt)
    return queries


#extract the sub-graph smaller
def extract_sub_graph_smaller(ttl_file, nodes, output_file):
    print("... extracting sub-graph smaller...")
    augmentation.rag_all_shortest_paths_all_nodes_smaller(ttl_file, nodes, output_file)

