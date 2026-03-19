# LOIS Integration Guide

## Overview

This guide covers how to integrate your LOIS frontend with the Busy Bee API for full chat functionality.

---

## 1. Chat Component (LOIS Frontend)

### Copy the Chat Component

Copy `docs/lois/LOISChat.jsx` into your LOIS project:

```bash
cp docs/lois/LOISChat.jsx /path/to/lois/src/components/
```

### Import and Use

```jsx
import LOISChat from './components/LOISChat';

function App() {
  return (
    <div>
      <LOISChat apiUrl="https://your-busybee-api.com" />
    </div>
  );
}
```

---

## 2. Deploy Busy Bee API

### Option A: Deploy to Render (Free)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) and sign up
3. Create a new Web Service:
   - Connect your GitHub repo
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.api.main:app --host 0.0.0.0 --port $PORT`

### Option B: Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Deploy from GitHub
3. Set environment variables

### Option C: Run Locally

```bash
# Install dependencies
pip install fastapi uvicorn pydantic

# Run the server
uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

---

## 3. Connect LOIS to Busy Bee API

### Update Chat Component API URL

In your LOIS app, update the API URL:

```jsx
// Production
<LOISChat apiUrl="https://your-busybee-api.onrender.com" />

// Or local development
<LOISChat apiUrl="http://localhost:8000" />
```

### Test the Connection

```bash
# Test health endpoint
curl https://your-api-url.com/health

# Test chat endpoint
curl -X POST https://your-api-url.com/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me my brief"}'
```

---

## 4. API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/briefs/latest` | GET | Get executive brief |
| `/briefs/generate` | POST | Generate brief |
| `/recommendations` | GET | List recommendations |
| `/recommendations/generate` | POST | Create recommendation |
| `/recommendations/{id}/approve` | POST | Approve |
| `/recommendations/{id}/reject` | POST | Reject |
| `/domains` | GET | List domains |
| `/chat/message` | POST | **Chat with Busy Bee** |

---

## 5. Sync Service (Optional)

To automatically sync recommendations to LOIS:

```python
from app.integrations import lois_sync_service

# Push approved recommendations
await lois_sync_service.sync_approved_recommendations(recommendations)
```

---

## 6. Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LOIS_BASE_URL` | LOIS frontend URL | `https://lois...base44.app` |
| `API_KEY` | API authentication key | (optional) |

---

## Quick Start Checklist

- [ ] Deploy Busy Bee API
- [ ] Get your API URL
- [ ] Update LOIS Chat component with API URL
- [ ] Test chat functionality
- [ ] Deploy updated LOIS app

---

## Troubleshooting

### CORS Errors
Add CORS middleware to the FastAPI app:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://lois-life-operating-intelligence-s-c8a842a9.base44.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Connection Refused
- Check that the API is running
- Verify the URL is correct
- Check firewall settings
