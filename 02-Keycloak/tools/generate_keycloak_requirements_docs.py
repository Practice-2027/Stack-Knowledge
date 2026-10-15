from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "keycloak-requirements"
OUT.mkdir(parents=True, exist_ok=True)

topics = [
    "Analyze the Complete Project First", "Project Overview", "What Is Keycloak?", "Why Use Keycloak?",
    "Complete Keycloak Architecture", "Technology Stack", "Keycloak Components", "Realm", "Client", "Client Types",
    "User", "Complete Login Flow", "OAuth 2.0 Explanation", "OpenID Connect", "Authorization Code Flow", "PKCE",
    "Token Types", "JWT Structure", "Complete Token Flow", "Protected API Flow", "API Documentation",
    "Authentication Middleware", "Authorization", "Realm Roles", "Client Roles", "Role Mapping", "Groups",
    "Client Scopes", "Protocol Mappers", "UserInfo", "Logout Flow", "Refresh Token Flow", "Keycloak Admin Console",
    "Docker / Keycloak Startup", "Keycloak Database", "Complete Database Flow", "Error Handling", "Common Keycloak Errors",
    "Security Analysis", "Environment Variables", "Frontend Flow", "Backend Flow", "Complete End-to-End Example",
    "Complete Token Example", "Keycloak vs Custom JWT", "Keycloak vs Other Identity Providers", "Scalability",
    "Production Keycloak Architecture", "High Availability", "Monitoring", "Testing", "Debugging Workflow",
    "Keycloak CLI / Admin Commands", "Folder Structure", "File-by-File Explanation", "Mermaid Diagrams",
    "Beginner Glossary", "Common Beginner Confusions", "Interview Questions", "2-Minute Project Explanation",
    "5-Minute Technical Explanation", "Learning Path", "Documentation Files", "Master Markdown File", "Complete PDF",
    "PDF Quality Check", "Final Master Flow", "Most Important Question", "Accuracy Rules",
]

focus = {
    "Analyze the Complete Project First": "This is the evidence-gathering stage. Read the real frontend, backend, Keycloak export, Docker files, environment examples, tests, and deployment files before making claims.",
    "Project Overview": "Describe the application in plain language and show how the user, application, Keycloak, tokens, and protected API fit together.",
    "What Is Keycloak?": "Explain Keycloak as an identity and access-management server that authenticates users, issues tokens, and centralizes access rules.",
    "Why Use Keycloak?": "Compare application-owned login with centralized identity management, including SSO, standard protocols, and reduced authentication code.",
    "Complete Keycloak Architecture": "Map browser, frontend, backend, Keycloak realm, client, database, and any application database to the actual deployment.",
    "Technology Stack": "Inventory only technologies found in the repository and explain what each one does, where it runs, and how it communicates.",
    "Keycloak Components": "Introduce realm, client, user, role, scope, mapper, identity provider, and authentication flow, giving detail only where the project uses them.",
    "Realm": "Explain a realm as an isolated identity space and document its real name, settings, users, clients, and roles without exposing secrets.",
    "Client": "Explain the Keycloak client as the registered application identity and document its ID, flow settings, redirect URIs, origins, and authentication mode.",
    "Client Types": "Explain public, confidential, and bearer-only clients, then identify the project's type and the security reason for that choice.",
    "User": "Explain how a Keycloak user is stored and authenticated, covering profile fields, enabled state, credentials, roles, and groups without passwords.",
    "Complete Login Flow": "Trace the real click-to-login sequence from the frontend to the authorization endpoint, login page, callback, token endpoint, and authenticated state.",
    "OAuth 2.0 Explanation": "Map resource owner, client, authorization server, resource server, authorization code, access token, and scope to this project.",
    "OpenID Connect": "Explain OIDC as the identity layer on OAuth 2.0, especially the ID token, user identity, and UserInfo endpoint.",
    "Authorization Code Flow": "Explain why a temporary authorization code is returned first and then exchanged for tokens by the correct client.",
    "PKCE": "Check whether PKCE is implemented. Explain verifier, challenge, and interception protection, and explicitly mark it as absent when not found.",
    "Token Types": "Compare access, ID, and refresh tokens by purpose, recipient, lifetime, and safe handling.",
    "JWT Structure": "Explain header, payload, and signature using a fake token and distinguish claims actually consumed by code from common Keycloak claims.",
    "Complete Token Flow": "Connect login, code exchange, token issuance, token storage, API authorization header, validation, expiry, and refresh.",
    "Protected API Flow": "Trace a protected request from frontend call through bearer-token extraction, validation, authorization, business logic, and response.",
    "API Documentation": "Document actual endpoints, methods, inputs, outputs, authentication requirements, roles, success responses, and failure responses.",
    "Authentication Middleware": "Identify middleware that proves token authenticity and explain issuer, signature, expiration, audience, and claim checks.",
    "Authorization": "Separate authentication from authorization and show how the project decides whether an authenticated user may perform an action.",
    "Realm Roles": "Explain realm-wide roles and document only roles present in the realm export or configuration.",
    "Client Roles": "Explain application-specific roles and show where their names are emitted, mapped, and checked.",
    "Role Mapping": "Trace how a user, group, realm role, or client role becomes an effective authorization decision.",
    "Groups": "Check whether groups exist and explain inheritance and membership only when demonstrated by project configuration.",
    "Client Scopes": "Explain scopes as sets of requested permissions and mapped claims, distinguishing default and optional scopes.",
    "Protocol Mappers": "Explain how mappers place identity or authorization data into tokens and identify every mapper relied on by the app.",
    "UserInfo": "Document whether the application calls UserInfo and why it would use that endpoint instead of relying only on token claims.",
    "Logout Flow": "Trace browser logout, Keycloak session termination, redirect behavior, local token cleanup, and failure handling.",
    "Refresh Token Flow": "Explain refresh-token exchange, rotation or reuse settings, expiry, revocation, and secure storage expectations.",
    "Keycloak Admin Console": "Explain the console areas needed to inspect realms, clients, users, roles, scopes, sessions, and events.",
    "Docker / Keycloak Startup": "Trace container startup, environment loading, realm import, port exposure, health readiness, and dependency order.",
    "Keycloak Database": "Identify the configured database and explain which identity data belongs to Keycloak versus application business data.",
    "Complete Database Flow": "Show how configuration and identity records are read or written during startup, login, token issuance, and administration.",
    "Error Handling": "For each failure, record cause, layer, status, response, user experience, and debugging evidence.",
    "Common Keycloak Errors": "Create Cause -> Check -> Fix guides for 401, 403, token, issuer, audience, redirect, client, realm, CORS, and connection errors.",
    "Security Analysis": "Separate implemented controls from production recommendations for HTTPS, secrets, PKCE, CORS, CSRF, XSS, MFA, brute force, and rate limits.",
    "Environment Variables": "List variable names, purpose, consumers, and safe example formats while redacting real secret values.",
    "Frontend Flow": "Document login initiation, callback, token handling, auth state, protected routes, API calls, and logout using actual files and functions.",
    "Backend Flow": "Document configuration loading, route registration, middleware order, token validation, authorization, and business logic.",
    "Complete End-to-End Example": "Walk through one login-to-protected-API scenario step by step, naming the request, response, file, function, token, and failure point.",
    "Complete Token Example": "Use only fake, sanitized JWT payloads to illustrate issuer, subject, audience, username, and expiry.",
    "Keycloak vs Custom JWT": "Compare who handles users, login, token issuance, roles, revocation, and operational burden.",
    "Keycloak vs Other Identity Providers": "Give a focused comparison with Auth0, Okta, Cognito, and Entra ID, centered on why this project may choose Keycloak.",
    "Scalability": "Explain how the design changes from a local setup to thousands, hundreds of thousands, and millions of users.",
    "Production Keycloak Architecture": "Describe load balancing, multiple Keycloak instances, a durable database, applications, and resource APIs.",
    "High Availability": "Explain redundancy, health checks, failover, backups, disaster recovery, and database availability.",
    "Monitoring": "Define useful production signals: login failures, token failures, health, latency, error rate, CPU, memory, and sessions.",
    "Testing": "Inventory existing tests and recommend authentication, authorization, token, API, logout, and error cases when missing.",
    "Debugging Workflow": "Give a repeatable browser -> redirect -> realm/client -> user -> backend -> token investigation path for login and API failures.",
    "Keycloak CLI / Admin Commands": "Include only commands compatible with the detected Keycloak version and startup method.",
    "Folder Structure": "Explain the real directories and identify where frontend, backend, Keycloak, Docker, tests, and documentation live.",
    "File-by-File Explanation": "For every important file, capture purpose, imports, functions, callers, calls, auth responsibility, inputs, and outputs.",
    "Mermaid Diagrams": "Create diagrams for architecture, realm, client, login, code flow, token validation, protected API, logout, roles, database, and production.",
    "Beginner Glossary": "Define identity terms in one or two plain-language sentences, including realm, client, JWT, issuer, audience, SSO, and MFA.",
    "Common Beginner Confusions": "Answer the common distinctions: Keycloak versus database, backend, API, JWT, OAuth, OIDC, access token, ID token, and frontend trust.",
    "Interview Questions": "Create project-specific beginner, intermediate, and advanced questions with technically correct, easy-to-say answers.",
    "2-Minute Project Explanation": "Provide a short interview answer describing the actual application, Keycloak responsibilities, tokens, backend validation, and role checks.",
    "5-Minute Technical Explanation": "Provide a deeper narrative from user and realm through client, authentication, code, tokens, API validation, roles, and response.",
    "Learning Path": "Order learning from HTTP to authentication, JWT, OAuth, OIDC, Keycloak, RBAC, SSO, MFA, and production IAM.",
    "Documentation Files": "Define a maintainable docs folder, stable filenames, a master index, and links between topic pages.",
    "Master Markdown File": "Assemble the complete learning path into one navigable Markdown document with implementation notes and production recommendations.",
    "Complete PDF": "Create a polished PDF containing the complete documentation, diagrams, examples, tables, page numbers, and redacted examples.",
    "PDF Quality Check": "Verify clipping, diagram overlap, readable code, table width, page numbers, contents, JSON formatting, and secret redaction.",
    "Final Master Flow": "End with one compact end-to-end flow from user to application, realm, client, login, tokens, API, validation, authorization, and response.",
    "Most Important Question": "Answer exactly what happens after Login is clicked, including where, why, request, response, token, failure, and production equivalent.",
    "Accuracy Rules": "Treat repository evidence as authoritative, never invent configuration, never expose secrets, and clearly separate implemented behavior from recommendations.",
}

def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def markdown_for(index, title):
    why = focus[title]
    workflow = (
        "Inspect the repository -> identify the relevant configuration or code -> explain the behavior in plain language "
        "-> trace the request/response workflow -> verify every claim against source evidence -> mark missing features explicitly."
    )
    return f"""# {index:02d}. {title}\n\n> Requirements guide generated from the pasted Keycloak documentation prompt. This page defines what to document; it does not claim that the feature exists in the repository.\n\n## In simple words\n\n{why}\n\n## Required workflow\n\n{workflow}\n\n## Evidence to capture\n\n- Exact repository file paths and function names.\n- Relevant Keycloak realm, client, user, role, scope, mapper, or Docker settings.\n- Request and response shape, including status codes and token involvement.\n- What is currently implemented.\n- What is absent and should be treated only as a production recommendation.\n\n## Safety rules\n\nUse fake examples only. Redact passwords, client secrets, access tokens, refresh tokens, private keys, and sensitive environment values. Never infer a Keycloak feature from documentation alone.\n\n## Expected result\n\nA beginner should be able to explain the concept, follow the workflow, locate the implementation, and distinguish observed behavior from recommended improvements.\n"""

all_pages = []
for i, title in enumerate(topics, 1):
    filename = f"{i:02d}-{slug(title)}.md"
    content = markdown_for(i, title)
    (OUT / filename).write_text(content, encoding="utf-8")
    all_pages.append((i, title, filename, content))

index_lines = ["# Keycloak Requirements Guide", "", "This guide contains **69 topics** extracted from the pasted prompt. The source prompt says 60 in one place, but its numbered sections run from 1 through 69.", "", "This is a requirements analysis and documentation blueprint. Repository-specific facts must be filled in only after inspecting the actual project.", "", "## Topics", ""]
for i, title, filename, _ in all_pages:
    index_lines.append(f"{i}. [{title}]({filename})")
index_lines += ["", "## Validation rule", "Every implementation statement must be backed by a repository file, configuration value, request trace, or test. If evidence is missing, write: `This feature is not currently implemented in this project.`"]
(OUT / "README.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

master = ["# Complete Keycloak Requirements Documentation", "", "## Scope", "", "The pasted prompt contains 69 numbered sections. This master file links each topic page. It is intentionally evidence-first: the actual repository must be inspected before any project-specific claim is added.", "", "## Topic pages", ""]
for i, title, filename, _ in all_pages:
    master.append(f"### {i:02d}. {title}")
    master.append(f"\n{focus[title]} See [{filename}]({filename}).\n")
master += ["## Final documentation standard", "", "Teach the project from beginner concepts through actual implementation, OAuth 2.0 and OIDC, token flow, protected APIs, security, operations, and production IAM. Keep implemented behavior separate from recommendations and never include real credentials or tokens."]
(OUT / "COMPLETE_KEYCLOAK_DOCUMENTATION.md").write_text("\n".join(master) + "\n", encoding="utf-8")

pdf_path = OUT / "COMPLETE_KEYCLOAK_DOCUMENTATION.pdf"
styles = getSampleStyleSheet()
title_style = ParagraphStyle("PageTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=20, leading=24, alignment=TA_CENTER, textColor=colors.HexColor("#123B5D"), spaceAfter=12)
subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#506070"), spaceAfter=18)
heading_style = ParagraphStyle("Heading", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=colors.HexColor("#0E6B78"), spaceBefore=8, spaceAfter=5)
body_style = ParagraphStyle("Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=12.5, spaceAfter=6)
small_style = ParagraphStyle("Small", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.2, leading=10.5, textColor=colors.HexColor("#52616B"), spaceAfter=4)

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D7E2E8"))
    canvas.line(18*mm, 14*mm, 192*mm, 14*mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#60727E"))
    canvas.drawString(18*mm, 9*mm, "Keycloak Requirements Guide - evidence-first documentation")
    canvas.drawRightString(192*mm, 9*mm, f"Page {doc.page}")
    canvas.restoreState()

story = []
for pos, (i, title, filename, content) in enumerate(all_pages):
    story.append(Paragraph(f"{i:02d}. {title}", title_style))
    story.append(Paragraph("Beginner-friendly requirements page", subtitle_style))
    story.append(Paragraph("In simple words", heading_style))
    story.append(Paragraph(focus[title], body_style))
    story.append(Paragraph("Required workflow", heading_style))
    story.append(Paragraph("Inspect repository -> identify evidence -> explain simply -> trace request/response -> verify -> label missing features.", body_style))
    story.append(Paragraph("Evidence checklist", heading_style))
    checklist = [["Capture", "What the final documentation must contain"], ["Implementation", "Exact files, functions, configuration, and observed behavior"], ["Workflow", "Actors, request, response, status, token, and failure path"], ["Safety", "Fake examples only; redact secrets and real tokens"], ["Clarity", "Implemented behavior separated from production recommendations"]]
    table = Table([[Paragraph(a, small_style), Paragraph(b, small_style)] for a, b in checklist], colWidths=[35*mm, 135*mm])
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8F2F4")), ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#B9C9D0")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6), ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)]))
    story.append(table)
    story.append(Spacer(1, 8))
    story.append(Paragraph("Expected result", heading_style))
    story.append(Paragraph("A beginner can explain the concept, follow the workflow, locate the implementation, and distinguish observed project behavior from recommended improvements.", body_style))
    story.append(Paragraph(f"Markdown page: {filename}", small_style))
    if pos != len(all_pages) - 1:
        story.append(PageBreak())

doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=16*mm, bottomMargin=18*mm, title="Complete Keycloak Requirements Documentation", author="Codex")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(f"Created {len(all_pages)} Markdown topic files, README.md, master Markdown, and {pdf_path}")
