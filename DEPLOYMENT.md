# Deployment Information

## Public URL

https://your-agent.railway.app

## Platform

Railway / Render / Cloud Run

## Test Commands

### Health Check
```bash
curl https://your-agent.railway.app/health
# Expected: {"status": "ok"}
```

### Authentication Required
```bash
curl https://your-agent.railway.app/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
# Expected: 401 Unauthorized
```

### API Test (with authentication)
```bash
curl -X POST https://your-agent.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
# Expected: 200 OK
```

### Rate Limiting
```bash
for i in {1..15}; do
  curl -H "X-API-Key: YOUR_KEY" https://your-agent.railway.app/ask \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"user_id":"test","question":"test"}'
done
# Expected: eventually returns 429 Too Many Requests
```

## Environment Variables Set

- `PORT`
- `REDIS_URL`
- `AGENT_API_KEY`
- `LOG_LEVEL`

## Screenshots

- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
