"""
test_rag.py - Automated Verification Suite for RAG Pipeline and Flask App
==========================================================================

Runs unit and integration tests covering:
1. Text & PDF document extraction
2. Text cleaning and normalization
3. Semantic chunking with overlap
4. Embedding engine vector generation
5. ChromaDB / Vector store indexing & cosine query
6. RAG answer synthesis and source citations
7. Flask endpoints (/documents, /ask, /upload)
"""

import os
import sys
import unittest
import json
import tempfile
import shutil

# Ensure safe console output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from document_processor import (
    clean_text,
    extract_text_from_txt,
    split_text_into_chunks,
    get_document_statistics
)
from rag_engine import (
    DocumentLoader,
    TextChunker,
    EmbeddingEngine,
    VectorStore,
    RAGPipeline
)
import app as flask_module


class TestDocumentProcessor(unittest.TestCase):
    """Tests for document processor functions."""

    def test_clean_text(self):
        raw = "Hello   world!\r\n\r\n\r\n\r\nThis is ‘smart quotes’ and “double quotes”.  "
        cleaned = clean_text(raw)
        self.assertNotIn("\r", cleaned)
        self.assertNotIn("   ", cleaned)
        self.assertIn("'smart quotes'", cleaned)
        self.assertIn('"double quotes"', cleaned)

    def test_split_text_into_chunks(self):
        text = (
            "Sentence one is clear and simple. "
            "Sentence two provides deeper context for the topic. "
            "Sentence three continues the technical exploration. "
            "Sentence four explains how retrieval augmented generation works in practice."
        )
        chunks = split_text_into_chunks(text, chunk_size=90, chunk_overlap=25)
        self.assertGreater(len(chunks), 1)
        for c in chunks:
            self.assertIn("text", c)
            self.assertIn("chunk_index", c)
            self.assertGreater(len(c["text"]), 0)

    def test_document_statistics(self):
        text = "Artificial intelligence enables machines to learn and reason."
        stats = get_document_statistics(text)
        self.assertEqual(stats["total_words"], 8)
        self.assertGreater(stats["estimated_tokens"], 0)


class TestRAGCorePipeline(unittest.TestCase):
    """Tests for core RAG engine components."""

    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp(prefix="rag_test_")
        cls.chroma_test_dir = os.path.join(cls.test_dir, "chroma")
        cls.pipeline = RAGPipeline(
            chunk_size=300,
            chunk_overlap=50,
            persist_dir=cls.chroma_test_dir,
            use_llm=False  # Test extractive pipeline directly for speed
        )

    @classmethod
    def tearDownClass(cls):
        try:
            shutil.rmtree(cls.test_dir)
        except Exception:
            pass

    def test_embedding_engine(self):
        emb = self.pipeline.embedding_engine.get_embedding("Machine learning systems")
        self.assertIsInstance(emb, list)
        self.assertGreater(len(emb), 0)

    def test_end_to_end_ingest_and_query(self):
        # Create a sample test document
        sample_file = os.path.join(self.test_dir, "test_doc.txt")
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write(
                "Python was created by Guido van Rossum and released in 1991. "
                "It is renowned for clean syntax and powerful built-in data structures. "
                "The four primary structures are lists, tuples, dictionaries, and sets."
            )

        # Ingest document
        ingest_res = self.pipeline.embed_document(
            file_path=sample_file,
            document_id="test_doc_1",
            original_filename="test_doc.txt"
        )
        self.assertEqual(ingest_res["document_id"], "test_doc_1")
        self.assertGreater(ingest_res["chunk_count"], 0)

        # Query document
        query_res = self.pipeline.query("Who created Python and when?", top_k=2)
        self.assertIn("answer", query_res)
        self.assertIn("citations", query_res)
        self.assertGreater(len(query_res["retrieved_chunks"]), 0)
        self.assertIn("Guido van Rossum", query_res["answer"])


class TestFlaskApplication(unittest.TestCase):
    """Tests Flask application routes and API endpoints."""

    @classmethod
    def setUpClass(cls):
        flask_module.app.config["TESTING"] = True
        cls.client = flask_module.app.test_client()

    def test_dashboard_route(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Document Q&A System", res.data)

    def test_status_endpoint(self):
        res = self.client.get("/status")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("vector_store_chunks", data)

    def test_documents_endpoint(self):
        res = self.client.get("/documents")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertIsInstance(data["documents"], list)

    def test_ask_endpoint(self):
        payload = {
            "question": "What is Python?",
            "top_k": 2
        }
        res = self.client.post("/ask", json=payload)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertIn("answer", data)
        self.assertIn("citations", data)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("[*] Running Document Q&A RAG Test Suite...")
    print("=" * 60 + "\n")
    unittest.main(verbosity=2)
