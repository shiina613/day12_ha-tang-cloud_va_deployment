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
[+] up 1/1
 ✔ Container production-redis-1 Running                            0.0s
Attaching to agent-1, nginx-1, redis-1
Container production-redis-1 Waiting 
Container production-redis-1 Healthy 
nginx-1  | /docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
nginx-1  | /docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
nginx-1  | /docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
nginx-1  | 10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf
nginx-1  | 10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
nginx-1  | /docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
nginx-1  | /docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
nginx-1  | /docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
nginx-1  | /docker-entrypoint.sh: Configuration complete; ready for start up
agent-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
agent-1  | INFO:     Started parent process [1]
agent-1  | INFO:     Started server process [9]
agent-1  | INFO:     Waiting for application startup.
agent-1  | INFO:     Started server process [8]
agent-1  | INFO:     Waiting for application startup.
agent-1  | {"time":"2026-04-17 09:33:12,977","level":"INFO","msg":"Starting agent..."}
agent-1  | {"time":"2026-04-17 09:33:12,977","level":"INFO","msg":"Starting agent..."}
agent-1  | {"time":"2026-04-17 09:33:13,078","level":"INFO","msg":"Agent ready"}
agent-1  | {"time":"2026-04-17 09:33:13,078","level":"INFO","msg":"Agent ready"}
agent-1  | INFO:     Application startup complete.
agent-1  | INFO:     Application startup complete.
agent-1  | INFO:     127.0.0.1:35756 - "GET /health HTTP/1.1" 200 OK
agent-1  | INFO:     172.18.0.5:59390 - "GET /health HTTP/1.1" 200 OK

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

- **URL:** https://day12-ha-tang-cloud-va-deployment-7j8u.onrender.com
- **Screenshot:** [screenshots/dashboard.png](screenshots/dashboard.png)

**Test output:**
```
shiina@Shiiina:/media/shiina/Shiina1/Documents and Settings/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment$ curl https://day12-ha-tang-cloud-va-deployment-7j8u.onrender.com/health
{"status":"ok","uptime_seconds":179.1,"platform":"Railway","timestamp":"2026-04-17T09:59:18.423553+00:00"}shiina@Shiiina:/media/shiina/Shiina1/Documents and Settings/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment$ 
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
curl http://localhost:8000/ask -X POST \host:8000/ask -X POST \
     -H "Content-Type: application/json" \
     -d '{"question": "hello"}'
{"detail":"Missing API key. Include header: X-API-Key: <your-key>"}
```

**With API key (expected: 200):**
```
curlcurl -X POST "http://localhost:8000/ask?question=hello" \
  -H "X-API-Key: my-secret-key"
{"question":"hello","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận."}
```

### Exercise 4.2: JWT authentication — test results

**Get token:**
```
shiina@Shiiina:~$ curl -X POST http://localhost:8000/auth/token      -H "Content-Type: application/json"      -d '{"username": "student", "password": "demo123"}'
{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHVkZW50Iiwicm9sZSI6InVzZXIiLCJpYXQiOjE3NzY0MjE0NDksImV4cCI6MTc3NjQyNTA0OX0.oew2hXzo-jwXuDxJMasLECfUHw8Qvg7z60seHYec01Q","token_type":"bearer","expires_in_minutes":60,"hint":"Include in header: Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."}
```

**Call API with token (expected: 200):**
```
shiina@Shiiina:~$ curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHVkZW50Iiwicm9sZSI6InVzZXIiLCJpYXQiOjE3NzY0MjE0NDksImV4cCI6MTc3NjQyNTA0OX0.oew2hXzo-jwXuDxJMasLECfUHw8Qvg7z60seHYec01Q" \
     http://localhost:8000/ask \
     -X POST -H "Content-Type: application/json" \
     -d '{"question": "what is docker?"}'
{"question":"what is docker?","answer":"Container là cách đóng gói app để chạy ở mọi nơi. Build once, run anywhere!","usage":{"requests_remaining":8,"budget_remaining_usd":5.7e-05}}
```

### Exercise 4.3: Rate limiting — test results

**After exceeding limit (expected: 429):**
```
shiina@Shiiina:~$ for i in {1..20}; do
  curl http://localhost:8000/ask -X POST \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHVkZW50Iiwicm9sZSI6InVzZXIiLCJpYXQiOjE3NzY0MjE0NDksImV4cCI6MTc3NjQyNTA0OX0.oew2hXzo-jwXuDxJMasLECfUHw8Qvg7z60seHYec01Q" \
    -H "Content-Type: application/json" \
    -d "{\"question\":\"Test $i\"}"
  echo ""
done
{"question":"Test 1","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","usage":{"requests_remaining":9,"budget_remaining_usd":7.5e-05}}
{"question":"Test 2","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.","usage":{"requests_remaining":8,"budget_remaining_usd":9.1e-05}}
{"question":"Test 3","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.","usage":{"requests_remaining":7,"budget_remaining_usd":0.000108}}
{"question":"Test 4","answer":"Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic.","usage":{"requests_remaining":6,"budget_remaining_usd":0.000129}}
{"question":"Test 5","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","usage":{"requests_remaining":5,"budget_remaining_usd":0.000147}}
{"question":"Test 6","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","usage":{"requests_remaining":4,"budget_remaining_usd":0.000166}}
{"question":"Test 7","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.","usage":{"requests_remaining":3,"budget_remaining_usd":0.000182}}
{"question":"Test 8","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.","usage":{"requests_remaining":2,"budget_remaining_usd":0.000198}}
{"question":"Test 9","answer":"Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic.","usage":{"requests_remaining":1,"budget_remaining_usd":0.000219}}
{"question":"Test 10","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","usage":{"requests_remaining":0,"budget_remaining_usd":0.000238}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":59}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":59}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":59}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":59}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":59}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":59}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":59}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":59}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":59}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":59}}
shiina@Shiiina:~$ 

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
shiina@Shiiina:~$ curl http://localhost:8000/health
{"status":"ok","uptime_seconds":58.4,"version":"1.0.0","environment":"development","timestamp":"2026-04-17T10:30:53.877973+00:00","checks":{"memory":{"status":"ok","used_percent":49.5}}}
```

**GET /ready:**
```
shiina@Shiiina:~$ curl http://localhost:8000/ready
{"ready":true,"in_flight_requests":1}
```

### Exercise 5.2: Graceful shutdown — log output

```
shiina@Shiiina:~$ ps aux | grep app.py
shiina     68427  0.4  0.3 249252 54692 pts/0    Sl+  17:29   0:00 python app.py
shiina     69083  0.0  0.0  17952  2336 pts/2    S+   17:32   0:00 grep --color=auto app.py
shiina@Shiiina:~$ kill -TERM 68427
shiina@Shiiina:~$ 

```

```
(venv) shiina@Shiiina:/media/shiina/Shiina1/Users/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment/05-scaling-reliability/develop$ python app.py
2026-04-17 17:29:55,492 INFO Starting agent on port 8000
INFO:     Started server process [68427]
INFO:     Waiting for application startup.
2026-04-17 17:29:55,510 INFO Agent starting up...
2026-04-17 17:29:55,510 INFO Loading model and checking dependencies...
2026-04-17 17:29:55,710 INFO ✅ Agent is ready!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:37570 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:37580 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:50728 - "GET /ready HTTP/1.1" 200 OK
INFO:     127.0.0.1:37706 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:60228 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:33976 - "GET /ready HTTP/1.1" 200 OK
INFO:     Shutting down
INFO:     Waiting for application shutdown.
2026-04-17 17:32:30,542 INFO 🔄 Graceful shutdown initiated...
2026-04-17 17:32:30,542 INFO ✅ Shutdown complete
INFO:     Application shutdown complete.
INFO:     Finished server process [68427]
2026-04-17 17:32:30,543 INFO Received signal 15 — uvicorn will handle graceful shutdown
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
(venv) shiina@Shiiina:/media/shiina/Shiina1/Users/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment/05-scaling-reliability/production$ sudo docker compose up --scale agent=3
WARN[0000] /media/shiina/Shiina1/Users/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment/05-scaling-reliability/production/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion 
WARN[0000] Found orphan containers ([production-qdrant-1]) for this project. If you removed or renamed this service in your compose file, you can run this command with the --remove-orphans flag to clean it up. 
[+] up 5/5
 ✔ Container production-redis-1 Running                            0.0s
 ✔ Container production-agent-1 Running                            0.0s
 ✔ Container production-agent-2 Running                            0.0s
 ✔ Container production-agent-3 Running                            0.0s
 ✔ Container production-nginx-1 Running                            0.0s
Attaching to agent-1, agent-2, agent-3, nginx-1, redis-1
Container production-redis-1 Waiting 
Container production-redis-1 Healthy 
agent-1  | INFO:     127.0.0.1:32806 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:32810 - "GET /health HTTP/1.1" 200 OK
agent-3  | INFO:     127.0.0.1:32812 - "GET /health HTTP/1.1" 200 OK
agent-1  | INFO:     127.0.0.1:36456 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:36468 - "GET /health HTTP/1.1" 200 OK
agent-3  | INFO:     127.0.0.1:36482 - "GET /health HTTP/1.1" 200 OK
agent-1  | INFO:     127.0.0.1:59732 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:59738 - "GET /health HTTP/1.1" 200 OK
agent-3  | INFO:     127.0.0.1:59740 - "GET /health HTTP/1.1" 200 OK
agent-1  | INFO:     127.0.0.1:43554 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:43560 - "GET /health HTTP/1.1" 200 OK
agent-3  | INFO:     127.0.0.1:43566 - "GET /health HTTP/1.1" 200 OK
agent-1  | INFO:     127.0.0.1:49680 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:49684 - "GET /health HTTP/1.1" 200 OK
agent-3  | INFO:     127.0.0.1:49698 - "GET /health HTTP/1.1" 200 OK
agent-1  | INFO:     127.0.0.1:52114 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:52124 - "GET /health HTTP/1.1" 200 OK
agent-3  | INFO:     127.0.0.1:52126 - "GET /health HTTP/1.1" 200 OK
agent-1  | INFO:     127.0.0.1:42964 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:42980 - "GET /health HTTP/1.1" 200 OK
agent-3  | INFO:     127.0.0.1:42984 - "GET /health HTTP/1.1" 200 OK
agent-1  | INFO:     127.0.0.1:56650 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:56656 - "GET /health HTTP/1.1" 200 OK
agent-3  | INFO:     127.0.0.1:56666 - "GET /health HTTP/1.1" 200 OK
agent-1  | INFO:     127.0.0.1:34476 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:34480 - "GET /health HTTP/1.1" 200 OK
agent-3  | INFO:     127.0.0.1:34484 - "GET /health HTTP/1.1" 200 OK
agent-3  | INFO:     172.19.0.6:49818 - "GET /health HTTP/1.1" 200 OK
agent-1  | INFO:     172.19.0.6:51640 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     172.19.0.6:43806 - "GET /health HTTP/1.1" 200 OK
agent-3  | INFO:     172.19.0.6:49824 - "GET /health HTTP/1.1" 200 OK
agent-1  | INFO:     172.19.0.6:51640 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     172.19.0.6:43806 - "GET /health HTTP/1.1" 200 OK
agent-3  | INFO:     172.19.0.6:49824 - "GET /health HTTP/1.1" 200 OK
agent-1  | INFO:     172.19.0.6:51640 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     172.19.0.6:43806 - "GET /health HTTP/1.1" 200 OK
agent-3  | INFO:     172.19.0.6:49824 - "GET /health HTTP/1.1" 200 OK
agent-1  | INFO:     172.19.0.6:51640 - "GET /health HTTP/1.1" 200 OK
agent-1  | INFO:     127.0.0.1:33774 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:33786 - "GET /health HTTP/1.1" 200 OK
agent-3  | INFO:     127.0.0.1:33792 - "GET /health HTTP/1.1" 200 OK
agent-1  | INFO:     127.0.0.1:40222 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:40238 - "GET /health HTTP/1.1" 200 OK
agent-3  | INFO:     127.0.0.1:40250 - "GET /health HTTP/1.1" 200 OK
agent-1  | INFO:     127.0.0.1:47542 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:47554 - "GET /health HTTP/1.1" 200 OK
agent-3  | INFO:     127.0.0.1:47558 - "GET /health HTTP/1.1" 200 OK

```

**Requests phân tán (served_by khác nhau):**
```
shiina@Shiiina:~$ for i in {1..10}; do
  curl -s http://localhost:8080/health
  echo ""
done
{"status":"ok","uptime_seconds":200.6,"version":"2.0.0","timestamp":"2026-04-17T10:39:48.299600"}
{"status":"ok","uptime_seconds":201.1,"version":"2.0.0","timestamp":"2026-04-17T10:39:48.315601"}
{"status":"ok","uptime_seconds":201.2,"version":"2.0.0","timestamp":"2026-04-17T10:39:48.324774"}
{"status":"ok","uptime_seconds":200.6,"version":"2.0.0","timestamp":"2026-04-17T10:39:48.340030"}
{"status":"ok","uptime_seconds":201.1,"version":"2.0.0","timestamp":"2026-04-17T10:39:48.348565"}
{"status":"ok","uptime_seconds":201.2,"version":"2.0.0","timestamp":"2026-04-17T10:39:48.356216"}
{"status":"ok","uptime_seconds":200.6,"version":"2.0.0","timestamp":"2026-04-17T10:39:48.364475"}
{"status":"ok","uptime_seconds":201.1,"version":"2.0.0","timestamp":"2026-04-17T10:39:48.373053"}
{"status":"ok","uptime_seconds":201.2,"version":"2.0.0","timestamp":"2026-04-17T10:39:48.386943"}
{"status":"ok","uptime_seconds":200.7,"version":"2.0.0","timestamp":"2026-04-17T10:39:48.398700"}
shiina@Shiiina:~$ 

```

### Exercise 5.5: Stateless test — output

```
shiina@Shiiina:/media/shiina/Shiina1/Documents and Settings/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment/05-scaling-reliability/production$ python3 test_stateless.py 
============================================================
Stateless Scaling Demo
============================================================

Session ID: 88f6d181-04e2-4bb9-b411-7853518d0a99

Request 1: [instance-dfeb45]
  Q: What is Docker?
  A: Container là cách đóng gói app để chạy ở mọi nơi. Build once, run anywhere!...

Request 2: [instance-05fd78]
  Q: Why do we need containers?
  A: Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận....

Request 3: [instance-43d2ed]
  Q: What is Kubernetes?
  A: Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận....

Request 4: [instance-dfeb45]
  Q: How does load balancing work?
  A: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé....

Request 5: [instance-05fd78]
  Q: What is Redis used for?
  A: Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ O...

------------------------------------------------------------
Total requests: 5
Instances used: {'instance-dfeb45', 'instance-05fd78', 'instance-43d2ed'}
✅ All requests served despite different instances!

--- Conversation History ---
Total messages: 10
  [user]: What is Docker?...
  [assistant]: Container là cách đóng gói app để chạy ở mọi nơi. Build once...
  [user]: Why do we need containers?...
  [assistant]: Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã đư...
  [user]: What is Kubernetes?...
  [assistant]: Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã đư...
  [user]: How does load balancing work?...
  [assistant]: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đ...
  [user]: What is Redis used for?...
  [assistant]: Đây là câu trả lời từ AI agent (mock). Trong production, đây...

✅ Session history preserved across all instances via Redis!
shiina@Shiiina:/media/shiina/Shiina1/Documents and Settings/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment/05-scaling-reliability/production$ 
```
