import os
import shutil

from .config_preprocess import *

from .nodeid_browsename_mapper import map_nodeids_to_browsenames
from .kg_pruner import prune_knowledge_graph
from .preprocess_formatter import format_kg_for_namespaces, convert_hashes_to_slashes
from .local_kg_processor import remove_owl_restrictions

def preprocess_pipeline(input_file_path=(INPUT_PATH + "/" + INPUT_KG_NAME), output_file_path=(OUTPUT_PATH + "/" + OUTPUT_KG_NAME), node_id_mapping_path=(OUTPUT_PATH + "/" + NODEID_BROWSENAME_MAPPING_NAME), intermediate_software_artifacts_directory=INTERMEDIATE_SOFTWARE_ARTIFACTS_PATH):
    print("Knowledge graph preparation pipeline started...")

    if FORMAT_NAMESPACES:
        format_kg_for_namespaces(input_file=os.path.abspath(input_file_path), intermediate_file=os.path.abspath((intermediate_software_artifacts_directory + "/formatted_kg_namespaces.ttl")))

    if PROCESS_KG_LOCALLY:
        print("The knowledge graph is being processed to remove the OWL restrictions.")
        if FORMAT_NAMESPACES:
            remove_owl_restrictions(input_file=os.path.abspath((intermediate_software_artifacts_directory + "/formatted_kg_namespaces.ttl")), output_file = os.path.abspath((intermediate_software_artifacts_directory + "/kg_without_owl_restrictions.ttl")))
        else:
            remove_owl_restrictions(input_file=os.path.abspath(input_file_path), output_file=os.path.abspath((intermediate_software_artifacts_directory + "/kg_without_owl_restrictions.ttl")))

    elif PROCESS_KG_REMOTELY:
        raise RuntimeError("Remote processing of the KG is not supported at the moment. ")

    else:
        raise RuntimeError("Unexpected value pair for the parameters PROCESS_KG_LOCALLY and PROCESS_KG_REMOTELY")

    if PRUNE_KG:
        prune_knowledge_graph(input_file=os.path.abspath((intermediate_software_artifacts_directory + "/kg_without_owl_restrictions.ttl")), output_file=os.path.abspath(output_file_path))

    if GENERATE_NODEID_BROWSENAME_MAPPINGS:
        map_nodeids_to_browsenames(input_file=os.path.abspath(output_file_path), output_file=os.path.abspath(node_id_mapping_path))

    if CONVERT_ALL_HASHES_TO_SLASHES:
        convert_hashes_to_slashes(file_path=os.path.abspath(output_file_path))
        convert_hashes_to_slashes(file_path=os.path.abspath(node_id_mapping_path))

    #remove temporary
    shutil.rmtree(intermediate_software_artifacts_directory)  
    print("Pipeline finished.")



if __name__ == "__main__":
    input_file_path = "../../inputs/saref_large.ttl"
    output_file_path = "./preprocessed_kg"
    node_id_mapping_path = "./preprocessed_map.csv"
    intermediate_software_artifacts_directory = "./pipeline_artifacts"
    preprocess_pipeline(input_file_path, output_file_path, node_id_mapping_path, intermediate_software_artifacts_directory)




