# NemoClaw Gateway Dashboard: Conceptual Design Document (v1.0)

## 🎯 Phase 1: Ideation & Architectural Development
This document outlines the core concepts and design decisions for the **Safe-by-Default** AI Control Plane. No code is currently being implemented; all focus is on refining the security posture and architectural logic.

---

## 🛡️ 1. Fail-Closed Logic Architecture
The central tenet of the design is that **safety is binary**. If the system cannot guarantee safety, it will not function.

### Failure Handling Flow:
1.  **Bootstrap Check**: The `safe_initializer` verifies OS-level hardening (e.g., Landlock supported, no root-running processes).
2.  **Identity Verification**: The gateway attempts to establish its SPIRE identity. 
    *   *If SPIRE is unreachable*: **HALT.** The gateway does not bind to any network port.
3.  **Policy Loading**: NeMo Guardrails load the "Deny-All" baseline.
    *   *If Policy is corrupted*: **HALT.** Do not load insecure defaults.
4.  **mTLS Handshake**: Inbound model traffic is checked for cryptographic signatures. 
    *   *If unencrypted*: **DROP.** No fallback to plain HTTP.

---

## 🔒 2. Zero-Assumption Initialization (ZAI)
We assume the environment is compromised until proven otherwise.

### Initialization Steps:
- **Entropy Audit**: Verify the system has sufficient entropy for cryptographic operations.
- **Dependency Pinning Audit**: Verify that all underlying AI runtimes (OpenShell, NemoClaw) match the cryptographically signed hashes in the manifest.
- **Port Silence**: No management ports are opened until after the TEE (Trusted Execution Environment) has verified the gateway's own memory integrity.

---

## 📈 3. AI Attack Graph (Neo4j Schema)
The "brain" of our security layer is a graph database that maps the potential paths an attacker (or rogue agent) could take.

### Core Nodes:
- `(User)`: The human requester (Identity via OIDC).
- `(Agent)`: The NemoClaw autonomous instance.
- `(Model)`: The LLM model (e.g., Nemotron).
- `(Tool)`: The external API/Tool the agent can call.
- `(DataStore)`: Sensitive databases or file systems.

### Scoring Logic:
- Every `Edge` has a **Risk Weight**.
- If a path exists from `(User)` -> `(Agent)` -> `(Tool: Shell)` -> `(DataStore: HR_DB)`, the graph triggers a **High Alert** even if the individual actions are permitted.

---

## 🏗️ 4. Data Isolation & Hardware Security
- **Confidential Computing**: Leveraging **NVIDIA Blackwell/Hopper TEEs** to ensure that model weights and prompts are never visible in host memory.
- **Landlock Sandboxing**: Using the Linux Landlock LSM to restrict the `OpenShell` runtime to only the specific files required for the task at hand.

---

## 📜 Roadmap (Ideation Phase)
1.  **v1.0 (Current)**: Safe-by-Default and Fail-Closed principles established.
2.  **v1.1**: Refine the **Human-in-the-Loop (HITL)** orchestration for high-risk prompt adjudication.
3.  **v1.2**: Define the **Forensic Playback** conceptual model (how to "rewind" a security incident).
4.  **v1.3**: Finalize the **NIST AI RMF** compliance mapping.
