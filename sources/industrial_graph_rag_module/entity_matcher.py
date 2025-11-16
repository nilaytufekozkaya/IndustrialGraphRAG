import pandas as pd
import json
from openai import OpenAI
import os

def get_labels(csv_path: str) -> list[str]:
    df = pd.read_csv(csv_path, dtype=str)
    labels = df["label"].dropna().str.strip().tolist()
    return labels

def call_llm_for_match(nlq, entity_list):
    
    api_key = os.getenv("OPENAI_API_KEY")   
    client = OpenAI(api_key=api_key)


    NER_PROMPT_TEMPLATE = """
    Task:   Identify and match the named entities from a given text and given list. 
    a word or phrase must be associated with a single entity in the list if there is a match, 
    but not every word or phrase have to have a corresponding item in the list. 
    Find exact matches or semantic matches or syntactic similar matches. 
    given text:
    {nlq}
    given list:
    {entity_list}
    Output the result as a JSON array of dictionaries, each with keys "matched_text" and "entity".
    Example of the output format: [{{"matched_text": "text from prompt", "entity": "entity from list"}}, ...]
    """

    
    entity_str = ", ".join(entity_list)

    template = NER_PROMPT_TEMPLATE.replace("{nlq}", nlq)
    template = template.replace("{entity_list}", entity_str)


    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "you are an ai assistant!"},
            {"role": "user", "content": template}
        ]
    )

    msg = response.choices[0].message.content
    return msg

def extract_matches(matched_output):
    try:
        start = '```json'
        end = '```'
        tt0 = matched_output.find(start)
        tt = tt0 + len(start)
        s2 = matched_output[tt:]
        zz = s2.find(end)
        json_output = s2[:zz]
        if tt0 == -1 or zz == -1:
            return json.loads("{}")
        parsed_match = json.loads(json_output)
        
        # extra validation to catch unexpected outputs like empty outputs
        
        if isinstance(parsed_match, list) and all(
            isinstance(item, dict) and 'matched_text' in item and 'entity' in item for item in parsed_match
        ):
            match = {item['matched_text']: item['entity'] for item in parsed_match}
            
        else:
            raise ValueError("Invalid output format from LLM.")
                
    except Exception:
        match = {} # when there is an exception in the format of the match, print the exception and return empty match
        # maybe we want to change this
        
        print("Error!")
        print(f"LLM output:{matched_output}")
        #print(traceback.format_exc())
        
    return match

def subject_uri_for(entity: str, csv_path: str) -> str | None:
    df = pd.read_csv(csv_path, dtype=str).dropna(subset=["label", "subject_uri"])
    mapping = dict(zip(
        df["label"].str.strip().str.casefold(),
        df["subject_uri"].str.strip()
    ))
    return mapping.get(entity.strip().casefold())


def run_entity_matcher(nlq, csv):
    entity_list = get_labels(csv)

    msg = call_llm_for_match(nlq, entity_list)
    matches = extract_matches(msg)
    subject_uris = []
    match2 = {}
    for k,v in matches.items():

        s_uri = subject_uri_for(v,csv)
        subject_uris.append(s_uri)
        match2[k] = s_uri

        
    return match2