"""
app.py - Main Flask Application for Document Q&A RAG System
============================================================

This is the main entry point for the Document Q&A system.
Features:
- Runs a local web server on port 5006
- Handles document uploads (.txt, .pdf, .md)
- Processes, chunks, and indexes documents into ChromaDB
- Provides an interactive Q&A interface with source citations
- Stores document metadata and search history in SQLite
- Supports sample document preloading for instant testing
"""

import os
import sys
import uuid
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Ensure safe console output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename

# Import the core RAG pipeline
from rag_engine import RAGPipeline

# ============================================================================
# Application Configuration & Logging
# ============================================================================

app = Flask(__name__)
app.config["SECRET_KEY"] = "rag-document-qa-super-secret-key-2026"
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB max upload limit

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DATA_FOLDER = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_FOLDER, "rag_documents.db")
CHROMA_DIR = os.path.join(DATA_FOLDER, "chroma_db")
SAMPLE_DOCS_DIR = os.path.join(BASE_DIR, "sample_documents")

ALLOWED_EXTENSIONS = {"txt", "pdf", "md"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("rag_app")


# ============================================================================
# SQLite Database Management
# ============================================================================

def get_db_connection():
    """Returns a connection to the SQLite metadata database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enables column access by name
    return conn


def init_sqlite_db():
    """Initializes the SQLite database schema if tables do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Documents metadata table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            file_type TEXT NOT NULL,
            chunk_count INTEGER DEFAULT 0,
            page_count INTEGER DEFAULT 1,
            word_count INTEGER DEFAULT 0,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'indexed'
        );
    """)

    # Query history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            model_used TEXT,
            top_k INTEGER DEFAULT 3,
            latency_ms INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()
    logger.info("SQLite metadata database initialized successfully.")


# Initialize SQLite tables on startup
init_sqlite_db()


# ============================================================================
# RAG Pipeline Initialization
# ============================================================================

print("\n" + "=" * 60)
print("[*] Initializing Document Q&A RAG System...")
print("=" * 60)

# Instantiate the central RAG pipeline
rag = RAGPipeline(
    chunk_size=500,
    chunk_overlap=100,
    persist_dir=CHROMA_DIR,
    use_llm=True
)

print("=" * 60)
print("[+] RAG Pipeline initialized and ready!")
print("=" * 60 + "\n")
print("=" * 60 + "\n")


def allowed_file(filename: str) -> bool:
    """Checks if the uploaded file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def auto_seed_sample_documents():
    """
    Automatically indexes sample documents if the database is currently empty.
    Allows beginners to immediately test questions without initial manual uploads.
    """
    conn = get_db_connection()
    doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    conn.close()

    if doc_count > 0:
        return

    if not os.path.exists(SAMPLE_DOCS_DIR):
        return

    sample_files = [f for f in os.listdir(SAMPLE_DOCS_DIR) if allowed_file(f)]
    if not sample_files:
        return

    logger.info(f"Empty database detected. Auto-indexing {len(sample_files)} sample documents...")
    print("[RAG] Auto-indexing sample documents for immediate testing...")

    for fname in sample_files:
        src_path = os.path.join(SAMPLE_DOCS_DIR, fname)
        doc_id = str(uuid.uuid4())[:8]
        ext = fname.rsplit(".", 1)[1].lower()
        size_bytes = os.path.getsize(src_path)

        try:
            stats = rag.embed_document(
                file_path=src_path,
                document_id=doc_id,
                original_filename=fname
            )

            conn = get_db_connection()
            conn.execute("""
                INSERT INTO documents (
                    id, filename, original_name, file_path, file_size, 
                    file_type, chunk_count, page_count, word_count, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_id, fname, fname, src_path, size_bytes,
                ext, stats["chunk_count"], stats["page_count"], stats["total_words"], "indexed"
            ))
            conn.commit()
            conn.close()
            print(f"[RAG] Successfully indexed sample document: '{fname}' ({stats['chunk_count']} chunks)")
        except Exception as e:
            logger.error(f"Failed to auto-index sample document '{fname}': {e}")


# Run auto-seed
auto_seed_sample_documents()


# ============================================================================
# Application Routes
# ============================================================================

@app.route("/", methods=["GET"])
def dashboard():
    """
    Renders the main single-page dashboard.
    Displays upload zone, document list, Q&A interface, and system stats.
    """
    conn = get_db_connection()
    docs = conn.execute("SELECT * FROM documents ORDER BY upload_date DESC").fetchall()
    recent_queries = conn.execute(
        "SELECT * FROM queries ORDER BY created_at DESC LIMIT 5"
    ).fetchall()
    conn.close()

    total_chunks = rag.vector_store.count()
    vector_backend = "ChromaDB" if rag.vector_store.use_chromadb else "Local VectorStore"
    embedding_backend = (
        f"sentence-transformers ({rag.embedding_engine.model_name})"
        if rag.embedding_engine.is_sentence_transformer
        else "Local Semantic Vectorizer"
    )
    generator_backend = (
        rag.generator_model_name
        if rag.generator_pipeline is not None
        else "Semantic Extractive Synthesizer"
    )

    system_stats = {
        "document_count": len(docs),
        "chunk_count": total_chunks,
        "vector_backend": vector_backend,
        "embedding_backend": embedding_backend,
        "generator_backend": generator_backend,
        "port": 5006
    }

    return render_template(
        "dashboard.html",
        documents=docs,
        recent_queries=recent_queries,
        stats=system_stats
    )


@app.route("/upload", methods=["POST"])
def upload_document():
    """
    Uploads and processes one or multiple documents.
    Extracts text, splits into chunks, computes embeddings, and indexes in ChromaDB.
    """
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part in request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "error": f"Unsupported file type. Please upload one of: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400

    original_filename = secure_filename(file.filename)
    doc_id = str(uuid.uuid4())[:8]
    ext = original_filename.rsplit(".", 1)[1].lower()
    stored_filename = f"{doc_id}_{original_filename}"
    file_path = os.path.join(UPLOAD_FOLDER, stored_filename)

    try:
        # Save file to disk
        file.save(file_path)
        file_size = os.path.getsize(file_path)

        # Ingest into RAG pipeline
        ingest_stats = rag.embed_document(
            file_path=file_path,
            document_id=doc_id,
            original_filename=original_filename
        )

        # Record metadata in SQLite
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO documents (
                id, filename, original_name, file_path, file_size, 
                file_type, chunk_count, page_count, word_count, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id, stored_filename, original_filename, file_path,
            file_size, ext, ingest_stats["chunk_count"],
            ingest_stats["page_count"], ingest_stats["total_words"], "indexed"
        ))
        conn.commit()
        conn.close()

        logger.info(f"Document '{original_filename}' successfully uploaded and indexed.")
        return jsonify({
            "success": True,
            "message": f"Successfully processed '{original_filename}' into {ingest_stats['chunk_count']} chunks.",
            "document": {
                "id": doc_id,
                "original_name": original_filename,
                "chunks": ingest_stats["chunk_count"],
                "pages": ingest_stats["page_count"],
                "words": ingest_stats["total_words"],
                "size_kb": round(file_size / 1024, 1)
            }
        })

    except Exception as e:
        logger.error(f"Error processing upload '{original_filename}': {e}", exc_info=True)
        # Clean up failed file if it exists
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        return jsonify({"success": False, "error": f"Failed to process document: {str(e)}"}), 500


@app.route("/ask", methods=["POST"])
def ask_question():
    """
    RAG Question-Answering endpoint.
    Accepts JSON: {"question": "...", "top_k": 3, "document_id": null}
    Retrieves most semantically relevant chunks and generates an answer with citations.
    """
    data = request.get_json(silent=True) or request.form

    question = data.get("question", "").strip()
    if not question:
        return jsonify({"success": False, "error": "Question cannot be empty"}), 400

    try:
        top_k = int(data.get("top_k", 3))
        top_k = max(1, min(10, top_k))  # Clamp between 1 and 10
    except (ValueError, TypeError):
        top_k = 3

    doc_id_filter = data.get("document_id") or None
    if doc_id_filter == "":
        doc_id_filter = None

    try:
        # Run RAG Query
        result = rag.query(
            question=question,
            top_k=top_k,
            document_id=doc_id_filter
        )

        # Log query to SQLite history
        try:
            conn = get_db_connection()
            conn.execute("""
                INSERT INTO queries (question, answer, model_used, top_k, latency_ms)
                VALUES (?, ?, ?, ?, ?)
            """, (
                question,
                result["answer"],
                result.get("model_used", "Standard"),
                top_k,
                result.get("latency_ms", 0)
            ))
            conn.commit()
            conn.close()
        except Exception as db_err:
            logger.warning(f"Failed to record query to SQLite history: {db_err}")

        return jsonify({
            "success": True,
            "question": result["question"],
            "answer": result["answer"],
            "model_used": result.get("model_used", "Local RAG"),
            "citations": result.get("citations", []),
            "retrieved_chunks": result.get("retrieved_chunks", []),
            "latency_ms": result.get("latency_ms", 0)
        })

    except Exception as e:
        logger.error(f"Error handling query '{question}': {e}", exc_info=True)
        return jsonify({"success": False, "error": f"RAG Query execution failed: {str(e)}"}), 500


@app.route("/documents", methods=["GET"])
def list_documents():
    """Returns a JSON list of all indexed documents."""
    conn = get_db_connection()
    docs = conn.execute("SELECT * FROM documents ORDER BY upload_date DESC").fetchall()
    conn.close()

    docs_list = [
        {
            "id": d["id"],
            "original_name": d["original_name"],
            "file_type": d["file_type"],
            "file_size": d["file_size"],
            "chunk_count": d["chunk_count"],
            "page_count": d["page_count"],
            "word_count": d["word_count"],
            "upload_date": d["upload_date"],
            "status": d["status"]
        }
        for d in docs
    ]
    return jsonify({"success": True, "count": len(docs_list), "documents": docs_list})


@app.route("/documents/<doc_id>", methods=["DELETE", "POST"])
def delete_document(doc_id: str):
    """
    Removes a document from SQLite, deletes its chunks from ChromaDB,
    and removes the file from the uploads directory.
    """
    conn = get_db_connection()
    doc = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()

    if not doc:
        conn.close()
        return jsonify({"success": False, "error": f"Document ID '{doc_id}' not found"}), 404

    file_path = doc["file_path"]
    original_name = doc["original_name"]

    try:
        # Delete from ChromaDB / Vector Store
        deleted_chunks = rag.vector_store.delete_document(doc_id)

        # Delete from SQLite
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
        conn.close()

        # Delete physical file
        if os.path.exists(file_path) and "uploads" in file_path:
            try:
                os.remove(file_path)
            except Exception as fe:
                logger.warning(f"Could not delete physical file: {fe}")

        logger.info(f"Deleted document '{original_name}' (ID: {doc_id}, Chunks: {deleted_chunks}).")

        # Support both JSON response and form submission redirect
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return jsonify({
                "success": True,
                "message": f"Document '{original_name}' and its {deleted_chunks} chunks removed.",
                "deleted_chunks": deleted_chunks
            })
        return redirect(url_for("dashboard"))

    except Exception as e:
        conn.close()
        logger.error(f"Error deleting document '{doc_id}': {e}", exc_info=True)
        return jsonify({"success": False, "error": f"Failed to delete document: {str(e)}"}), 500


@app.route("/preload-samples", methods=["POST"])
def preload_samples():
    """Forces reloading or seeding of sample documents from sample_documents/."""
    if not os.path.exists(SAMPLE_DOCS_DIR):
        return jsonify({"success": False, "error": "Sample documents directory missing"}), 404

    sample_files = [f for f in os.listdir(SAMPLE_DOCS_DIR) if allowed_file(f)]
    loaded_docs = []

    for fname in sample_files:
        src_path = os.path.join(SAMPLE_DOCS_DIR, fname)
        doc_id = str(uuid.uuid4())[:8]
        ext = fname.rsplit(".", 1)[1].lower()
        size_bytes = os.path.getsize(src_path)

        try:
            stats = rag.embed_document(
                file_path=src_path,
                document_id=doc_id,
                original_filename=fname
            )

            conn = get_db_connection()
            conn.execute("""
                INSERT INTO documents (
                    id, filename, original_name, file_path, file_size, 
                    file_type, chunk_count, page_count, word_count, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_id, fname, fname, src_path, size_bytes,
                ext, stats["chunk_count"], stats["page_count"], stats["total_words"], "indexed"
            ))
            conn.commit()
            conn.close()
            loaded_docs.append(fname)
        except Exception as e:
            logger.error(f"Error loading sample file '{fname}': {e}")

    return jsonify({
        "success": True,
        "message": f"Preloaded {len(loaded_docs)} sample document(s).",
        "loaded": loaded_docs
    })


@app.route("/status", methods=["GET"])
def system_status():
    """Returns real-time health and configuration metrics of the RAG system."""
    conn = get_db_connection()
    doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    conn.close()

    return jsonify({
        "status": "healthy",
        "documents_count": doc_count,
        "vector_store_chunks": rag.vector_store.count(),
        "vector_backend": "ChromaDB" if rag.vector_store.use_chromadb else "Local Store",
        "embedding_model": rag.embedding_engine.model_name,
        "embedding_dimension": rag.embedding_engine.dimension,
        "llm_model": rag.generator_model_name if rag.generator_pipeline else "Extractive Synthesizer",
        "python_version": sys.version.split()[0],
        "port": 5006
    })


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    port = 5006
    print(f"\n" + "=" * 60)
    print(f"[+] Document Q&A System is running at: http://localhost:{port}")
    print(f"[+] Open your web browser to test uploading documents and asking questions.")
    print(f"=" * 60 + "\n")

    app.run(host="0.0.0.0", port=port, debug=False)
