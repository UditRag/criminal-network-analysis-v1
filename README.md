# AI-Powered Criminal Network Analysis System (SIH26189 Prototype V1)

A database-free, in-memory prototype built for Smart India Hackathon 2026. This system ingests fragmented text (FIRs), CSV (Call Detail Records), and Financial transactions, normalizes entities, builds a graph, and flags suspicious network patterns.

## Team
- **Udit Raghuwanshi**: Data, Graph Analytics, Architecture (NetworkX, Streamlit)
- **Aniruddha**: NLP, Entity Extraction pipeline

## Setup Instructions
1. Open terminal and create a virtual environment: `python -m venv .venv`
2. Activate environment:
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `streamlit run app.py`
5. Click **"Load Demo Investigation"** in the sidebar.
