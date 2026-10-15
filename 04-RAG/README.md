# 🧠 Document Q&A System: Beginner-Friendly RAG Project

A complete, production-ready **Retrieval-Augmented Generation (RAG)** application built in Python and Flask. This project lets you upload text and PDF documents, automatically splits them into semantic chunks, indexes them into a local vector database, and answers user questions with **direct source citations**.

> **No paid API keys required!** This project runs entirely on free, open-source models on your local CPU.

---

## 📑 Table of Contents

1. [What is RAG? (Beginner Explanation)](#what-is-rag)
2. [Why RAG? The Core Problems It Solves](#why-rag)
3. [Key Concepts Demystified](#key-concepts-demystified)
4. [Architecture & ASCII Pipeline Diagram](#architecture-diagram)
5. [How Embeddings Work](#how-embeddings-work)
6. [How Vector Similarity Search Works](#how-vector-similarity-search-works)
7. [Prerequisites](#prerequisites)
8. [Step-by-Step Setup Guide (Windows)](#step-by-step-setup)
9. [How to Run and Test](#how-to-run-and-test)
10. [End-to-End Query Walkthrough](#end-to-end-query-walkthrough)
11. [Chunking Strategies Explained](#chunking-strategies)
12. [Comparison: RAG vs. Fine-Tuning vs. Prompt Engineering](#rag-vs-fine-tuning-vs-prompt-engineering)
13. [Performance Tips](#performance-tips)
14. [Troubleshooting & Common Errors](#troubleshooting)
15. [Beginner Challenges & Exercises](#learning-exercises)

---

## 1. What is RAG? <a name="what-is-rag"></a>

**RAG** stands for **Retrieval-Augmented Generation**.

### The Student Exam Analogy 🎓
Imagine two students taking a challenging final exam:

* **Student A (Standard LLM / Closed-Book Exam):** Must answer every question purely from memory. If they studied two years ago, they won't know anything that happened last month. If they can't remember a specific fact, they might confidently make something up (a *hallucination*).
* **Student B (RAG / Open-Book Exam):** Has a library of reference textbooks open on their desk. When asked a question, they:
  1. **Retrieve** the exact book pages containing relevant facts.
  2. **Read** those specific excerpts.
  3. **Generate** an answer grounded in the text, citing the book and page number.

**RAG turns an AI model from Student A into Student B.**

---

## 2. Why RAG? The Core Problems It Solves <a name="why-rag"></a>

Standard Large Language Models (LLMs) suffer from three critical bottlenecks:

| Problem | Standard AI | With RAG |
| :--- | :--- | :--- |
| **Hallucination** | Fabricates plausible-sounding but false answers when uncertain. | Grounded strictly in factual reference documents. |
| **Knowledge Cutoff** | Knows only what was in its training data (months or years old). | Instantly updated simply by dropping in new files. |
| **Private Data** | Cannot access proprietary company reports or personal PDFs. | Securely indexes local, private documents without cloud sharing. |
| **Explainability** | Cannot tell you *where* or *how* it learned a specific answer. | Highlights exact source document, page, and chunk index. |

---

## 3. Key Concepts Demystified <a name="key-concepts-demystified"></a>

1. **Document Ingestion**: Reading files (`.txt`, `.pdf`, `.md`) and extracting clean, raw text.
2. **Chunking**: Breaking a massive 50-page document into bite-sized, overlapping segments (e.g., 500 characters each).
3. **Embeddings**: Converting words and sentences into numerical lists (vectors) that mathematically capture semantic meaning.
4. **Vector Database**: A specialized database (like **ChromaDB**) engineered to index high-dimensional vectors and retrieve nearest neighbors in milliseconds.
5. **Semantic Search**: Finding text passages based on **meaning and concept** rather than exact keyword matching (e.g., searching for "automobile repairs" matches text about "fixing cars").
6. **Context Window**: The maximum amount of text an AI model can read at one time. RAG feeds only the top 3–5 most relevant chunks into this window.
7. **Grounding & Citations**: Providing the user with the exact origin of each fact (filename, page number, confidence percentage).

---

## 4. Architecture & ASCII Pipeline Diagram <a name="architecture-diagram"></a>

```
                     DOCUMENT INGESTION PIPELINE (Offline / On Upload)
                     =================================================

  +------------------+      +--------------------+      +----------------------+
  |  Raw Documents   | ---> |  DocumentProcessor | ---> |     Text Chunker     |
  | (.txt, .pdf, .md)|      |  (Text extraction) |      | (500 chars + overlap)|
  +------------------+      +--------------------+      +----------------------+
                                                                   |
                                                                   v
  +------------------+      +--------------------+      +----------------------+
  | Vector Database  | <--- |     ChromaDB       | <--- |   Embedding Engine   |
  |  (data/chroma_db)|      |  (Vector indexing) |      | (all-MiniLM-L6-v2)   |
  +------------------+      +--------------------+      +----------------------+


                      QUERY & GENERATION PIPELINE (Online / On Ask)
                      =============================================

                                  +----------------------+
                                  |    User Question     |
                                  | ("What is PaaS in   |
                                  |  cloud computing?")  |
                                  +----------------------+
                                             |
                                             v
                                  +----------------------+
                                  |   Embed Question     |
                                  | (384-d dense vector) |
                                  +----------------------+
                                             |
                                             v
                                  +----------------------+
                                  | Cosine Vector Search |
                                  | (Query ChromaDB)     |
                                  +----------------------+
                                             |
                                             v
                                  +----------------------+
                                  | Top-3 Chunks Retrieved
                                  | (Scores: 91%, 86%...) |
                                  +----------------------+
                                             |
                                             v
                                  +----------------------+
                                  | Grounded Synthesis   |
                                  | (Template/Flan-T5)   |
                                  +----------------------+
                                             |
                                             v
                                  +------------------------------------+
                                  | Answer + Verified Source Citations |
                                  | [Page 1, cloud_computing.txt]      |
                                  +------------------------------------+
```

---

## 5. How Embeddings Work <a name="how-embeddings-work"></a>

Computers cannot understand the dictionary definitions of words. Instead, an embedding model turns human language into lists of numbers called **vectors**.

In this project, our embedding model (`all-MiniLM-L6-v2`) converts any passage of text into a list of **384 numbers**:

```
"Machine learning algorithm" -> [ 0.042, -0.129,  0.301, ..., -0.054 ]
"Artificial intelligence"    -> [ 0.039, -0.118,  0.298, ..., -0.061 ]
"Chocolate chip cookies"     -> [-0.210,  0.450, -0.012, ...,  0.180 ]
```

Notice how "Machine learning algorithm" and "Artificial intelligence" produce numbers that are very close to each other, while "Chocolate chip cookies" produces completely different values.

---

## 6. How Vector Similarity Search Works <a name="how-vector-similarity-search-works"></a>

To find the best answers, the system measures the **angle** between the question's vector ($\vec{Q}$) and each stored chunk's vector ($\vec{C}$) using **Cosine Similarity**:

$$\text{Cosine Similarity} = \frac{\vec{Q} \cdot \vec{C}}{\|\vec{Q}\| \|\vec{C}\|}$$

* **Score = 1.0 (100% match)**: Vectors point in identical directions (identical meaning).
* **Score = 0.0 (0% match)**: Vectors are completely orthogonal (unrelated topics).

ChromaDB uses Hierarchical Navigable Small World (HNSW) indexing to compare vectors across millions of documents in a fraction of a millisecond.

---

## 7. Prerequisites <a name="prerequisites"></a>

- **OS**: Windows 10/11, macOS, or Linux.
- **Python**: Version 3.8 to 3.13.
- **RAM**: Minimum 4 GB RAM.
- **Storage**: ~500 MB for local model caches.
- **Internet**: Required on first run to download model weights; runs 100% offline afterwards.

---

## 8. Step-by-Step Setup Guide (Windows) <a name="step-by-step-setup"></a>

Open **PowerShell** or **Command Prompt** and follow these commands:

### Step 1: Navigate to the Project Folder
```powershell
cd "c:\Users\itzme\Desktop\All Stacks\04-RAG"
```

### Step 2: Create a Virtual Environment
```powershell
python -m venv .venv
```

### Step 3: Activate the Virtual Environment
On Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```
*(If PowerShell shows an execution policy error, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

On Windows Command Prompt (CMD):
```cmd
.venv\Scripts\activate.bat
```

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 9. How to Run and Test <a name="how-to-run-and-test"></a>

### Start the Application
```powershell
python app.py
```

You will see output similar to:
```
============================================================
🚀 Initializing Document Q&A RAG System...
============================================================
[EmbeddingEngine] Loading model 'all-MiniLM-L6-v2'...
[VectorStore] ChromaDB loaded. Existing chunks: 24
[RAG] Auto-indexing sample documents for immediate testing...
[RAG] Successfully indexed sample document: 'ai_basics.txt' (8 chunks)
[RAG] Successfully indexed sample document: 'python_guide.txt' (7 chunks)
[RAG] Successfully indexed sample document: 'cloud_computing.txt' (9 chunks)
============================================================
✅ RAG Pipeline initialized and ready!
============================================================

🌟 Document Q&A System is running at: http://localhost:5006
📄 Open your web browser to test uploading documents and asking questions.
```

### Open Your Web Browser
Open your browser and navigate to:
👉 **[http://localhost:5006](http://localhost:5006)**

---

## 10. End-to-End Query Walkthrough <a name="end-to-end-query-walkthrough"></a>

Here is what happens when you click the question chip **"What is the difference between Narrow AI and General AI?"**:

1. **Client Request**: Browser sends an HTTP `POST /ask` with `{"question": "What is the difference between Narrow AI and General AI?", "top_k": 3}`.
2. **Question Embedding**: The EmbeddingEngine converts the question string into a 384-dimensional float vector.
3. **ChromaDB Vector Query**: The VectorStore searches all indexed chunks and calculates cosine similarities.
4. **Top-K Selection**: ChromaDB returns the 3 closest matches:
   - *Chunk 1:* `ai_basics.txt`, Page 1, Chunk 1 (Score: 92.4%)
   - *Chunk 2:* `ai_basics.txt`, Page 1, Chunk 2 (Score: 84.1%)
   - *Chunk 3:* `python_guide.txt`, Page 1, Chunk 5 (Score: 41.2%)
5. **Context Augmentation**: Chunks 1 and 2 are packaged into a structured context block.
6. **Answer Synthesis**: The answer generator extracts key facts and formulates an answer.
7. **Response with Citations**: The frontend displays the synthesized answer, along with citation cards highlighting `ai_basics.txt` (Page 1) and match scores.

---

## 11. Chunking Strategies Explained <a name="chunking-strategies"></a>

| Strategy | Description | Best Used For |
| :--- | :--- | :--- |
| **Fixed-Size Chunking** | Splits text strictly every $N$ characters (e.g. 500 chars). | Simple baseline, fast. |
| **Sentence-Aware Chunking (Used Here)** | Searches for sentence boundaries (`.`, `!`, `?`) near the chunk threshold so sentences aren't cut mid-thought. | Articles, guides, textbooks. |
| **Sliding Window with Overlap** | Backtracks 100 characters before starting the next chunk so facts spanning borders aren't lost. | Technical documentation and legal contracts. |

---

## 12. Comparison: RAG vs. Fine-Tuning vs. Prompt Engineering <a name="rag-vs-fine-tuning-vs-prompt-engineering"></a>

| Dimension | Prompt Engineering | Retrieval-Augmented Generation (RAG) | Fine-Tuning |
| :--- | :--- | :--- | :--- |
| **Compute Cost** | Lowest (zero training) | Very Low (CPU embeddings) | High (requires GPUs) |
| **Data Freshness** | Manual copy-pasting | Real-time (upload new files anytime) | Static (requires retraining) |
| **Source Citations** | None | Direct and transparent | None |
| **Hallucination Risk**| Moderate | Lowest (grounded in context) | Moderate |
| **Best For** | Ad-hoc queries | Knowledge bases, document search, enterprise manuals | Adapting tone, style, or specific grammar |

---

## 13. Performance Tips <a name="performance-tips"></a>

1. **Adjust Chunk Size**:
   - For short, fact-dense FAQs: Use smaller chunks (200–300 characters).
   - For long narrative chapters: Use larger chunks (700–1000 characters).
2. **Adjust Top-K**:
   - Retrieve 2–3 chunks for targeted factual queries.
   - Retrieve 5–7 chunks for broad summaries.
3. **Persist ChromaDB**: The database automatically writes to `data/chroma_db/`, so vectors survive server restarts without re-embedding.

---

## 14. Troubleshooting & Common Errors <a name="troubleshooting"></a>

### Error: `No module named 'flask'`
* **Solution**: Ensure your virtual environment is active:
  ```powershell
  .venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

### Error: `Address already in use` on port 5006
* **Solution**: Another program is using port 5006. Open `app.py` and change `port = 5006` to `port = 5007`.

### Error: PDF extracts blank text
* **Cause**: The PDF consists of scanned images without an OCR text layer.
* **Solution**: Ensure your PDF has selectable text. For scanned PDFs, run an OCR tool (e.g., Tesseract OCR) prior to upload.

---

## 15. Beginner Challenges & Exercises <a name="learning-exercises"></a>

Ready to level up your RAG skills? Try these hands-on challenges:

1. **Challenge 1: Add Word Export** — Add an "Export Answer to Word/Markdown" button to save Q&A results.
2. **Challenge 2: Query Threshold Filter** — Filter out retrieved chunks whose cosine similarity score is below 60%.
3. **Challenge 3: Keyword Search Hybrid** — Combine vector search with classic BM25 keyword search (Hybrid Search).
4. **Challenge 4: Multi-File Querying** — Upload 5 research papers and ask a question that compares insights across all 5 documents simultaneously!
