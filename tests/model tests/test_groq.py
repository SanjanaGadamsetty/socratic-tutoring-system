"""
Quick test to check Groq API connection and available models
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

print("="*60)
print("🔍 GROQ API TEST")
print("="*60)

# Check if API key exists
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ GROQ_API_KEY not found in .env file!")
    exit(1)

print(f"✅ API Key found: {api_key[:10]}...{api_key[-5:]}")

# Try to connect
try:
    client = Groq(api_key=api_key)
    print("✅ Groq client initialized")
except Exception as e:
    print(f"❌ Failed to initialize Groq client: {e}")
    exit(1)

# Try different models
models_to_test = [
    "llama-3.1-8b-instant",
    "llama3-8b-8192",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "gemma-7b-it",
]

print("\n" + "="*60)
print("🧪 TESTING MODELS")
print("="*60)

for model in models_to_test:
    print(f"\nTrying {model}...")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say 'hello' in one word"}],
            max_tokens=10
        )
        result = response.choices[0].message.content
        print(f"✅ {model} WORKS! Response: {result}")
        print(f"   👉 USE THIS MODEL!")
        break
    except Exception as e:
        print(f"❌ {model} failed: {str(e)[:100]}")

print("\n" + "="*60)
print("Done!")
print("="*60)
