"""List available Google Generative AI models to find correct embedding model."""
import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("=== Available Embedding Models ===")
for m in genai.list_models():
    if "embed" in m.name.lower() or "embedding" in m.name.lower():
        print(f"  Name: {m.name}")
        print(f"  Supported methods: {m.supported_generation_methods}")
        print()

print("\n=== ALL Available Models ===")
for m in genai.list_models():
    print(f"  {m.name}  ->  methods: {m.supported_generation_methods}")
