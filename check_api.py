from google import genai
import time

# Use your key
client = genai.Client(api_key="") 

print("Testing API Status...")
try:
    # Try to generate just ONE simple word
    response = client.models.generate_content(
        model='gemini-2.0-flash-lite-001',
        contents="Say 'Ready'",
    )
    print(f"✅ SUCCESS! The API replied: {response.text}")
    print("You are likely ready to run the full experiment.")
except Exception as e:
    print(f"❌ Still Waiting. Error: {e}")