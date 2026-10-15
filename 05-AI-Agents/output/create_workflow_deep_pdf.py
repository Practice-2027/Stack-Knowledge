from pathlib import Path
import ast, re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

SRC = Path('output/create_requirements_pdf.py').read_text(encoding='utf-8')
titles = ast.literal_eval(re.search(r'titles = (\[.*?\])\n\n', SRC, re.S).group(1))
OUT = Path('output/pdf/AI_AGENT_WORKFLOW_DIAGRAMS_DEEP_EXPLANATION.pdf')
OUT.parent.mkdir(parents=True, exist_ok=True)

W, H = A4
NAVY = colors.HexColor('#12355B')
BLUE = colors.HexColor('#2563EB')
PALE = colors.HexColor('#EFF6FF')
LINE = colors.HexColor('#94A3B8')
TEXT = colors.HexColor('#243447')
GREEN = colors.HexColor('#DCFCE7')
AMBER = colors.HexColor('#FEF3C7')

def category(title):
    t = title.lower()
    if 'analyze' in t: return ('Evidence discovery workflow', ['Repository', 'Dependencies', 'Entry points', 'Agent + APIs', 'Tests', 'Verified docs'], 'Start with inventory, then follow imports and runtime paths. Every claim must point to a real file, function, configuration value, or test. Missing behavior is recorded explicitly instead of being filled with assumptions.')
    if 'api' in t or 'request' in t: return ('Request-response workflow', ['Client', 'HTTP request', 'Route', 'Agent', 'Tool/API', 'HTTP response'], 'The workflow begins at the client boundary. Validate the request, route it to the backend, assemble agent context, perform model or tool work, normalize the result, and return a stable response or a safe error.')
    if 'tool' in t or 'function calling' in t: return ('Tool execution workflow', ['User goal', 'Model selects tool', 'Arguments', 'Permission + validation', 'Tool runs', 'Observation'], 'A tool is a controlled capability, not just an API. The model proposes a name and arguments, but the application must validate permissions and inputs before execution. The result is converted into an observation the model can use.')
    if 'memory' in t or 'state' in t or 'context' in t: return ('State and context workflow', ['Input', 'Context assembly', 'Model step', 'Tool result', 'State update', 'Persist or return'], 'State is the structured information needed to continue a run. Context is the portion sent to the model. Explain creation, updates, persistence, retrieval, clearing, and privacy boundaries separately.')
    if 'prompt' in t: return ('Prompt assembly workflow', ['System rules', 'Tool descriptions', 'User message', 'History/context', 'Model request', 'Text or tool call'], 'Prompt construction determines what the model can see and what it is asked to do. Document the observable contract, but never expose secrets or private chain-of-thought.')
    if 'security' in t or 'injection' in t or 'privacy' in t or 'human' in t: return ('Safety gate workflow', ['Identity', 'Authorization', 'Untrusted input', 'Policy checks', 'Approval/tool', 'Audited result'], 'Action-capable agents require gates before risky work. Authenticate the caller, authorize the operation, isolate untrusted instructions, apply least privilege, and require human approval where impact is high.')
    if 'error' in t or 'failure' in t or 'debug' in t: return ('Failure-handling workflow', ['Failure occurs', 'Detect', 'Classify', 'Retry/fallback?', 'Log safely', 'User response'], 'A useful error path is deterministic. Identify where the failure is detected, whether retry is safe, what information can be logged, and what the user receives. Avoid leaking credentials or internal prompts.')
    if 'test' in t or 'evaluation' in t: return ('Evaluation workflow', ['Test case', 'Expected behavior', 'Run system', 'Capture trace', 'Score', 'Improve + regress'], 'Evaluation turns an agent from a demo into an engineered system. Score task completion, tool choice, arguments, answer quality, safety, latency, and cost, then rerun regression cases after changes.')
    if 'production' in t or 'scale' in t or 'performance' in t or 'cost' in t or 'observability' in t or 'deploy' in t or 'docker' in t: return ('Production operations workflow', ['Build', 'Deploy', 'Health check', 'Trace + metrics', 'Scale/cache', 'Alert/recover'], 'Production workflow adds operational controls around the same agent loop. Measure each boundary, control concurrency and budgets, preserve session state, and make failures recoverable.')
    if 'interview' in t or 'minute' in t: return ('Explanation workflow', ['Problem', 'Architecture', 'Agent loop', 'Tools/model', 'Result', 'Tradeoffs'], 'A strong explanation follows the runtime path. Start with the problem, then explain the smallest accurate architecture, show one request through the loop, and finish with limits and improvements.')
    if 'vs' in t or 'confusion' in t: return ('Concept comparison workflow', ['Concept A', 'Concept B', 'Observable behavior', 'Example', 'Boundary', 'Rule of thumb'], 'Compare concepts by what they do at runtime, not by marketing labels. Use the same example for both sides and state where they can be combined.')
    if 'glossary' in t or 'roadmap' in t or 'documentation' in t or 'master' in t or 'pdf' in t: return ('Learning-document workflow', ['Requirements', 'Focused topic', 'Example/diagram', 'Implementation evidence', 'Review', 'Deliverable'], 'Each topic should teach a beginner, connect to implementation, and end in a reviewable artifact. Keep current behavior and recommended future behavior visibly separate.')
    return ('Agent decision workflow', ['User goal', 'Understand', 'Choose action', 'Execute', 'Observe', 'Answer or continue'], 'The core agent workflow is a controlled loop. The model interprets the goal and proposes the next action; the runtime executes allowed actions, feeds back results, and stops when the goal is satisfied or a limit/error is reached.')

def wrap(text, max_chars=86):
    words, lines, line = text.split(), [], ''
    for w in words:
        if len(line) + len(w) + 1 > max_chars:
            lines.append(line); line = w
        else: line = (line + ' ' + w).strip()
    if line: lines.append(line)
    return lines

def arrow(c, x1, y1, x2, y2):
    c.setStrokeColor(BLUE); c.setLineWidth(1.4); c.line(x1, y1, x2, y2)
    c.setFillColor(BLUE); c.setFont('Helvetica-Bold', 12)
    c.drawCentredString((x1+x2)/2, y1-5, '>')

def box(c, x, y, w, h, label, fill):
    c.setFillColor(fill); c.setStrokeColor(BLUE); c.setLineWidth(1)
    c.roundRect(x, y, w, h, 7, fill=1, stroke=1)
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 9)
    lines = wrap(label, 18)
    yy = y + h/2 + 4*(len(lines)-1)
    for line in lines:
        c.drawCentredString(x+w/2, yy, line); yy -= 11

c = canvas.Canvas(str(OUT), pagesize=A4)
for i, title in enumerate(titles, 1):
    kind, steps, explanation = category(title)
    c.setTitle('AI Agent Workflow Diagrams - Deep Explanation')
    c.setFillColor(BLUE); c.setFont('Helvetica-Bold', 9); c.drawString(18*mm, H-18*mm, f'TOPIC {i} OF 77')
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 19)
    # title wrap
    tlines = wrap(title, 42); yy = H-31*mm
    for line in tlines:
        c.drawString(18*mm, yy, line); yy -= 23
    c.setFillColor(BLUE); c.setFont('Helvetica-Bold', 10); c.drawString(18*mm, yy-7, kind)
    # diagram
    top = yy - 35
    left, right = 22*mm, W-22*mm
    bw, bh = 38*mm, 18*mm
    cols = 3
    gap = (right-left - cols*bw) / (cols-1)
    row_gap = 15*mm
    first_y = top - bh
    positions = []
    for j, step in enumerate(steps):
        row, col = divmod(j, cols)
        x = left + col*(bw+gap)
        y = first_y - row*(bh+row_gap)
        positions.append((x, y))
        box(c, x, y, bw, bh, step, PALE if j not in (0, len(steps)-1) else GREEN)
        if col < cols-1 and j < len(steps)-1:
            arrow(c, x+bw, y+bh/2, x+bw+gap, y+bh/2)
        elif j < len(steps)-1:
            nx, ny = left, y-(bh+row_gap)
            c.setStrokeColor(BLUE); c.setLineWidth(1.4); c.line(x+bw/2, y, nx+bw/2, ny+bh)
            c.setFillColor(BLUE); c.setFont('Helvetica-Bold', 12); c.drawCentredString(x+bw/2+6, (y+ny+bh)/2, 'v')
    y = positions[-1][1]
    # explanation panels
    py = y - 22*mm
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 11); c.drawString(18*mm, py, 'Deep workflow explanation')
    py -= 8*mm; c.setFillColor(TEXT); c.setFont('Helvetica', 10.2)
    for line in wrap(explanation, 92):
        c.drawString(18*mm, py, line); py -= 15
    py -= 6
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 11); c.drawString(18*mm, py, 'What to verify in the repository')
    py -= 8*mm; c.setFillColor(TEXT); c.setFont('Helvetica', 10.2)
    checklist = 'Actual files and symbols; inputs and outputs at each boundary; error and stop conditions; current implementation versus production recommendation.'
    for line in wrap(checklist, 92):
        c.drawString(18*mm, py, line); py -= 15
    py -= 6
    c.setFillColor(AMBER); c.roundRect(18*mm, py-22*mm, W-36*mm, 22*mm, 5, fill=1, stroke=0)
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 10); c.drawString(23*mm, py-8*mm, 'Accuracy rule')
    c.setFont('Helvetica', 9.5); c.setFillColor(TEXT)
    for k, line in enumerate(wrap('Do not invent implementation details. If a feature is absent, label it NOT IMPLEMENTED IN THIS PROJECT. Do not expose secrets or private chain-of-thought.', 87)):
        c.drawString(23*mm, py-14*mm-(k*12), line)
    c.setStrokeColor(colors.HexColor('#CBD5E1')); c.line(18*mm, 14*mm, W-18*mm, 14*mm)
    c.setFillColor(colors.HexColor('#64748B')); c.setFont('Helvetica', 8)
    c.drawString(18*mm, 9*mm, 'AI Agent Workflow Diagrams - Deep Explanation')
    c.drawRightString(W-18*mm, 9*mm, f'Page {i} of 77')
    c.showPage()
c.save()
print(OUT.resolve())
