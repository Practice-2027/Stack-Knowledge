"""
document_processor.py - Document Processing Utilities for RAG
==============================================================

This module handles:
1. Text extraction from PDF documents using PyPDF2 / pypdf.
2. Robust text extraction from plain text files with encoding fallbacks.
3. Text cleaning, normalization, and sanitization.
4. Semantic chunking with configurable chunk size, overlap, and rich metadata.
5. Statistical analysis (word counts, estimated tokens, reading time).

Every chunk produced contains metadata tracing back to its original document,
page number, and chunk index, enabling precise citations in RAG answers.
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional, Tuple

# Configure logging for document processing
logger = logging.getLogger("document_processor")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [DocProcessor] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def clean_text(text: str) -> str:
    """
    Cleans and normalizes raw text for embedding and retrieval.
    
    Operations performed:
    - Normalizes line breaks (converts CRLF to LF)
    - Replaces non-breaking and irregular whitespace with standard spaces
    - Collapses consecutive whitespace characters (spaces/tabs) into a single space
    - Strips excessive blank lines while preserving paragraph boundaries
    - Normalizes common unicode quotation marks and dashes
    - Trims leading and trailing whitespace
    
    Args:
        text: Raw input string from document loader
        
    Returns:
        Cleaned, normalized string ready for chunking
    """
    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Normalize unicode quotes and hyphens
    text = re.sub(r'[\u2018\u2019]', "'", text)
    text = re.sub(r'[\u201C\u201D]', '"', text)
    text = re.sub(r'[\u2013\u2014]', '-', text)
    text = text.replace("\u00a0", " ")  # Non-breaking space

    # Remove non-printable control characters except standard whitespace
    text = "".join(ch for ch in text if ch == "\n" or ch == "\t" or (ord(ch) >= 32 and ord(ch) != 127))

    # Collapse horizontal spaces/tabs into a single space
    text = re.sub(r'[ \t]+', ' ', text)

    # Collapse more than two consecutive newlines into double newlines (paragraphs)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Trim leading/trailing whitespace
    return text.strip()


def extract_text_from_txt(file_path: str) -> List[Dict[str, Any]]:
    """
    Reads a plain text file using multiple character encoding fallbacks.
    
    Handles UTF-8, UTF-8 with BOM, Latin-1, and Windows-1252 to ensure
    seamless processing of files created across different operating systems.
    
    Args:
        file_path: Absolute or relative path to the .txt file
        
    Returns:
        A list of dictionaries representing document sections:
        [{"page_number": 1, "text": "...", "char_count": ..., "word_count": ...}]
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Text file not found: {file_path}")

    encodings_to_try = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    content = None
    used_encoding = None

    for enc in encodings_to_try:
        try:
            with open(file_path, "r", encoding=enc) as f:
                content = f.read()
                used_encoding = enc
                break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if content is None:
        # Ultimate fallback: read in binary and decode with error replacement
        with open(file_path, "rb") as f:
            raw_bytes = f.read()
            content = raw_bytes.decode("utf-8", errors="replace")
            used_encoding = "utf-8 (lossy fallback)"

    logger.info(f"Loaded text file '{os.path.basename(file_path)}' using {used_encoding} ({len(content)} chars)")
    cleaned = clean_text(content)

    return [{
        "page_number": 1,
        "text": cleaned,
        "char_count": len(cleaned),
        "word_count": len(cleaned.split()),
        "source": os.path.basename(file_path)
    }]


def extract_text_from_pdf(file_path: str) -> List[Dict[str, Any]]:
    """
    Extracts text page-by-page from a PDF document using PyPDF2 or pypdf.
    
    Extracts text from each page individually so chunks can retain accurate
    page number metadata for direct citations.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        A list of page dictionaries containing page_number and extracted text.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    pages_data: List[Dict[str, Any]] = []

    # Attempt to import PyPDF2 or pypdf
    pdf_reader_cls = None
    try:
        import pypdf
        pdf_reader_cls = pypdf.PdfReader
    except ImportError:
        try:
            import PyPDF2
            pdf_reader_cls = PyPDF2.PdfReader
        except ImportError:
            pass

    if pdf_reader_cls is None:
        logger.warning("Neither pypdf nor PyPDF2 is installed. Extracting PDF text via basic fallback.")
        # Fallback for plain binary scan if pypdf is not yet installed
        try:
            with open(file_path, "rb") as f:
                raw_bytes = f.read()
                # Find plain text strings between stream and endstream if possible
                text_matches = re.findall(rb'BT[\s\S]*?ET', raw_bytes)
                extracted = " ".join([m.decode("ascii", errors="ignore") for m in text_matches])
                cleaned = clean_text(extracted)
                if not cleaned:
                    cleaned = "PDF text could not be extracted. Please install pypdf or PyPDF2."
                return [{
                    "page_number": 1,
                    "text": cleaned,
                    "char_count": len(cleaned),
                    "word_count": len(cleaned.split()),
                    "source": os.path.basename(file_path)
                }]
        except Exception as e:
            raise RuntimeError(f"Failed to read PDF file without pypdf: {e}")

    try:
        reader = pdf_reader_cls(file_path)
        total_pages = len(reader.pages)
        logger.info(f"Extracting {total_pages} pages from PDF '{os.path.basename(file_path)}'...")

        for idx, page in enumerate(reader.pages):
            page_num = idx + 1
            try:
                page_raw = page.extract_text() or ""
            except Exception as page_err:
                logger.warning(f"Could not extract text on page {page_num}: {page_err}")
                page_raw = ""

            cleaned_page = clean_text(page_raw)
            if cleaned_page:  # Only add pages with actual text
                pages_data.append({
                    "page_number": page_num,
                    "text": cleaned_page,
                    "char_count": len(cleaned_page),
                    "word_count": len(cleaned_page.split()),
                    "source": os.path.basename(file_path)
                })

        # If no text was found on any page (e.g. scanned image PDF)
        if not pages_data:
            logger.warning(f"No text extracted from PDF '{os.path.basename(file_path)}' (scanned or empty).")
            pages_data.append({
                "page_number": 1,
                "text": "[Notice: This PDF contains scanned images or no extractable text layer.]",
                "char_count": 0,
                "word_count": 0,
                "source": os.path.basename(file_path)
            })

        logger.info(f"Successfully extracted {len(pages_data)} pages from '{os.path.basename(file_path)}'")
        return pages_data

    except Exception as e:
        logger.error(f"Error parsing PDF file {file_path}: {e}")
        raise RuntimeError(f"Could not parse PDF file: {e}")


def split_text_into_chunks(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
    base_metadata: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Splits text into overlapping chunks while preserving sentence/word boundaries.
    
    Why Chunking and Overlap Matter in RAG:
    - Chunking: Language models and vector embeddings have token limits. 
      Small, cohesive passages ensure that specific semantic answers aren't 
      diluted by surrounding unrelated text.
    - Overlap: Ensures critical facts straddling the boundary of two adjacent 
      chunks aren't severed, preserving semantic continuity.
      
    Args:
        text: Normalized text to split
        chunk_size: Target character length per chunk (e.g., 500)
        chunk_overlap: Character overlap between consecutive chunks (e.g., 100)
        base_metadata: Dictionary with document-level metadata (doc_id, source, etc.)
        
    Returns:
        List of chunk dictionaries with:
        {
            "chunk_index": int,
            "text": str,
            "char_count": int,
            "word_count": int,
            "start_char": int,
            "end_char": int,
            ...metadata
        }
    """
    if base_metadata is None:
        base_metadata = {}

    cleaned = clean_text(text)
    if not cleaned:
        return []

    # If text is smaller than or equal to target chunk size, return as a single chunk
    if len(cleaned) <= chunk_size:
        chunk_dict = {
            "chunk_index": 0,
            "text": cleaned,
            "char_count": len(cleaned),
            "word_count": len(cleaned.split()),
            "start_char": 0,
            "end_char": len(cleaned),
        }
        chunk_dict.update(base_metadata)
        return [chunk_dict]

    # Sentence boundary regex
    sentence_endings = re.compile(r'([.!?]\s+)')

    chunks: List[Dict[str, Any]] = []
    start = 0
    text_len = len(cleaned)
    chunk_idx = 0

    while start < text_len:
        # Determine candidate end point
        end = min(start + chunk_size, text_len)

        if end < text_len:
            # Look for sentence boundary within the last 120 characters of this window
            search_window_start = max(start, end - 120)
            sub = cleaned[search_window_start:end + 50]  # give a small lookahead buffer
            matches = list(sentence_endings.finditer(sub))

            if matches:
                # Pick the match closest to chunk_size without going too far
                chosen_match = None
                for m in reversed(matches):
                    abs_pos = search_window_start + m.end()
                    if abs_pos <= end + 50:
                        chosen_match = abs_pos
                        break
                if chosen_match and chosen_match > start + 50:
                    end = chosen_match
            else:
                # If no sentence boundary, break at the nearest word boundary (space)
                space_pos = cleaned.rfind(' ', max(start, end - 80), end)
                if space_pos > start + 50:
                    end = space_pos

        chunk_text = cleaned[start:end].strip()

        if chunk_text:
            chunk_dict = {
                "chunk_index": chunk_idx,
                "text": chunk_text,
                "char_count": len(chunk_text),
                "word_count": len(chunk_text.split()),
                "start_char": start,
                "end_char": end,
            }
            chunk_dict.update(base_metadata)
            chunks.append(chunk_dict)
            chunk_idx += 1

        if end >= text_len:
            break

        # Advance start position taking overlap into account
        new_start = end - chunk_overlap
        if new_start <= start:
            # Guarantee forward progress to prevent infinite loops
            new_start = end
        start = new_start

    return chunks


def get_document_statistics(text_or_pages: Any) -> Dict[str, Any]:
    """
    Computes statistical overview of text or list of document pages.
    
    Args:
        text_or_pages: String or list of page dictionaries
        
    Returns:
        Dict with total_characters, total_words, estimated_tokens, reading_time_minutes
    """
    if isinstance(text_or_pages, str):
        full_text = text_or_pages
    elif isinstance(text_or_pages, list):
        full_text = " ".join([p.get("text", "") for p in text_or_pages])
    else:
        full_text = str(text_or_pages)

    char_count = len(full_text)
    words = full_text.split()
    word_count = len(words)
    # Rule of thumb: 1 word ≈ 1.33 tokens
    estimated_tokens = int(word_count * 1.33)
    # Average adult reading speed: ~200-250 words per minute
    reading_time = round(word_count / 220, 1) if word_count > 0 else 0.0

    return {
        "total_characters": char_count,
        "total_words": word_count,
        "estimated_tokens": estimated_tokens,
        "reading_time_minutes": reading_time
    }
