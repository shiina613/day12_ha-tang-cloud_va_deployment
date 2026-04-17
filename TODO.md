# TODO — Day 12 Lab (Deadline: 17/4/2026)
> Làm theo thứ tự từ trên xuống. Tick [ ] khi xong từng bước.
> Sau mỗi phần: ghi kết quả vào MISSION_ANSWERS.md rồi commit.

---

## PHẦN 1 — Bài tập Part 1-5 (40 điểm)

### PART 1: Localhost vs Production (8đ)

**Bước 1.1 — Chạy develop version**
```bash
cd 01-localhost-vs-production/develop
pip install -r requirements.txt
python app.py
```
Mở terminal khác:
```bash
curl "http://localhost:8000/ask?question=Hello" -X POST
```
- [ ] Thấy response → chụp màn hình hoặc copy output

**Bước 1.2 — Tìm anti-patterns**

Mở file `01-localhost-vs-production/develop/app.py`, tìm và ghi vào `MISSION_ANSWERS.md` mục `Exercise 1.1`:
- [ ] `OPENAI_API_KEY = "sk-hardcoded..."` → hardcode secret
- [ ] `DATABASE_URL = "postgresql://admin:password123..."` → hardcode password
- [ ] Không có `/health` endpoint
- [ ] `port=8000` cứng, không đọc từ env var
- [ ] `host="localhost"` → không nhận traffic từ ngoài
- [ ] `reload=True` và `DEBUG = True` hardcode
- [ ] Dùng `print()` thay vì logging
- [ ] `print(f"[DEBUG] Using key: {OPENAI_API_KEY}")` → log ra secret

**Bước 1.3 — Chạy production version**
```bash
cd ../production
cp .env.example .env
pip install -r requirements.txt
python app.py
```
Test:
```bash
curl http://localhost:8000/health
curl "http://localhost:8000/ask" -X POST -H "Content-Type: application/json" -d '{"question":"Hello"}'
```
- [ ] Thấy response từ production version

**Bước 1.4 — Điền bảng so sánh vào MISSION_ANSWERS.md**
- [ ] Điền cột "Develop" và "Production" trong bảng Exercise 1.3
- [ ] Paste output của 2 lần test vào phần Exercise 1.2

---

### PART 2: Docker (8đ)

**Bước 2.1 — Trả lời câu hỏi Dockerfile**

Mở `02-docker/develop/Dockerfile`, điền vào `MISSION_ANSWERS.md` mục Exercise 2.1:
- [ ] Base image: `python:3.11`
- [ ] Working directory: `/app`
- [ ] Tại sao copy requirements trước: Docker layer cache
- [ ] CMD vs ENTRYPOINT: CMD có thể override, ENTRYPOINT thì không

**Bước 2.2 — Build develop image**

> Chạy từ ROOT folder của project!
```bash
cd /media/shiina/Shiina1/Users/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment

docker build -f 02-docker/develop/Dockerfile -t my-agent:develop .
docker run -p 8000:8000 my-agent:develop
```
Test:
```bash
curl "http://localhost:8000/ask?question=Hello" -X POST
```
Xem image size:
```bash
docker images my-agent:develop
```
- [ ] Ghi image size vào MISSION_ANSWERS.md mục Exercise 2.3

**Bước 2.3 — Build production image (multi-stage)**
```bash
cd 02-docker/production
docker build -t my-agent:production .
docker images | grep my-agent
```
- [ ] So sánh 2 image size, ghi vào MISSION_ANSWERS.md
- [ ] Giải thích tại sao production nhỏ hơn

**Bước 2.4 — Chạy Docker Compose**
```bash
cd 02-docker/production
docker compose up
```
Test:
```bash
curl http://localhost/health
curl http://localhost/ask -X POST -H "Content-Type: application/json" -d '{"question":"test"}'
```
- [ ] Vẽ architecture diagram vào MISSION_ANSWERS.md (Client → Nginx → Agent → Redis)
- [ ] Ghi services nào được start

---

### PART 3: Cloud Deployment (8đ)

**Bước 3.1 — Deploy lên Railway**
```bash
cd 03-cloud-deployment/railway

# Cài Railway CLI nếu chưa có
npm i -g @railway/cli

railway login
railway init
railway variables set PORT=8000
railway variables set AGENT_API_KEY=my-secret-key-123
railway up
railway domain
```
Test public URL:
```bash
curl https://YOUR-APP.railway.app/health
curl "https://YOUR-APP.railway.app/ask?question=Hello" -X POST
```
- [ ] Điền URL vào MISSION_ANSWERS.md mục Exercise 3.1
- [ ] Chụp màn hình Railway dashboard → lưu vào `screenshots/dashboard.png`
- [ ] Chụp màn hình kết quả test → lưu vào `screenshots/test.png`
- [ ] Điền URL vào `DEPLOYMENT.md`

**Bước 3.2 — So sánh config files**

Mở `03-cloud-deployment/railway/railway.toml` và `03-cloud-deployment/render/render.yaml`:
- [ ] Điền bảng so sánh vào MISSION_ANSWERS.md mục Exercise 3.2

---

### PART 4: API Security (8đ)

**Bước 4.1 — Test API key auth**
```bash
cd 04-api-gateway/develop
pip install -r requirements.txt
AGENT_API_KEY=my-secret-key python app.py
```
Test không có key (phải ra 401):
```bash
curl http://localhost:8000/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'
```
Test có key (phải ra 200):
```bash
curl http://localhost:8000/ask -X POST \
  -H "X-API-Key: my-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'
```
- [ ] Paste cả 2 output vào MISSION_ANSWERS.md mục Exercise 4.1

**Bước 4.2 — Test JWT**
```bash
cd ../production
pip install -r requirements.txt
python app.py
```
Lấy token:
```bash
curl http://localhost:8000/auth/token -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"demo123"}'
```
Dùng token:
```bash
TOKEN="paste-token-here"
curl http://localhost:8000/ask -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"Explain JWT"}'
```
- [ ] Paste token và response vào MISSION_ANSWERS.md mục Exercise 4.2

**Bước 4.3 — Test rate limiting**
```bash
for i in {1..20}; do
  curl http://localhost:8000/ask -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"question\":\"Test $i\"}"
  echo ""
done
```
- [ ] Paste output (đặc biệt phần 429) vào MISSION_ANSWERS.md mục Exercise 4.3

**Bước 4.4 — Cost guard**
- [ ] Đọc `04-api-gateway/production/cost_guard.py` để hiểu logic
- [ ] Giải thích cách hoạt động trong MISSION_ANSWERS.md mục Exercise 4.4

---

### PART 5: Scaling & Reliability (8đ)

**Bước 5.1 — Health checks**
```bash
cd 05-scaling-reliability/develop
pip install -r requirements.txt
python app.py
```
Test:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```
- [ ] Paste output vào MISSION_ANSWERS.md mục Exercise 5.1

**Bước 5.2 — Graceful shutdown**
```bash
# Terminal 1: chạy app
python app.py

# Terminal 2: lấy PID và gửi SIGTERM
ps aux | grep app.py
kill -TERM <PID>
```
- [ ] Quan sát log "Graceful shutdown" trong Terminal 1
- [ ] Paste log vào MISSION_ANSWERS.md mục Exercise 5.2

**Bước 5.3 — Stateless design**

Mở `05-scaling-reliability/production/app.py`:
- [ ] Tìm hàm `save_session()` và `load_session()` — đây là stateless pattern
- [ ] Giải thích sự khác biệt memory vs Redis trong MISSION_ANSWERS.md

**Bước 5.4 — Load balancing**
```bash
cd 05-scaling-reliability/production
docker compose up --scale agent=3
```
Test:
```bash
for i in {1..10}; do
  curl http://localhost/health
  echo ""
done
```
- [ ] Quan sát `served_by` khác nhau giữa các request (instance-xxx)
- [ ] Paste output vào MISSION_ANSWERS.md

**Bước 5.5 — Test stateless**
```bash
python test_stateless.py
```
- [ ] Paste kết quả vào MISSION_ANSWERS.md

---

## PHẦN 2 — Final Project Part 6 (60 điểm)

> Tham khảo `06-lab-complete/` để hiểu cấu trúc, nhưng tự viết code.

**Bước 6.1 — Tạo folder project**
```bash
mkdir my-production-agent
cd my-production-agent
mkdir -p app utils screenshots
```

**Bước 6.2 — Copy mock LLM (được phép dùng)**
```bash
cp ../utils/mock_llm.py utils/
```

**Bước 6.3 — Viết `app/config.py`**

Tham khảo `06-lab-complete/app/config.py`. Cần có:
- [ ] `PORT`, `HOST`, `ENVIRONMENT`, `DEBUG`
- [ ] `AGENT_API_KEY`
- [ ] `RATE_LIMIT_PER_MINUTE` (mặc định 10)
- [ ] `DAILY_BUDGET_USD`
- [ ] `REDIS_URL`
- [ ] Hàm `validate()` — raise lỗi nếu thiếu key trong production

**Bước 6.4 — Viết `app/main.py`**

Tham khảo `06-lab-complete/app/main.py`. Cần có:
- [ ] `POST /ask` — nhận JSON body `{"question": "..."}`, yêu cầu `X-API-Key`
- [ ] `GET /health` — trả `{"status": "ok", ...}`
- [ ] `GET /ready` — trả 200 hoặc 503
- [ ] API key authentication (header `X-API-Key`)
- [ ] Rate limiting: 10 req/phút per key
- [ ] Cost guard: dừng khi vượt budget
- [ ] Graceful shutdown: `signal.signal(signal.SIGTERM, handler)`
- [ ] JSON structured logging
- [ ] Security headers middleware

**Bước 6.5 — Viết `Dockerfile`**

Tham khảo `06-lab-complete/Dockerfile`. Cần có:
- [ ] Multi-stage: `FROM python:3.11-slim AS builder` + `FROM python:3.11-slim AS runtime`
- [ ] Non-root user: `RUN useradd -m appuser` + `USER appuser`
- [ ] `HEALTHCHECK CMD curl -f http://localhost:8000/health`
- [ ] Dùng `python:3.11-slim` (không phải full)

**Bước 6.6 — Viết `docker-compose.yml`**

Cần có:
- [ ] Service `agent` (build từ Dockerfile)
- [ ] Service `redis` (image: redis:7-alpine)
- [ ] Environment variables từ `.env` file
- [ ] Port mapping `80:8000` hoặc `8000:8000`

**Bước 6.7 — Viết các file còn lại**
- [ ] `requirements.txt` — fastapi, uvicorn, pydantic-settings, redis
- [ ] `.env.example` — PORT, AGENT_API_KEY, REDIS_URL, LOG_LEVEL, DAILY_BUDGET_USD
- [ ] `.dockerignore` — .env, __pycache__, .git, *.pyc
- [ ] `railway.toml` hoặc `render.yaml`

**Bước 6.8 — Test local**
```bash
cp .env.example .env
# Sửa .env: đặt AGENT_API_KEY=test-key-123

docker compose up

# Test health
curl http://localhost:8000/health

# Test auth (không key → 401)
curl http://localhost:8000/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'

# Test auth (có key → 200)
curl http://localhost:8000/ask -X POST \
  -H "X-API-Key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'

# Test rate limit (gọi 15 lần → 429)
for i in {1..15}; do
  curl http://localhost:8000/ask -X POST \
    -H "X-API-Key: test-key-123" \
    -H "Content-Type: application/json" \
    -d '{"question":"test"}'
  echo ""
done
```
- [ ] Tất cả test pass

**Bước 6.9 — Chạy production readiness check**
```bash
cd ..
python 06-lab-complete/check_production_ready.py
```
- [ ] Đạt 100% (hoặc fix các ❌ còn lại)

**Bước 6.10 — Deploy lên Railway**
```bash
cd my-production-agent
railway login
railway init
railway variables set AGENT_API_KEY=your-secret-key
railway variables set REDIS_URL=redis://...   # Railway cung cấp Redis addon
railway up
railway domain
```
- [ ] Có public URL hoạt động
- [ ] Test public URL từ điện thoại hoặc thiết bị khác
- [ ] Điền URL vào `DEPLOYMENT.md`
- [ ] Chụp màn hình dashboard → `screenshots/dashboard.png`

---

## PHẦN 3 — Nộp bài

- [ ] Điền tên và MSSV vào đầu `MISSION_ANSWERS.md`
- [ ] Điền tất cả `[Paste output here]` trong `MISSION_ANSWERS.md`
- [ ] Điền URL thật vào `DEPLOYMENT.md`
- [ ] Có đủ 3 screenshots trong `screenshots/`
- [ ] Kiểm tra `.env` KHÔNG có trong repo: `git status` không thấy `.env`
- [ ] Kiểm tra không có secret trong code: `grep -r "sk-" app/`
- [ ] Repo là public trên GitHub

Commit và push tất cả:
```bash
cd /media/shiina/Shiina1/Users/quang/Documents/AI20K26/assignments/day12_ha-tang-cloud_va_deployment
git add .
git commit -m "complete day12 lab submission"
git push origin main
```

Nộp link: `https://github.com/shiina613/day12_ha-tang-cloud_va_deployment`

---

## Thứ tự ưu tiên nếu hết thời gian

1. Part 6 (60đ) — quan trọng nhất
2. Part 1 + Part 2 (16đ) — dễ nhất
3. Part 3 deployment (8đ) — cần Railway
4. Part 4 + Part 5 (16đ) — chạy test và paste output
