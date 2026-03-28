# IndustrialGraphRAG

IndustrialGraphRAG is a **research prototype** for **validating**, **querying**, and **instantiating** large-scale industrial knowledge graphs using **natural language questions (NLQs)** and multiple **Retrieval-Augmented Generation (RAG)** strategies.

Given:

- a **large knowledge graph** (e.g., a `.ttl` file), and  
- a **natural-language question (NLQ)**

IndustrialGraphRAG produces:

1. a **compact, query-relevant subgraph** (suitable as LLM context), and  
2. a **corresponding SPARQL query** answering the NLQ.

The framework is designed for **industrial semantic artifacts**, with a strong focus on **OPC UA Companion Specifications** and **large ontology-based KGs**.

---

## 🧠 LLM Backends

IndustrialGraphRAG supports **two interchangeable LLM backends**:

- **OpenAI API** (ChatGPT / GPT-4o)  
- **Azure OpenAI API** (GPT-4o deployments)

The backend is selected implicitly via the folder you run from:

| Folder | LLM Backend | API Key Used |
|------|------------|-------------|
| `sources/` | OpenAI | `OPENAI_API_KEY` |
| `sources_azure/` | Azure OpenAI | `AZURE_OPENAI_API_KEY` |

⚠️ **Important:**  
You must configure the `.env` file **according to the backend you want to use**. The keys and environment variables differ between OpenAI and Azure OpenAI.

---

## 📁 Project Structure

```
IndustrialGraphRAG/
├─ inputs/
│  ├─ saref/
│  │  ├─ saref_large.ttl
│  │  ├─ saref_large.txt
│  │  └─ competency_questions.xlsx
│  │
│  ├─ robotics/
│  │  └─ robotics_compliance_rules.xlsx
│  │
│  └─ packml/
│     └─ packml_compliance_rules.xlsx
│
│
├─ sources/                # OpenAI-based implementations
│  ├─ our_rag.py
│  ├─ lightweight_rag.py
│  ├─ schema_aware_rag.py
│  └─ .env
│
├─ sources_azure/          # Azure OpenAI-based implementations
│  ├─ our_rag_azure.py
│  ├─ lightweight_rag_azure.py
│  ├─ schema_aware_rag_azure.py
│  └─ .env
│
└─ test_results/
   ├─ packml/
   ├─ robotics/
   └─ saref/
```

---

##  Inputs

### 1 `inputs/saref/` — (KG Public)

This folder contains **all data required for full end-to-end GraphRAG experiments** on a **publicly available ontology**.

- **`saref_large.ttl`** — complete SAREF KG (ontology + instances)
- **`saref_large.txt`** — text dump for LLM-only baselines
- **`information_retrieval_nlqs_gt.xlsx`** — NLQs, ground-truth SPARQL

---

### 2 `inputs/robotics/` — OPC UA Robotics (KG Confidential)

Contains rule-level datasets only:

- **`robotics_validation.xlsx`** — rules + ground-truth SPARQL

Used for **industrial compliance validation** without exposing the KG.

---

### 3 `inputs/packml/` — OPC UA PackML (KG Confidential)

- **`packml_validation.xlsx`** — rules + ground-truth SPARQL

---

## RAG Implementations

All RAG methods are runnable via the same CLI interface:

```bash
python <method>.py --ttl_file <KG> --nlq "<question>"
```

Below, we describe each method in detail.

---

## 1 Industrial Graph RAG (Our Method)

**File:** `our_rag.py`  
**Implements:** our proposed large-KG → subgraph → SPARQL pipeline  
**Requires:** `.ttl` file

**Example:**

```bash
cd sources
python our_rag.py   --ttl_file "../inputs/saref/saref_large.ttl"   --nlq "what is the instance of the temperature sensor?"
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

## 2 Lightweight RAG (LLM-only Baseline)

**File:** `lightweight_rag.py`  
**Description:**  
This mimics ChatGPT’s “upload document and ask a question” behavior.  
It is **not graph-based** and **not a real RAG pipeline**, but is included for comparison.

**Requires:** `.txt` graph file

**Example:**

```bash
cd sources
python lightweight_rag.py   --ttl_file "../inputs/saref/saref_large.txt"   --nlq "what is the instance of the temperature sensor?"
```

**Output:**  
- SPARQL query generated directly from the LLM with no graph-aware retrieval.

---

## 3 Schema-aware RAG

**File:** `schema_aware_rag.py.py`  
**Description:**  
A Schema-aware RAG pipeline adapted to work over SAREF-like graphs.  
Uses structured or textified forms of the KG.

**Example:**

```bash
cd sources
python schema_aware_rag.py   --ttl_file "../inputs/saref/saref_large.ttl"   --nlq "what is the instance of the temperature sensor?"
```

**Output:**  
- SPARQL query for the NLQ.
---

## Test Results

All results in the scope of our experiments under `test_results/` were generated using **Azure OpenAI** to ensure **experimental consistency with the accompanying publication**.

- `packml/` → validation results  
- `robotics/` → validation + detailed information retrieval  
- `saref/` → extensive information retrieval benchmarks

---

## 🚀 Environment Setup

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure API keys

**OpenAI:**
```bash
export OPENAI_API_KEY="your_key_here"
```

**Azure OpenAI:**
```bash
export AZURE_OPENAI_API_KEY="your_key_here"
export AZURE_OPENAI_ENDPOINT="https://<resource>.openai.azure.com"
export AZURE_OPENAI_DEPLOYMENT="gpt-4o"
```

---


## Notes

- Research prototype (not production-ready)
- Azure OpenAI used for all reported results
- Designed to balance **reproducibility**, **industrial realism**, and **confidentiality**

## Citation

This repository has been archived on Zenodo to ensure reproducibility and provide a citable frozen version of the implementation:

Concept: [![DOI](https://zenodo.org/badge/1097175087.svg)](https://doi.org/10.5281/zenodo.19289838)

Frozen Release DOI: https://doi.org/10.5281/zenodo.19289838

