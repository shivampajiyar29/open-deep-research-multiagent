# Next-Gen Deep Research App

This folder contains a **simpler, more user-friendly app** built on top of the original Deep Research project.

- You do **not** need to know LangGraph, notebooks, or Python internals.
- You just start the backend, open a web page, type your question, and get a full report.

---

## 1. What this app does

You type a research question (for example: *"Compare the long-term prospects of solar vs nuclear energy in India"*).

The app will:

1. Understand and scope your question.
2. Search the web (and optionally your documents).
3. Coordinate multiple research agents for complex topics.
4. Write a clear, readable report that you can copy or download.

All the advanced logic reuses the existing project in `src/deep_research_from_scratch`.

---

## 2. Requirements

Before running this app, make sure you have:

- Python dependencies installed (from the project root):

  ```bash
  uv sync
  ```

- A `.env` file in the project root with at least:
-
-  ```bash
-  TAVILY_API_KEY=your_tavily_key_here
-  GOOGLE_API_KEY=your_gemini_key_here
-  LANGSMITH_API_KEY=your_langsmith_key_here   # optional, for tracing/analytics
-  ```

(You can copy `.env.example` to `.env` and fill in your keys.)

---

## 3. Start the backend API

From the project root (same folder as `pyproject.toml`):

```bash
uv run uvicorn nextgen-research-app.backend.app:app --reload --host 0.0.0.0 --port 8000
```

This will start a small HTTP API on `http://localhost:8000` that exposes:

- `POST /api/research` – run a full deep research job and return the final report.

> If this command fails, double-check that `uv sync` completed and that your `.env` file exists.

---

## 4. Open the web interface

The frontend is a single static HTML file.

You can open it directly in your browser:

1. Go to the `nextgen-research-app/frontend/` folder.
2. Open `index.html` with your browser (double-click or use "Open with...").

Then:

1. Type your question in the big text box.
2. Choose a **mode** (Deep web research is recommended).
3. Optionally choose a **preset** (academic review, market study, learn a topic).
4. Click **"Start research"**.
5. Wait while it runs (this can take a minute or more for complex topics).
6. Scroll down to read your report, copy it, or download it as a text file.

> Note: By default the page sends requests to `http://localhost:8000/api/research`. Make sure the backend is running before you click the button.

---

## 5. Troubleshooting

**Problem: The page says something went wrong / cannot reach backend.**

- Check that the backend command is still running in your terminal.
- Make sure the port is `8000` (or update the URL in `frontend/index.html` if you change it).

**Problem: API errors about missing keys.**

- Check your `.env` file in the project root and confirm `TAVILY_API_KEY` and `GOOGLE_API_KEY` are set.
- Restart the backend after changing `.env`.

**Problem: Reports look empty or very short.**

- Try asking a more specific question.
- Or use the "Academic" / "Market" templates to give the model more guidance.

---

## 6. Observability with LangSmith (optional)

If you want to record traces of each run (inputs, intermediate steps, model calls) in LangSmith:

1. Add the following to your `.env` in the project root:

   ```bash
   LANGSMITH_API_KEY=your_langsmith_key_here
   LANGSMITH_TRACING_V2=true
   # optional, depending on your account setup:
   # LANGSMITH_ENDPOINT=https://api.smith.langchain.com
   # LANGCHAIN_PROJECT=deep-research-nextgen
   ```

2. Restart the backend. All calls made through LangChain/LangGraph (including `/api/research`) will be sent to LangSmith.

You can then inspect runs in the LangSmith UI to debug prompts, see tool usage, and understand costs.

## 7. For developers (optional)

If you want to extend this app:

- Backend code lives in `nextgen-research-app/backend/app.py`.
- It calls the existing LangGraph full pipeline via `deep_research_from_scratch.research_agent_full.agent`.
- You can:
  - Add more modes (e.g., call `research_agent` directly for a lighter quick mode).
  - Add your own templates in the frontend JavaScript or create a small config module.

The original notebooks and LangGraph graphs remain unchanged, so you still have the full tutorial / learning path alongside this simpler app.
