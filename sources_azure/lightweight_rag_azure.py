import os
import time
import argparse
import pandas as pd
from dotenv import load_dotenv
from openai import AzureOpenAI  


def prep():
    
    # Load environment variables from the specified .env file  
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    env_base = os.path.join(BASE_DIR, ".env") 
    load_dotenv(dotenv_path=env_base, override=True) 

    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview"),
    )

    # OpenAI style vector store (Azure'da muhtemelen YOK)
    vs = client.vector_stores.create(name="SAREF Store")
    return client, vs


def create_batch_vectors(client, vs, ttl_path):

    with open(ttl_path, "rb") as f:
        batch = client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vs.id,
            files=[f]
        )
    return batch

#pure open ai feaature noting to dow ith azure
def bind_assistant_to_file_search(client, vs):

    assistant = client.beta.assistants.create(
        name="RAG Agent",
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        tools=[{"type": "file_search"}],
        tool_resources={"file_search": {"vector_store_ids": [vs.id]}},
    )
    return assistant


def create_message_form(client, nlq):
    input_path = "rag_template.txt"

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    text = text.replace("{SCHEMA}", "")
    text = text.replace("{NLQ}", nlq)
    prompt = text.replace("{QT}", "SELECT")

    print("prompt:", prompt)

    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
    )

    return client, thread


def run_llm(client, thread, assistant):

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        if run.status in ("completed", "failed", "cancelled", "expired"):
            break
        time.sleep(0.5)

    msgs = client.beta.threads.messages.list(thread_id=thread.id)

    for m in reversed(msgs.data):
        for p in m.content:
            if p.type == "text" and m.role == "assistant":
                q = str(p.text.value)
                print(q)
                return q

    return "not generated"


def read_nlqs(nlq_file):
    df = pd.read_excel(nlq_file)
    return df


def save_queries(df, queries):
    df["generated queries lightweight rag"] = queries
    df.to_excel("../outputs/lightweight_rag_combined_mixed.xlsx", index=False)


def run_batch(ttl_path, nlq_file):
    df = read_nlqs(nlq_file)
    nlq_list = df["NLQ"].tolist()
    queries = []

    for nlq in nlq_list:
        client, vs = prep()
        create_batch_vectors(client, vs, ttl_path)
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Azure OpenAI Lightweight RAG")

    parser.add_argument(
        "--ttl_file",
        type=str,
        required=True,
        help="txt_file knowledge graph file",
    )

    parser.add_argument(
        "--nlq",
        type=str,
        required=True,
        help="NLQ input string",
    )

    args = parser.parse_args()

    sparql_query = run(args.ttl_file, args.nlq)
    print(sparql_query)

    # python lightweight_rag_azure.py --ttl_file "../inputs/saref/saref_large.txt" --nlq "what is the instance of the temperature sensor?"
