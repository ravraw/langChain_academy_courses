##Langchain-academy AI Project Setup Guide

https://github.com/langchain-ai/langchain-academy/blob/main/README.md

This repository contains a **LangGraph-based AI Agent project** built using Python, OpenAI APIs, and LangSmith observability tools.  
The setup is designed for modern **agentic AI workflows**, running locally or connected to **LangGraph Studio** for visualization and debugging.

---

## 🚀 Tech Stack

| Category                     | Tool / Library                             |
| ---------------------------- | ------------------------------------------ |
| **Language**                 | Python ≥ 3.11                              |
| **Package Manager**          | [UV](https://github.com/astral-sh/uv)      |
| **LLM Provider**             | [OpenAI API](https://platform.openai.com/) |
| **Core Frameworks**          | LangGraph, LangChain, LangSmith            |
| **Dev Tools**                | LangGraph Studio, Jupyter Notebook         |
| **Database (Checkpointing)** | SQLite                                     |
| **Integrations**             | Tavily Search, Wikipedia, TrustCall        |

---

## 🧩 Project Dependencies

```bash
langgraph
langgraph-prebuilt
langgraph-sdk
langgraph-checkpoint-sqlite
langsmith
langchain-community
langchain-core
langchain-openai
notebook
tavily-python
wikipedia
trustcall
langgraph-cli[inmem]
```
