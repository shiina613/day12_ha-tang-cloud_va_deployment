# Deployment Information

## Public URL

https://day12ha-tang-cloudvadeployment-production-bc56.up.railway.app

## Platform

Railway

## Test Commands

### Health Check
```bash
curl https://day12ha-tang-cloudvadeployment-production-bc56.up.railway.app/health
# Expected: {"status": "ok"}
```

### Chat (no auth required)
```bash
curl -X POST https://day12ha-tang-cloudvadeployment-production-bc56.up.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test"}'
# Expected: 200 OK with reply
```

### Rate Limiting
```bash
for i in {1..25}; do
  curl -s -X POST https://day12ha-tang-cloudvadeployment-production-bc56.up.railway.app/chat \
    -H "Content-Type: application/json" \
    -d '{"message":"test","session_id":"ratelimit-test"}'
  echo ""
done
# Expected: eventually returns 429 Too Many Requests
```

## Environment Variables Set

- `PORT=8000`
- `AGENT_API_KEY`
- `ENVIRONMENT`
- `DAILY_BUDGET_USD`

## Screenshots

- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
