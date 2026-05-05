import sys
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bonus.agent import HybridMemoryAgent

def test_bonus():
    print("🚀 Starting Bonus Challenge Demo...")
    agent = HybridMemoryAgent(user_id="u_001")

    # 1. Remember some episodic memories
    print("\n--- 1. Remembering events ---")
    memories = [
        "Tôi đã tham gia khóa học AICB Ngày 19 về Vector Store và Feature Store.",
        "Tôi thích sử dụng Qdrant vì nó hỗ trợ in-memory mode rất tiện lợi.",
        "Kế hoạch tuần tới là tìm hiểu sâu hơn về RRF và cách gộp kết quả tìm kiếm.",
        "Ghi chú: Kubernetes là một hệ thống điều phối container mạnh mẽ.",
        "Dự án sắp tới sẽ sử dụng FastAPI làm backend."
    ]
    for m in memories:
        agent.remember(m)
        print(f"  Saved: {m[:40]}...")

    # 2. Demo Queries
    print("\n--- 2. Recall Queries ---")
    queries = [
        "Tôi đã đọc gì về Kubernetes?",
        "Recommend đọc gì tiếp (dựa trên topic_affinity)",
        "Tôi đang quan tâm gì gần đây? (dựa trên queries_last_hour)",
        "Tài liệu về hệ thống điều phối container?",
        "Tóm tắt về cloud và AI cho tôi"
    ]

    for i, q in enumerate(queries, 1):
        print(f"\nQ{i}: {q}")
        context = agent.recall(q)
        print(f"Assembled Context:\n{context}")

if __name__ == "__main__":
    try:
        test_bonus()
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        sys.exit(1)
