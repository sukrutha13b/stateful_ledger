# 🛡️ Stateful Ledger

### **Automated Auditing & Safety Net for AI Outputs**

A dual-layer verification engine designed to make AI-generated content reliable, self-consistent, and verifiably grounded in real-world facts. By continuously auditing outputs in real-time, it eliminates logical contradictions, minimizes compliance risks, and dramatically reduces the cost and fatigue of human oversight.

---

## 💼 Executive Summary & Business Value

Generative AI models are incredibly capable, but they suffer from three core challenges when deployed in business workflows:
1. **Logical Drift (Forgetfulness):** In long conversations, AI models tend to forget initial guidelines, budget constraints, or policy rules.
2. **Silent Hallucinations:** AI outputs often state assumptions as absolute facts, forcing human operators to perform tedious, manual line-by-line checks.
3. **Overconfidence in Ambiguity:** AI models often take a definitive stance on highly debated or subjective topics rather than presenting a balanced, multi-perspective view.

**Stateful Ledger** acts as an automated, concurrent audit layer between the AI and the user. It ensures that every response is factually verified and logically aligned with your initial constraints.

### **Core Business Benefits**
*   **🤝 High-Legibility Trust:** Instead of treating AI as a "black box," stakeholders are given full visibility into *why* the AI generated a specific answer and *what* sources back it up.
*   **📜 Session Portability & Compliance Auditing:** Save, export, and load complete session ledgers to maintain a clear audit trail of AI-human interactions.
*   **⚡ Custom Scorecards:** Automatically generates tailor-made evaluation criteria based on the goal of the conversation.

---

## 🔍 How It Works: The Dual-Layer Guardrail

The engine operates on two concurrent layers to evaluate AI outputs before they are finalized.

```
       [ User Query ]
             │
             ▼
    ┌─────────────────┐
    │ Stateful Ledger │◄──── (Maintains rules, constraints, and assumptions)
    └────────┬────────┘
             │
             ▼
     ┌──────────────┐
     │  Gemini AI   │
     └───────┬──────┘
             │
             ▼
 ┌───────────────────────┐
 │ DUAL-LAYER VERIFIER   │
 ├───────────────────────┤
 │ Layer 1: Consistency  │ ──► Checks against established session rules
 ├───────────────────────┤
 │ Layer 2: Grounding    │ ──► Fact-checks against Google Search in real-time
 └───────────┬───────────┘
             │
             ▼
   [ Visual Audit Trail ] ──► (Inference markers, perspectives, and completeness audit)
```

### 1. **Layer 1: Contextual Consistency (Internal Auditing)**
The system maintains a **Stateful Ledger**—an active, transparent database of the session’s rules, constraints, and assumptions.
*   **The Guardrail:** If the AI attempts to violate a rule established earlier in the session (e.g., proposing a budget exceeding a previously agreed-upon cap), the system instantly flags the conflict.
*   **No Auto-Silencing:** The system presents the conflict to the user rather than silently rewriting it, ensuring absolute decision-making transparency.

### 2. **Layer 2: Real-World Grounding (External Auditing)**
The engine automatically extracts factual claims from the AI's response and verifies them in the background using Google Search grounding.
*   **🟢 Grounded:** The claim is confirmed by high-agreement, credible external sources.
*   **🟡 Contested:** The claim is technically defensible but represents one side of an active debate. The system prompts the user with alternative perspectives.
*   **🔴 Unverified:** No solid grounding could be found. It is flagged so operators know to treat it with caution.

---

## ✨ Key Features Built for Business Operators

### 📊 **Trust Calibration Gauge**
Provides a real-time "Trust Index" score for the current session. As operators mark outputs as *accurate*, *inaccurate*, or *uncertain*, the Trust Index calibrates dynamically to help teams understand the reliability of the model for that specific task.

### 📋 **Contextual Rubric Generator**
At the start of any interaction, the system infers the type of task (e.g., Creative Writing, Technical Code, Analytical Review) and generates a customized scorecard. Users can review and edit this rubric to align the AI's audit standards with their business goals.

### 🧩 **Completeness Tracker**
A structural audit tool that checks if the AI actually answered every part of your query. If you asked for "pros, cons, and a budget breakdown" and the AI forgot the budget, the completeness tracker highlights the gap and prompts you to address it.

### 🏷️ **Fact vs. Inference Labeling**
Every claim is visually labeled inline:
*   `[Established]`: Fact-checked and grounded.
*   `[Reasoned]`: Logical deduction based on rules in the ledger.
*   `[Inferred]`: Educated guess or generated without explicit grounding.

---

## 🖥️ Interactive Dashboards

The project features two highly visual user interfaces designed for different stakeholders:

### 1. **Streamlit Live Audit Workspace**
Designed for day-to-day operators.
*   **Live Chat Panel:** Speak with the AI model directly.
*   **Dynamic Ledger Sidebar:** View, add, edit, or delete active rules and constraints in real-time.
*   **Live Audit Badges:** Instant visual highlights of contradictions, unverified claims, and completeness scores.

### 2. **Real-Time Developer & Compliance Dashboard**
Designed for administrators and developers.
*   **Operational Telemetry:** Monitored system health, latency, and success rates.
*   **Live Claim Stream:** Tracks active claims categorized by their verification status (Grounded, Contested, Unverified).
*   **Audit Logging:** Outputs raw ledger entries and logs for complete compliance visibility.

---

## 🚀 Getting Started

### **Prerequisites**
*   **Python:** Version 3.10 or higher.
*   **Gemini API Key:** A valid Google Gemini API key (set in your environment).

### **Installation**
1. Clone the repository to your local system.
2. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your API key:
   ```env
   GEMINI_API_KEY="your-api-key-here"
   ```

### **Running the Applications**

*   **To run the main Operator Interface (Streamlit App):**
    ```bash
    streamlit run app.py
    ```
    This will open the beautiful web interface in your browser at `http://localhost:8501`.

*   **To run the Developer Telemetry Dashboard:**
    Simply open the static developer panel `dev_dashboard/index.html` in any web browser, or host it locally.

*   **To run the Automated Tests:**
    ```bash
    pytest
    ```

---

## 🎯 Our Design Philosophy

1.  **Transparency Over Authority:** The system does not claim to be an absolute source of truth. It is designed to expose limits, highlight uncertainties, and present data clearly to empower **your** judgment.
2.  **Preservation of Ambiguity:** When questions are complex or open-ended, the system preserves that ambiguity rather than forcing an artificial or biased resolution.
3.  **Human-in-the-Loop:** Every flag, rubric adjustment, and calibration signal is designed to keep the human operator in control of the interaction.
