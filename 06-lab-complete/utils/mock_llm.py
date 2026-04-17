"""
Mock LLM — fallback khi OpenAI không khả dụng.
"""
import time
import random

MOCK_RESPONSES = [
    "Xin lỗi, tôi đang chạy ở chế độ offline (mock). OpenAI API hiện không khả dụng.",
    "Mock response: Agent đang hoạt động nhưng không kết nối được OpenAI.",
    "Tôi là mock LLM. Vui lòng kiểm tra lại OPENAI_API_KEY.",
]

def ask(question: str) -> str:
    time.sleep(0.1 + random.uniform(0, 0.05))
    return random.choice(MOCK_RESPONSES)
