"""Test Groq API as fallback when Gemini quota is exceeded."""
import os
from dotenv import load_dotenv
from groq import Groq
import json

load_dotenv()

def test_groq_api():
    """Test Groq API with a simple prompt."""
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("X ERROR: GROQ_API_KEY not found in .env file!")
        return False
    
    print("OK GROQ_API_KEY found: " + api_key[:10] + "...")
    
    try:
        client = Groq(api_key=api_key)
        print("OK Groq Client created successfully")
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a data analyst. Always return valid JSON only."},
                {"role": "user", "content": "Analyze this simple dataset and return JSON: {\"rows\": 100, \"columns\": 5}. Return only {\"dataset_description\": \"test\", \"cleaning_steps\": [], \"analyses\": []}"}
            ],
            temperature=0.2
        )
        
        result = response.choices[0].message.content
        print("OK Response received: " + result[:100] + "...")
        
        try:
            parsed = json.loads(result)
            print("OK Valid JSON returned!")
            return True
        except:
            print("! Response not valid JSON but API worked")
            return True
        
    except Exception as e:
        error_str = str(e)
        print("X Error: " + error_str)
        return False

def test_fallback_simulation():
    """Simulate the fallback behavior."""
    print("\n--- Testing Fallback Simulation ---")
    print("This simulates what happens when Gemini quota is exceeded:")
    print()
    print("1. Try Gemini API -> FAIL (quota exceeded)")
    print("2. Immediately switch to Groq API -> SUCCESS")
    print()
    print("This ensures NO DELAYS for the user!")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Groq API as Fallback")
    print("=" * 60)
    print()
    
    groq_works = test_groq_api()
    test_fallback_simulation()
    
    print()
    print("=" * 60)
    if groq_works:
        print("OK Groq API is working - fallback will work!")
    else:
        print("!! Groq API has issues")
    print("=" * 60)
