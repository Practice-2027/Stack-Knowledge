from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "keycloak-requirements" / "KEYCLOAK_WORKFLOW_DIAGRAMS_AND_DEEP_EXPLANATION.pdf"

styles = getSampleStyleSheet()
title = ParagraphStyle("title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=23, leading=27, alignment=TA_CENTER, textColor=colors.HexColor("#123B5D"), spaceAfter=12)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=10, leading=14, alignment=TA_CENTER, textColor=colors.HexColor("#52616B"), spaceAfter=18)
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=colors.HexColor("#123B5D"), spaceAfter=8)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12.5, leading=15, textColor=colors.HexColor("#0E6B78"), spaceBefore=8, spaceAfter=5)
body = ParagraphStyle("body", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.3, leading=13, spaceAfter=7)
small = ParagraphStyle("small", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.2, leading=10.5, textColor=colors.HexColor("#52616B"), spaceAfter=4)
node = ParagraphStyle("node", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=9, leading=11, alignment=TA_CENTER, textColor=colors.HexColor("#123B5D"))

def P(text, style=body):
    return Paragraph(text, style)

def diagram(labels, caption=None):
    rows = []
    for i, label in enumerate(labels):
        rows.append([P(label, node)])
        if i != len(labels) - 1:
            rows.append([P("v", ParagraphStyle("arrow", parent=node, fontSize=12, leading=14, textColor=colors.HexColor("#0E6B78")))])
    t = Table(rows, colWidths=[150*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#E8F2F4")),
        ("BOX", (0,0), (-1,-1), 0.8, colors.HexColor("#7CAAB2")),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.HexColor("#B9C9D0")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    items = [t]
    if caption:
        items.append(Spacer(1, 4))
        items.append(P(caption, small))
    return items

def two_col(left, right):
    t = Table([[P(left, body), P(right, body)]], colWidths=[77*mm, 77*mm])
    t.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("BOX", (0,0), (-1,-1), 0.35, colors.HexColor("#C5D2D8")), ("INNERGRID", (0,0), (-1,-1), 0.35, colors.HexColor("#C5D2D8")), ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F7FAFB")), ("LEFTPADDING", (0,0), (-1,-1), 7), ("RIGHTPADDING", (0,0), (-1,-1), 7), ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6)]))
    return t

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D7E2E8"))
    canvas.line(18*mm, 14*mm, 192*mm, 14*mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#60727E"))
    canvas.drawString(18*mm, 9*mm, "Keycloak Workflow Diagrams and Deep Explanation")
    canvas.drawRightString(192*mm, 9*mm, f"Page {doc.page}")
    canvas.restoreState()

story = []
story += [P("Keycloak Workflow Diagrams", title), P("Deep beginner-friendly explanation of authentication, tokens, APIs, authorization, and production flow", sub)]
story += [P("Important scope note", h2), P("This companion PDF explains the workflows required by the pasted prompt. It is not a claim that every step is implemented in the current repository. To convert the reference workflows into project documentation, verify each step against actual files, configuration, requests, and tests.", body)]
story += diagram(["User", "Frontend application", "Keycloak realm and client", "Authentication and authorization", "Tokens", "Protected backend API", "Response shown to user"], "The central mental model: identity is verified by Keycloak; the API trusts only a validated access token.")
story += [PageBreak(), P("1. The complete system workflow", h1), P("A Keycloak application is a chain of responsibilities. The frontend starts the user journey, Keycloak proves identity and issues tokens, and the backend independently checks the access token before serving protected data. The frontend is not the authority for API access.", body)]
story += diagram(["1. User opens the application", "2. Frontend starts login", "3. Browser visits Keycloak authorization endpoint", "4. Keycloak identifies realm and client", "5. User authenticates", "6. Keycloak returns an authorization result", "7. Application obtains tokens", "8. Frontend calls protected API", "9. Backend validates token and roles", "10. Business logic returns response"], "Each arrow represents a request, redirect, local state change, or server-side validation step.")
story += [P("How to read this workflow", h2), P("The browser may move between the application and Keycloak several times. A redirect is not the same as an API call: it changes where the browser is located. The authorization code is also not the access token. It is a short-lived result that the correct client exchanges at the token endpoint.", body), P("The backend repeats security checks even if the frontend already displays the user as logged in. This protects the API when someone calls it directly, modifies browser state, or replays an old request.", body), PageBreak()]

story += [P("2. Login and Authorization Code Flow", h1), P("The authorization code flow separates the browser-facing login step from the server-facing token exchange. This reduces the chance that long-lived credentials or tokens are exposed in the browser URL.", body)]
story += diagram(["User clicks Login", "Frontend builds authorization request", "Browser redirects to Keycloak", "Keycloak shows login page", "User submits credentials", "Keycloak validates user", "Keycloak redirects with temporary code", "Client exchanges code at token endpoint", "Keycloak returns access, ID, and possibly refresh tokens"], "A code is temporary and single-purpose. It must be exchanged, not sent to a protected API.")
story += [P("Step-by-step", h2), P("1. The frontend chooses the realm and client through its configuration. 2. It sends the browser to the authorization endpoint with values such as client_id, redirect_uri, response_type=code, and scope. 3. Keycloak validates that the client and redirect URI are allowed. 4. Keycloak authenticates the user inside the selected realm. 5. Keycloak sends the browser back to the registered redirect URI with a temporary code. 6. The client sends the code, redirect URI, and client credentials or verifier to the token endpoint. 7. Keycloak validates the exchange and issues tokens.", body), P("Failure points include an unknown realm, wrong client ID, redirect URI mismatch, disabled user, invalid credentials, expired code, or a client that is not allowed to use the selected flow. The documentation must name the exact file and function that starts the request and handles the callback.", body), PageBreak()]

story += [P("3. PKCE: protecting the code exchange", h1), P("PKCE adds a proof that the same application instance that started login is the one exchanging the authorization code. It is especially important for public clients that cannot keep a client secret safely.", body)]
story += diagram(["Application creates random code verifier", "Application derives code challenge", "Authorization request contains challenge", "Keycloak returns authorization code", "Token request contains verifier", "Keycloak derives challenge and compares", "Tokens are returned only if they match"], "The verifier stays private to the application instance; the challenge travels through the authorization request.")
story += [P("Why it matters", h2), P("Without PKCE, an attacker who obtains an authorization code may try to exchange it before the legitimate application. With PKCE, the attacker also needs the verifier. The verifier should be high-entropy, single-use, and associated with the login transaction.", body), P("If the repository does not implement PKCE, say so explicitly. Do not describe PKCE as implemented merely because the Keycloak server supports it. Record the client type, library options, generated parameters, and callback behavior as evidence.", body), PageBreak()]

story += [P("4. Token lifecycle", h1), P("Tokens are different documents with different audiences. The access token is for the resource server, the ID token is for the client application, and the refresh token is used to obtain new access tokens when allowed.", body)]
story.append(two_col("<b>Access token</b><br/>Sent in the Authorization header to a protected API. The API validates its signature and claims before using it.", "<b>ID token</b><br/>Describes the authenticated user to the client. It is not a general-purpose API permission token."))
story.append(Spacer(1, 7))
story.append(two_col("<b>Refresh token</b><br/>Used at the token endpoint to request a new access token. It needs stronger protection because it can extend a session.", "<b>Authorization code</b><br/>A temporary exchange artifact. It should not be stored as the user's API credential."))
story += [P("Lifecycle workflow", h2)]
story += diagram(["Login succeeds", "Code exchanged", "Access token used for API", "Access token expires or is near expiry", "Refresh request sent to Keycloak", "New access token returned", "If refresh fails, user signs in again"], "The exact storage method, rotation policy, and expiry values must be verified from project code and Keycloak configuration.")
story += [P("JWT validation is not decryption", h2), P("A signed JWT can be decoded by anyone who has it. The signature proves that an issuer with the corresponding signing key created it and that the contents were not changed. The API must also check issuer, audience when applicable, expiration, and any required scopes or roles.", body), PageBreak()]

story += [P("5. Protected API and token validation", h1), P("A protected API request should fail closed. A missing, malformed, expired, incorrectly issued, or insufficiently authorized token must not reach protected business logic.", body)]
story += diagram(["Frontend creates API request", "Authorization: Bearer <access-token>", "Backend receives request", "Middleware extracts bearer token", "Validate signature and issuer", "Check expiration and audience", "Extract subject and roles", "Authorization policy checks permission", "Route handler runs or request is rejected"], "Authentication answers: who are you? Authorization answers: may you do this action?")
story += [P("Typical decision outcomes", h2), P("401 Unauthorized means the request lacks a valid authentication credential. Examples include no header, malformed token, invalid signature, wrong issuer, or expired token. 403 Forbidden means authentication succeeded but the identity lacks the required permission or role. The exact status and response body must be verified in the backend implementation.", body), P("The safest middleware order is: parse the request, extract the token, validate cryptography and claims, attach a minimal identity object to the request, check authorization, then call business logic. Logging should avoid printing full tokens.", body), PageBreak()]

story += [P("6. Roles, scopes, and authorization", h1), P("Keycloak can carry authorization information through realm roles, client roles, groups, scopes, and protocol mappers. The application still needs a clear policy describing which claim grants which action.", body)]
story += diagram(["User belongs to group or receives role", "Keycloak maps roles and scopes", "Token contains selected claims", "Backend reads claims", "Policy maps claim to permission", "Allow or reject endpoint"], "A role only becomes useful when the backend checks it consistently at a protected decision point.")
story += [P("Example reasoning", h2), P("Suppose an endpoint requires an admin client role. The documentation should show where that role is created, how it is assigned, which token claim carries it, how the backend extracts it, and which middleware checks it. If a role exists in the realm but no code checks it, it is configuration, not effective authorization.", body), P("Scopes are not automatically the same as roles. A scope often describes requested access or claims, while a role usually expresses an authorization position. Protocol mappers decide which data appears in tokens. These relationships must be confirmed from the realm export and application code.", body), PageBreak()]

story += [P("7. Logout and refresh workflows", h1), P("Logout has both a Keycloak session side and an application side. Ending one without the other can leave confusing behavior, such as a local screen that appears logged out while a browser session can silently log in again.", body)]
story += diagram(["User clicks Logout", "Application clears local auth state", "Browser visits Keycloak logout endpoint", "Keycloak ends the user session", "Keycloak redirects to registered post-logout URI", "Application shows signed-out state"], "The redirect URI must be registered and should not be accepted from arbitrary user input.")
story += [P("Refresh workflow", h2), P("When the access token expires, the application may send the refresh token to the token endpoint. Keycloak checks the session, client, token validity, and rotation or reuse policy. A successful response replaces the usable access token. A failed response should clear stale local state and require a fresh login.", body), P("Document whether the project stores tokens in memory, browser storage, cookies, or a library-managed session. The choice affects exposure to XSS, CSRF, tab persistence, and logout behavior.", body), PageBreak()]

story += [P("8. Docker, startup, and database workflow", h1), P("Local Keycloak projects often use containers to make the server, database, and configuration repeatable. Startup order is not the same as readiness: a container can be running before Keycloak can accept requests.", body)]
story += diagram(["Docker Compose loads services and environment", "Database starts", "Keycloak starts", "Keycloak reads database and realm import", "Health/readiness becomes available", "Application connects to Keycloak", "User can log in"], "The exact import behavior and environment variable names must be verified from compose files and startup commands.")
story += [P("Identity data versus business data", h2), P("Keycloak's database stores identity-management data such as users, clients, sessions, credentials metadata, roles, and realm configuration. The application database stores business records. They may be related by a stable subject identifier, but the application should not copy or manage passwords.", body), P("Document startup failures separately from authentication failures. A database connection error may prevent Keycloak from starting at all; a bad redirect URI may allow Keycloak to run but break login.", body), PageBreak()]

story += [P("9. Debugging workflow", h1), P("Debugging is fastest when each layer is checked in order. Begin with the browser-visible URL and only move deeper after the previous layer is correct.", body)]
story += diagram(["Browser URL and network tab", "Realm and client", "Redirect URI and web origin", "User and credentials", "Authorization code callback", "Token response", "Authorization header", "Backend issuer/signature/expiry", "Roles and policy", "Business response"], "Use the first failing layer as the starting point; later symptoms may only be consequences.")
story += [P("Common diagnosis", h2), P("A redirect URI error points to client configuration. A login loop often points to callback handling or lost state. A 401 points to the token or validation configuration. A 403 points to role mapping or policy. A CORS error points to browser origin rules and does not necessarily mean the token is invalid.", body), P("Capture request method, URL without secrets, status code, safe response details, issuer, audience, expiry, and relevant source location. Never paste full access or refresh tokens into logs, tickets, or documentation.", body), PageBreak()]

story += [P("10. Production architecture workflow", h1), P("A simple local setup can evolve into a production identity platform by adding redundancy, durable storage, secure networking, observability, and operational controls.", body)]
story += diagram(["Users", "Load balancer / reverse proxy", "Keycloak instance 1 and instance 2", "Highly available Keycloak database", "Applications and backend APIs", "Monitoring, logs, alerts, backups", "Disaster recovery process"], "Production architecture adds operational reliability around the same authentication and authorization concepts.")
story += [P("Scaling decisions", h2), P("Multiple Keycloak instances require compatible configuration and a database strategy that supports concurrent operation. Health checks should distinguish process health from readiness. Backups must be tested by restoring them. Monitoring should cover login failures, token failures, latency, error rates, database health, CPU, memory, and active sessions.", body), P("Security improvements include HTTPS, strict redirect URIs, protected secrets, short access-token lifetimes, safe refresh-token handling, brute-force protection, MFA where appropriate, rate limiting, least privilege, and centralized audit logs.", body), PageBreak()]

story += [P("11. The exact Login answer", h1), P("When asked, 'What exactly happens when I click Login?', use this sequence and replace the generic names with verified filenames and functions from the repository.", body)]
story += diagram(["1. User clicks Login", "2. Frontend starts authentication", "3. Browser redirects to Keycloak", "4. Keycloak selects realm and client", "5. User enters credentials", "6. Keycloak authenticates user", "7. Keycloak returns authorization code", "8. Application exchanges code for tokens", "9. Frontend stores or manages auth state", "10. Frontend sends access token to API", "11. Backend validates token", "12. Backend checks roles", "13. Business logic executes", "14. Response returns to frontend"], "For every step, document what, why, where, which file/function, request, response, token, and failure behavior.")
story += [P("Beginner summary", h2), P("Keycloak is the identity authority. The application asks Keycloak to authenticate the user. Keycloak returns proof in the form of tokens. The backend does not trust the browser's claim that the user is logged in; it trusts only a valid access token and an authorization policy that allows the requested operation.", body), P("Repository-specific completion means replacing every generic actor with evidence: actual realm name, client ID, redirect URI, library, callback handler, middleware, endpoint, role claim, and database configuration. If evidence is absent, write that the feature is not currently implemented.", body), PageBreak()]

story += [P("12. Documentation checklist", h1), P("Use this final checklist while converting the diagrams into repository-specific documentation.", body)]
checklist = [["Workflow area", "Evidence required"], ["Login", "Frontend trigger, authorization URL, callback, code exchange"], ["Keycloak", "Version, realm, client, redirect URIs, user and role configuration"], ["Tokens", "Token library, claims used, storage, expiry and refresh behavior"], ["API", "Routes, middleware order, status codes, authorization checks"], ["Security", "HTTPS, secrets, CORS, CSRF, PKCE, MFA, rate limits"], ["Operations", "Docker, database, readiness, logs, backups, monitoring"], ["Accuracy", "Implemented versus recommended; no secrets or real tokens"]]
t = Table([[P(a, small), P(b, small)] for a,b in checklist], colWidths=[38*mm, 132*mm])
t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8F2F4")), ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#B9C9D0")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6), ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)]))
story.append(t)
story += [Spacer(1, 10), P("Final principle", h2), P("Explain the system as a chain of evidence, not as a list of Keycloak features. Every diagram arrow should correspond to a real request, redirect, configuration relationship, validation step, or documented recommendation.", body)]

doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=16*mm, bottomMargin=18*mm, title="Keycloak Workflow Diagrams and Deep Explanation", author="Codex")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
