from .matchner import LLMMatchner
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_openai import ChatOpenAI



from langchain.callbacks.base import BaseCallbackHandler
import os
from .config import ENV_PATH

class CustomCallbackHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        for prompt in prompts:
            print("callback matchner ", prompt)


def call_matchner(nlq, csv_file):
    # Load environment variables from the specified .env file  
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    env_base = os.path.join(BASE_DIR, ENV_PATH) 
    load_dotenv(dotenv_path=env_base, override=True)  

    # Fetch the API key, endpoint, API version, deployment name, model name, and temperature from the environment variables  
    #api_key = os.getenv("AZURE_OPENAI_API_KEY")  
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")  
    #api_version = os.getenv("OPENAI_API_VERSION")  
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")  
    model_name = deployment_name 
    temperature = 0  # Default to 0 if not set  

    callback_handler = CustomCallbackHandler()

    llm = AzureChatOpenAI(  
        model_name=model_name,  
        deployment_name=deployment_name,  
        azure_endpoint=endpoint,  
        temperature=temperature,  
        callbacks=[callback_handler]  
    ) 
    

    lwm = LLMMatchner(csv_file, llm)  # llm based matching from nodeId mapping .csv file

    el_nodeid, el_subject_uri = lwm.match(nlq)
    print("el_subject_uri:", el_subject_uri.items )
    
    return el_subject_uri