"""Vector Memory Manager using Pinecone SDK and Google Generative AI Embeddings."""

import os
import json
import uuid
import logging
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

logger = logging.getLogger("memory.vector_store")

# Pinecone index dimension (must match your Pinecone index configuration)
EMBEDDING_DIMENSION = 768


class VectorMemoryManager:
    """Manages task vector memory with Pinecone SDK and Google Embeddings."""

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "ai-ops-memory")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        
        self.index = None
        self._genai_configured = False
        
        self._initialize_store()

    def _initialize_store(self):
        """Initialize Pinecone client and Google genai SDK."""
        if not self.api_key:
            logger.warning("PINECONE_API_KEY not set - Vector memory features disabled")
            return
            
        if not self.gemini_key:
            logger.warning("GEMINI_API_KEY not set - Google embeddings disabled")
            return

        try:
            from pinecone import Pinecone
            import google.generativeai as genai

            # Configure Google Generative AI SDK for embeddings
            genai.configure(api_key=self.gemini_key)
            self._genai_configured = True

            # Initialize direct Pinecone client & target index
            pc = Pinecone(api_key=self.api_key)
            self.index = pc.Index(self.index_name)
            
            logger.info(f"Successfully connected to Pinecone index '{self.index_name}'")

        except Exception as e:
            logger.error(f"Failed to initialize Pinecone vector store: {str(e)}")
            self.index = None

    def _get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector using Google genai SDK directly.
        Uses models/gemini-embedding-001 with output_dimensionality=768 to match Pinecone index.
        """
        import google.generativeai as genai
        
        if not self._genai_configured:
            genai.configure(api_key=self.gemini_key)
            self._genai_configured = True

        response = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text,
            output_dimensionality=EMBEDDING_DIMENSION
        )
        
        embedding = response["embedding"]
        logger.info(f"Generated {len(embedding)}-dim embedding via models/gemini-embedding-001")
        return embedding

    def search_similar_tasks(self, user_task: str, k: int = 2) -> List[Dict[str, Any]]:
        """
        Query Pinecone for past tasks similar to the current user task.
        """
        if not self.index or not self._genai_configured:
            logger.warning("Vector memory store not active. Returning empty memories.")
            return []

        try:
            logger.info(f"Querying vector DB for similar tasks: '{user_task}'")
            
            query_vector = self._get_embedding(user_task)

            response = self.index.query(
                vector=query_vector,
                top_k=k,
                include_metadata=True
            )

            memories = []
            matches = response.get("matches", []) if isinstance(response, dict) else getattr(response, "matches", [])
            
            for match in matches:
                metadata = match.get("metadata", {}) if isinstance(match, dict) else getattr(match, "metadata", {})
                score = match.get("score", 0.0) if isinstance(match, dict) else getattr(match, "score", 0.0)
                
                plan_json = metadata.get("plan_json", "{}")
                try:
                    plan = json.loads(plan_json) if isinstance(plan_json, str) else plan_json
                except Exception:
                    plan = {}

                memories.append({
                    "task": metadata.get("text", user_task),
                    "score": float(score),
                    "task_summary": metadata.get("task_summary", ""),
                    "plan": plan,
                    "saved_at": metadata.get("saved_at", "")
                })

            logger.info(f"Retrieved {len(memories)} past memory matches from Pinecone")
            return memories

        except Exception as e:
            logger.error(f"Error querying vector memory: {str(e)}")
            return []

    def save_successful_task(self, user_task: str, plan: Dict[str, Any], verification: Dict[str, Any]) -> bool:
        """
        Save a successful task execution plan and verification outcome to Pinecone.
        """
        if not self.index or not self._genai_configured:
            logger.warning("Vector memory store not active. Cannot save task.")
            return False

        try:
            task_summary = plan.get("task_summary", user_task)
            plan_str = json.dumps(plan)
            verification_str = json.dumps(verification)
            saved_at = datetime.utcnow().isoformat() + "Z"
            doc_id = str(uuid.uuid4())

            # Generate 768-dim embedding via Google genai SDK
            embedding_vector = self._get_embedding(user_task)

            metadata = {
                "text": user_task,
                "task_summary": task_summary,
                "plan_json": plan_str,
                "verification_json": verification_str,
                "saved_at": saved_at
            }

            logger.info(f"Upserting vector {doc_id} to Pinecone index '{self.index_name}'...")
            
            upsert_res = self.index.upsert(
                vectors=[{
                    "id": doc_id,
                    "values": embedding_vector,
                    "metadata": metadata
                }]
            )
            
            logger.info(f"Task successfully saved to Pinecone vector memory! Response: {upsert_res}")
            return True

        except Exception as e:
            logger.error(f"Failed to save task to Pinecone: {str(e)}")
            return False
