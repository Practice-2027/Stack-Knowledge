from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib.units import inch
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
MD_DIR = ROOT / 'output' / 'rag_topics_md'
PDF_DIR = ROOT / 'output' / 'rag_topics_pdf'
MD_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)

topics = [
    (1, 'First - Analyze the Entire Project', 'Inspect the real repository before writing documentation.',
     'Repository files, source code, configuration, dependencies, APIs, prompts, databases, deployment files, logging, errors, and tests.',
     ['Map the repository.', 'Identify implemented technologies and data flow.', 'Record evidence from filenames and code.', 'Mark anything absent as NOT IMPLEMENTED IN THIS PROJECT.', 'Separate production recommendations from current behavior.'],
     'Repository -> evidence collection -> implementation map -> gaps and recommendations -> documentation'),
    (2, 'Project Overview', 'Explain what the project does at four levels: one sentence, beginner, technical, and interview-ready.',
     'A clear explanation of the problem, source of information, retrieval step, LLM answer generation, and why RAG is used.',
     ['State the user problem.', 'Trace a question from user to answer.', 'Name the real data source.', 'Explain why direct LLM-only answers are insufficient.', 'Keep implementation claims tied to repository evidence.'],
     'User question -> application -> retrieval -> context -> LLM -> answer'),
    (3, 'What Is RAG?', 'Break Retrieval-Augmented Generation into retrieval, augmentation, and generation.',
     'Retrieval finds useful source chunks; augmentation adds them to the prompt; generation asks the LLM to produce the response.',
     ['Convert the question into a searchable representation.', 'Find relevant document chunks.', 'Add those chunks to the prompt.', 'Call the LLM.', 'Return a grounded answer.'],
     'Question -> embedding -> search -> chunks -> augmented prompt -> LLM -> answer'),
    (4, 'RAG vs Normal LLM', 'Compare an LLM answering from learned knowledge with a RAG system that retrieves current or private context.',
     'The comparison must cover hallucinations, knowledge limits, private data, changing information, domain specificity, advantages, and disadvantages.',
     ['Describe the normal LLM path.', 'Describe the RAG path.', 'Compare grounding, freshness, complexity, and cost.', 'Explain that retrieval improves evidence access but does not guarantee truth.', 'Document trade-offs.'],
     'Normal: user -> LLM -> answer | RAG: user -> retriever -> context -> LLM -> answer'),
    (5, 'Complete Project Architecture', 'Show the actual frontend, backend, embedding model, vector database, retriever, prompt builder, and LLM connections.',
     'A Mermaid architecture diagram adapted from code, not a generic diagram. Every component must be verified or labeled absent.',
     ['Identify system boundaries.', 'Trace request and response paths.', 'Connect ingestion components separately from query components.', 'Label integrations and configuration points.', 'Mark missing components explicitly.'],
     'User <-> frontend <-> API <-> query pipeline <-> retrieval and generation'),
    (6, 'Complete RAG Pipeline', 'Explain the full lifecycle from document ingestion to question answering.',
     'The ingestion path is documents -> loader -> extraction -> cleaning -> chunking -> embeddings -> vector database. The query path should connect retrieval to prompt construction and generation.',
     ['Describe Phase A: data ingestion.', 'Describe the query-time path.', 'Identify where metadata travels.', 'Identify failure points.', 'Connect each phase to actual code.'],
     'Documents -> loader -> text -> chunks -> embeddings -> vector store -> retrieval -> prompt -> LLM'),
    (7, 'Document Ingestion', 'Identify exactly which document and data sources the project accepts.',
     'PDF, TXT, DOCX, CSV, web pages, database records, or other sources must be confirmed from the implementation rather than assumed.',
     ['List supported file types and sources.', 'Name each loader.', 'Explain the loader output structure.', 'Describe metadata captured.', 'Mark unsupported sources as not implemented.'],
     'Source -> loader -> documents/pages/records -> normalized content'),
    (8, 'Text Extraction', 'Explain how raw files become usable text and whether page numbers or metadata are preserved.',
     'A reader should understand the transformation from document to pages or records to text, and why metadata helps with citations, filtering, and debugging.',
     ['Locate extraction code.', 'Describe page or record boundaries.', 'Describe cleaning or normalization.', 'List preserved metadata.', 'Explain how downstream chunks use that metadata.'],
     'Document -> loader -> pages/records -> extracted text + metadata'),
    (9, 'Text Chunking', 'Explain chunks, chunk size, overlap, and their effect on retrieval quality in beginner-friendly language.',
     'The final documentation must report the exact chunk_size and chunk_overlap from code when available, and explain the consequences of large or small chunks.',
     ['Find the splitter implementation.', 'Record exact size and overlap values.', 'Show a short chunking example.', 'Explain context continuity.', 'Relate chunk settings to retrieval quality and token cost.'],
     'Long text -> splitter -> chunk 1 + overlap -> chunk 2 + overlap -> chunk N'),
    (10, 'Embeddings', 'Explain how text is converted into vectors so semantically similar text can be found.',
     'Document the exact embedding model, provider, dimensions only when identifiable, input/output behavior, cost, and local-versus-cloud trade-off.',
     ['Identify the embedding integration.', 'Record model and provider.', 'Verify vector dimension if exposed.', 'Explain query and document embeddings.', 'Explain semantic similarity without inventing model details.'],
     'Text -> embedding model -> vector [numbers...]'),
    (11, 'Vector Database', 'Explain the actual vector database and why it is used.',
     'Describe stored vectors, chunks, metadata, IDs, collections or indexes, and the difference between normal database lookups and similarity search.',
     ['Identify the vector technology.', 'Find collection/index configuration.', 'Describe stored records.', 'Explain persistence and lifecycle.', 'Mark absent databases clearly.'],
     'Chunk + vector + metadata -> collection/index -> similarity search'),
    (12, 'Vector Storage', 'Show how one chunk is represented and how storage is created, updated, deleted, persisted, and retrieved.',
     'The documentation should use the project’s actual schema or data structure, with a conceptual fallback only when code does not expose internals.',
     ['Describe IDs.', 'Describe chunk text.', 'Describe embedding vectors.', 'Describe metadata.', 'Explain insertion, updates, deletion, and persistence behavior.'],
     'Document ID + text chunk + embedding + metadata -> persistent store'),
    (13, 'Similarity Search', 'Explain query vectors, stored vectors, similarity, distance, ranking, and Top-K.',
     'Only claim cosine similarity, Euclidean distance, dot product, or another metric when configuration or code confirms it.',
     ['Embed the user query.', 'Search stored vectors.', 'Rank candidates.', 'Select Top-K results.', 'Explain what K means and what happens when results are weak.'],
     'User query -> query vector -> vector search -> ranked Top-K chunks'),
    (14, 'Retriever', 'Distinguish the vector database from the retriever that applies search behavior.',
     'Document search method, Top-K, filters, metadata filtering, thresholds, hybrid search, and reranking only when implemented.',
     ['Locate retriever construction.', 'Record search parameters.', 'Describe filters and thresholds.', 'Explain returned objects and metadata.', 'Mark unsupported features as not implemented.'],
     'Query -> retriever policy -> vector database -> ranked documents'),
    (15, 'Reranking', 'Explain the optional second ranking stage that improves the order of initially retrieved chunks.',
     'If absent, state: This project currently does not implement reranking. Then explain why production systems may add it after initial retrieval.',
     ['Check whether a reranker exists.', 'If present, document its model and inputs.', 'If absent, state the required phrase.', 'Explain initial Top-20 to best-5 as a conceptual example.', 'Describe quality and latency trade-offs.'],
     'Query -> initial retrieval -> larger candidate set -> reranker -> best context'),
    (16, 'Query Processing', 'Explain what happens when a user asks a question, from request intake through the answer.',
     'The source text stops mid-topic here, so the complete request/response fields and exact query workflow still need the missing continuation and repository inspection.',
     ['Trace the request into the backend.', 'Identify validation and preprocessing.', 'Create the query embedding if implemented.', 'Retrieve and assemble context.', 'Build the prompt, call the LLM, and return the response.', 'Record the exact request and response formats from code.'],
     'User question -> API request -> query processing -> retrieval -> prompt -> LLM -> API response'),
]

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleCenter', parent=styles['Title'], alignment=TA_CENTER, textColor=colors.HexColor('#17324D'), spaceAfter=18))
styles.add(ParagraphStyle(name='Topic', parent=styles['Heading1'], textColor=colors.HexColor('#17324D'), spaceBefore=8, spaceAfter=8))
styles.add(ParagraphStyle(name='Sub', parent=styles['Heading2'], textColor=colors.HexColor('#247BA0'), spaceBefore=10, spaceAfter=5))
styles.add(ParagraphStyle(name='Body2', parent=styles['BodyText'], leading=14, spaceAfter=7))

def slug(n, title):
    return f'{n:02d}-' + ''.join(c.lower() if c.isalnum() else '-' for c in title).strip('-').replace('--', '-')

def md_for(topic):
    n, title, purpose, scope, steps, workflow = topic
    lines = [f'# Topic {n}: {title}', '', '> Source basis: the pasted “SIMPLE RAG PROJECT — COMPLETE DOCUMENTATION PROMPT”. This file explains the documentation requirement; it does not claim that the repository implements any feature until code inspection confirms it.', '', '## In plain words', '', purpose, '', '## What this topic requires', '', scope, '', '## Required understanding and workflow', '']
    lines += [f'{i}. {s}' for i, s in enumerate(steps, 1)]
    lines += ['', '## Workflow', '', '```text', workflow, '```', '', '## Evidence rule', '', '- Inspect the repository and cite the relevant file or configuration before describing implementation behavior.', '- If a feature is missing, write `NOT IMPLEMENTED IN THIS PROJECT`.', '- If it is only a recommendation, write `PRODUCTION RECOMMENDATION - NOT CURRENTLY IMPLEMENTED`.', '', '## Output expectation', '', 'The finished project documentation should explain this topic from beginner level through engineering-level detail, with concrete examples derived from the actual code.']
    return '\n'.join(lines) + '\n'

def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#666666'))
    canvas.drawString(0.7 * inch, 0.45 * inch, 'Simple RAG requirements guide')
    canvas.drawRightString(7.8 * inch, 0.45 * inch, f'Page {doc.page}')
    canvas.restoreState()

def pdf_for(topic, path):
    n, title, purpose, scope, steps, workflow = topic
    doc = SimpleDocTemplate(str(path), pagesize=letter, rightMargin=0.7*inch, leftMargin=0.7*inch, topMargin=0.65*inch, bottomMargin=0.7*inch)
    story = [Paragraph(f'Topic {n}: {escape(title)}', styles['TitleCenter']), Paragraph('Simple RAG Project - Requirements Guide', styles['Sub']), Paragraph(escape(purpose), styles['Body2']), Paragraph('What this topic requires', styles['Sub']), Paragraph(escape(scope), styles['Body2']), Paragraph('Required understanding and workflow', styles['Sub'])]
    for i, item in enumerate(steps, 1):
        story.append(Paragraph(f'<b>{i}.</b> {escape(item)}', styles['Body2']))
    story += [Paragraph('Workflow', styles['Sub']), Preformatted(workflow, styles['Code']), Spacer(1, 10), Paragraph('Evidence rule', styles['Sub']), Paragraph('Describe implementation only after repository inspection. Missing features must be labeled NOT IMPLEMENTED IN THIS PROJECT. Recommendations must be labeled PRODUCTION RECOMMENDATION - NOT CURRENTLY IMPLEMENTED.', styles['Body2'])]
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)

index = ['# Simple RAG Project - Topic Pack', '', '## Count result', '', 'The pasted text contains **16 numbered topics**, not 60. It ends partway through Topic 16, so this pack covers the 16 topics that are actually present.', '', '## Important scope note', '', 'The prompt asks for documentation based on the actual repository, but the pasted text is a requirements prompt rather than the repository source code. Therefore these files explain what each topic must cover and the workflow for documenting it. They do not invent project technologies or implementation details.', '', '## Files', '']
for n, title, *_ in topics:
    s = slug(n, title)
    md_path = MD_DIR / f'{s}.md'
    pdf_path = PDF_DIR / f'{s}.pdf'
    md_path.write_text(md_for((n, title, topics[n-1][2], topics[n-1][3], topics[n-1][4], topics[n-1][5])), encoding='utf-8')
    pdf_for(topics[n-1], pdf_path)
    index.append(f'- Topic {n}: [{title}]({md_path.relative_to(ROOT).as_posix()}) | PDF: `{pdf_path.relative_to(ROOT).as_posix()}`')
index += ['', '## Missing continuation', '', 'The source file ends immediately after “Explain” under Topic 16. Topics 17-60 are not present in the pasted text and cannot be counted or generated faithfully without the missing content.', '']
(ROOT / 'output' / 'rag_topics_index.md').write_text('\n'.join(index), encoding='utf-8')
print(f'Generated {len(topics)} Markdown files, {len(topics)} PDF files, and one index.')
