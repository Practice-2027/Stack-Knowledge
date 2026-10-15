# 🚀 All Stacks — Master Workflow & Architecture Guide

> **A beginner-friendly learning workspace covering 5 essential modern tech stacks.**
> Each folder is a complete, runnable project with its own README. This document is
> your map — it explains how all 5 stacks connect, what each one teaches, and how to
> run them step-by-step.

---

## 📋 Table of Contents

1. [Overview & Learning Path](#1-overview--learning-path)
2. [Project Map](#2-project-map)
3. [Stack-by-Stack Breakdown](#3-stack-by-stack-breakdown)
   - [01-Kafka: Task Queue System](#31-kafka-task-queue-system)
   - [02-Keycloak: Secure Notes App](#32-keycloak-secure-notes-app)
   - [03-IDP: Custom Identity Provider](#33-idp-custom-identity-provider)
   - [04-RAG: Document Q&A System](#34-rag-document-qa-system)
   - [05-AI-Agents: Multi-Agent Task Automation](#35-ai-agents-multi-agent-task-automation)
4. [How All Stacks Connect (The Big Picture)](#4-how-all-stacks-connect-the-big-picture)
5. [Prerequisites & Global Setup](#5-prerequisites--global-setup)
6. [Quick Start Commands (All Projects)](#6-quick-start-commands-all-projects)
7. [Complexity & Learning Progression](#7-complexity--learning-progression)
8. [Glossary of Key Terms](#8-glossary-of-key-terms)

---

## 1. Overview & Learning Path

This workspace teaches you **5 critical backend & AI technologies** used in modern
production systems. Each project is self-contained, uses **Python + Flask**, and
includes comprehensive documentation.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LEARNING PROGRESSION                             │
│                                                                     │
│   START HERE                                                        │
│      │                                                              │
│      ▼                                                              │
│   ┌──────────┐    ┌───────────┐    ┌─────────┐                     │
│   │ 01-Kafka │───▶│02-Keycloak│───▶│ 03-IDP  │                     │
│   │  (Async  │    │  (Auth    │    │ (Build   │                     │
│   │Messaging)│    │  Service) │    │  Your    │                     │
│   └──────────┘    └───────────┘    │  Own IDP)│                     │
│       │                            └────┬─────┘                     │
│       │    ┌────────────────────────────┘                           │
│       │    │                                                        │
│       ▼    ▼                                                        │
│   ┌──────────┐    ┌────────────┐                                   │
│   │  04-RAG  │───▶│05-AI-Agents│                                   │
│   │ (AI +    │    │(Multi-Agent│                                    │
│   │ Search)  │    │Orchestrate)│                                    │
│   └──────────┘    └────────────┘                                   │
│                          │                                          │
│                          ▼                                          │
│                    🎓 MASTERY                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### What You'll Learn

| Stack | Core Skill | Real-World Use Case |
|-------|-----------|-------------------|
| **Kafka** | Event-driven architecture, async messaging | How Netflix/Uber process millions of events/sec |
| **Keycloak** | Enterprise SSO, OAuth2, OIDC | How Google/GitHub "Login with..." buttons work |
| **IDP** | JWT tokens, cryptographic auth | How identity systems work under the hood |
| **RAG** | Vector search, embeddings, AI retrieval | How ChatGPT + your documents work together |
| **AI Agents** | Multi-agent orchestration, tool use | How AI assistants delegate and collaborate |

---

## 2. Project Map

```
All Stacks/
│
├── WORKFLOW.md              ◄── YOU ARE HERE (this file)
│
├── 01-Kafka/                ◄── Apache Kafka Task Queue System
│   ├── docker-compose.yml       Kafka + ZooKeeper containers
│   ├── producer.py              Flask API + Kafka producer (port 5001)
│   ├── consumer.py              Kafka consumer worker
│   ├── templates/dashboard.html Web dashboard
│   ├── requirements.txt
│   └── README.md                Complete Kafka documentation
│
├── 02-Keycloak/             ◄── Secure Notes with Keycloak Auth
│   ├── docker-compose.yml       Keycloak server container (port 8080)
│   ├── app.py                   Flask notes app (port 5002)
│   ├── keycloak_config.py       OIDC helper module
│   ├── setup_keycloak.py        Automated realm/user setup
│   ├── init_db.py               SQLite database init
│   ├── templates/               6 HTML templates
│   ├── requirements.txt
│   └── README.md                Complete Keycloak documentation
│
├── 03-IDP/                  ◄── Custom Identity Provider from Scratch
│   ├── idp_server.py            IDP server (port 5003)
│   ├── resource_server.py       Protected API (port 5004)
│   ├── client_app.py            Client web app (port 5005)
│   ├── run_all.py               Starts all 3 servers
│   ├── generate_keys.py         RSA key pair generator
│   ├── test_flow.py             End-to-end test suite
│   ├── templates/               4 HTML templates
│   ├── requirements.txt
│   └── README.md                Complete IDP documentation
│
├── 04-RAG/                  ◄── Document Q&A with RAG Pipeline
│   ├── app.py                   Flask web server (port 5006)
│   ├── rag_engine.py            Core RAG pipeline engine
│   ├── document_processor.py    PDF/text processing utilities
│   ├── sample_documents/        3 sample articles
│   ├── templates/dashboard.html Interactive Q&A dashboard
│   ├── test_rag.py              Automated tests
│   ├── requirements.txt
│   └── README.md                Complete RAG documentation
│
└── 05-AI-Agents/            ◄── Multi-Agent Task Automation
    ├── agent_framework.py       Core framework (BaseAgent, MessageBus, Tool)
    ├── agents/                  5 specialized agents
    │   ├── orchestrator.py      Task decomposition & delegation
    │   ├── researcher.py        Knowledge lookup & summarization
    │   ├── calculator.py        Math, statistics, finance
    │   ├── writer.py            Report generation & formatting
    │   └── file_agent.py        File I/O & workspace management
    ├── tools.py                 15 tool implementations
    ├── app.py                   Flask dashboard (port 5007)
    ├── run.py                   Entry point
    ├── example_tasks.py         4 pre-built demo scenarios
    ├── workspace/               Sample data files
    ├── requirements.txt
    └── README.md                Complete AI Agents documentation
```

---

## 3. Stack-by-Stack Breakdown

### 3.1 Kafka: Task Queue System

> **What it is**: Apache Kafka is a distributed event streaming platform. Think of it
> as a super-fast, reliable post office that can handle millions of messages per second.

#### How It Works (Data Flow)

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  Web Browser │     │   KAFKA BROKER   │     │  Consumer Worker │
│  (Dashboard) │     │                  │     │                  │
│              │     │  ┌────────────┐  │     │                  │
│  Submit Task ├────▶│  │ task-queue │  ├────▶│  Process Task    │
│  via Form    │ HTTP│  │   TOPIC    │  │MSG  │  (Simulate Work) │
│              │     │  └────────────┘  │     │                  │
│  View Status │◀────┤                  │     │  Write Results   │
│              │ JSON│  Stores messages │     │  to JSON file    │
└──────────────┘     │  on disk (log)   │     └──────────────────┘
                     └─────────────────┘
     Port 5001          Port 9092             Terminal Process
     (Flask)            (Docker)              (Python Script)
```

#### Key Concepts Learned
- **Producer**: Sends messages to Kafka (the Flask API)
- **Consumer**: Reads and processes messages (the worker)
- **Topic**: A named channel for messages (`task-queue`)
- **Broker**: The Kafka server that stores and delivers messages
- **Consumer Group**: Multiple consumers sharing the work load
- **ZooKeeper**: Manages Kafka cluster coordination

#### Run Commands
```powershell
cd "c:\Users\itzme\Desktop\All Stacks\01-Kafka"
docker compose up -d                    # Start Kafka + ZooKeeper
pip install -r requirements.txt
# Terminal 1:
python consumer.py                      # Start the consumer worker
# Terminal 2:
python producer.py                      # Start Flask on port 5001
# Open http://localhost:5001
```

#### 📖 Full docs → [01-Kafka/README.md](./01-Kafka/README.md)

---

### 3.2 Keycloak: Secure Notes App

> **What it is**: Keycloak is an enterprise-grade Identity and Access Management (IAM)
> server. It's what companies use so you can "Login with Google/GitHub" or enforce
> role-based access (admin vs regular user).

#### How It Works (OAuth2 Authorization Code Flow)

```
┌──────────┐      ┌────────────┐      ┌──────────────┐
│  Browser │      │  Flask App │      │   KEYCLOAK   │
│  (User)  │      │  (port 5002)│     │  (port 8080) │
└────┬─────┘      └─────┬──────┘      └──────┬───────┘
     │  1. Click Login  │                     │
     ├─────────────────▶│                     │
     │                  │  2. Redirect to     │
     │                  │     Keycloak        │
     │◀─────────────────┤────────────────────▶│
     │  3. Keycloak shows login form          │
     │◀───────────────────────────────────────┤
     │  4. User enters credentials            │
     ├───────────────────────────────────────▶│
     │                  │  5. Keycloak sends  │
     │                  │     auth code back  │
     │                  │◀────────────────────┤
     │                  │  6. Exchange code   │
     │                  │     for JWT token   │
     │                  ├────────────────────▶│
     │                  │◀────────────────────┤
     │  7. Logged in!   │     Access Token    │
     │◀─────────────────┤                     │
     │  (Session has    │                     │
     │   JWT token)     │                     │
     │                  │                     │
     │  8. View Notes   │                     │
     ├─────────────────▶│                     │
     │  9. Check role   │                     │
     │     in JWT:      │                     │
     │   user → own     │                     │
     │   admin → all    │                     │
     │◀─────────────────┤                     │
```

#### Key Concepts Learned
- **Realm**: An isolated security domain in Keycloak
- **Client**: Your application registered with Keycloak
- **OIDC (OpenID Connect)**: Identity layer on top of OAuth2
- **JWT (JSON Web Token)**: Compact, signed token carrying user info
- **Roles**: `user` sees own notes, `admin` sees all notes
- **CSRF Protection**: `state` parameter prevents cross-site attacks

#### Run Commands
```powershell
cd "c:\Users\itzme\Desktop\All Stacks\02-Keycloak"
docker compose up -d                    # Start Keycloak server
pip install -r requirements.txt
python init_db.py                       # Initialize SQLite
python setup_keycloak.py                # Configure realm, users, roles
python app.py                           # Start Flask on port 5002
# Open http://localhost:5002
# Login: testuser/password or admin/password
```

#### 📖 Full docs → [02-Keycloak/README.md](./02-Keycloak/README.md)

---

### 3.3 IDP: Custom Identity Provider

> **What it is**: Instead of using a pre-built solution like Keycloak, this project
> teaches you to **build an Identity Provider from scratch**. You'll understand
> exactly how JWT tokens are signed, how OAuth2 authorization codes work, and how
> three independent servers communicate securely.

#### How It Works (Three-Server Architecture)

```
┌─────────────────────────────────────────────────────────────────┐
│                   ARCHITECTURE OVERVIEW                         │
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐       │
│  │  IDP SERVER  │   │  RESOURCE    │   │   CLIENT     │       │
│  │  (port 5003) │   │  SERVER      │   │   APP        │       │
│  │              │   │  (port 5004) │   │  (port 5005) │       │
│  │ • Register   │   │              │   │              │       │
│  │ • Login      │   │ • /api/      │   │ • Web UI     │       │
│  │ • Issue JWT  │   │   profile    │   │ • Login flow │       │
│  │ • Auth codes │   │ • /api/data  │   │ • Sessions   │       │
│  │ • JWKS keys  │   │              │   │              │       │
│  │ • OIDC       │   │ Validates    │   │ Stores       │       │
│  │   discovery  │   │ tokens via   │   │ tokens in    │       │
│  │              │   │ JWKS (no     │   │ server-side  │       │
│  │ Signs JWTs   │   │ shared       │   │ session      │       │
│  │ with RSA     │   │ secret!)     │   │              │       │
│  │ private key  │   │              │   │              │       │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘       │
│         │                  │                   │               │
│         │   ┌──────────────┤                   │               │
│         │   │  Fetches     │                   │               │
│         │   │  public key  │                   │               │
│         │   │  from /jwks  │                   │               │
│         ▼   ▼              ▼                   ▼               │
│  ┌─────────────────────────────────────────────────┐           │
│  │           RSA ASYMMETRIC CRYPTOGRAPHY           │           │
│  │  Private Key (IDP only) ←→ Public Key (shared)  │           │
│  │  Sign tokens            ←→ Verify tokens        │           │
│  └─────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

#### OAuth2 Authorization Code Flow (Step-by-Step)

```
Step 1: User clicks "Login" on Client App (port 5005)
Step 2: Client redirects browser to IDP /authorize (port 5003)
Step 3: IDP shows login form, user enters credentials
Step 4: IDP validates credentials against SQLite database
Step 5: IDP generates a one-time authorization code (expires in 5 min)
Step 6: IDP redirects browser back to Client /callback with the code
Step 7: Client sends code + client_id to IDP /token (back-channel)
Step 8: IDP validates code, issues JWT access token + refresh token
Step 9: Client stores tokens in server-side session
Step 10: Client uses access token to call Resource Server APIs
Step 11: Resource Server fetches IDP's public key from /jwks
Step 12: Resource Server verifies JWT signature → grants access
```

#### Key Concepts Learned
- **RSA Key Pairs**: Private key signs, public key verifies (no shared secrets)
- **Authorization Code**: One-time code exchanged for tokens (prevents token theft)
- **Access Token vs Refresh Token**: Short-lived access (15 min) vs long-lived refresh (7 days)
- **JWKS (JSON Web Key Set)**: How servers discover signing keys
- **OIDC Discovery**: `/.well-known/openid-configuration` endpoint
- **CSRF via `state` parameter**: Prevents cross-site request forgery

#### Run Commands
```powershell
cd "c:\Users\itzme\Desktop\All Stacks\03-IDP"
pip install -r requirements.txt
python generate_keys.py                 # Generate RSA key pair (if needed)
python run_all.py                       # Starts all 3 servers at once
# Open http://localhost:5005
# Pre-seeded users: alice/password123, bob/secret456
# Run tests: python test_flow.py
```

#### 📖 Full docs → [03-IDP/README.md](./03-IDP/README.md)

---

### 3.4 RAG: Document Q&A System

> **What it is**: RAG (Retrieval Augmented Generation) lets AI answer questions about
> YOUR documents. Instead of making things up, the AI first searches your documents
> for relevant information, then generates an answer with citations. Think of it as
> giving the AI an open-book exam.

#### How It Works (RAG Pipeline)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     RAG PIPELINE (4 STAGES)                         │
│                                                                     │
│  STAGE 1: INGEST                   STAGE 2: EMBED                  │
│  ┌──────────────┐                  ┌──────────────────┐            │
│  │  Upload PDF  │    ┌────────┐    │  all-MiniLM-L6   │            │
│  │  or TXT file │───▶│ Chunker│───▶│  (Transformer)   │            │
│  │              │    │ 500char│    │                   │            │
│  └──────────────┘    │overlap │    │  Text → 384-dim   │            │
│                      │ 100   │    │  number vectors   │            │
│                      └────────┘    └────────┬──────────┘            │
│                                             │                       │
│                                             ▼                       │
│                                    ┌──────────────────┐            │
│                                    │    ChromaDB       │            │
│                                    │  Vector Database  │            │
│                                    │  (stores chunks   │            │
│                                    │   + embeddings)   │            │
│                                    └────────┬──────────┘            │
│                                             │                       │
│  STAGE 3: RETRIEVE                          │                       │
│  ┌──────────────┐                           │                       │
│  │ User asks:   │    ┌────────────┐         │                       │
│  │ "What is     │───▶│  Embed the │─────────┘                       │
│  │  machine     │    │  question  │    cosine                       │
│  │  learning?"  │    │  too       │    similarity                   │
│  └──────────────┘    └────────────┘    search                       │
│                                             │                       │
│                                             ▼                       │
│  STAGE 4: GENERATE                 ┌──────────────────┐            │
│  ┌──────────────────┐              │  Top 3 matching  │            │
│  │  Answer with     │◀─────────────│  chunks returned │            │
│  │  source citations│              │  with scores     │            │
│  │                  │              └──────────────────┘            │
│  │  "Machine        │                                              │
│  │   learning is... │                                              │
│  │   [Source: ai_   │                                              │
│  │   basics.txt,    │                                              │
│  │   chunk 3]"      │                                              │
│  └──────────────────┘                                              │
└─────────────────────────────────────────────────────────────────────┘
```

#### What Happens When You Ask a Question

```
1. Your question → "What is deep learning?"
2. The question text is converted to a 384-dimensional vector
   [0.023, -0.156, 0.891, 0.002, ... 380 more numbers]
3. ChromaDB compares this vector against ALL stored chunk vectors
   using cosine similarity (measures "angle" between vectors)
4. Top 3 most similar chunks are retrieved:
   - Chunk 7 from ai_basics.txt (score: 0.89) ← most relevant
   - Chunk 3 from ai_basics.txt (score: 0.72)
   - Chunk 12 from python_guide.txt (score: 0.45)
5. These chunks are combined with your question into a prompt
6. The answer generator creates a response citing the exact sources
```

#### Key Concepts Learned
- **Embeddings**: Converting text to numbers that capture meaning
- **Vector Database**: A database optimized for similarity search (ChromaDB)
- **Chunking**: Splitting large documents into searchable pieces
- **Cosine Similarity**: Measuring how "similar" two vectors are
- **Semantic Search**: Finding by meaning, not just keywords
- **Context Window**: How much text the AI can "see" at once

#### Run Commands
```powershell
cd "c:\Users\itzme\Desktop\All Stacks\04-RAG"
pip install -r requirements.txt         # First run downloads ~90MB model
python app.py                           # Start Flask on port 5006
# Open http://localhost:5006
# Sample documents are auto-loaded on first run
# Try asking: "What is machine learning?"
```

#### 📖 Full docs → [04-RAG/README.md](./04-RAG/README.md)

---

### 3.5 AI Agents: Multi-Agent Task Automation

> **What it is**: AI Agents are autonomous programs that can understand tasks, use
> tools, and collaborate with other agents to get work done. Think of it as a team
> of specialists — each expert at one thing — coordinated by a manager.

#### How It Works (Multi-Agent Architecture)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT SYSTEM                                │
│                                                                     │
│   User Task: "Research renewable energy and write a report"         │
│                           │                                         │
│                           ▼                                         │
│              ┌────────────────────────┐                             │
│              │   🎯 ORCHESTRATOR      │                             │
│              │   Analyzes task         │                             │
│              │   Creates execution     │                             │
│              │   plan, delegates work  │                             │
│              └───┬────┬────┬────┬─────┘                             │
│                  │    │    │    │                                    │
│         ┌────────┘    │    │    └────────┐                          │
│         ▼             ▼    ▼             ▼                          │
│  ┌──────────┐  ┌────────┐ ┌────────┐ ┌──────────┐                 │
│  │🔍Research│  │🧮Calc  │ │📝Writer│ │📁File    │                 │
│  │  Agent   │  │  Agent │ │  Agent │ │  Agent   │                 │
│  │          │  │        │ │        │ │          │                 │
│  │ Knowledge│  │ Math   │ │ Report │ │ Read CSV │                 │
│  │ lookup   │  │ Stats  │ │ Format │ │ Write    │                 │
│  │ Summarize│  │ Finance│ │ Render │ │ output   │                 │
│  └────┬─────┘  └───┬────┘ └───┬────┘ └────┬─────┘                 │
│       │            │          │            │                        │
│       └────────────┴──────────┴────────────┘                        │
│                           │                                         │
│                    ┌──────┴───────┐                                 │
│                    │  MESSAGE BUS │                                 │
│                    │  (In-Memory) │                                 │
│                    │              │                                 │
│                    │ Routes msgs  │                                 │
│                    │ between all  │                                 │
│                    │ agents       │                                 │
│                    └──────────────┘                                 │
└─────────────────────────────────────────────────────────────────────┘
```

#### Example Task Walkthrough

```
TASK: "Calculate compound interest for $10,000 at 5% for 10 years"

Step 1: User submits task via dashboard (port 5007)
Step 2: Orchestrator receives task, analyzes keywords
Step 3: Orchestrator identifies this as a CALCULATION task
Step 4: Orchestrator delegates to CalculatorAgent via MessageBus
        Message: {type: TASK, from: orchestrator, to: calculator,
                  content: "compound_interest principal=10000 rate=5 years=10"}
Step 5: CalculatorAgent uses compound_interest tool
        Result: Future Value = $16,288.95, Total Interest = $6,288.95
Step 6: CalculatorAgent sends result back via MessageBus
        Message: {type: RESULT, from: calculator, to: orchestrator, ...}
Step 7: Orchestrator sends to WriterAgent for formatting
Step 8: WriterAgent creates formatted Markdown report
Step 9: Orchestrator returns final result to user dashboard
```

#### Key Concepts Learned
- **Agent**: An autonomous unit with a role, tools, and decision logic
- **Orchestrator Pattern**: A manager agent that delegates to specialists
- **Message Bus**: Decoupled communication channel between agents
- **Tools**: Functions that agents can call (calculator, file I/O, search)
- **Task Decomposition**: Breaking complex tasks into sub-tasks
- **Agent Communication**: Structured message passing (TASK, RESULT, ERROR)

#### Run Commands
```powershell
cd "c:\Users\itzme\Desktop\All Stacks\05-AI-Agents"
pip install -r requirements.txt
python run.py                           # Start Flask on port 5007
# Open http://localhost:5007
# Click example task buttons or type your own
# CLI mode: python example_tasks.py
```

#### 📖 Full docs → [05-AI-Agents/README.md](./05-AI-Agents/README.md)

---

## 4. How All Stacks Connect (The Big Picture)

In a real-world production system, these 5 technologies work **together**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                 REAL-WORLD SYSTEM ARCHITECTURE                      │
│                                                                     │
│  ┌─────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │  User   │     │  KEYCLOAK /  │     │   BACKEND    │            │
│  │ Browser ├────▶│  IDP (Auth)  ├────▶│   API        │            │
│  │         │     │              │     │              │            │
│  │         │     │  "Who are    │     │  Validates   │            │
│  │         │     │   you?"      │     │  JWT tokens  │            │
│  └─────────┘     └──────────────┘     └──────┬───────┘            │
│                                              │                     │
│                  ┌───────────────────────────┘                     │
│                  │                                                  │
│         ┌────────┴────────┐        ┌──────────────────┐           │
│         │   KAFKA         │        │   RAG ENGINE     │           │
│         │                 │        │                  │           │
│         │  "Process this  │        │  "Answer this    │           │
│         │   task async"   │        │   question from  │           │
│         │                 │        │   our documents" │           │
│         │  Events, logs,  │        │                  │           │
│         │  notifications  │        │  Embeddings +    │           │
│         └────────┬────────┘        │  Vector Search   │           │
│                  │                 └────────┬─────────┘           │
│                  │                          │                      │
│                  └──────────┬───────────────┘                      │
│                             │                                      │
│                    ┌────────┴─────────┐                            │
│                    │   AI AGENTS      │                            │
│                    │                  │                            │
│                    │  Orchestrate     │                            │
│                    │  everything:     │                            │
│                    │  • Auth check    │                            │
│                    │  • Queue tasks   │                            │
│                    │  • Search docs   │                            │
│                    │  • Generate      │                            │
│                    │    responses     │                            │
│                    └──────────────────┘                            │
└─────────────────────────────────────────────────────────────────────┘

FLOW: User authenticates (Keycloak/IDP) → Sends request → Kafka queues it
      → AI Agent picks it up → Uses RAG to search documents → Returns answer
```

### How They Connect

| From | To | Connection |
|------|----|-----------|
| **User** → **Keycloak/IDP** | Authentication | User logs in, gets JWT token |
| **Keycloak/IDP** → **Backend** | Authorization | JWT token validates user identity & roles |
| **Backend** → **Kafka** | Async Processing | Tasks queued for background processing |
| **Kafka** → **AI Agents** | Event Consumption | Agents consume and process queued tasks |
| **AI Agents** → **RAG** | Knowledge Retrieval | Agents search documents for answers |
| **RAG** → **User** | Response | Cited answers returned to the user |

---

## 5. Prerequisites & Global Setup

### Required Software

| Software | Version | Purpose | Install |
|----------|---------|---------|---------|
| **Python** | 3.10+ | All projects | [python.org](https://python.org) |
| **Docker Desktop** | Latest | Kafka, Keycloak | [docker.com](https://docker.com) |
| **pip** | Latest | Python packages | Comes with Python |
| **Git** | Latest | Version control | [git-scm.com](https://git-scm.com) |
| **Web Browser** | Any modern | Dashboards | Already installed |

### Verify Installation

```powershell
python --version          # Should show 3.10+
docker --version          # Should show Docker version
docker compose version    # Should show Docker Compose v2+
pip --version             # Should show pip
```

### Port Map (No Conflicts)

| Port | Project | Service |
|------|---------|---------|
| 2181 | 01-Kafka | ZooKeeper |
| 5001 | 01-Kafka | Flask Producer |
| 5002 | 02-Keycloak | Flask Notes App |
| 5003 | 03-IDP | IDP Server |
| 5004 | 03-IDP | Resource Server |
| 5005 | 03-IDP | Client App |
| 5006 | 04-RAG | RAG Dashboard |
| 5007 | 05-AI-Agents | Agents Dashboard |
| 8088 | 02-Keycloak | Keycloak Auth & Admin |
| 9092 | 01-Kafka | Kafka Broker |

> All ports are unique — you can run ALL projects simultaneously!

---

## 6. Quick Start Commands (All Projects)

### ⚡ One-Click Runners (.cmd)

Double-click or run from PowerShell / Command Prompt:

```cmd
install_all.cmd    # 1. Install all dependencies & initialize databases
run.cmd            # 2. Run ALL 5 projects at once (auto-opens dashboards)
check_status.cmd   # 3. Check health and status of all ports
stop.cmd           # 4. Stop all projects and free all ports
```

---

### Run Each Project Individually (Copy-Paste Ready)

```powershell
# ═══════════════════════════════════════════
# PROJECT 1: KAFKA TASK QUEUE
# ═══════════════════════════════════════════
cd "c:\Users\itzme\Desktop\All Stacks\01-Kafka"
docker compose up -d
pip install -r requirements.txt
# Terminal 1: python consumer.py
# Terminal 2: python producer.py
# Dashboard:  http://localhost:5001

# ═══════════════════════════════════════════
# PROJECT 2: KEYCLOAK SECURE NOTES
# ═══════════════════════════════════════════
cd "c:\Users\itzme\Desktop\All Stacks\02-Keycloak"
docker compose up -d
pip install -r requirements.txt
python init_db.py
python setup_keycloak.py
python app.py
# Dashboard:  http://localhost:5002
# Keycloak:   http://localhost:8080 (admin/admin)

# ═══════════════════════════════════════════
# PROJECT 3: CUSTOM IDP
# ═══════════════════════════════════════════
cd "c:\Users\itzme\Desktop\All Stacks\03-IDP"
pip install -r requirements.txt
python run_all.py
# Client:     http://localhost:5005
# Test:       python test_flow.py

# ═══════════════════════════════════════════
# PROJECT 4: RAG DOCUMENT Q&A
# ═══════════════════════════════════════════
cd "c:\Users\itzme\Desktop\All Stacks\04-RAG"
pip install -r requirements.txt
python app.py
# Dashboard:  http://localhost:5006

# ═══════════════════════════════════════════
# PROJECT 5: AI AGENTS
# ═══════════════════════════════════════════
cd "c:\Users\itzme\Desktop\All Stacks\05-AI-Agents"
pip install -r requirements.txt
python run.py
# Dashboard:  http://localhost:5007
```

---

## 7. Complexity & Learning Progression

```
DIFFICULTY LEVEL
│
│  ████████████████████████████████████████  05-AI-Agents
│  ████████████████████████████████████      04-RAG
│  ██████████████████████████████            03-IDP
│  ████████████████████████                  02-Keycloak
│  ██████████████████                        01-Kafka
│
└──────────────────────────────────────────  BEGINNER → ADVANCED
```

| Level | Project | New Concepts | Time to Learn |
|-------|---------|-------------|---------------|
| ⭐ | 01-Kafka | Message queues, producers/consumers | 2-3 hours |
| ⭐⭐ | 02-Keycloak | OAuth2, SSO, role-based access | 3-4 hours |
| ⭐⭐⭐ | 03-IDP | JWT internals, RSA crypto, OIDC from scratch | 4-5 hours |
| ⭐⭐⭐⭐ | 04-RAG | Embeddings, vector DBs, semantic search | 4-6 hours |
| ⭐⭐⭐⭐⭐ | 05-AI-Agents | Multi-agent orchestration, tool use | 5-7 hours |

### Recommended Study Order

1. **Start with Kafka** — Learn async messaging (the simplest architecture)
2. **Then Keycloak** — Learn how authentication works with a pre-built IDP
3. **Then build your own IDP** — Now you understand what Keycloak does internally
4. **Then RAG** — Enter the AI world with document search
5. **Finally AI Agents** — Combine everything: agents can use auth, queue tasks, search docs

---

## 8. Glossary of Key Terms

| Term | Definition |
|------|-----------|
| **API** | Application Programming Interface — how programs talk to each other |
| **Async** | Asynchronous — work happens in the background, not blocking the user |
| **Bearer Token** | An access token sent in HTTP headers: `Authorization: Bearer <token>` |
| **Broker** | A server that receives, stores, and delivers messages (Kafka) |
| **Chunking** | Splitting large documents into smaller, searchable pieces (RAG) |
| **Consumer** | A program that reads messages from a queue (Kafka) |
| **CORS** | Cross-Origin Resource Sharing — allows web pages to call different servers |
| **Cosine Similarity** | Mathematical measure of how "similar" two vectors are (0 to 1) |
| **Embedding** | Converting text/images into numerical vectors that capture meaning |
| **Flask** | A lightweight Python web framework used in all 5 projects |
| **JWT** | JSON Web Token — a compact, signed token carrying user claims |
| **JWKS** | JSON Web Key Set — public keys used to verify JWT signatures |
| **Message Bus** | Communication channel between agents or services |
| **OAuth2** | Authorization framework — how apps get permission to access user data |
| **OIDC** | OpenID Connect — identity layer built on OAuth2 |
| **Orchestrator** | A manager that delegates tasks to specialist workers |
| **Producer** | A program that sends messages to a queue (Kafka) |
| **RAG** | Retrieval Augmented Generation — AI that searches before answering |
| **Realm** | An isolated security domain in Keycloak |
| **Refresh Token** | A long-lived token used to get new access tokens without re-login |
| **RSA** | An asymmetric encryption algorithm using key pairs (public + private) |
| **SSO** | Single Sign-On — log in once, access multiple applications |
| **Topic** | A named channel for messages in Kafka |
| **Vector Database** | A database optimized for similarity search on embeddings |
| **ZooKeeper** | Coordination service for distributed systems (used by Kafka) |

---

## 📚 How to Use This Document

- **Starting fresh?** Follow the [Learning Progression](#7-complexity--learning-progression) from top to bottom
- **Need to run a project?** Jump to [Quick Start Commands](#6-quick-start-commands-all-projects)
- **Want deep details?** Read each project's `README.md` file
- **Want improvements?** Tell me to "refer the [project] README" and I'll know exactly what to modify
- **Confused by a term?** Check the [Glossary](#8-glossary-of-key-terms)

> **💡 Tip**: Each project's `README.md` has its own troubleshooting section,
> learning exercises, and "what to try next" suggestions. Start there when you're
> stuck!

---

*Generated for: All Stacks Learning Workspace*
*Last updated: October 2026*
