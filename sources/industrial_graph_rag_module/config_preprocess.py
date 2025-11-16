# Configuration settings for the knowledge graph preparation and processing pipeline

# Paths
INPUT_PATH = "./input"
INTERMEDIATE_SOFTWARE_ARTIFACTS_PATH = "./pipeline_artifacts"
OUTPUT_PATH = "./output"
INPUT_KG_NAME = "plant_robot_large_kg.ttl"
OUTPUT_KG_NAME = "preprocessed_kg.ttl"
NODEID_BROWSENAME_MAPPING_NAME = "preprocessed_map.csv"

# Kg formatting flags
FORMAT_NAMESPACES = True

# Remote-Local processing flags

# Variables relevant when SPARQL queries for
PROCESS_KG_REMOTELY = False
# Local processing flags (Currently unsupported)
PROCESS_KG_LOCALLY = not PROCESS_KG_REMOTELY
SAVE_TO_FILE = True

# NodeID - BrowseName mapping generation
GENERATE_NODEID_BROWSENAME_MAPPINGS = True

# Graph pruning and formatting
PRUNE_KG = True
CONVERT_ALL_HASHES_TO_SLASHES = True
