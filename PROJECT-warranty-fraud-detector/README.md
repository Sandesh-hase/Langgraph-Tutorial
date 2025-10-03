# Warranty Fraud Detector (Langgraph Tutorial)

A small demo project that uses LangGraph + an Azure OpenAI-backed LLM to validate warranty claims, score fraud likelihood, collect evidence, and make an adjudication decision. The project includes a Streamlit app (`app.py`) and a demonstration notebook (`agent.ipynb`).

Purpose: This repository is provided for study and educational purposes only. You are free to use, adapt, and experiment with the code for learning, demonstrations, and research. It is not intended as a production-ready system. If you plan to use this code with real data or in production, implement appropriate security, privacy, and compliance measures before doing so.

## What this project contains

- `app.py` - Streamlit application to interact with the claims pipeline.
- `agent.ipynb` - Jupyter notebook demonstrating the `StateGraph` implementation, LLM-driven agents, and a small demo run.
- `data/` - demo data and the policy PDF used by the agents:
  - `warranty_claims.csv` - sample claims data
  - `AutoDrive_Warranty_Policy_2025.pdf` - policy manual used for policy checks
- `reqirements.txt` - Python dependencies for the project (note the filename is intentionally present in the repository as `reqirements.txt`).

## Prerequisites

- Python 3.10+ (project was developed with modern Python 3.x)
- Streamlit (installed via the requirements file)
- An Azure OpenAI deployment (optional but required for the LLM-driven behavior)
- A local virtual environment (recommended)
- Windows (instructions below use `cmd.exe`)

Note about the package manager: you mentioned using the UV Python package manager. The README below shows standard `python -m venv` + `pip` commands which will work even if you used `uv` to create the `.venv`. If you prefer `uv` workflows, use the same virtual environment activation commands you normally use with `uv`, then run the `pip install -r reqirements.txt` step.

## Setup (Windows, cmd.exe)

1. Open a `cmd.exe` terminal in the project root:

2. Create a virtual environment (if you don't already have one):

```cmd
python -m venv .venv
```

3. Activate the virtual environment:

```cmd
.venv\Scripts\activate
```

4. Install dependencies from the repository's requirements file:

```cmd
pip install --upgrade pip
pip install -r reqirements.txt
```

If you used the UV package manager to create/activate your environment already, skip steps 2–3 and simply install dependencies while your venv is active.

## Environment variables

This project expects sensitive keys to be provided via a `.env` file (the notebook calls `load_dotenv()`), or via environment variables. Create a `.env` file in the project root with the following keys filled in:

```
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-azure-endpoint
# Optional: the LLM deployment name used in the notebook/app
DEPLOYMENT_NAME=gpt-4o
```

Make sure your Azure deployment name, key and endpoint match what you use in the notebook/app. Without valid keys, the LLM calls will fail and the notebook/app will fall back to rule-based logic (if implemented).

## Run the Streamlit app

With the virtual environment active, run:

```cmd
streamlit run app.py
```

This will start the Streamlit server and open a browser tab where you can interact with the claims adjudication UI.

## Run the demo notebook

Open `agent.ipynb` using Jupyter or VS Code's notebook interface. The notebook contains a small demo that:

- loads `data/warranty_claims.csv` (3-row demo dataset),
- loads and concatenates the policy PDF, and
- runs each claim through the LangGraph `StateGraph` pipeline.

Ensure your virtual environment is active and the `.env` variables are set so the notebook can call the Azure LLM.

## Output

- The Streamlit app provides interactive evaluation of claims.
- The notebook writes a small `results_df` DataFrame (and you can uncomment the `results_df.to_csv("demo_claims_results.csv", index=False)` line to save CSV output).

## Troubleshooting

- If Streamlit fails to run: confirm the virtual environment is active and that `streamlit` is installed.
- If the LLM calls fail: check your `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT`. Inspect the notebook/app logs for helpful error traces.
- If you see `ModuleNotFoundError` for packages referenced in the notebook, re-run `pip install -r reqirements.txt` and confirm the correct Python interpreter/venv is active.

## Notes & next steps

- The project is a tutorial/demo. For production use you should add robust error handling, rate limiting, and secrets management (do not store API keys in plaintext).
- Consider renaming `reqirements.txt` to `requirements.txt` to match common conventions (remember to update any scripts that refer to the filename).

---

If you'd like, I can also:

- rename `reqirements.txt` to `requirements.txt` and update the README accordingly,
- add a short example `.env.example` file to the repo, or
- add a minimal Dockerfile or GitHub Actions workflow for reproducible runs.

Let me know which of those you'd like me to do next.

License: MIT (feel free to change)

Copyright © 2025 AaiTech. All rights reserved.

Owner: Sandesh Hase
