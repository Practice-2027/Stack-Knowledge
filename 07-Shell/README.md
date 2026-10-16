# 🌐 07-Shell — Micro-Frontend Portal & API Gateway

> **A beginner-friendly Single-Pane-of-Glass application portal and reverse-proxy API Gateway that routes, manages, and connects all microservices in your architecture.**

---

## 1. What is an Application Shell & API Gateway? (Beginner Analogy)

Imagine visiting a luxury hotel:
- You don't walk into the kitchen to order dinner, wander into the basement to pay your bill, or knock on the electrical room to check room lights.
- Instead, you visit the **Front Desk / Concierge (The Shell & Gateway)**:
  - You tell them what you need.
  - The concierge routes your request to the Kitchen, Housekeeping, or Maintenance.
  - The concierge attaches your **Room Key / Tenant Identity** to ensure you only access your own room.
  - The concierge monitors which hotel amenities are currently open.

In software architecture, **07-Shell** sits at the perimeter on **Port 5009**:
1. Provides a **Unified UI** (Single-Pane-of-Glass) linking all distributed dashboards.
2. Acts as an **API Gateway (Reverse Proxy)**: clients talk to `/gateway/<service>/...`, and Shell routes downstream without exposing internal ports directly.
3. Injects tenant security headers (`X-Tenant-ID`, `X-Gateway-Forwarded`).
4. Performs live **Port Probing** to display an instant status matrix of the entire ecosystem.

---

## 2. Architecture & Data Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                        WEB BROWSER / CLIENT                            │
│                  Visits http://localhost:5009                          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       07-SHELL (Port 5009)                             │
│                                                                        │
│   ┌───────────────────────────┐    ┌───────────────────────────────┐   │
│   │ Unified Portal Navigation │    │ Transparent Reverse-Proxy     │   │
│   │ & Service Health Matrix   │    │ Gateway Router                │   │
│   └───────────────────────────┘    └───────────────┬───────────────┘   │
│                                                    │ Injects           │
│                                                    │ X-Tenant-ID       │
└────────────────────────────────────────────────────┼───────────────────┘
                                                     │
         ┌───────────────────┬───────────────────────┼───────────────────┐
         │                   │                       │                   │
         ▼                   ▼                       ▼                   ▼
┌──────────────────┐┌──────────────────┐┌──────────────────┐┌──────────────────┐
│06-Platform-Core  ││08-Injest Engine  ││04-RAG Vector     ││05-AI-Agents      │
│  (Port 5008)     ││  (Port 5010)     ││  (Port 5006)     ││  (Port 5007)     │
└──────────────────┘└──────────────────┘└──────────────────┘└──────────────────┘
```

---

## 3. How Reverse Proxy Routing Works

When a client calls:
```http
POST /gateway/ingest/api/event
```
1. Shell recognizes target prefix `ingest` -> resolves destination `http://localhost:5010/api/event`.
2. Shell probes `localhost:5010` to confirm health.
3. Injects standard enterprise tracking headers:
   - `X-Gateway-Forwarded: 07-Shell-Portal-v1.0`
   - `X-Tenant-ID: tenant-dev-03`
4. Dispatches the HTTP request downstream via `requests`.
5. Returns the exact response body, status code, and content type back to the client while calculating roundtrip latency.

---

## 4. How to Run & Test

### Run Standalone
```powershell
cd "c:\Users\itzme\Desktop\All Stacks\07-Shell"
pip install -r requirements.txt
python app.py
```

### Access Portal
- Open your browser to: **`http://localhost:5009`**
- View the **Ecosystem Status Matrix** on the left.
- Use the **Shell API Gateway Proxy Console** on the right to trigger live requests through the gateway!

### Test via Terminal (PowerShell or cURL)

#### 1. Query Gateway Health
```powershell
curl http://localhost:5009/health
```

#### 2. Call Platform-Core via Gateway
```powershell
curl http://localhost:5009/gateway/platform/api/health
```

#### 3. Fetch Ingestion Metrics via Gateway
```powershell
curl http://localhost:5009/gateway/ingest/api/metrics
```

---

## 5. File Structure

```
07-Shell/
├── app.py                     # Main Flask Gateway & Portal Server (Port 5009)
├── requirements.txt           # Minimal dependencies (Flask, requests)
├── templates/
│   └── portal.html            # Dark-theme Portal & Interactive Gateway Tester
└── README.md                  # This documentation guide
```
