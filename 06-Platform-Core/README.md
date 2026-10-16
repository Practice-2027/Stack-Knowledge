# 🏛️ 06-Platform-Core — Enterprise Backbone & Service Registry Hub

> **A beginner-friendly central platform hub that manages Service Discovery, Feature Flags, Multi-Tenancy, and Platform-wide Audit Logging.**

---

## 1. What is Platform-Core? (Beginner Analogy)

Imagine a large modern airport:
- Airplanes (Microservices like Ingestion, Shell, RAG, AI Agents) fly in and out constantly.
- But who knows which runway is open? Who manages airport rules and passenger records?
- **Air Traffic Control & Airport Operations (Platform Core)** acts as the central brain:
  1. **Service Registry**: Tells every plane where the gates are (`http://localhost:5001`, `5008`, `5010`).
  2. **Feature Flags**: Turns runway lights on or off dynamically without rebuilding the airport.
  3. **Tenant & API Key Directory**: Verifies airline credentials and ticket levels (Standard, Pro, Enterprise).
  4. **Audit Trail**: Records every takeoff, landing, and operational adjustment in a central black-box ledger.

In this project, **06-Platform-Core** serves as this central backbone on **Port 5008**.

---

## 2. Architecture & Request Flow

```
                      ┌─────────────────────────────────────────┐
                      │        07-Shell Portal (Port 5009)      │
                      │  (Calls Core for Services & Flags)      │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       06-PLATFORM-CORE (Port 5008)                          │
│                                                                             │
│   ┌─────────────────────┐   ┌─────────────────────┐   ┌──────────────────┐  │
│   │  Service Registry   │   │ Dynamic Feature     │   │ Tenant Directory │  │
│   │  & Health Probing   │   │ Flags Manager       │   │ & API Key Verify │  │
│   └──────────┬──────────┘   └──────────┬──────────┘   └────────┬─────────┘  │
│              │                         │                       │            │
│              └─────────────────────────┼───────────────────────┘            │
│                                        ▼                                    │
│                         ┌─────────────────────────────┐                     │
│                         │ SQLite Store: platform_core │                     │
│                         │ (services, flags, audit)    │                     │
│                         └─────────────────────────────┘                     │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │ Probes Port Status
                                        ▼
             ┌──────────────────────────┴─────────────────────────┐
             │                                                    │
             ▼                                                    ▼
   ┌──────────────────┐                                 ┌──────────────────┐
   │ 01-Kafka (5001)  │                                 │ 08-Injest (5010) │
   └──────────────────┘                                 └──────────────────┘
```

---

## 3. Key Concepts Explained

### A. Service Registry & Discovery
Instead of hardcoding URLs across all applications, services register themselves with the Platform Core:
- When a service boots up, it pings `POST /api/registry/register`.
- The Platform Core stores the host, port, category, and health endpoint.
- Calling `POST /api/registry/probe` actively tests all ports via socket probing and updates `ONLINE` / `OFFLINE` status live!

### B. Dynamic Feature Flags
Feature flags allow engineering teams to toggle system behaviors **without restarting servers or redeploying code**:
- `enable_realtime_ingestion`: Turn on/off streaming ETL pipeline.
- `maintenance_mode`: Lock write APIs across downstream applications.
- Changing a toggle in the UI updates the SQLite database immediately and dispatches an audit log event.

### C. Unified Platform Audit Trail
Every critical administrative event (flag toggled, service registered, tenant key verified) is appended to an immutable audit ledger with timestamps and severity ratings (`INFO`, `WARN`, `ERROR`).

---

## 4. How to Run & Test

### Run Standalone
```powershell
cd "c:\Users\itzme\Desktop\All Stacks\06-Platform-Core"
pip install -r requirements.txt
python app.py
```

### Access Dashboard
- Open your browser to: **`http://localhost:5008`**
- Try toggling a feature flag and see the live status change.
- Click **"Probe Service Health"** to see which services are currently online.

### Test via Terminal (PowerShell or cURL)

#### 1. Fetch Registered Services
```powershell
curl http://localhost:5008/api/registry/services
```

#### 2. Probe All Services Live
```powershell
curl -X POST http://localhost:5008/api/registry/probe
```

#### 3. Toggle a Feature Flag
```powershell
curl -X POST http://localhost:5008/api/flags/toggle `
     -H "Content-Type: application/json" `
     -d '{"flag_key": "maintenance_mode", "enabled": 1}'
```

#### 4. Verify a Tenant API Key
```powershell
curl -X POST http://localhost:5008/api/tenants/verify `
     -H "Content-Type: application/json" `
     -d '{"api_key": "key_live_acme98234710"}'
```

---

## 5. File Structure

```
06-Platform-Core/
├── app.py                     # Main Flask server & REST API (Port 5008)
├── init_db.py                 # SQLite schema initialization and seed data
├── requirements.txt           # Minimal dependencies (Flask, requests, dotenv)
├── platform_core.db           # SQLite database (auto-created on first run)
├── templates/
│   └── dashboard.html         # Responsive Dark UI with live toggles
└── README.md                  # This documentation guide
```
