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
shiina@Shiiina:/media/shiina/Shiina1/Documents and Settings/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment$ curl "http://localhost:8000/ask?question=Hello" -X POST
{"answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé."}shiina@Shiiina:/media/shiina/Shiina1/Documents and Settings/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment$ 
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
shiina@Shiiina:/media/shiina/Shiina1/Documents and Settings/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment$curl http://localhost:8000/health
{"status":"ok","uptime_seconds":10.7,"version":"1.0.0","environment":"development","timestamp":"2026-04-17T09:08:10.807934+00:00"}shiina@Shiiina:/media/shiina/Shiina1/Documents and Settings/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment$ curl "http://localhost:8000/ask" -X POST -H "Content-Type: application/json" -d '{"question":"Hello"}'
{"question":"Hello","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","model":"gpt-4o-mini"}shiina@Shiiina:/media/shiina/Shiina1/Documents and Settings/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment$ 
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
(venv) shiina@Shiiina:/media/shiina/Shiina1/Users/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment/02-docker$ cd /media/shiina/Shiina1/Users/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment

docker build -f 02-docker/develop/Dockerfile -t my-agent:develop .
docker run -p 8000:8000 my-agent:develop
[+] Building 1.4s (12/12) FINISHED                                        docker:default
 => [internal] load build definition from Dockerfile                                0.0s
 => => transferring dockerfile: 1.37kB                                              0.0s
 => [internal] load metadata for docker.io/library/python:3.11                      1.2s
 => [internal] load .dockerignore                                                   0.0s
 => => transferring context: 2B                                                     0.0s
 => [1/7] FROM docker.io/library/python:3.11@sha256:8f004bb4a5d9e8107f9d0a1aae78b9  0.0s
 => => resolve docker.io/library/python:3.11@sha256:8f004bb4a5d9e8107f9d0a1aae78b9  0.0s
 => [internal] load build context                                                   0.0s
 => => transferring context: 1.29kB                                                 0.0s
 => CACHED [2/7] WORKDIR /app                                                       0.0s
 => CACHED [3/7] COPY 02-docker/develop/requirements.txt .                          0.0s
 => CACHED [4/7] RUN pip install --no-cache-dir -r requirements.txt                 0.0s
 => CACHED [5/7] COPY 02-docker/develop/app.py .                                    0.0s
 => CACHED [6/7] RUN mkdir -p utils                                                 0.0s
 => CACHED [7/7] COPY utils/mock_llm.py utils/                                      0.0s
 => exporting to image                                                              0.1s
 => => exporting layers                                                             0.0s
 => => exporting manifest sha256:0a3d74ddd40016494bc35114dc6d833ac8b6788a16cf106ac  0.0s
 => => exporting config sha256:61ff4fdcf187fe34870a717bd6eedd2e3c518aa6c58283ab366  0.0s
 => => exporting attestation manifest sha256:a4ecfaf66710f2945b9c34408766524fddcd9  0.0s
 => => exporting manifest list sha256:4d7008681e8a4311f5ae47eb01da036846eefd3e176e  0.0s
 => => naming to docker.io/library/my-agent:develop                                 0.0s
 => => unpacking to docker.io/library/my-agent:develop                              0.0s
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     172.17.0.1:47280 - "POST /ask?question=Hello HTTP/1.1" 200 OK

```


```
shiina@Shiiina:/media/shiina/Shiina1/Documents and Settings/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment$ curl "http://localhost:8000/ask?question=Hello" -X POST
{"answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận."}shiina@Shiiina:/media/shiina/Shiina1/Documents and Settings/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment$ 

```


### Exercise 2.3: Image size comparison

```
(venv) shiina@Shiiina:/media/shiina/Shiina1/Users/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment$ docker images | grep my-agent

WARNING: This output is designed for human readability. For machine-readable output, please use --format.

my-agent:develop       84be90633a75       1.66GB          424MB   U    

my-agent:production    bb6a15074c07        236MB         56.6MB        

(venv) shiina@Shiiina:/media/shiina/Shiina1/Users/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment$ 
```

- Develop: [424] MB
- Production: [56.6] MB
- Difference: [86]% smaller

**Tại sao production nhỏ hơn:**
Multi-stage build — Stage 1 (builder) cài dependencies, Stage 2 (runtime) chỉ copy kết quả, không chứa build tools. Dùng `slim` base image.

### Exercise 2.4: Docker Compose stack

**Architecture diagram:**
```
Client → Nginx (port 80) → Agent (port 8000) → Redis (port 6379)
```

**Services được start:**
```
(venv) shiina@Shiiina:/media/shiina/Shiina1/Users/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment$ docker compose -f 02-docker/production/docker-compose.yml up nginx agent redis
WARN[0000] /media/shiina/Shiina1/Users/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment/02-docker/production/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion 
[+] Building 0.6s (19/19) FINISHED                                     
 => [internal] load local bake definitions                        0.0s
 => => reading from stdin 696B                                    0.0s
 => [internal] load build definition from Dockerfile              0.0s
 => => transferring dockerfile: 3.29kB                            0.0s
 => [internal] load metadata for docker.io/library/python:3.11-s  0.3s
 => [internal] load .dockerignore                                 0.0s
 => => transferring context: 2B                                   0.0s
 => [internal] load build context                                 0.0s
 => => transferring context: 2.59kB                               0.0s
 => [builder 1/5] FROM docker.io/library/python:3.11-slim@sha256  0.0s
 => => resolve docker.io/library/python:3.11-slim@sha256:233de06  0.0s
 => CACHED [runtime 2/8] RUN groupadd -r appuser && useradd -r -  0.0s
 => CACHED [runtime 3/8] WORKDIR /app                             0.0s
 => CACHED [builder 2/5] WORKDIR /app                             0.0s
 => CACHED [builder 3/5] RUN apt-get update && apt-get install -  0.0s
 => CACHED [builder 4/5] COPY 02-docker/production/requirements.  0.0s
 => CACHED [builder 5/5] RUN pip install --no-cache-dir --user -  0.0s
 => CACHED [runtime 4/8] COPY --from=builder /root/.local /home/  0.0s
 => CACHED [runtime 5/8] COPY 02-docker/production/main.py .      0.0s
 => CACHED [runtime 6/8] RUN mkdir -p /app/utils                  0.0s
 => CACHED [runtime 7/8] COPY utils/mock_llm.py /app/utils/mock_  0.0s
 => CACHED [runtime 8/8] RUN chown -R appuser:appuser /app        0.0s
 => exporting to image                                            0.1s
 => => exporting layers                                           0.0s
 => => exporting manifest sha256:d0073b35e4c53f78ffe22f3c16758d8  0.0s
 => => exporting config sha256:1ba0f8d7d4fdec169737049f10672d9d3  0.0s
 => => exporting attestation manifest sha256:8ce0d07ac8f3d58b193  0.0s
 => => exporting manifest list sha256:e0700782fc1d9da567f3fe4ffe  0.0s
 => => naming to docker.io/library/production-agent:latest        0.0s
 => => unpacking to docker.io/library/production-agent:latest     0.0s
 => resolving provenance for metadata file                        0.0s
[+] up 8/8
 ✔ Image production-agent        Built                             0.7s
 ✔ Network production_internal   Created                           0.0s
 ✔ Volume production_qdrant_data Created                           0.0s
 ✔ Volume production_redis_data  Created                           0.0s
 ✔ Container production-redis-1  Created                           0.1s
 ✔ Container production-qdrant-1 Created                           0.0s
 ✔ Container production-agent-1  Created                           0.0s
 ✔ Container production-nginx-1  Created                           0.1s
Attaching to agent-1, nginx-1, redis-1
Container production-qdrant-1 Waiting 
Container production-redis-1 Waiting 
redis-1  | 1:C 17 Apr 2026 09:31:28.337 # WARNING Memory overcommit must be enabled! Without it, a background save or replication may fail under low memory condition. Being disabled, it can also cause failures without low memory condition, see https://github.com/jemalloc/jemalloc/issues/1328. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
redis-1  | 1:C 17 Apr 2026 09:31:28.337 * oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
redis-1  | 1:C 17 Apr 2026 09:31:28.337 * Redis version=7.4.8, bits=64, commit=00000000, modified=0, pid=1, just started
redis-1  | 1:C 17 Apr 2026 09:31:28.337 * Configuration loaded
redis-1  | 1:M 17 Apr 2026 09:31:28.338 * Increased maximum number of open files to 10032 (it was originally set to 1024).
redis-1  | 1:M 17 Apr 2026 09:31:28.338 * monotonic clock: POSIX clock_gettime
redis-1  | 1:M 17 Apr 2026 09:31:28.339 * Running mode=standalone, port=6379.
redis-1  | 1:M 17 Apr 2026 09:31:28.339 * Server initialized
redis-1  | 1:M 17 Apr 2026 09:31:28.339 * Ready to accept connections tcp
Container production-redis-1 Healthy 
```

**Test output:**
```
shiina@Shiiina:/media/shiina/Shiina1/Documents and Settings/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment$ curl http://localhost/health
{"status":"ok","uptime_seconds":4.6,"version":"2.0.0","timestamp":"2026-04-17T09:33:17.608781"}shiina@Shiiina:/media/shiina/Shiina1/Documents 
shiina@Shiiina:/media/shiina/Shiina1/Documents and Settings/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment$ 
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
