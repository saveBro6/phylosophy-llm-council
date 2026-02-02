# Philosophy LLM Council

![llmcouncil](header.png)

A web application that simulates a philosophical council where multiple LLMs roleplay as historical philosophers (e.g., Plato, Descartes, Nietzsche, Confucius), engaging in debate and critique. A chairman LLM (Lenin) synthesizes their arguments and produces a final answer rooted in dialectical-materialist analysis.

Instead of asking a single LLM provider for answers, this project creates a council of philosophical personas that collectively explore questions from diverse intellectual traditions, then adjudicates between them.

## How it works

When you submit a query, the system performs three stages of deliberation:

1. **Stage 1: Philosophical Perspectives**. The user query is given to each philosopher-LLM individually, configured with system prompts that encode their distinctive doctrines, rhetorical style, and historical context. Responses are displayed in a tab view so users can inspect each philosopher's unique viewpoint.

2. **Stage 2: Critique**. Each philosopher is presented with the responses of the others and asked to critique them—identifying tensions, contradictions, logical flaws, or historical/philosophical objections. Critiques are parsed and displayed alongside raw text for transparency.

3. **Stage 3: Synthesis & Judgement**. Lenin (the chairman) receives all Stage 1 responses and Stage 2 critiques, identifies errors and insights, contrasts them with dialectical materialism, and produces the final answer with reasoned justification.

## Setup

### 1. Install Dependencies

The project uses [uv](https://docs.astral.sh/uv/) for project management.

**Backend:**
```bash
uv sync
```

**Frontend:**
```bash
cd frontend
npm install
cd ..
```

### 2. Configure API Keys

Create a `.env` file in the project root (you can use `.env.example` as a template):

```bash
# Required: OpenRouter API key for LLM queries
OPENROUTER_API_KEY=sk-or-v1-...

# Optional: ElevenLabs for Text-to-Speech (voice in Council Courtroom)
ELEVENLABS_API_KEY=your-elevenlabs-key

# Optional: JSON array of 5 voice IDs for [Lenin, Plato, Descartes, Nietzsche, Confucius]
ELEVENLABS_VOICE_ID=["voice_id_1", "voice_id_2", "voice_id_3", "voice_id_4", "voice_id_5"]
```

**OpenRouter:** Get your API key at [openrouter.ai](https://openrouter.ai/). Purchase credits or enable automatic top-up.

**ElevenLabs (Optional):** Get your API key at [elevenlabs.io](https://elevenlabs.io). Voice IDs can be found in your ElevenLabs dashboard.

### 3. Configure Models (Optional)

Edit `backend/config.py` to customize the council:

```python
COUNCIL_MODELS = [
    "openai/gpt-5.1",
    "google/gemini-3-pro-preview",
    "anthropic/claude-sonnet-4.5",
    "x-ai/grok-4",
]

CHAIRMAN_MODEL = "google/gemini-3-pro-preview"
```

## Running the Application

**Option 1: Use the start script**
```bash
./start.sh
```

**Option 2: Run manually**

Terminal 1 (Backend):
```bash
uv run python -m backend.main
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

Then open http://localhost:5173 in your browser.

## Tech Stack

- **Backend:** FastAPI (Python 3.10+), async httpx, OpenRouter API
- **Frontend:** React + Vite, react-markdown for rendering
- **Storage:** JSON files in `data/conversations/`
- **Text-to-Speech:** ElevenLabs API integration (optional)
- **Package Management:** uv for Python, npm for JavaScript
