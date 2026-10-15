from pathlib import Path
import ast
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Flowable

SOURCE = Path("create_rag_requirements_pdf.py")
OUT = Path("output/pdf/simple_rag_60_topic_workflow_diagrams_deep_guide.pdf")
OUT.parent.mkdir(parents=True, exist_ok=True)

tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
data = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
        if node.targets[0].id in {"titles", "meaning", "workflow"}:
            data[node.targets[0].id] = ast.literal_eval(node.value)
titles, meaning, workflow = data["titles"], data["meaning"], data["workflow"]
assert len(titles) == 60

class WorkflowDiagram(Flowable):
    def __init__(self, steps):
        super().__init__()
        self.steps = [s.strip() for s in steps if s.strip()]
        self.width = 174*mm
        self.height = 38*mm

    def draw(self):
        c = self.canv
        n = min(len(self.steps), 5)
        gap = 5
        box_w = (self.width - gap*(n-1))/n
        box_h = 22*mm
        y = 9*mm
        for i, step in enumerate(self.steps[:n]):
            x = i*(box_w+gap)
            c.setFillColor(colors.HexColor("#EAF4F6") if i % 2 == 0 else colors.HexColor("#F4F7F8"))
            c.setStrokeColor(colors.HexColor("#6FAAB3"))
            c.roundRect(x, y, box_w, box_h, 5, fill=1, stroke=1)
            c.setFillColor(colors.HexColor("#12304A"))
            words = step.split()
            lines, line = [], ""
            for word in words:
                if len(line) + len(word) + 1 > 17:
                    lines.append(line)
                    line = word
                else:
                    line = (line + " " + word).strip()
            if line:
                lines.append(line)
            c.setFont("Helvetica-Bold", 7.5)
            total = len(lines)*9
            for j, line in enumerate(lines[:4]):
                c.drawCentredString(x+box_w/2, y+box_h/2+total/2-j*9-7, line)
            if i < n-1:
                c.setStrokeColor(colors.HexColor("#1E7A8A"))
                c.setLineWidth(1.2)
                ax = x+box_w+1
                c.line(ax, y+box_h/2, ax+gap-2, y+box_h/2)
                c.line(ax+gap-2, y+box_h/2, ax+gap-5, y+box_h/2+2)
                c.line(ax+gap-2, y+box_h/2, ax+gap-5, y+box_h/2-2)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle2", parent=styles["Title"], fontSize=24, leading=30, alignment=1, textColor=colors.HexColor("#12304A")))
styles.add(ParagraphStyle(name="CoverSub2", parent=styles["Normal"], fontSize=12, leading=18, alignment=1, textColor=colors.HexColor("#35586F")))
styles.add(ParagraphStyle(name="No2", parent=styles["Normal"], fontSize=9, leading=12, textColor=colors.HexColor("#1E7A8A")))
styles.add(ParagraphStyle(name="Topic2", parent=styles["Heading1"], fontSize=19, leading=23, textColor=colors.HexColor("#12304A"), spaceAfter=5))
styles.add(ParagraphStyle(name="Label2", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=colors.HexColor("#1E7A8A"), spaceBefore=4, spaceAfter=2))
styles.add(ParagraphStyle(name="Body3", parent=styles["BodyText"], fontSize=9.2, leading=12.5, textColor=colors.HexColor("#243746"), spaceAfter=4))
styles.add(ParagraphStyle(name="Small2", parent=styles["BodyText"], fontSize=8.3, leading=11, textColor=colors.HexColor("#566B78")))

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D7E3E8"))
    canvas.line(18*mm, 13*mm, 192*mm, 13*mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#71828A"))
    canvas.drawString(18*mm, 8*mm, "Simple RAG workflow diagrams")
    canvas.drawRightString(192*mm, 8*mm, f"Page {doc.page}")
    canvas.restoreState()

doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=15*mm, bottomMargin=18*mm, title="Simple RAG Project - Deep Workflow Diagrams")
story = [Spacer(1, 32*mm), Paragraph("SIMPLE RAG PROJECT", styles["CoverTitle2"]), Spacer(1, 4*mm), Paragraph("60 deep workflow explanations with visual diagrams", styles["CoverSub2"]), Spacer(1, 15*mm), Paragraph("Each topic page contains a workflow diagram, a deeper explanation of the sequence, and implementation verification guidance. The diagrams describe the required workflow conceptually; repository-specific components must be confirmed from source code.", styles["Body3"]), Spacer(1, 12*mm), Paragraph("Page count: 61 total (1 cover + 60 topic pages)", styles["Body3"]), PageBreak()]

for i, title in enumerate(titles, 1):
    steps = workflow[title].split("->")
    story += [Paragraph(f"TOPIC {i} OF 60", styles["No2"]), Paragraph(title, styles["Topic2"]), Paragraph("Workflow diagram", styles["Label2"]), WorkflowDiagram(steps), Spacer(1, 2*mm), Paragraph("Deep explanation", styles["Label2"])]
    first = f"The workflow for {title.lower()} has a clear handoff between stages. "
    second = f"It starts with {steps[0].strip()} and moves through the intermediate stages until {steps[-1].strip()}. "
    third = f"The important engineering question is what data is created at each handoff, which component owns it, and what happens when that stage fails. {meaning[title]}"
    story += [Paragraph(first + second + third, styles["Body3"]), Paragraph("Verification workflow", styles["Label2"]), Paragraph("Locate the relevant source files, configuration, dependency, and tests. Trace one real execution path from input to output. Record exact names and values; if evidence is absent, use the required NOT IMPLEMENTED IN THIS PROJECT or PRODUCTION RECOMMENDATION - NOT CURRENTLY IMPLEMENTED label.", styles["Body3"])]
    story += [Paragraph("Beginner takeaway: follow the arrows from left to right. Each box transforms information or makes a decision before handing the result to the next box.", styles["Small2"])]
    if i != 60:
        story.append(PageBreak())

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT.resolve())
