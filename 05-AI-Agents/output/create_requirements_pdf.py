from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak

OUT = Path('output/pdf/AI_AGENT_REQUIREMENTS_77_TOPICS.pdf')
OUT.parent.mkdir(parents=True, exist_ok=True)

titles = [
"FIRST - ANALYZE THE ENTIRE PROJECT", "PROJECT OVERVIEW", "WHAT IS AN AI AGENT?", "AI AGENT VS NORMAL LLM", "AI AGENT ARCHITECTURE", "COMPLETE AGENT PIPELINE", "WHAT MAKES THIS PROJECT AN AGENT?", "COMPLETE USER REQUEST FLOW", "LLM", "AGENT FRAMEWORK", "AGENT CORE", "TOOLS", "TOOL CALLING", "FUNCTION CALLING", "AGENT DECISION LOOP", "SINGLE-STEP AGENT", "MULTI-STEP AGENT", "PLANNING", "MEMORY", "AGENT STATE", "WORKFLOW / GRAPH", "STOP CONDITION", "MAXIMUM ITERATIONS", "PROMPTS", "SYSTEM PROMPT", "TOOL DESCRIPTIONS", "CONTEXT", "RAG + AI AGENT", "AGENT + API", "API DOCUMENTATION", "COMPLETE REQUEST -> RESPONSE FLOW", "FRONTEND FLOW", "BACKEND FLOW", "FILE-BY-FILE EXPLANATION", "FUNCTION-BY-FUNCTION EXPLANATION", "ENVIRONMENT VARIABLES", "LOCAL SETUP", "COMPLETE REAL-WORLD EXAMPLE", "AGENT OBSERVATION", "ERROR HANDLING", "TOOL FAILURE", "SECURITY", "PROMPT INJECTION", "TOOL SECURITY", "HUMAN-IN-THE-LOOP", "MEMORY AND PRIVACY", "AGENT VS RAG", "AGENT VS CHATBOT", "AGENT VS AUTOMATION", "SINGLE AGENT VS MULTI-AGENT", "PRODUCTION ARCHITECTURE", "SCALABILITY", "PERFORMANCE", "COST", "OBSERVABILITY", "TESTING", "AGENT EVALUATION", "DEBUGGING GUIDE", "DEPLOYMENT", "DOCKER", "BIG PROJECT IMPLEMENTATION", "ADVANCED AGENT FEATURES", "DETERMINISTIC WORKFLOW VS AUTONOMOUS AGENT", "COMPLETE END-TO-END FLOW", "COMPLETE REQUEST/RESPONSE EXAMPLE", "SECURITY ARCHITECTURE", "INTERVIEW QUESTIONS", "2-MINUTE PROJECT EXPLANATION", "5-MINUTE PROJECT EXPLANATION", "BEGINNER GLOSSARY", "COMMON CONFUSIONS", "LEARNING ROADMAP", "DOCUMENTATION FILE STRUCTURE", "MASTER DOCUMENT", "PDF DOCUMENT", "FINAL QUALITY CHECK", "MOST IMPORTANT RULES"
]

def content(title):
    t = title.lower()
    if title == 'MOST IMPORTANT RULES':
        return ('Apply the non-negotiable rules: inspect first, never invent implementation details, label missing features, separate current code from recommendations, and protect secrets.', 'Inspect -> document evidence -> label unknowns -> protect secrets -> verify -> deliver')
    if 'analyze' in t:
        meaning = 'Inspect the real repository before making any documentation claim. Identify languages, frameworks, models, tools, APIs, state, memory, tests, deployment files, and missing features.'
        flow = 'Repository -> dependencies/config -> entry points -> agent components -> APIs/tools -> tests -> evidence-backed docs'
    elif 'overview' in t:
        meaning = 'Explain the project purpose, problem, inputs, outputs, capabilities, and value at beginner, technical, and interview levels.'
        flow = 'Problem -> user input -> agent capability -> output -> beginner explanation -> technical explanation'
    elif 'vs' in t or 'confusion' in t:
        meaning = 'Compare the two concepts using definitions, observable behavior, an example, and a practical rule of thumb. Keep distinctions precise.'
        flow = 'Concept A -> definition -> Concept B -> definition -> difference -> example -> rule of thumb'
    elif 'architecture' in t or 'pipeline' in t or 'end-to-end' in t or 'request' in t and 'response' in t:
        meaning = 'Show how the parts connect as one system: user, frontend, API, agent, model, tools, external services, state, and response.'
        flow = 'User -> frontend -> backend API -> agent <-> LLM -> tool/service -> observation -> final response'
    elif 'tool' in t or 'function calling' in t:
        meaning = 'Document tool purpose, schema, arguments, execution, result handling, permissions, and failure behavior. Only describe tools confirmed in code.'
        flow = 'Tool schema -> model selection -> arguments -> validation -> service call -> result -> agent'
    elif 'memory' in t or 'state' in t or 'context' in t:
        meaning = 'Explain what information is carried between steps, where it is stored, how it is retrieved or updated, and whether it persists across sessions.'
        flow = 'Input/history/state -> context assembly -> model/tool use -> state or memory update -> response'
    elif 'prompt' in t:
        meaning = 'Identify system, user, agent, tool, and output instructions. Explain their purpose without exposing secrets or private chain-of-thought.'
        flow = 'Role + rules + tools + context + output contract -> model request -> text or tool call'
    elif 'api' in t:
        meaning = 'Document actual HTTP methods, paths, headers, request and response bodies, backend processing, external calls, and errors.'
        flow = 'HTTP request -> route -> validation -> controller/service -> agent/model/tool -> response or error'
    elif 'frontend' in t:
        meaning = 'Map pages and components from user input through submit, loading, API communication, error handling, and response rendering.'
        flow = 'Input -> submit -> loading -> API -> response/error -> render/history'
    elif 'backend' in t:
        meaning = 'Trace the backend route, controller/service, agent, model, tools, result normalization, and HTTP response using actual files.'
        flow = 'Request -> route -> service -> agent -> model/tool -> serializer -> response'
    elif 'security' in t or 'injection' in t or 'privacy' in t or 'human' in t:
        meaning = 'Analyze risk at every boundary. Separate current controls from production recommendations, and apply least privilege, validation, approval, and safe logging.'
        flow = 'Identity -> authorization -> agent boundary -> permission check -> tool/external system -> audit-safe result'
    elif 'error' in t or 'failure' in t or 'debug' in t:
        meaning = 'Describe the symptom, likely cause, detection point, handling policy, user-safe response, and verification step.'
        flow = 'Failure -> detection -> retry/fallback/stop decision -> log/metric -> safe response -> retest'
    elif 'test' in t or 'evaluation' in t:
        meaning = 'Define tests and measurements for correctness, tool selection, argument validity, safety, latency, cost, and end-to-end task success.'
        flow = 'Test task -> expected behavior -> run -> score -> analyze failures -> improve -> regression check'
    elif 'production' in t or 'scale' in t or 'performance' in t or 'cost' in t or 'observability' in t or 'deploy' in t or 'docker' in t:
        meaning = 'Translate the simple project into reliable operations: deployment, security, monitoring, budgets, latency control, scaling, and recovery.'
        flow = 'Build/configure -> deploy -> health check -> trace/measure -> scale or remediate'
    elif 'interview' in t or 'minute' in t:
        meaning = 'Prepare a technically correct explanation based on verified project facts, with a clear problem, solution, architecture, flow, and tradeoffs.'
        flow = 'Problem -> solution -> stack -> agent/model -> tools -> decision flow -> result -> tradeoffs'
    elif 'glossary' in t or 'roadmap' in t or 'documentation' in t or 'master' in t or 'pdf' in t:
        meaning = 'Turn the requirements into a structured learning artifact that is easy to navigate, beginner-friendly, technically accurate, and reviewable.'
        flow = 'Source requirements -> focused topics/files -> master narrative -> render -> inspect -> deliver'
    else:
        meaning = 'Explain this topic from beginner level to implementation level, then separate what exists in the repository from what is only recommended for production.'
        flow = 'Requirement -> repository evidence -> implementation explanation -> production recommendation -> verification'
    return meaning, flow

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Topic', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=21, leading=26, textColor=colors.HexColor('#12355B'), spaceAfter=8))
styles.add(ParagraphStyle(name='Kicker', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#2563EB'), spaceAfter=4))
styles.add(ParagraphStyle(name='Body2', parent=styles['BodyText'], fontName='Helvetica', fontSize=10.5, leading=15, textColor=colors.HexColor('#243447'), spaceAfter=8))
styles.add(ParagraphStyle(name='Label', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#12355B'), spaceBefore=7, spaceAfter=4))
styles.add(ParagraphStyle(name='Flow', parent=styles['BodyText'], fontName='Courier', fontSize=9, leading=13, backColor=colors.HexColor('#F1F5F9'), borderColor=colors.HexColor('#CBD5E1'), borderWidth=0.5, borderPadding=8, spaceBefore=4, spaceAfter=10))

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#CBD5E1'))
    canvas.line(18*mm, 14*mm, 192*mm, 14*mm)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#64748B'))
    canvas.drawString(18*mm, 9*mm, 'AI Agent Documentation Requirements Blueprint')
    canvas.drawRightString(192*mm, 9*mm, f'Topic page {doc.page} of 77')
    canvas.restoreState()

doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=16*mm, bottomMargin=20*mm)
story = []
for n, title in enumerate(titles, 1):
    meaning, flow = content(title)
    story += [Paragraph(f'TOPIC {n} OF 77', styles['Kicker']), Paragraph(title, styles['Topic'])]
    story += [Paragraph('Requirements understanding', styles['Label']), Paragraph(meaning, styles['Body2'])]
    story += [Paragraph('Expected documentation output', styles['Label']), Paragraph('Use evidence from actual source code, configuration, dependencies, routes, prompts, state, tools, tests, and runtime behavior. If absent, write <b>NOT IMPLEMENTED IN THIS PROJECT</b>. If it is future advice, write <b>PRODUCTION RECOMMENDATION - NOT CURRENTLY IMPLEMENTED</b>.', styles['Body2'])]
    story += [Paragraph('Workflow', styles['Label']), Paragraph(flow.replace('->', '-&gt;'), styles['Flow'])]
    story += [Paragraph('Accuracy checkpoint', styles['Label']), Paragraph('Never infer implementation from a common AI-agent pattern. Verify it in the repository and do not expose credentials, private information, or hidden chain-of-thought.', styles['Body2'])]
    if n < len(titles): story.append(PageBreak())
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT.resolve())
