from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle

OUT = Path("output/pdf/simple_rag_60_topic_requirements_guide.pdf")
OUT.parent.mkdir(parents=True, exist_ok=True)

titles = [
"Project purpose","Repository inspection","Frontend identification","Backend identification","Languages and frameworks",
"LLM identification","Embedding model identification","Vector database identification","Normal database identification","Document source inventory",
"Document loaders","Text extraction","Metadata preservation","Cleaning and normalization","Chunk concept","Chunk size","Chunk overlap",
"Chunk quality trade-offs","Embedding fundamentals","Embedding input/output","Embedding dimensions and cost","Vector storage schema",
"Collection/index lifecycle","Persistence","Similarity search","Top-K retrieval","Retriever role","Retriever filters","Similarity thresholds",
"Hybrid search","Reranking","Query intake","Query embedding","Context assembly","Prompt template","Prompt safety","LLM call",
"Answer generation","RAG chain","Response format","API endpoints","Authentication","Environment variables","Configuration files",
"Docker configuration","Deployment configuration","Error handling","Logging","Testing strategy","Ingestion workflow",
"Question-answer workflow","Normal LLM vs RAG","Hallucination and grounding","Private and changing data","Architecture diagram",
"Beginner explanation","Technical explanation","Interview explanation","Evidence and gaps","Production readiness review"
]
assert len(titles) == 60

meaning = {
"Project purpose":"Define what the RAG project is expected to do and what problem it solves.",
"Repository inspection":"Inspect the complete repository before writing implementation documentation.",
"Frontend identification":"Find the user-facing application and explain how it collects and displays questions and answers.",
"Backend identification":"Find the server-side application that handles ingestion, retrieval, and generation.",
"Languages and frameworks":"Inventory programming languages, frameworks, and major libraries.",
"LLM identification":"Identify the exact language model used to generate answers.",
"Embedding model identification":"Identify the model that converts text and queries into vectors.",
"Vector database identification":"Identify the vector store and explain its role in retrieval.",
"Normal database identification":"Check whether a conventional database is used for users, metadata, jobs, or application state.",
"Document source inventory":"List exactly where knowledge comes from: files, URLs, records, uploads, or other sources.",
"Document loaders":"Explain the loader used for each supported document type.","Text extraction":"Show how a raw document becomes usable text.",
"Metadata preservation":"Explain which metadata travels with each chunk and why it matters.",
"Cleaning and normalization":"Identify whitespace cleanup, encoding fixes, or text normalization.",
"Chunk concept":"Explain a chunk as a small searchable piece of a document.","Chunk size":"Record the configured maximum chunk size and its unit.",
"Chunk overlap":"Record how much neighboring chunks repeat.","Chunk quality trade-offs":"Explain how overly large or tiny chunks affect retrieval and generation.",
"Embedding fundamentals":"Explain why text is converted into numbers for semantic search.","Embedding input/output":"Document the exact input text and vector output path.",
"Embedding dimensions and cost":"Report vector dimension and operational cost only when confirmed.",
"Vector storage schema":"Describe how each indexed item is represented.","Collection/index lifecycle":"Explain creation, loading, reuse, update, and deletion behavior.",
"Persistence":"Explain whether vectors survive process restarts.","Similarity search":"Explain how a query vector is compared with stored vectors.",
"Top-K retrieval":"Explain K as the number of candidate chunks returned.","Retriever role":"Distinguish the vector database from the retriever abstraction.",
"Retriever filters":"Check for metadata filters, namespaces, tenant filters, or source restrictions.",
"Similarity thresholds":"Check whether weak matches are rejected before prompting the LLM.",
"Hybrid search":"Check whether keyword and vector search are combined.","Reranking":"Explain the optional second ranking stage.",
"Query intake":"Trace how a user question enters the system.","Query embedding":"Explain how the question is embedded for retrieval.",
"Context assembly":"Explain how retrieved chunks are combined for the prompt.","Prompt template":"Document the exact instruction template used around the context.",
"Prompt safety":"Check for instructions that reduce prompt injection or unsupported claims.","LLM call":"Explain the code path that sends the prompt to the model.",
"Answer generation":"Explain how the model turns context into a response.","RAG chain":"Describe how retrieval, prompt construction, and generation connect.",
"Response format":"Document the API or UI response structure.","API endpoints":"Inventory routes used for upload, indexing, querying, health, or administration.",
"Authentication":"Check whether the project protects APIs or documents.","Environment variables":"List required secrets, model names, URLs, paths, and tuning values.",
"Configuration files":"Explain where settings live and which values override others.","Docker configuration":"Check for Dockerfiles, compose files, volumes, ports, and services.",
"Deployment configuration":"Check for hosting, process, reverse proxy, or cloud deployment instructions.",
"Error handling":"Trace failures in loading, embedding, retrieval, and generation.","Logging":"Identify what events and diagnostics are recorded.",
"Testing strategy":"Inventory unit, integration, API, retrieval, and end-to-end tests.",
"Ingestion workflow":"Summarize the offline or startup indexing process.",
"Question-answer workflow":"Summarize the online query path.","Normal LLM vs RAG":"Compare direct generation with context-grounded generation.",
"Hallucination and grounding":"Explain how unsupported answers can occur and how evidence helps.",
"Private and changing data":"Explain why RAG is useful for internal or frequently updated knowledge.",
"Architecture diagram":"Create a diagram that matches actual components and data flow.",
"Beginner explanation":"Explain the project without assuming knowledge of embeddings or vector stores.",
"Technical explanation":"Explain the same system with precise engineering vocabulary.",
"Interview explanation":"Prepare a concise 1-2 minute explanation of the project.",
"Evidence and gaps":"Separate confirmed behavior, unknowns, and recommendations.",
"Production readiness review":"Turn the requirements into a final gap analysis."
}

workflow = {
"Project purpose":"Goal -> user question -> grounded answer","Repository inspection":"List files -> read source/config -> trace execution -> record evidence",
"Frontend identification":"User -> UI input -> request -> response -> UI output","Backend identification":"HTTP request -> route -> service -> response",
"Languages and frameworks":"Manifest files -> dependencies -> runtime components","LLM identification":"Prompt + context -> model -> answer",
"Embedding model identification":"Text/query -> embedding model -> vector","Vector database identification":"Chunk + vector + metadata -> index -> search",
"Normal database identification":"Application event -> database read/write -> result","Document source inventory":"Source -> loader -> extracted content -> indexing",
"Document loaders":"File/source -> loader -> document objects","Text extraction":"Document -> pages/records -> text -> metadata",
"Metadata preservation":"Source metadata -> chunk metadata -> filters/citations/debugging","Cleaning and normalization":"Raw text -> cleaned text -> chunker",
"Chunk concept":"Long document -> smaller passages -> searchable units","Chunk size":"Text -> sized chunks -> embeddings",
"Chunk overlap":"Chunk N overlaps with chunk N+1 -> continuity","Chunk quality trade-offs":"Chunking -> retrieval precision/context -> answer quality",
"Embedding fundamentals":"Text meaning -> vector representation -> nearest neighbors","Embedding input/output":"Text -> embedding call -> vector -> storage/search",
"Embedding dimensions and cost":"Model choice -> dimension/cost/latency -> database settings","Vector storage schema":"ID + text + vector + metadata -> vector store",
"Collection/index lifecycle":"Startup/ingest -> create/open -> write -> query","Persistence":"Store -> restart -> data available or missing",
"Similarity search":"Question -> query vector -> distance -> ranked chunks","Top-K retrieval":"Ranked results -> first K chunks -> context",
"Retriever role":"Retriever settings -> vector store query -> documents","Retriever filters":"Query + filters -> narrowed search -> results",
"Similarity thresholds":"Results -> score threshold -> accepted context","Hybrid search":"Query -> lexical + vector search -> merged ranking",
"Reranking":"Query -> initial top 20 -> reranker -> best 5 -> LLM","Query intake":"Request body -> validation -> query variable",
"Query embedding":"Question -> embedding model -> query vector","Context assembly":"Retrieved chunks -> ordered context -> prompt input",
"Prompt template":"Question + context + rules -> formatted prompt","Prompt safety":"Untrusted text -> boundaries/instructions -> safer generation",
"LLM call":"Formatted prompt -> client call -> model output","Answer generation":"Grounded prompt -> generation -> answer",
"RAG chain":"Question -> retrieve -> format -> generate -> return","Response format":"Answer + metadata/errors -> JSON/UI",
"API endpoints":"Client -> route -> handler -> service -> response","Authentication":"Identity/token -> authorization -> operation",
"Environment variables":"Environment/config -> startup -> runtime behavior","Configuration files":"Config + environment -> resolved settings",
"Docker configuration":"Image build -> container startup -> network/storage","Deployment configuration":"Code -> build -> deploy -> service",
"Error handling":"Failure -> exception handling -> log/status -> user response","Logging":"Runtime event -> logger -> output",
"Testing strategy":"Test input -> component/system -> expected result","Ingestion workflow":"Documents -> load -> extract -> clean -> chunk -> embed -> store",
"Question-answer workflow":"Question -> embed -> retrieve -> prompt -> LLM -> response","Normal LLM vs RAG":"Direct: user -> LLM; RAG: user -> retrieve -> context -> LLM",
"Hallucination and grounding":"Weak evidence -> model guess; strong evidence -> grounded answer","Private and changing data":"Documents -> re-index -> retrieve current evidence -> answer",
"Architecture diagram":"User -> frontend -> API -> retrieval/generation -> response","Beginner explanation":"Plain concept -> example -> workflow",
"Technical explanation":"Components -> interfaces -> data structures -> runtime sequence","Interview explanation":"Problem -> architecture -> retrieval -> generation -> trade-offs",
"Evidence and gaps":"Source evidence -> implemented / not implemented / recommended","Production readiness review":"Evidence -> risks -> prioritized improvements"
}

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontSize=25, leading=31, alignment=TA_CENTER, textColor=colors.HexColor("#12304A")))
styles.add(ParagraphStyle(name="CoverSub", parent=styles["Normal"], fontSize=12, leading=18, alignment=TA_CENTER, textColor=colors.HexColor("#35586F")))
styles.add(ParagraphStyle(name="No", parent=styles["Normal"], fontSize=9, leading=12, textColor=colors.HexColor("#1E7A8A")))
styles.add(ParagraphStyle(name="Topic", parent=styles["Heading1"], fontSize=20, leading=24, textColor=colors.HexColor("#12304A")))
styles.add(ParagraphStyle(name="Label", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=colors.HexColor("#1E7A8A"), spaceBefore=7, spaceAfter=3))
styles.add(ParagraphStyle(name="Body2", parent=styles["BodyText"], fontSize=10.5, leading=15, textColor=colors.HexColor("#243746"), spaceAfter=7))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.5, leading=12, textColor=colors.HexColor("#566B78")))

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D7E3E8"))
    canvas.line(18*mm, 13*mm, 192*mm, 13*mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#71828A"))
    canvas.drawString(18*mm, 8*mm, "Simple RAG requirements analysis")
    canvas.drawRightString(192*mm, 8*mm, f"Page {doc.page}")
    canvas.restoreState()

doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm, title="Simple RAG Project - 60 Topic Requirements Guide")
story = [Spacer(1, 35*mm), Paragraph("SIMPLE RAG PROJECT", styles["CoverTitle"]), Spacer(1, 5*mm), Paragraph("60-topic requirements analysis and workflow guide", styles["CoverSub"]), Spacer(1, 14*mm)]
cover = [["What was analyzed", "The pasted documentation prompt"], ["Number of topics", "60 distinct requirements"], ["Page structure", "One topic per page after this cover"], ["Scope note", "Repository-specific values must be verified from source code."]]
table = Table(cover, colWidths=[42*mm, 120*mm])
table.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),colors.HexColor("#EAF4F6")),("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),10),("LEADING",(0,0),(-1,-1),14),("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#C8DCE2")),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
story += [table, Spacer(1, 18*mm), Paragraph("Reading rule: this is a requirements breakdown, not a claim that the unseen repository already implements every item. Use the required labels NOT IMPLEMENTED IN THIS PROJECT and PRODUCTION RECOMMENDATION - NOT CURRENTLY IMPLEMENTED when evidence is missing.", styles["Small"]), PageBreak()]

for i, title in enumerate(titles, 1):
    story += [Paragraph(f"TOPIC {i} OF 60", styles["No"]), Paragraph(title, styles["Topic"]), Paragraph("What this requirement means", styles["Label"]), Paragraph(meaning[title], styles["Body2"]), Paragraph("Workflow", styles["Label"]), Paragraph(workflow[title].replace("->", "  ->  "), styles["Body2"]), Paragraph("Documentation guidance", styles["Label"])]
    guidance = "Trace this behavior to source files, functions, configuration, dependencies, and tests. Do not guess."
    if title in {"Reranking", "Hybrid search", "Authentication", "Normal database identification", "Testing strategy"}:
        guidance += " If absent, state: NOT IMPLEMENTED IN THIS PROJECT. If proposed for production, state: PRODUCTION RECOMMENDATION - NOT CURRENTLY IMPLEMENTED."
    if title == "Evidence and gaps":
        guidance = "Separate confirmed behavior, unknowns, and recommendations. The prompt explicitly requires this distinction."
    story += [Paragraph(guidance, styles["Body2"])]
    if i != 60:
        story.append(PageBreak())

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT.resolve())
