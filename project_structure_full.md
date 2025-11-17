# 📁 Project Structure

``` text
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
   ├─ mini_rag.py
   ├─ node2vec_rag.py
   ├─ llamaindex_rag.py
   └─ rag_module/
```

# 📘 Explanation of the Input Data

## **1. `inputs/saref/` --- Full Open Knowledge Graph**

This folder contains all data required for **end-to-end GraphRAG
experiments** on an openly available ontology.

-   **`saref_large.ttl`**\
    Complete SAREF knowledge graph (ontology + instances) for
    large-scale subgraph extraction, NLQ→SPARQL generation, and
    evaluation.

-   **`saref_large.txt`**\
    Plain-text dump of the same KG for text-only RAG baselines (e.g.,
    MiniRAG).

-   **`competency_questions.xlsx`**\
    Benchmark with:

    -   natural-language competency questions (NLQs)\
    -   expected answer types\
    -   optional ground-truth SPARQL queries

This folder supports **full GraphRAG pipeline demonstrations** on a
publicly accessible dataset.

------------------------------------------------------------------------

## **2. `inputs/robotics/` --- OPC UA Robotics (Confidential KG)**

The OPC UA Robotics Companion Specification is **confidential**, so the
KG itself cannot be shared.

Instead, this folder provides:

-   **`robotics_compliance_rules.xlsx`**
    -   Rule sentences extracted from the official Companion
        Specification\
    -   Ground-truth SPARQL queries\
    -   Additional rule metadata (optional)

This dataset enables **industrial-grade evaluation** of NLQ→SPARQL and
rule-validation logic without exposing the confidential Robotics model.

------------------------------------------------------------------------

## **3. `inputs/packml/` --- OPC UA PackML (Confidential KG)**

Similarly, the PackML Companion Specification is proprietary. Therefore:

-   **`packml_compliance_rules.xlsx`**
    -   Rule sentences from the PackML specification\
    -   Corresponding ground-truth SPARQL queries\
    -   Optional annotations

These rule-level datasets allow benchmarking the generalizability of the
approach across **multiple OPC UA domains**.

------------------------------------------------------------------------

## 🔍 Why This Structure?

-   **SAREF** is open → the full KG is included → allows end-to-end
    GraphRAG and SPARQL evaluation.
-   **Robotics & PackML** are confidential → only rule sentences &
    SPARQL ground truths are shared.
-   This design enables:
    -   Demonstration of the **complete pipeline** on a public KG.
    -   Evaluation on **real industrial rule datasets**.
    -   Compliance with data confidentiality requirements.
