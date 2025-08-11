# 📦 API VERSIONS

## prompt_api/__init__.py — v1.0.0
- Initializes FastAPI router module
- Used as part of API import structure
- Last Updated: 2025-07-18

---

## prompt_api/main.py — v1.0.0
- FastAPI main entrypoint for backend API
- Includes route mounting, CORS setup
- Last Updated: 2025-07-18

🔜 Next:
- Add startup and shutdown hooks
- Health check endpoint
---

## prompt_api/analyze.py — v1.0.0
- Analyzes prompts and routes to relevant model or agent
- Planned to use `filters.py` for safety checks
- Currently minimal
- Last Updated: 2025-07-18

🔜 Next:
- Add route to call security filters
- Integrate spec_model-based suggestions
---

## prompt_api/feedback.py — v1.0.0
- Accepts and saves prompt feedback to `feedback_log.jsonl`
- Structure: prompt, response, rating, timestamp
- Used in: feedback modal from frontend
- Last Updated: 2025-07-18

🔜 Next:
- Add rating/tagging system
- Expose admin feedback query API
---

## prompt_api/admin_feedback.py — v1.0.0
- Returns filtered feedback logs for admin viewing
- Used in: AdminFeedbackTable.tsx
- Supports basic read-only access
- Last Updated: 2025-07-18

🔜 Next:
- Add filter by model or rating
- Date range + export to CSV
---

## prompt_api/suggest.py — v1.0.0
- Suggests improvements or related prompts
- Uses basic in-memory logic for now
- Placeholder logic only
- Last Updated: 2025-07-18

🔜 Next:
- Add prompt similarity model (OpenAI or local)
- History-based contextual suggestion
---