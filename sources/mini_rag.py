import os
from openai import OpenAI


def prep():
    client = OpenAI()  
    vs = client.vector_stores.create(name="SAREF Store")
    
    return client, vs


def create_batch_vectors(client, vs, ttl_path): #txt
    with open(ttl_path, "rb") as f:
        batch = client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vs.id,
            files=[f]
    )
    return batch


def bind_assistant_to_file_search(client, vs):
    assistant = client.beta.assistants.create(
        name="GraphRAG Agent",
        model="gpt-4o",
        tools=[{"type": "file_search"}],
        tool_resources={"file_search": {"vector_store_ids": [vs.id]}}
    )
    
    return assistant

# 4) Thread + mesaj
def create_message_form(client, nlq):
    
    # file paths
    input_path = "rag_template.txt"

    # read file
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    # replace placeholder
    text = text.replace("{SCHEMA}", "")
    text = text.replace("{NLQ}", nlq)
    prompt = text.replace("{QT}", "SELECT")

    print("prompt:", prompt)
    
    
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )
    
    return client, thread

import time
def run_llm(client, thread, assistant):

    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)


    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status in ("completed", "failed", "cancelled", "expired"):
            break
        time.sleep(0.5)

    msgs = client.beta.threads.messages.list(thread_id=thread.id)
    queries = []
    i = 0
    for m in reversed(msgs.data):
        
            for p in m.content:
                if p.type == "text" and m.role == "assistant":
                    #queries.append = p.text.value
                    q = str(p.text.value)
                    print(q)
                    return q
                
    return "not generated"


import pandas as pd
def read_nlqs(nlq_file):
    df = pd.read_excel(nlq_file)
    return df

def save_queries(df, queries):
    df["generated queries minirag"] = queries

    df.to_excel("../outputs/minirag_combined_mixed.xlsx", index=False)

def run_batch(ttl_path, nlq_file):
    df = read_nlqs(nlq_file)
    nlq_list = df["NLQ"].tolist()
    queries = []
    for nlq in nlq_list:
        client, vs = prep()
        batch = create_batch_vectors(client, vs, ttl_path)
        assistant = bind_assistant_to_file_search(client, vs)
        client, thread = create_message_form(client, nlq)
        query = run_llm(client, thread, assistant)
        queries.append(query)
        print(nlq)
        print(query)
        print("-----")
    save_queries(df, queries)
    
def run(ttl_path, nlq):

    client, vs = prep()
    create_batch_vectors(client, vs, ttl_path)
    assistant = bind_assistant_to_file_search(client, vs)
    client, thread = create_message_form(client, nlq)
    query = run_llm(client, thread, assistant)

    return query

    

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Industrial Graph RAG")

    parser.add_argument(
        "--txt_file",
        type=str,
        required=True,
        help="txt_file knowledge graph file"
    )

    parser.add_argument(
        "--nlq",
        type=str,
        required=True,
        help="Path to the NLQ input"
    )

    args = parser.parse_args()

    sparql_query = run(args.txt_file, args.nlq)
    print(sparql_query)
    
    #ttl_path = "../inputs/saref_large.txt"
    #nlq_file = "../inputs/competency_question.xlsx"
    #run_batch(ttl_path, nlq_file)
    
# python mini_rag.py --txt_file "../inputs/saref_large.txt" --nlq "what is the instance of the temperature sensor?"



