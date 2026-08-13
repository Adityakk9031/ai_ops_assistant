"""Scratch test script to test Pinecone vector store upsert directly."""

import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_pinecone")

from memory.vector_store import VectorMemoryManager

print("Initializing VectorMemoryManager...")
vmm = VectorMemoryManager()

if not vmm.vector_store:
    print("ERROR: vector_store is None!")
else:
    print("VectorMemoryManager initialized successfully.")
    task = "Test London Weather Task"
    plan = {"task_summary": "Test London Weather", "steps": []}
    verification = {"confidence": 1.0, "issues": []}

    print(f"Calling save_successful_task for: '{task}'...")
    res = vmm.save_successful_task(task, plan, verification)
    print(f"save_successful_task result: {res}")

    print("Querying similar tasks...")
    memories = vmm.search_similar_tasks(task, k=2)
    print(f"Retrieved memories count: {len(memories)}")
    for m in memories:
        print(f" - {m}")
