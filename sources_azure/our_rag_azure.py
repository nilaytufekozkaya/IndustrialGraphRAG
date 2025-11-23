import sys
import os

# current file: sources_azure/our_rag_azure.py
# we need to go 1 level up to reach project root
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))

# add parent (RAG_GIT root) to PYTHONPATH
sys.path.append(parent_dir)


from sources.industrial_graph_rag_module.main import run_our_rag, run_our_rag_batch_single
from sources.industrial_graph_rag_module.config import LLM_ENGINE_TYPES, LLM_ENGINE
import argparse

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

    sparql_query = run_our_rag(args.ttl_file, args.nlq, llm_engine = LLM_ENGINE_TYPES.AZURE)
    print(sparql_query)
    
#python our_rag_azure.py --ttl_file "../inputs/saref/saref_large.ttl" --nlq "what is the instance of the temperature sensor?"