import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams, Filter, FieldCondition, MatchValue
from feast import FeatureStore

class HybridMemoryAgent:
    """AI Assistant Memory POC.
    Combines Episodic Memory (Qdrant) and User Profile (Feast).
    """

    def __init__(self, user_id: str = "u_001"):
        self.user_id = user_id
        self.repo_root = Path(__file__).resolve().parent.parent
        self.feast_dir = self.repo_root / "app" / "feast_repo"
        
        # 1. Initialize Embedder (multilingual friendly for Vietnamese)
        # Using the same model as the lab for consistency
        self.embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        
        # 2. Initialize Qdrant (Episodic Memory)
        qdrant_mode = os.getenv("QDRANT_MODE", "memory")
        if qdrant_mode == "server":
            self.q_client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
        else:
            self.q_client = QdrantClient(":memory:")
            
        self.collection_name = "personal_memory"
        
        # Recreate collection if it doesn't exist
        collections = self.q_client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            self.q_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )

        # 3. Initialize Feast (Feature Store)
        self.fs = FeatureStore(repo_path=str(self.feast_dir))
        
        # Request features from NB4
        self.request_features = [
            "user_profile_features:reading_speed_wpm",
            "user_profile_features:preferred_language",
            "user_profile_features:topic_affinity",
            "query_velocity_features:queries_last_hour",
        ]

    def remember(self, text: str) -> None:
        """Add a new episodic memory."""
        if not text.strip():
            return

        # In a real system, we'd chunk here. For POC, we treat each call as one memory.
        vector = list(self.embedder.embed([text]))[0].tolist()
        
        point_id = int(time.time() * 1000) # Simple ms-based ID
        self.q_client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "user_id": self.user_id,
                        "text": text,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            ]
        )

    def recall(self, query: str) -> str:
        """Retrieve memories + profile features to build context."""
        # 1. Get User Profile from Feast
        try:
            profile = self.fs.get_online_features(
                features=self.request_features,
                entity_rows=[{"user_id": self.user_id}],
            ).to_dict()
            
            # Extract values (Feast returns lists)
            speed = profile.get("reading_speed_wpm", [0])[0]
            lang = profile.get("preferred_language", ["unknown"])[0]
            affinity = profile.get("topic_affinity", ["none"])[0]
            q_velocity = profile.get("queries_last_hour", [0])[0]
        except Exception as e:
            # Fallback if Feast is not materialized
            speed, lang, affinity, q_velocity = "N/A", "N/A", "N/A", "N/A"

        # 2. Search Episodic Memory in Qdrant
        q_vec = list(self.embedder.embed([query]))[0].tolist()
        hits = self.q_client.query_points(
            collection_name=self.collection_name,
            query=q_vec,
            query_filter=Filter(
                must=[FieldCondition(key="user_id", match=MatchValue(value=self.user_id))]
            ),
            limit=3
        ).points
        
        memories = [h.payload["text"] for h in hits]
        
        # 3. Assemble Context (Prompt Engineering)
        context = f"--- USER PROFILE ---\n"
        context += f"User: {self.user_id} | Prefers: {lang} | Topic Affinity: {affinity}\n"
        context += f"Reading Speed: {speed} wpm | Activity (last hour): {q_velocity} queries\n\n"
        
        context += f"--- RELEVANT MEMORIES ---\n"
        if memories:
            for i, m in enumerate(memories, 1):
                context += f"{i}. {m}\n"
        else:
            context += "No relevant memories found.\n"
            
        return context
