# 💰 Financial Decision Agent

An AI-powered financial decision-support agent that helps users evaluate whether they can afford a purchase or recurring financial commitment based on their income, essential expenses, existing commitments, and a conservative safety buffer.

Built as a practical AI Agent prototype for the GDGC MCET Organizer practical evaluation.

## 🎯 Problem

People often make purchase decisions without considering their existing financial commitments or maintaining a basic safety margin.

This project lets a user describe their financial situation naturally and asks:

> "Can I afford this purchase or commitment without putting my remaining monthly finances under unnecessary pressure?"

Instead of relying on an LLM to perform financial calculations, the agent uses Gemini for interpretation and orchestration while deterministic calculations are handled by Python tools.

## 🤖 How It Works

```text
User's Natural-Language Request
              ↓
       Gemini AI Agent
              ↓
     Tool Selection & Calls
              ↓
 ┌─────────────────────────────┐
 │ Python Financial Tools       │
 │                             │
 │ • Input validation          │
 │ • Financial position        │
 │ • Safety buffer calculation │
 │ • Commitment evaluation     │
 │ • Recurring cost conversion │
 └─────────────────────────────┘
              ↓
      Deterministic Result
              ↓
       Gemini Explanation
              ↓
       Streamlit Dashboard