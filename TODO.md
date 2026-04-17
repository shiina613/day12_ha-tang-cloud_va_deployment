# TODO — Day 12 Lab (Deadline: 17/4/2026)
> Làm theo thứ tự. Tick vào [ ] khi xong.

---

## PHẦN 1 — Bài tập Part 1-5 → file `MISSION_ANSWERS.md` (40 điểm)

### Part 1: Localhost vs Production (8đ)

- [ ] Chạy `01-localhost-vs-production/develop/app.py`
  ```bash
  cd 01-localhost-vs-production/develop
  pip install -r requirements.txt
  python app.py
  # Test: curl "http://localhost:8000/ask?question=Hello" -X POST
  ```
- [ ] Liệt kê 5+ anti-patterns tìm được trong `develop/app.py` vào `MISSION_ANSWERS.md` (2đ)
- [ ] Chạy `01-localhost-vs-production/production/app.py`
  ```bash
  cd 01-localhost-vs-production/production
  cp .env.example .env
  pip install -r requirements.txt
  python app.py
  ```
- [ ] Điền bảng so sánh develop vs production vào `MISSION_ANSWERS.md` (4đ)
  - Config | Health check | Logging | Shutdown | Port | Secrets
- [ ] Ghi lại kết quả chạy thành công (screenshot hoặc paste output) (2đ)

---

### Part 2: Docker (8đ)

- [ ] Đọc `02-docker/develop/Dockerfile`, trả lời 4 câu hỏi vào `MISSION_ANSWERS.md` (2đ)
  - Base image là gì?
  - Working directory là gì?
  - Tại sao COPY requirements.txt trước?
  - CMD vs ENTRYPOINT khác nhau thế nào?
- [ ] Build và chạy container develop, ghi image size (2đ)
  ```bash
  cd 02-docker/develop
  docker build -t my-agent:develop .
  docker run -p 8000:8000 my-agent:develop
  docker images my-agent:develop
  ```
- [ ] Build container production (multi-stage), so sánh image size (2đ)
  ```bash
  cd 02-docker/production
  docker build -t my-agent:production .
  docker images | grep my-agent
  ```
- [ ] Chạy Docker Compose stack, vẽ architecture diagram vào `MISSION_ANSWERS.md` (2đ)
  ```bash
  cd 02-docker/production
  docker compose up
  curl http://localhost/health
  ```

---

### Part 3: Cloud Deployment (8đ)

- [ ] Deploy lên Railway (4đ)
  ```bash
  cd 03-cloud-deployment/railway
  npm i -g @railway/cli
  railway login
  railway init
  railway variables set PORT=8000
  railway variables set AGENT_API_KEY=my-secret-key
  railway up
  railway domain
  ```
- [ ] Test public URL hoạt động, ghi URL vào `MISSION_ANSWERS.md`
  ```bash
  curl https://your-app.railway.app/health
  ```
- [ ] So sánh `railway.toml` vs `render/render.yaml`, ghi vào `MISSION_ANSWERS.md` (3đ)
- [ ] (Bonus) Đọc `production-cloud-run/cloudbuild.yaml`, giải thích CI/CD pipeline (1đ)

---

### Part 4: API Security (8đ)

- [ ] Chạy `04-api-gateway/develop/app.py`, test có key / không có key, paste output vào `MISSION_ANSWERS.md` (2đ)
  ```bash
  cd 04-api-gateway/develop
  python app.py
  # Không key → 401
  curl http://localhost:8000/ask -X POST -H "Content-Type: application/json" -d '{"question":"Hello"}'
  # Có key → 200
  curl http://localhost:8000/ask -X POST -H "X-API-Key: secret-key-123" -H "Content-Type: application/json" -d '{"question":"Hello"}'
  ```
- [ ] Chạy JWT flow trong `04-api-gateway/production/app.py`, lấy token rồi gọi API (2đ)
  ```bash
  cd 04-api-gateway/production
  python app.py
  curl http://localhost:8000/token -X POST -H "Content-Type: application/json" -d '{"username":"admin","password":"secret"}'
  # Dùng token để gọi /ask
  ```
- [ ] Test rate limiting (gọi 20 lần, quan sát 429), paste output (2đ)
  ```bash
  for i in {1..20}; do curl http://localhost:8000/ask -X POST -H "X-API-Key: secret-key-123" -H "Content-Type: application/json" -d '{"question":"test"}'; echo ""; done
  ```
- [ ] Implement hàm `check_budget()` trong `cost_guard.py`, giải thích logic (2đ)

---

### Part 5: Scaling & Reliability (8đ)

- [ ] Implement `/health` và `/ready` endpoint trong `05-scaling-reliability/develop/app.py` (2đ)
- [ ] Implement SIGTERM graceful shutdown handler (2đ)
- [ ] Refactor code sang stateless — chuyển conversation history từ memory sang Redis (2đ)
- [ ] Chạy `docker compose up --scale agent=3`, test load balancing (1đ)
  ```bash
  cd 05-scaling-reliability/production
  docker compose up --scale agent=3
  ```
- [ ] Chạy `python test_stateless.py`, paste kết quả (1đ)

---

## PHẦN 2 — Final Project Part 6 (60 điểm)

> Build từ đầu trong folder riêng. Tham khảo `06-lab-complete/` nếu cần.

### Setup (không tính điểm riêng nhưng bắt buộc)

- [ ] Tạo folder project riêng (hoặc dùng thẳng `06-lab-complete/`)
- [ ] Tạo đủ file: `app/main.py`, `app/config.py`, `app/auth.py`, `app/rate_limiter.py`, `app/cost_guard.py`
- [ ] Tạo `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `.env.example`, `.dockerignore`
- [ ] Tạo `railway.toml` hoặc `render.yaml`

### Functionality — 20đ

- [ ] `POST /ask` trả lời câu hỏi đúng (10đ)
- [ ] Lưu và đọc conversation history từ Redis (5đ)
  - Gọi "My name is Alice" → gọi "What is my name?" → phải trả lời đúng
- [ ] Xử lý lỗi graceful — input sai trả 422 rõ ràng (5đ)

### Docker & Config — 15đ

- [ ] Dockerfile multi-stage build (`AS builder` + `AS runtime`) (5đ)
- [ ] Image size < 500 MB (3đ)
- [ ] `docker-compose.yml` có đủ `agent` + `redis` (4đ)
- [ ] Toàn bộ config đọc từ env vars, không hardcode (3đ)

### Security — 20đ

- [ ] API key authentication: không có key → 401 (5đ)
- [ ] Rate limiting: > 10 req/phút → 429 (5đ)
- [ ] Cost guard: vượt $10/tháng → 402 (5đ)
- [ ] Không có secret nào hardcode trong code (5đ)

### Reliability — 15đ

- [ ] `GET /health` trả 200 (3đ)
- [ ] `GET /ready` trả 200 khi Redis OK, 503 khi không (3đ)
- [ ] Xử lý SIGTERM graceful shutdown (4đ)
- [ ] Stateless: state lưu Redis, không lưu trong memory (5đ)

### Deployment — 10đ

- [ ] Deploy lên Railway hoặc Render (5đ)
- [ ] Có `railway.toml` hoặc `render.yaml` đúng cấu hình (3đ)
- [ ] Set đủ env vars trên platform: PORT, REDIS_URL, AGENT_API_KEY (2đ)

### Kiểm tra trước khi nộp

- [ ] Chạy `python 06-lab-complete/check_production_ready.py` → 100%
- [ ] Test public URL từ thiết bị khác

---

## PHẦN 3 — Nộp bài

- [ ] Tạo `MISSION_ANSWERS.md` với đầy đủ câu trả lời Part 1-5
- [ ] Tạo `DEPLOYMENT.md` với public URL + test commands + screenshots
- [ ] Tạo folder `screenshots/` với ảnh deployment dashboard + service running + test results
- [ ] Kiểm tra `.env` KHÔNG có trong repo (chỉ có `.env.example`)
- [ ] Kiểm tra không có secret nào trong git history
- [ ] Push lên GitHub (repo public hoặc share với giảng viên)
- [ ] Nộp link GitHub repo

---

## Tự test trước khi nộp

```bash
# 1. Health check
curl https://your-app.railway.app/health
# → {"status": "ok"}

# 2. Không có key → 401
curl https://your-app.railway.app/ask -X POST -H "Content-Type: application/json" -d '{"user_id":"test","question":"Hello"}'

# 3. Có key → 200
curl https://your-app.railway.app/ask -X POST -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" -d '{"user_id":"test","question":"Hello"}'

# 4. Rate limit → 429
for i in {1..15}; do curl -X POST https://your-app.railway.app/ask -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" -d '{"user_id":"test","question":"test"}'; done
```
