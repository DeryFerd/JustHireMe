# JustHireMe: The Autonomous Job-Seeking Engine

JustHireMe is a sophisticated, local-first autonomous system designed to handle the end-to-end job-seeking process. It leverages state-of-the-art AI, graph databases, and browser automation to scout, evaluate, and apply for jobs while keeping the user's data private and their activity stealthy.

---

## 🚀 Project Vision
A zero-dependency engine that transforms a user's professional profile into a "Knowledge Brain," allowing autonomous agents to act as a personal recruiter and executive assistant. It operates on a **Local-First** principle, ensuring all sensitive data (resumes, API keys, application history) stays on the user's machine.

---

## 🛠️ Technical Stack

### 🏗️ Shell & Orchestration
- **Tauri 2.0 (Rust):** The parent process that manages the application lifecycle, system tray, and secure storage. It bridges the gap between the desktop environment and the backend logic.
- **Python 3.12+ (uv):** Managed by the `uv` package manager for high-performance dependency handling. This sidecar process houses the "heavy lifting" logic.
- **LangGraph:** The state machine orchestrator that manages complex multi-agent workflows.
- **FastAPI:** Provides a local REST and WebSocket API for communication between the UI and the sidecar.

### 🎨 Frontend
- **React (Vite) & TypeScript:** For a type-safe, high-performance UI.
- **Tailwind CSS & Vanilla CSS:** Combined for flexible, premium styling (glassmorphism, modern typography).
- **Framer Motion:** Powering smooth micro-animations and transitions.

### 🧠 The Knowledge Brain (Storage)
- **Kùzu (Embedded Property Graph):** The primary engine for relational knowledge. It stores the user's career history as a graph of nodes (Skills, Projects, Experience) and edges.
- **LanceDB:** An embedded vector store used for semantic similarity searches between job descriptions and the user's profile.
- **SQLite:** A local relational database for CRM-style lead tracking, system settings, and audit logs.

---

## 🤖 Agent Modules (The DAG Nodes)

JustHireMe uses a modular agent architecture where each agent is a specialist node in a LangGraph workflow:

### 1. The Ingestor Agent
- **Function:** Parses PDF resumes, LinkedIn profiles, and GitHub handles.
- **Logic:** Uses LLMs to extract entities and map them to the Graph Ontology.
- **Output:** A structured Professional Graph in Kùzu.

### 2. The Scout Agent
- **Function:** Discovers new job opportunities across the web.
- **Logic:** Hybrid approach using Apify (for LinkedIn/X) and local Playwright instances (for niche boards and RSS).
- **Output:** Raw job leads stored in the SQLite CRM.

### 3. The Evaluator Agent (GraphRAG)
- **Function:** Determines the "Fit Score" for every discovered lead.
- **Logic:** Generates Cypher queries against the Kùzu graph to find "Proof of Work" (e.g., "Has the user used React in a FinTech project?").
- **Output:** A 0-100 score with qualitative reasoning.

### 4. The Generator Agent
- **Function:** Tailors the application package.
- **Logic:** Modifies the user's resume and cover letter (Markdown) to highlight specific skills relevant to the job lead.
- **Output:** A customized PDF ready for submission.

### 5. The Actuator Agent (The Hands)
- **Function:** Physically applies for the job.
- **Logic:** Uses Playwright for DOM-based interaction. If the DOM is too complex, it falls back to **Vision-based Actuation** (VLM) using coordinates.
- **Output:** Submission confirmation and status update in the CRM.

---

## 🕹️ Execution Modes

1. **Ghost Mode:** The "Set and Forget" mode. The engine runs every 6 hours in the background, scouting, evaluating, and applying without human intervention.
2. **Sniper Mode:** The "Human-in-the-loop" mode. The engine scouts and evaluates, but pauses for the user to review and click "Execute" in the Tauri UI before applying.

---

## 🔒 Security & Stealth
- **AES-256 Encryption:** API keys and sensitive tokens are stored using Windows DPAPI or Machine_UUID.
- **Resident IPs:** Since it runs locally, applications originate from the user's own IP, avoiding "bot detection" from VPNs/Data Centers.
- **Playwright Jitter:** Randomized delays and mouse movements simulate human behavior.
- **Fingerprint Rotation:** User-Agents and browser fingerprints are rotated to maintain a low profile.

---

## 📂 Project Structure

```text
JustHireMe/
├── src-tauri/             # Rust source (Tauri configuration, system tray)
├── backend/               # Python sidecar
│   ├── agents/            # Specialized agent logic (Ingestor, Scout, etc.)
│   ├── db/                # Kùzu, LanceDB, and SQLite clients
│   ├── graph/             # Cypher queries and graph schema
│   ├── main.py            # FastAPI server entry point
│   └── llm.py             # LLM provider abstractions (Anthropic, Groq, Ollama)
├── src/                   # React/TS frontend
│   ├── components/        # Reusable UI components
│   ├── App.tsx            # Main UI orchestrator (Dashboard, Pipeline, Graph)
│   └── index.css          # Core design system
├── SPEC.md                # Project technical specification
└── ARCHITECTURE.html      # Visual architecture documentation
```

---

## 📈 Roadmap & Milestones
- **Phase 0:** The Bridge (Tauri + Python Sidecar + WS Heartbeat) — **Completed**
- **Phase 1:** The Brain (Kùzu Schema + Ingestor Agent) — **In Progress**
- **Phase 2:** The Scout (Scrapers + Deduplication)
- **Phase 3:** The Hands (Tailored PDF Generator + DOM Actuator)
- **Phase 4:** Stealth (VLM Fallback + Fingerprint Spooling)
