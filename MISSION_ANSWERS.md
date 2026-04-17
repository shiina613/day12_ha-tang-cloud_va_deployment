# Day 12 Lab - Mission Answers

> **Student Name:** Nguyen Quang Tung  
> **Student ID:** 2A202600197  
> **Date:** 17/4/2026

---

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found in `develop/app.py`

1. API key hardcode trong code: `OPENAI_API_KEY = "sk-hardcoded-fake-key-never-do-this"`
2. Database URL hardcode với password: `DATABASE_URL = "postgresql://admin:password123@localhost:5432/mydb"`
3. Không có health check endpoint — platform không biết khi nào restart
4. Port cố định `port=8000` — không đọc từ env var `PORT`
5. `host="localhost"` — chỉ chạy được local, không nhận traffic từ bên ngoài
6. `reload=True` và `DEBUG = True` hardcode — không nên dùng trong production
7. Dùng `print()` thay vì structured logging
8. Log ra secret: `print(f"[DEBUG] Using key: {OPENAI_API_KEY}")`

### Exercise 1.2: Run basic version — output

```
[Paste output của curl "http://localhost:8000/ask?question=Hello" -X POST ở đây]
```

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

**Output production version:**
```
[Paste output của curl http://localhost:8000/health ở đây]
```

---

## Part 2: Docker

### Exercise 2.1: Dockerfile questions

1. **Base image:** `python:3.11` — full Python distribution (~1GB), chứa OS + Python runtime
2. **Working directory:** `/app` — thư mục làm việc trong container, nơi code được copy vào
3. **Tại sao COPY requirements.txt trước:** Docker cache layers — nếu requirements không đổi thì không cần rebuild layer `pip install`, chỉ rebuild khi code thay đổi → build nhanh hơn
4. **CMD vs ENTRYPOINT:** `CMD` là default command, có thể override khi `docker run image <other-cmd>`. `ENTRYPOINT` là command cố định, không thể override

### Exercise 2.2: Build and run basic container — output

```
[Paste output của docker run + curl test ở đây]
```

### Exercise 2.3: Image size comparison

```
[Paste output của docker images | grep my-agent ở đây]
```

- Develop: [X] MB
- Production: [Y] MB
- Difference: [Z]% smaller

**Tại sao production nhỏ hơn:**
Multi-stage build — Stage 1 (builder) cài dependencies, Stage 2 (runtime) chỉ copy kết quả, không chứa build tools. Dùng `slim` base image.

### Exercise 2.4: Docker Compose stack

**Architecture diagram:**
```
Client → Nginx (port 80) → Agent (port 8000) → Redis (port 6379)
```

**Services được start:**
```
[Paste output của docker compose up ở đây — phần services started]
```

**Test output:**
```
[Paste output của curl http://localhost/health ở đây]
```

---

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment

- **URL:** https://[your-app].railway.app
- **Screenshot:** [screenshots/dashboard.png](screenshots/dashboard.png)

**Test output:**
```
[Paste output của curl https://your-app.railway.app/health ở đây]
```

### Exercise 3.2: Config file comparison

| Aspect | railway.toml | render.yaml |
|--------|--------------|-------------|
| Format | TOML | YAML |
| Build | `[build]` section | `buildCommand` field |
| Start | `[deploy]` section | `startCommand` field |
| Env vars | Qua CLI hoặc dashboard | Trong file hoặc dashboard |

---

## Part 4: API Security

### Exercise 4.1: API key authentication — test results

**Without API key (expected: 401):**
```
[Paste output ở đây]
```

**With API key (expected: 200):**
```
[Paste output ở đây]
```

### Exercise 4.2: JWT authentication — test results

**Get token:**
```
[Paste token response ở đây]
```

**Call API with token (expected: 200):**
```
[Paste response ở đây]
```

### Exercise 4.3: Rate limiting — test results

**After exceeding limit (expected: 429):**
```
[Paste output của vòng lặp 20 requests ở đây — đặc biệt phần 429]
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

**Giải thích:** Dùng Redis key `budget:{user_id}:{YYYY-MM}` để track spending theo tháng. TTL 32 ngày để tự cleanup. Reset tự động đầu tháng vì key mới được tạo.

---

## Part 5: Scaling & Reliability

### Exercise 5.1: Health and readiness checks — output

**GET /health:**
```
[Paste output của curl http://localhost:8000/health ở đây]
```

**GET /ready:**
```
[Paste output của curl http://localhost:8000/ready ở đây]
```

### Exercise 5.2: Graceful shutdown — log output

```
[Paste log từ terminal khi gửi kill -TERM ở đây]
```

### Exercise 5.3: Stateless design — explanation

**Before (stateful — không scale được):**
```python
conversation_history = {}  # In-memory, mỗi instance có bản riêng

@app.post("/ask")
def ask(user_id: str, question: str):
    history = conversation_history.get(user_id, [])
    # Instance 1 lưu, Instance 2 không biết → bug khi scale
```

**After (stateless — scale được):**
```python
@app.post("/chat")
def chat(body: ChatRequest):
    session = load_session(session_id)   # Đọc từ Redis
    history = session.get("history", [])
    # Bất kỳ instance nào cũng đọc được cùng 1 Redis
```

### Exercise 5.4: Load balancing — output

```
[Paste output của docker compose up --scale agent=3 ở đây]
```

**Requests phân tán (served_by khác nhau):**
```
[Paste output của 10 curl requests ở đây — thấy instance-xxx khác nhau]
```

### Exercise 5.5: Stateless test — output

```
[Paste output của python test_stateless.py ở đây]
```
