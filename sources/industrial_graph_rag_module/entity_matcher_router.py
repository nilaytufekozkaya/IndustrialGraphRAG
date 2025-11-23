from .config import LLM_ENGINE_TYPES, LLM_ENGINE
from .entity_matcher import run_entity_matcher
from .my_matchner import call_matchner

def run_entity_matcher_router(nlq, csv_path):
    
    if LLM_ENGINE == LLM_ENGINE_TYPES.OPENAI:
        return run_entity_matcher(nlq, csv_path)
    else:
        return call_matchner(nlq, csv_path)
        
        
    
