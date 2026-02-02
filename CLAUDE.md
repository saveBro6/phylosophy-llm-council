# CLAUDE.md — Project Summary & Developer Notes

This document describes the "LLM Council" project adapted as a philosophical council: multiple LLMs roleplay well-known historical philosophers, they critique one another, and a chairman (Lenin) synthesizes the final judgement and answer.

## Purpose
- Present users with diverse philosophical perspectives: each council member represents a famous philosopher and answers from that thinker’s viewpoint.
- Stage 2 provides adversarial critique between philosophers, surfacing conflicts and tensions between doctrines.
- Stage 3: Lenin (the chairman) evaluates responses and critiques, highlights errors or inconsistencies, contrasts conclusions with dialectical materialism where relevant, and produces a final answer.

## Quick summary
- System: 3-stage deliberation (collect → critique → synthesize).
- Roles: council members = historical philosophers (LLMs configured with philosopher system prompts); chairman = Lenin (LLM with synthesis/critique prompt emphasizing dialectical-materialist analysis).
- Goal: educational exploration of viewpoints and comparison with Leninist dialectical materialism.

## Run (local dev)
- Backend (FastAPI) — from project root:

```bash
python -m backend.main
```

- Frontend (Vite):

```bash
cd frontend
npm install
npm run dev
```

- Env: set `OPENROUTER_API_KEY` and any TTS keys (see `backend/config.py` and `backend/tts_config.py`).

## Core flow (3 stages)
- Stage 1 — Collect philosophers' answers:
  - Query each philosopher-model in parallel for an answer to the user question, seeding prompts with the philosopher's persona, major works, and characteristic reasoning style.
- Stage 2 — Philosophers critique one another:
  - Responses are anonymized (Response A, B, ...). Each philosopher evaluates the others' arguments and points out tensions, contradictions, or historical/philosophical objections.
  - Outputs follow a structured format to make parsing reliable (e.g., a clear "FINAL RANKING:" or "CRITIQUES:" block). Parsed critiques and extracted points are stored alongside raw text.
- Stage 3 — Lenin synthesizes and judges:
  - The chairman receives Stage 1 responses and Stage 2 critiques, identifies errors or useful insights, contrasts them with dialectical materialism, and produces the final answer with justification.

## Architecture
### Backend 
Only the primary files and their responsibilities are listed below — refer to the repository for full code.

- `backend/config.py` — council/ chairman model lists and other constants, environment key names.
- `backend/council.py` — orchestration of Stage 1, Stage 2, Stage 3; parsing and aggregation helpers.
- `backend/openrouter.py` — helper functions to call models (single/parallel calls, error handling, timeouts).
- `backend/storage.py` — JSON conversation persistence under `data/conversations/`.
- `backend/main.py` — FastAPI server, route handlers, CORS settings used by the frontend.
- `backend/system_prompt.py` — canonical persona prompts for philosophers and the Lenin chairman.
- `backend/elevenlabs_tts.py`, `backend/tts_config.py`, `VOICE_IDS.json` — optional ElevenLabs TTS integration.


### Frontend
- `frontend/src/api.js` — client API helpers; ensure base URL/port match backend.
- `frontend/src/App.jsx` — main app state and conversation orchestration.
- `frontend/src/components/Stage1.jsx` — displays each philosopher's answer.
- `frontend/src/components/Stage2.jsx` — shows raw critiques and parsed critique/ranking extractions.
- `frontend/src/components/Stage3.jsx` — shows Lenin's synthesized final answer.

- `data/conversations/` — persisted conversation JSON files (one per conversation).
- `start.sh`, `README.md` — convenience and documentation.

## API & data model
- Main route: POST `/api/conversations/{id}/message` — accepts user question and returns Stage 1 answers, Stage 2 critiques, Stage 3 synthesis, and metadata (label mappings, parsed critiques, aggregated rankings).
- Conversation JSON: includes `id`, `created_at`, `messages[]`. Assistant messages store stage payloads; metadata is returned by the API and may be persisted if configured.

## Prompting and persona notes
- Each philosopher gets a system/instruction prompt that encodes core doctrines, rhetorical style, and key works to emulate authentic reasoning. Prompts should be concise but contain pointers to primary emphases (e.g., "Hegel: dialectics, development of contradictions").
- Lenin (chairman) prompt emphasizes dialectical materialism: identifying socio-historical material conditions, contradictions, and practical/political implications. Lenin's synthesis both adjudicates correctness and highlights departures from dialectical-materialist analysis.
- Stage 2 prompts instruct philosophers to evaluate others' arguments and produce clearly parseable critique blocks (so automated parsing can extract key objections and rankings).

## Parsing, aggregation, and display
- Stage 2 outputs are kept raw for audit; the backend parses structured sections (e.g., "CRITIQUES:") into `parsed_critiques`.
- Frontend displays raw text and parsed results side-by-side so users can verify parsing and understand differences between raw critique and automated interpretation.

## Developer notes & gotchas
- Run backend as a module from project root: `python -m backend.main` to avoid relative import issues.
- CORS: ensure frontend dev origin (default 5173) is allowed in `backend/main.py`.
- Tolerate model failures: the system proceeds with available responses; Stage 3 still synthesizes from whatever inputs succeeded.
- Ensure Stage 2 prompts are strict enough for consistent parsing; fallback regexes handle imperfect outputs but are less reliable.

## Ethics & framing
- The system roleplays historical philosophers for educational purposes; ensure prompts and UI clarify that outputs are modeled interpretations, not historical quotations or definitive scholarship.
- Lenin is used as a synthetic chairman persona to explore dialectical-materialist analysis — include a UI note explaining this framing and encouraging critical reading.

## Next steps & improvements
- Add UI controls to select which philosophers are in the council and to toggle whether to show Lenin's dialectical commentary.
- Persist label mappings for audit logs if needed.
- Add automated unit tests for `council.parse_ranking_from_text()` and for Stage 3 synthesis prompts to ensure consistent behavior.

---

