from enum import Enum 


RELATIVE_PATH = "./"
ENV_PATH = RELATIVE_PATH + "internal.env"
MODEL_NMAE = "gpt-4o"
DEPLOYMENT_NAME = "gpt-4o"
SUB_GRAPH_FILE = "temp_subgraph.ttl"
COMBINED_SUB_GRAPH_FILE = "combined_subgraph.ttl"
PREPROCESSED_KG_FILE = "preprocessed_kg.ttl"
INPUT_KG_FILE = "input_kg.ttl"
PREPROCESSED_CSV_FILE = "preprocessed_map.csv"
RAG_TEMPLATE_FILE = RELATIVE_PATH + "rag_template.txt"
INFORMATION_MODEL_FILE_INTERNAL = "information_model.xml"
SUB_GRAPH_FILE = "temp_subgraph.ttl"
COMBINED_SUB_GRAPH_FILE = "combined_subgraph.ttl"
INPUT_KG_FILE = "input_kg.ttl"
IM_OUTPUT_FOLDER = "tmp_output_im/"

class NLQ_TYPE(Enum):  
    CR = "CR"  
    CQ = "CQ"
    IM = "IM"  
  
QUERY_TYPE = {  
    NLQ_TYPE.CR: "ASK",  
    NLQ_TYPE.CQ: "SELECT",  
    NLQ_TYPE.IM: ""
}


