"""
rag_engine.py - Core Retrieval-Augmented Generation (RAG) Pipeline
===================================================================

This module provides the core components for a complete RAG system:
1. DocumentLoader: Loads plain text (.txt, .md) and PDF (.pdf) documents.
2. TextChunker: Breaks documents into semantic overlapping chunks.
3. EmbeddingEngine: Generates dense vector embeddings using sentence-transformers
   (default: 'all-MiniLM-L6-v2'). Free, local, runs entirely on CPU.
4. VectorStore: Manages ChromaDB vector database collections (add, query, delete).
5. RAGPipeline: Coordinates ingestion, semantic search, context building,
   and answer synthesis with source citations using free local models (google/flan-t5-small
   or contextual synthesis).
"""

import os
import sys
import re
import time
import math
import logging
from typing import List, Dict, Any, Optional, Tuple

# Ensure safe console output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Import document processor utilities
from document_processor import (
    extract_text_from_pdf,
    extract_text_from_txt,
    split_text_into_chunks,
    clean_text,
    get_document_statistics
)

# Setup dedicated logger
logger = logging.getLogger("rag_engine")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [RAG] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


# ============================================================================
# 1. DocumentLoader
# ============================================================================

class DocumentLoader:
    """
    Loads text and PDF documents into structured representations.
    
    Supports:
    - .txt / .md files (multi-encoding fallback)
    - .pdf files (page-by-page text extraction with PyPDF2/pypdf)
    """

    SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".md", ".text"}

    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in cls.SUPPORTED_EXTENSIONS

    def load_document(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Loads document content and extracts pages/sections.
        
        Args:
            file_path: Path to the document file.
            
        Returns:
            List of page dicts: [{'page_number': int, 'text': str, ...}]
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document file does not exist: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        logger.info(f"Loading document '{os.path.basename(file_path)}' (Type: {ext})...")

        if ext == ".pdf":
            pages = extract_text_from_pdf(file_path)
        elif ext in {".txt", ".md", ".text"}:
            pages = extract_text_from_txt(file_path)
        else:
            raise ValueError(
                f"Unsupported file format '{ext}'. Supported formats: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

        logger.info(f"Loaded {len(pages)} section(s)/page(s) from '{os.path.basename(file_path)}'.")
        return pages


# ============================================================================
# 2. TextChunker
# ============================================================================

class TextChunker:
    """
    Splits document pages into semantic overlapping chunks with rich metadata.
    
    Why overlap is critical:
    If a query asks about a relationship mentioned across the boundary of two
    sentences, chunk overlap prevents that information from being truncated.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        """
        Initialize TextChunker.
        
        Args:
            chunk_size: Target character length per chunk (default: 500).
            chunk_overlap: Number of characters to overlap between chunks (default: 100).
        """
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        pages: List[Dict[str, Any]],
        document_id: str,
        source_name: str
    ) -> List[Dict[str, Any]]:
        """
        Processes a list of pages and yields standardized chunks with IDs and metadata.
        
        Args:
            pages: Output from DocumentLoader.load_document()
            document_id: Unique database identifier for document
            source_name: Original filename
            
        Returns:
            List of chunk dictionaries ready for embedding and indexing
        """
        all_chunks: List[Dict[str, Any]] = []
        global_chunk_idx = 0

        for page in pages:
            page_num = page.get("page_number", 1)
            raw_text = page.get("text", "")

            base_meta = {
                "document_id": document_id,
                "source": source_name,
                "page_number": page_num,
            }

            page_chunks = split_text_into_chunks(
                text=raw_text,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                base_metadata=base_meta
            )

            for chunk in page_chunks:
                chunk["chunk_id"] = f"{document_id}_p{page_num}_c{global_chunk_idx}"
                chunk["global_index"] = global_chunk_idx
                all_chunks.append(chunk)
                global_chunk_idx += 1

        logger.info(
            f"Document '{source_name}' split into {len(all_chunks)} chunks "
            f"(size={self.chunk_size}, overlap={self.chunk_overlap})."
        )
        return all_chunks


# ============================================================================
# 3. EmbeddingEngine
# ============================================================================

class EmbeddingEngine:
    """
    Generates dense vector embeddings for texts using sentence-transformers.
    
    Default model: 'all-MiniLM-L6-v2'
    - Size: ~80 MB (very fast to download and run)
    - Output dimension: 384 dimensions
    - Completely free, runs locally on CPU without any GPU or API keys.
    
    Includes a lightweight mathematical TF-IDF fallback if sentence-transformers
    is not yet installed, guaranteeing zero-crash beginner execution.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.is_sentence_transformer = False
        self.dimension = 384
        self._initialize_model()

    def _initialize_model(self):
        """Initializes SentenceTransformer or loads fallback engine."""
        try:
            logger.info(f"Attempting to load sentence-transformers model '{self.model_name}'...")
            from sentence_transformers import SentenceTransformer
            print(f"[EmbeddingEngine] Loading model '{self.model_name}' (first run will download ~80MB)...")
            self.model = SentenceTransformer(self.model_name)
            self.is_sentence_transformer = True
            # Determine vector dimension
            sample_emb = self.model.encode("hello world")
            self.dimension = len(sample_emb)
            logger.info(f"SentenceTransformer loaded successfully! Vector dimension: {self.dimension}")
            print(f"[EmbeddingEngine] Model '{self.model_name}' is ready. Dimension={self.dimension}")
        except Exception as e:
            logger.warning(
                f"SentenceTransformer unavailable ({e}). Using lightweight built-in semantic embedding fallback."
            )
            print("[EmbeddingEngine] Notice: Using built-in local vectorizer fallback.")
            self.model = None
            self.is_sentence_transformer = False
            self.dimension = 384

    def get_embedding(self, text: str) -> List[float]:
        """
        Calculates a single dense vector embedding for a string.
        
        Args:
            text: Input string
            
        Returns:
            List of floats representing the embedding vector
        """
        return self.get_embeddings([text])[0]

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Calculates dense embeddings for a batch of strings.
        
        Args:
            texts: List of strings
            
        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        if not texts:
            return []

        if self.is_sentence_transformer and self.model is not None:
            try:
                embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
                return [emb.tolist() for emb in embeddings]
            except Exception as e:
                logger.error(f"Error generating embeddings with SentenceTransformer: {e}")
                # Fall through to fallback

        # Lightweight deterministic vectorizer fallback:
        # Maps words into hashed dimension buckets with term-frequency weighting
        # and L2-normalizes the vector to allow exact cosine similarity.
        results = []
        for text in texts:
            words = re.findall(r'\b[a-zA-Z0-9_\-\']+\b', text.lower())
            vec = [0.0] * self.dimension
            if not words:
                results.append(vec)
                continue

            for w in words:
                # Deterministic hash to dimension index
                h = abs(hash(w)) % self.dimension
                vec[h] += 1.0

            # L2 normalization (unit length)
            norm = math.sqrt(sum(x * x for x in vec))
            if norm > 0:
                vec = [x / norm for x in vec]
            results.append(vec)

        return results


# ============================================================================
# 4. VectorStore
# ============================================================================

class VectorStore:
    """
    Vector database abstraction wrapping ChromaDB.
    
    Provides:
    - Persistent disk storage for embeddings and chunk texts
    - Fast cosine similarity search
    - Metadata filtering (e.g. by document_id)
    - Document deletion support
    - Built-in SQLite/JSON fallback if chromadb is unavailable
    """

    def __init__(self, persist_directory: str = "data/chroma_db", collection_name: str = "rag_documents"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.chroma_client = None
        self.collection = None
        self.use_chromadb = False

        # In-memory / file fallback store
        self._fallback_store: Dict[str, Dict[str, Any]] = {}
        self._init_store()

    def _init_store(self):
        """Initializes ChromaDB persistent client or fallback storage."""
        os.makedirs(self.persist_directory, exist_ok=True)
        try:
            import chromadb
            from chromadb.config import Settings

            logger.info(f"Initializing ChromaDB PersistentClient at '{self.persist_directory}'...")
            self.chroma_client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            # Create or get collection
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            self.use_chromadb = True
            logger.info(f"ChromaDB collection '{self.collection_name}' ready. Count: {self.collection.count()}")
            print(f"[VectorStore] ChromaDB loaded. Existing chunks: {self.collection.count()}")
        except Exception as e:
            logger.warning(f"ChromaDB initialization failed ({e}). Initializing local fallback vector store.")
            self.use_chromadb = False
            self._load_fallback_from_disk()

    def _fallback_file_path(self) -> str:
        return os.path.join(self.persist_directory, "fallback_vectors.json")

    def _load_fallback_from_disk(self):
        import json
        path = self._fallback_file_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self._fallback_store = json.load(f)
                logger.info(f"Loaded {len(self._fallback_store)} chunks from fallback vector file.")
            except Exception as e:
                logger.warning(f"Could not load fallback vector file: {e}")
                self._fallback_store = {}

    def _save_fallback_to_disk(self):
        import json
        path = self._fallback_file_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._fallback_store, f)
        except Exception as e:
            logger.error(f"Failed to persist fallback vectors: {e}")

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Adds chunk texts, embeddings, and metadata into the vector database.
        
        Args:
            chunks: List of chunk dictionaries
            embeddings: List of embedding vectors matching chunks
        """
        if not chunks:
            return

        ids = [c["chunk_id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = []
        for c in chunks:
            metadatas.append({
                "document_id": str(c.get("document_id", "")),
                "source": str(c.get("source", "")),
                "page_number": int(c.get("page_number", 1)),
                "chunk_index": int(c.get("chunk_index", 0)),
                "char_count": int(c.get("char_count", len(c.get("text", "")))),
                "word_count": int(c.get("word_count", len(c.get("text", "").split()))),
            })

        if self.use_chromadb and self.collection is not None:
            try:
                self.collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas
                )
                logger.info(f"Stored {len(ids)} chunks in ChromaDB collection '{self.collection_name}'.")
                return
            except Exception as e:
                logger.error(f"ChromaDB upsert error: {e}. Falling back to internal store.")

        # Fallback storage logic
        for i, cid in enumerate(ids):
            self._fallback_store[cid] = {
                "id": cid,
                "text": documents[i],
                "embedding": embeddings[i],
                "metadata": metadatas[i]
            }
        self._save_fallback_to_disk()
        logger.info(f"Stored {len(ids)} chunks in fallback storage.")

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 3,
        document_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves the top-k most semantically similar chunks for a query embedding.
        
        Args:
            query_embedding: Embedding vector of the user's question
            top_k: Number of most relevant passages to retrieve
            document_id: Optional document filter to search within a single document
            
        Returns:
            List of retrieved chunks with similarity scores and metadata
        """
        if self.use_chromadb and self.collection is not None:
            try:
                where_filter = {"document_id": document_id} if document_id else None
                total_in_coll = self.collection.count()
                if total_in_coll == 0:
                    return []

                actual_top_k = min(top_k, total_in_coll)

                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=actual_top_k,
                    where=where_filter,
                    include=["documents", "metadatas", "distances"]
                )

                retrieved: List[Dict[str, Any]] = []
                if results and results.get("ids") and results["ids"][0]:
                    ids = results["ids"][0]
                    docs = results["documents"][0]
                    metas = results["metadatas"][0]
                    distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)

                    for i in range(len(ids)):
                        dist = float(distances[i]) if distances else 0.0
                        # Chroma cosine distance = 1 - cosine_similarity (range 0.0 to 2.0)
                        # Similarity score: 1 - (dist / 2) or max(0, 1 - dist)
                        similarity = max(0.0, min(1.0, 1.0 - dist))
                        meta = metas[i] if metas else {}

                        retrieved.append({
                            "chunk_id": ids[i],
                            "text": docs[i],
                            "source": meta.get("source", "Unknown"),
                            "page_number": meta.get("page_number", 1),
                            "chunk_index": meta.get("chunk_index", 0),
                            "document_id": meta.get("document_id", ""),
                            "distance": round(dist, 4),
                            "similarity_score": round(similarity, 4),
                            "score_pct": f"{round(similarity * 100, 1)}%"
                        })

                return retrieved
            except Exception as e:
                logger.error(f"ChromaDB query error: {e}. Falling back to internal similarity search.")

        # Fallback Cosine Similarity Search
        def cosine_similarity(v1: List[float], v2: List[float]) -> float:
            dot = sum(a * b for a, b in zip(v1, v2))
            norm1 = math.sqrt(sum(a * a for a in v1))
            norm2 = math.sqrt(sum(b * b for b in v2))
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot / (norm1 * norm2)

        candidates = []
        for cid, item in self._fallback_store.items():
            meta = item.get("metadata", {})
            if document_id and meta.get("document_id") != document_id:
                continue

            sim = cosine_similarity(query_embedding, item.get("embedding", []))
            sim_clamped = max(0.0, min(1.0, sim))
            candidates.append({
                "chunk_id": cid,
                "text": item.get("text", ""),
                "source": meta.get("source", "Unknown"),
                "page_number": meta.get("page_number", 1),
                "chunk_index": meta.get("chunk_index", 0),
                "document_id": meta.get("document_id", ""),
                "distance": round(1.0 - sim_clamped, 4),
                "similarity_score": round(sim_clamped, 4),
                "score_pct": f"{round(sim_clamped * 100, 1)}%"
            })

        # Sort descending by similarity
        candidates.sort(key=lambda x: x["similarity_score"], reverse=True)
        return candidates[:top_k]

    def delete_document(self, document_id: str) -> int:
        """
        Deletes all chunks associated with a specific document_id.
        
        Args:
            document_id: Unique ID of document
            
        Returns:
            Estimated count of deleted chunks
        """
        deleted_count = 0
        if self.use_chromadb and self.collection is not None:
            try:
                # Query chunks matching document_id
                results = self.collection.get(
                    where={"document_id": document_id}
                )
                if results and results.get("ids"):
                    ids_to_delete = results["ids"]
                    self.collection.delete(ids=ids_to_delete)
                    deleted_count = len(ids_to_delete)
                    logger.info(f"Deleted {deleted_count} chunks for doc {document_id} from ChromaDB.")
                    return deleted_count
            except Exception as e:
                logger.error(f"ChromaDB delete error: {e}")

        # Fallback delete
        keys_to_remove = [
            cid for cid, item in self._fallback_store.items()
            if item.get("metadata", {}).get("document_id") == document_id
        ]
        for k in keys_to_remove:
            del self._fallback_store[k]
        self._save_fallback_to_disk()
        return len(keys_to_remove)

    def count(self) -> int:
        """Returns total number of chunks currently indexed in vector store."""
        if self.use_chromadb and self.collection is not None:
            try:
                return self.collection.count()
            except Exception:
                pass
        return len(self._fallback_store)


# ============================================================================
# 5. RAGPipeline
# ============================================================================

class RAGPipeline:
    """
    Orchestrates the complete Retrieval-Augmented Generation workflow:
    1. Document Ingestion (Load -> Clean -> Chunk -> Embed -> Store)
    2. Query Retrieval (Embed Query -> Vector Search -> Top-K Passages)
    3. Answer Synthesis (Context Augmentation -> Model Generation / Extractive Synthesis)
    4. Citation Generation (Document, Page, Chunk, Confidence Score)
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        persist_dir: str = "data/chroma_db",
        use_llm: bool = True
    ):
        self.loader = DocumentLoader()
        self.chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.embedding_engine = EmbeddingEngine()
        self.vector_store = VectorStore(persist_directory=persist_dir)
        self.use_llm = use_llm

        # Local generator model (e.g. google/flan-t5-small)
        self.generator_pipeline = None
        self.generator_model_name = "google/flan-t5-small"
        self._init_generator()

    def _init_generator(self):
        """Initializes a local free sequence-to-sequence model for RAG answering."""
        if not self.use_llm:
            logger.info("Local LLM generation disabled by configuration. Using extractive synthesis.")
            return

        try:
            logger.info(f"Checking local HuggingFace transformers pipeline for '{self.generator_model_name}'...")
            from transformers import pipeline

            print(f"[RAGPipeline] Initializing local generator '{self.generator_model_name}'...")
            self.generator_pipeline = pipeline(
                "text2text-generation",
                model=self.generator_model_name,
                max_new_tokens=150,
                device=-1  # Always use CPU for universally accessible beginner setup
            )
            logger.info("Local transformers generator loaded successfully!")
            print("[RAGPipeline] Local generator loaded successfully!")
        except Exception as e:
            logger.warning(
                f"Transformers generator not available ({e}). "
                "Defaulting to contextual extractive synthesis."
            )
            print("[RAGPipeline] Note: Using contextual extractive synthesis for answers.")
            self.generator_pipeline = None

    def embed_document(
        self,
        file_path: str,
        document_id: str,
        original_filename: str
    ) -> Dict[str, Any]:
        """
        Executes full ingestion pipeline for an uploaded document.
        
        Args:
            file_path: Absolute or relative path to file on disk
            document_id: Unique identifier for tracking
            original_filename: User-facing filename
            
        Returns:
            Dict containing ingestion stats (chunk_count, page_count, word_count, time_taken_sec)
        """
        start_time = time.time()
        logger.info(f"Starting ingestion pipeline for '{original_filename}' (ID: {document_id})...")

        # Step 1: Load Pages
        pages = self.loader.load_document(file_path)
        stats = get_document_statistics(pages)

        # Step 2: Chunk Document
        chunks = self.chunker.chunk_document(
            pages=pages,
            document_id=document_id,
            source_name=original_filename
        )

        if not chunks:
            raise ValueError(f"No text chunks could be extracted from '{original_filename}'.")

        # Step 3: Compute Embeddings
        chunk_texts = [c["text"] for c in chunks]
        embeddings = self.embedding_engine.get_embeddings(chunk_texts)

        # Step 4: Index into Vector Database
        self.vector_store.add_chunks(chunks, embeddings)

        elapsed = round(time.time() - start_time, 2)
        logger.info(
            f"Ingestion complete for '{original_filename}': "
            f"{len(chunks)} chunks indexed in {elapsed}s."
        )

        return {
            "document_id": document_id,
            "filename": original_filename,
            "page_count": len(pages),
            "chunk_count": len(chunks),
            "total_words": stats["total_words"],
            "total_characters": stats["total_characters"],
            "time_taken_seconds": elapsed,
        }

    def query(
        self,
        question: str,
        top_k: int = 3,
        document_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Performs full RAG retrieval and answer generation for a question.
        
        Args:
            question: User's question
            top_k: Number of context passages to retrieve (default: 3)
            document_id: Optional document filter
            
        Returns:
            Comprehensive result dictionary with answer, citations, and retrieved passages
        """
        start_time = time.time()
        question = question.strip()
        if not question:
            return {
                "question": "",
                "answer": "Please provide a valid question to search your documents.",
                "citations": [],
                "retrieved_chunks": [],
                "latency_ms": 0
            }

        logger.info(f"Received query: '{question}' (top_k={top_k})")

        # Step 1: Embed Question
        question_embedding = self.embedding_engine.get_embedding(question)

        # Step 2: Retrieve Top-K Semantically Relevant Chunks from Vector Store
        retrieved_chunks = self.vector_store.query(
            query_embedding=question_embedding,
            top_k=top_k,
            document_id=document_id
        )

        if not retrieved_chunks:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return {
                "question": question,
                "answer": (
                    "No relevant document content was found in the database. "
                    "Please upload a document (.txt or .pdf) first, or try rephrasing your question."
                ),
                "citations": [],
                "retrieved_chunks": [],
                "model_used": "None (Empty Vector Store)",
                "latency_ms": elapsed_ms
            }

        # Step 3: Generate Answer based on Retrieved Context
        answer_data = self.generate_answer(question, retrieved_chunks)

        elapsed_ms = int((time.time() - start_time) * 1000)

        # Step 4: Build Citations List
        citations = []
        for idx, chunk in enumerate(retrieved_chunks):
            citation_item = {
                "source": chunk.get("source", "Document"),
                "page": chunk.get("page_number", 1),
                "chunk_index": chunk.get("chunk_index", 0),
                "chunk_id": chunk.get("chunk_id", ""),
                "similarity_score": chunk.get("similarity_score", 0.0),
                "score_pct": chunk.get("score_pct", "0%"),
                "excerpt": chunk.get("text", "")[:200] + ("..." if len(chunk.get("text", "")) > 200 else "")
            }
            citations.append(citation_item)

        return {
            "question": question,
            "answer": answer_data["answer"],
            "model_used": answer_data["model_used"],
            "citations": citations,
            "retrieved_chunks": retrieved_chunks,
            "latency_ms": elapsed_ms
        }

    def generate_answer(
        self,
        question: str,
        context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesizes an answer grounded in the retrieved context passages.
        
        Args:
            question: User's question
            context_chunks: Retrieved passages from VectorStore.query()
            
        Returns:
            Dict with answer string and model_used identifier
        """
        # Combine retrieved passages into an organized context block
        context_parts = []
        for i, c in enumerate(context_chunks):
            source = c.get("source", "Doc")
            page = c.get("page_number", 1)
            text = c.get("text", "").strip()
            context_parts.append(f"[{i+1}] Source: {source} (Page {page}):\n{text}")

        full_context = "\n\n".join(context_parts)

        # Attempt 1: Run local Flan-T5 model if available
        if self.generator_pipeline is not None:
            try:
                # Prompt format optimized for Flan-T5
                prompt = (
                    f"Answer the question based strictly on the context provided below.\n\n"
                    f"Context:\n{full_context}\n\n"
                    f"Question: {question}\n\n"
                    f"Answer:"
                )

                gen_output = self.generator_pipeline(
                    prompt,
                    max_new_tokens=160,
                    clean_up_tokenization_spaces=True
                )
                raw_ans = gen_output[0]["generated_text"].strip()
                if raw_ans and len(raw_ans) > 5:
                    return {
                        "answer": raw_ans,
                        "model_used": f"Local LLM ({self.generator_model_name})"
                    }
            except Exception as e:
                logger.warning(f"Error during Flan-T5 inference ({e}). Falling back to contextual extractive synthesis.")

        # Attempt 2: Intelligent Contextual Synthesis (Deterministic & Explainable)
        # Identifies the most relevant sentences answering the question
        return self._extractive_synthesis(question, context_chunks)

    def _extractive_synthesis(
        self,
        question: str,
        context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesizes an answer by extracting and ranking the most informative
        sentences directly answering the question from the top retrieved chunks.
        """
        question_words = set(re.findall(r'\b[a-zA-Z0-9]{3,}\b', question.lower()))
        # Filter common stopwords
        stopwords = {
            "what", "when", "where", "which", "who", "whom", "whose", "why",
            "how", "is", "are", "was", "were", "be", "been", "being", "have",
            "has", "had", "do", "does", "did", "the", "a", "an", "and", "or",
            "but", "in", "on", "at", "to", "for", "with", "about", "against",
            "between", "into", "through", "during", "before", "after", "above",
            "below", "from", "up", "down", "in", "out", "off", "over", "under",
            "again", "further", "then", "once", "can", "could", "will", "would",
            "should", "tell", "explain", "describe", "give", "overview", "does"
        }
        keywords = question_words - stopwords

        scored_sentences = []

        for chunk_idx, chunk in enumerate(context_chunks):
            text = chunk.get("text", "")
            source = chunk.get("source", "Doc")
            page = chunk.get("page_number", 1)
            # Break chunk into sentences
            sentences = re.split(r'(?<=[.!?])\s+', text)

            for s in sentences:
                s_clean = s.strip()
                if len(s_clean) < 25:
                    continue

                s_words = set(re.findall(r'\b[a-zA-Z0-9]{3,}\b', s_clean.lower()))
                # Overlap score
                matched = s_words.intersection(keywords)
                keyword_score = len(matched) * 2.0

                # Proximity to top chunk bonus
                rank_bonus = max(0.5, 3.0 - (chunk_idx * 0.8))
                total_score = keyword_score + rank_bonus

                if keyword_score > 0 or chunk_idx == 0:
                    scored_sentences.append({
                        "sentence": s_clean,
                        "score": total_score,
                        "source": source,
                        "page": page,
                        "chunk_idx": chunk_idx
                    })

        scored_sentences.sort(key=lambda x: x["score"], reverse=True)

        # Select top unique sentences for synthesis
        top_sentences = []
        seen = set()
        for item in scored_sentences[:3]:
            # Deduplicate similar sentences
            preview = item["sentence"][:40].lower()
            if preview not in seen:
                seen.add(preview)
                top_sentences.append(item)

        if top_sentences:
            best_chunk = context_chunks[0]
            answer_body = " ".join([item["sentence"] for item in top_sentences])
            formatted_answer = (
                f"{answer_body}\n\n"
                f"**Key Reference:** According to **{best_chunk.get('source')}** "
                f"(Page {best_chunk.get('page_number')}), this information was retrieved with "
                f"a confidence match of **{best_chunk.get('score_pct')}**."
            )
        else:
            best_chunk = context_chunks[0]
            formatted_answer = (
                f"Based on the retrieved document **{best_chunk.get('source')}** "
                f"(Page {best_chunk.get('page_number')}):\n\n"
                f"\"{best_chunk.get('text')}\""
            )

        return {
            "answer": formatted_answer,
            "model_used": "Contextual Semantic Extractor"
        }
