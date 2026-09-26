"""
List all available Groq models
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

print("="*60)
print("📋 AVAILABLE GROQ MODELS")
print("="*60)

try:
    # List all available models
    models = client.models.list()

    print(f"\nFound {len(models.data)} models:\n")

    for model in models.data:
        print(f"✅ {model.id}")
        if hasattr(model, 'owned_by'):
            print(f"   Owner: {model.owned_by}")
        print()

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTrying alternative method...")

    # If models.list() doesn't work, try common 2026 models
    test_models = [
        "llama-3.2-1b-preview",
        "llama-3.2-3b-preview",
        "llama-3.2-11b-vision-preview",
        "llama-3.2-90b-vision-preview",
        "llama-3.3-70b-versatile",
        "llama-3.3-70b-specdec",
        "gemma2-9b-it",
        "qwen-2.5-72b-chat",
    ]

    print("\n🧪 Testing common models:")
    for model in test_models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            print(f"✅ {model} - WORKS!")
        except:
            print(f"❌ {model} - not available")

print("\n" + "="*60)
