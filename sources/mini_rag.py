import os
from openai import OpenAI


def prep():
    client = OpenAI()  # OPENAI_API_KEY ortamda olmalı
    # 1) Vector store oluştur
    vs = client.vector_stores.create(name="SAREF Store")
    
    return client, vs

# 2) Dosyayı store'a yükleyip indeksle (poll’lu toplu yükleme)

def create_batch_vectors(client, vs, ttl_path): #txt
    with open(ttl_path, "rb") as f:
        batch = client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vs.id,
            files=[f]
    )
    #assert batch.status == "completed"
    return batch

# 3) Assistant’ı file_search + tool_resources ile bağla

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
    # 5) Run ve sonuç
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
    # Yeni kolon(lar) ekle
    df["generated queries minirag"] = queries

    # Yeni dosyaya kaydet
    df.to_excel("../outputs/minirag_combined_mixed.xlsx", index=False)

def run(ttl_path, nlq_file):
    #ttl_path = "../tmp_output_im/saref_old/preprocessed_kg_all_last.ttl"
    #nlq_file = competency_question.xlsx
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

    
    
if __name__ == "__main__":
    ttl_path = "../inputs/saref_large.txt"
    nlq_file = "../inputs/competency_question.xlsx"
    run(ttl_path, nlq_file)



