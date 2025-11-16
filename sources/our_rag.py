
from industrial_graph_rag_module.main import run_our_rag, run_our_rag_batch_single
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

    sparql_query = run_our_rag(args.ttl_file, args.nlq)
    print(sparql_query)
    
#python our_rag.py --ttl_file "../inputs/saef_large.ttl" --nlq "what is the instance of the temperature sensor?"