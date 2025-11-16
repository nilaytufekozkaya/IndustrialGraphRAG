
from industrial_graph_rag_module.main import run_our_rag, run_our_rag_batch_single

if __name__ == "__main__":
    ttl_path = "../inputs/saref_large.ttl"
    nlq_file = "../inputs/competency_question.xlsx"
    run_our_rag_batch_single(ttl_path, nlq_file)