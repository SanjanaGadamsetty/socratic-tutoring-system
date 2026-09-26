"""
Test which chat models work for our tutoring agent
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

# Test the chat-capable models from your list
chat_models = [
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
    "canopylabs/orpheus-v1-english",
]

print("="*60)
print("🧪 TESTING CHAT MODELS")
print("="*60)

for model in chat_models:
    print(f"\nTrying {model}...")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "What is 2+2? Answer in one sentence."}
            ],
            max_tokens=50
        )
        result = response.choices[0].message.content
        print(f"✅ SUCCESS! Response: {result}")
        print(f"   👉👉👉 USE THIS MODEL: {model}")
        print()
    except Exception as e:
        print(f"❌ Failed: {str(e)[:150]}")

print("\n" + "="*60)
