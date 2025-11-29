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
├─ outputs/
│  └─ ... 
│
└─ sources/
   ├─ our_rag.py
   ├─ lightweight_rag.py
   ├─ schema_aware_rag.py
   └─ rag_module/

```

---

## 📥 Inputs

### **1. `inputs/saref/` --- Full Open Knowledge Graph**

This folder contains all data required for **end-to-end GraphRAG
experiments** on an openly available ontology.

-   **`saref_large.ttl`**\
    Complete SAREF knowledge graph (ontology + instances) for
    large-scale subgraph extraction, NLQ→SPARQL generation, and
    evaluation.

-   **`saref_large.txt`**\
    Plain-text dump of the same KG for text-only RAG baselines (e.g.,
    lightweight RAG).

-   **`competency_question.xlsx`**\
    Benchmark with:

    -   natural-language competency questions (NLQs)\
    -   expected answer types\
    -   optional ground-truth SPARQL queries

This folder supports **full GraphRAG pipeline demonstrations** on a
publicly accessible dataset.

------------------------------------------------------------------------

### **2. `inputs/robotics/` --- OPC UA Robotics (Confidential KG)**

The OPC UA Robotics Companion Specification is **confidential**, so the
KG itself cannot be shared.

Instead, this folder provides:

-   **`compliance_rules_gt.xlsx`**
    -   Rule sentences extracted from the official Companion
        Specification\
    -   Ground-truth SPARQL queries

This dataset enables **industrial-grade evaluation** of NLQ→SPARQL and
rule-validation logic without exposing the confidential Robotics model.

------------------------------------------------------------------------

### **3. `inputs/packml/` --- OPC UA PackML (Confidential KG)**

Similarly, the PackML Companion Specification is proprietary. Therefore:

-   **`compliance_rules_gt.xlsx`**
    -   Rule sentences from the PackML specification\
    -   Corresponding ground-truth SPARQL queries

These rule-level datasets allow benchmarking the generalizability of the
approach across **multiple OPC UA domains**.

------------------------------------------------------------------------

### 🔍 Why This Structure?

-   **SAREF** is open → the full KG is included → allows end-to-end
    GraphRAG and SPARQL evaluation.
-   **Robotics & PackML** are confidential → only rule sentences &
    SPARQL ground truths are shared.
-   This design enables:
    -   Demonstration of the **complete pipeline** on a public KG.
    -   Evaluation on **real industrial rule datasets**.
    -   Compliance with data confidentiality requirements.

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
python schema_aware_rag.py.py   --ttl_file "../inputs/saref/saref_large.ttl"   --nlq "what is the instance of the temperature sensor?"
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
- `schema_aware_rag.py` → Schema-aware RAG  
- `lightweight_rag.py` → LLM baseline


---


