# Marriage App

FastAPI matrimony prototype for the Nagar Brahmin community.

## Use

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Add DB URL in `.env`:
```env
SUPA_POOL_URL=your_supabase_pooler_url
```

3. Run:
```bash
uvicorn app:app --reload
```

Then open `http://127.0.0.1:8000`.

## Render

Use this start command on Render:

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

The default `uvicorn app:app` binds to `127.0.0.1`, which Render cannot expose publicly.
