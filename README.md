# IndustrialGraphRAG

IndustrialGraphRAG is a research prototype for **validating**, **querying**, and **instantiating** large knowledge graphs using **natural language (NLQ) inputs** and multiple **RAG (Retrieval-Augmented Generation)** approaches.

Given:

- a **large knowledge graph** (TTL file), and  
- a **natural-language question (NLQ)**

the system produces:

1. A **compact subgraph** (suitable as context for an LLM prompt), and  
2. A **corresponding SPARQL query** for the NLQ.

The main LLM backend is **OpenAI ChatGPT 4o**.  
You must provide an `OPENAI_API_KEY` as an environment variable.

---

## 📁 Project Structure

```
IndustrialGraphRAG/
├─ inputs/
│  ├─ saref_large.ttl
│  ├─ saref_large.txt
│  └─ competency_question.txt   (or .xlsx)
├─ outputs/
│  └─ ...                      # batch outputs (e.g., Excel with SPARQL results)
└─ sources/
   ├─ our_rag.py               # proposed Industrial Graph RAG
   ├─ mini_rag.py              # LLM-only baseline
   ├─ node2vec_rag.py          # Node2Vec RAG
   ├─ llamaindex_rag.py        # LlamaIndex RAG
   └─ rag_module/              # Industrial Graph RAG implementation
```

---

## 📥 Inputs

### 1. `saref_large.ttl` and `saref_large.txt`

Based on publicly available **SAREF ontologies**:

- **Core**
- **ENER (Energy)**
- **INMA (Industry & Manufacturing)**

Original source: <https://saref.etsi.org>

- Combined together into a unified TTL file (~3000 triples).
- `.txt` is just a renamed copy for methods that do not accept `.ttl`.

### 2. `competency_question.xlsx`

Contains 10 NLQs used to validate parts of the SAREF KG.  
Derived from evaluation questions used in the referenced paper.

---

## 📤 Outputs

Batch runs write results under `outputs/`.  
This may include:

- Extracted subgraphs
- SPARQL queries
- Execution results in Excel/CSV

---

## 🧩 RAG Implementations

All runnable via:

```bash
cd sources
python <file.py> --ttl_file <path> --nlq "<your question>"
```

Below are the four methods.

---

## 1️⃣ Industrial Graph RAG (Our Method)

**File:** `our_rag.py`  
**Implements:** our proposed large-KG → subgraph → SPARQL pipeline  
**Requires:** `.ttl` file

**Example:**

```bash
cd sources
python our_rag.py   --ttl_file "../inputs/saref_large.ttl"   --nlq "what is the instance of the temperature sensor?"
```

**Outputs:**

- A SPARQL query (e.g., querying instances of `TemperatureSensor`)

```bash
PREFIX saref: <http://example.org/saref#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?instance
WHERE {
  ?instance rdf:type saref:TemperatureSensor .
}
```

- A small extracted subgraph stored under `sources/` (e.g., `temp_graph.ttl`)

---

## 2️⃣ Mini RAG (LLM-only Baseline)

**File:** `mini_rag.py`  
**Description:**  
This mimics ChatGPT’s “upload document and ask a question” behavior.  
It is **not graph-based** and **not a real RAG pipeline**, but is included for comparison.

**Requires:** `.txt` graph file

**Example:**

```bash
cd sources
python mini_rag.py   --ttl_file "../inputs/saref_large.txt"   --nlq "what is the instance of the temperature sensor?"
```

**Output:**  
- SPARQL query generated directly from the LLM with no graph-aware retrieval.

---

## 3️⃣ Node2Vec RAG

**File:** `node2vec_rag.py`  
**Description:**  
Uses **Node2Vec embeddings** for graph-based retrieval:  
- Nodes are embedded using Node2Vec  
- Most relevant nodes to the NLQ are retrieved  
- A subgraph is formed  
- A SPARQL query is produced from retrieved triples

**Example:**

```bash
cd sources
python node2vec_rag.py   --ttl_file "../inputs/saref_large.ttl"   --nlq "what is the instance of the temperature sensor?"
```

**Output:**  
- SPARQL query built from Node2Vec-retrieved subgraph.

---

## 4️⃣ LlamaIndex RAG

**File:** `llamaindex_rag.py`  
**Description:**  
A LlamaIndex-based RAG pipeline adapted to work over SAREF-like graphs.  
Uses structured or textified forms of the KG.

**Example:**

```bash
cd sources
python llamaindex_rag.py   --ttl_file "../inputs/saref_large.ttl"   --nlq "what is the instance of the temperature sensor?"
```

**Output:**  
- SPARQL query for the NLQ.

---

## 🚀 Environment Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your OpenAI API key

```bash
export OPENAI_API_KEY="your_key_here"
```

---

## ▶️ Running the System End-to-End

All methods use the same interface:

```
python <rag_method>.py --ttl_file <KG> --nlq <question>
```

Preferred:

- `our_rag.py` → full industrial RAG  
- `node2vec_rag.py` → graph-embedding RAG  
- `llamaindex_rag.py` → LlamaIndex RAG  
- `mini_rag.py` → LLM baseline

---

## 📚 Citation

If you use this system, please cite:

```bibtex
@inproceedings{tufek2024validating,
  title        = {Validating semantic artifacts with large language models},
  author       = {Tufek, Nilay and Thuluva, Aparna Saissre and Just, Valentin Philipp
                  and Ekaputra, Fajar J and Bandyopadhyay, Tathagata and Sabou, Marta
                  and Hanbury, Allan},
  booktitle    = {European Semantic Web Conference},
  pages        = {92--101},
  year         = {2024},
  organization = {Springer}
}
```
---


