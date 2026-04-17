# Day 12 Lab - Mission Answers

> **Student Name:** Nguyen Quang Tung 
> **Student ID:** 2A202600197  
> **Date:** 17/4/2026

---

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found

1. API key hardcode trong code: `OPENAI_API_KEY = "sk-hardcoded-fake-key-never-do-this"`
2. Database URL hardcode với password: `DATABASE_URL = "postgresql://admin:password123@localhost:5432/mydb"`
3. Không có health check endpoint — platform không biết khi nào restart
4. Port cố định `port=8000` — không đọc từ env var `PORT`
5. `host="localhost"` — chỉ chạy được local, không nhận traffic từ bên ngoài
6. `reload=True` và `DEBUG = True` hardcode — không nên dùng trong production
7. Dùng `print()` thay vì structured logging
8. Log ra secret: `print(f"[DEBUG] Using key: {OPENAI_API_KEY}")`

### Exercise 1.3: Comparison table

| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config | Hardcode trong code | Đọc từ environment variables | Dễ thay đổi giữa environments, không commit secrets |
| Secrets | `api_key = "sk-abc123"` | `os.getenv("OPENAI_API_KEY")` | Bảo mật, không lộ khi push lên GitHub |
| Port | Cố định `8000` | Từ `PORT` env var | Cloud platforms inject PORT khác nhau |
| Host | `localhost` | `0.0.0.0` | Cho phép nhận traffic từ bên ngoài container |
| Health check | Không có | `GET /health` | Platform biết khi nào restart, monitoring |
| Logging | `print()` | Structured JSON | Dễ parse, search, analyze trong production |
| Shutdown | Đột ngột | Graceful (SIGTERM) | Không mất data, hoàn thành requests đang xử lý |
| Debug mode | `reload=True` | `reload=False` | Performance tốt hơn, không expose debug info |

---

## Part 2: Docker

### Exercise 2.1: Dockerfile questions

1. **Base image:** `python:3.11` — full Python distribution (~1GB), chứa OS + Python runtime
2. **Working directory:** `/app` — thư mục làm việc trong container, nơi code được copy vào
3. **Tại sao COPY requirements.txt trước:** Docker cache layers — nếu requirements không đổi thì không cần rebuild layer `pip install`, chỉ rebuild khi code thay đổi → build nhanh hơn
4. **CMD vs ENTRYPOINT:** `CMD` là default command, có thể override khi `docker run image <other-cmd>`. `ENTRYPOINT` là command cố định, không thể override

### Exercise 2.3: Image size comparison

- Develop: [X] MB
- Production: [Y] MB
- Difference: [Z]%

### Exercise 2.4: Architecture diagram

```
Client → Nginx (port 80) → Agent (port 8000) → Redis (port 6379)
```

---

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment

- **URL:** https://your-app.railway.app
- **Screenshot:** [Link to screenshot in repo]

### Exercise 3.2: Config file comparison

| Aspect | railway.toml | render.yaml |
|--------|--------------|-------------|
| Format | TOML | YAML |
| Build | `[build]` section | `buildCommand` field |
| Start | `[deploy]` section | `startCommand` field |
| Env vars | Qua CLI hoặc dashboard | Trong file hoặc dashboard |

---

## Part 4: API Security

### Exercise 4.1-4.3: Test results

**Without API key (401):**
```
[Paste output here]
```

**With API key (200):**
```
[Paste output here]
```

**Rate limiting (429 after threshold):**
```
[Paste output here]
```

### Exercise 4.4: Cost guard implementation

```python
import redis
from datetime import datetime

r = redis.Redis()

def check_budget(user_id: str, estimated_cost: float) -> bool:
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    current = float(r.get(key) or 0)
    if current + estimated_cost > 10:
        return False
    
    r.incrbyfloat(key, estimated_cost)
    r.expire(key, 32 * 24 * 3600)  # 32 days TTL
    return True
```

Dùng Redis key `budget:{user_id}:{YYYY-MM}` để track spending theo tháng. TTL 32 ngày để tự cleanup.

---

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes

**Health & readiness checks:**
```python
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    try:
        r.ping()
        return {"status": "ready"}
    except:
        return JSONResponse(status_code=503, content={"status": "not ready"})
```

**Graceful shutdown:**
```python
import signal, sys

def shutdown_handler(signum, frame):
    print("Graceful shutdown...")
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
```

**Stateless refactor:**
```python
# ❌ Before — state in memory
conversation_history = {}

# ✅ After — state in Redis
history = r.lrange(f"history:{user_id}", 0, -1)
```

**Load balancing test:**
```
[Paste docker compose up --scale agent=3 output here]
```

**Stateless test result:**
```
[Paste python test_stateless.py output here]
```
