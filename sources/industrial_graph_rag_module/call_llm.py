import rdflib
from rdflib.plugins.sparql import prepareQuery  
import time
import os
from openai import AzureOpenAI
from .config import ENV_PATH
from dotenv import load_dotenv
import tiktoken
from openai import OpenAI


def call_queries(queries, kg_name):
    print("kg_name", kg_name)
    graph = rdflib.Graph()
    graph = graph.parse(kg_name)
    results = []
    for query in queries:
        # Prepare and execute the query  
        if query == "not found":
            results.append("FALSE")
        
        else:
            try:
                q = prepareQuery(query)
                result = graph.query(q)  
                results.append(result)                

            except:
                #results.append("broken")
                results.append("not found")
    return results

def num_tokens_from_string(text, encoding_name = "cl100k_base"):
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(text))
    return num_tokens

def num_tokens_from_messages(messages, model="gpt-4o-mini-2024-07-18"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using o200k_base encoding.")
        encoding = tiktoken.get_encoding("o200k_base")
    if model in {
        "gpt-3.5-turbo-0125",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        "gpt-4o-mini-2024-07-18",
        "gpt-4o-2024-08-06"
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0125.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0125")
    elif "gpt-4o-mini" in model:
        print("Warning: gpt-4o-mini may update over time. Returning num tokens assuming gpt-4o-mini-2024-07-18.")
        return num_tokens_from_messages(messages, model="gpt-4o-mini-2024-07-18")
    elif "gpt-4o" in model:
        print("Warning: gpt-4o and gpt-4o-mini may update over time. Returning num tokens assuming gpt-4o-2024-08-06.")
        return num_tokens_from_messages(messages, model="gpt-4o-2024-08-06")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens



def run_prompt(prompt):

    queries = []
    q = call_gpt4(prompt)
    time.sleep(5)
    queries.append(q)
    return queries
        
def run_nlqs(template, nlqs):

    queries = []
    for nlq in nlqs:
        prompt = template.replace("{NLQ}", nlq)
        q = call_gpt4(prompt)
        time.sleep(5)
        queries.append(q)
    return queries, prompt

def call_gpt_only_without_azure(prompt):
    
    api_key = os.getenv("OPENAI_API_KEY")   
    client = OpenAI(api_key=api_key)

    message_text = [{"role":"system","content":"You are an AI assistant that helps people find information."},{"role":"user","content":prompt}]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=message_text
    )

    print(response.choices[0].message.content)
    return response.choices[0].message.content

def call_gpt_only(prompt):
    # Load environment variables from the specified .env file  
    load_dotenv(dotenv_path=ENV_PATH, override=True)  

    # Fetch the API key, endpoint, API version, and deployment name from the environment variables  
    api_key = os.getenv("AZURE_OPENAI_API_KEY")  
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")  
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")  
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")  

    # Construct the full endpoint URL  
    full_endpoint = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"  

    # Initialize the client with the API key and full endpoint  
    client = AzureOpenAI(api_key=api_key, azure_endpoint=full_endpoint)  

    # Prepare your message  
    message_text = [{"role":"system","content":"You are an AI assistant that helps people find information."},{"role":"user","content":prompt}]


    # Create the completion  
    completion = client.chat.completions.create(  
        model=deployment,  
        messages=message_text,  
        max_tokens=4096,
        temperature=0,  
        top_p=0.95,  
        frequency_penalty=0,  
        presence_penalty=0,  
        stop=None,  
        stream=False  
    )  
    return completion

def call_gpt4(prompt): 

    completion = call_gpt_only_without_azure(prompt)

    #print(completion.to_json())

        
    #s = completion.choices[0].message.content
    s = completion
    start = '```sparql'
    end = '```'
    tt0 = s.find(start)
    tt = tt0 + len(start)
    s2 = s[tt:]
    zz = s2.find(end)
    sparql_query = s2[:zz]
    if tt0 == -1 or zz == -1:
        return "not found"
    return sparql_query

def call_gpt4_im(prompt):
    """
    Calls GPT, but does NOT look for ```sparql fences.
    Returns the full text from the assistant.
    """
    completion = call_gpt_only(prompt)
    return completion.choices[0].message.content


def run_prompt_im(prompt):
    """
    For generating or modifying OPC UA XML.
    Calls GPT to get the raw text as a single string.
    """
    response = call_gpt4_im(prompt)
    time.sleep(5)
    return response
