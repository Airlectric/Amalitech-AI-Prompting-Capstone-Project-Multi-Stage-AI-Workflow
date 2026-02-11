"""Test Gemini API connectivity and quota status."""
import os
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()

def test_gemini_api():
    """Test Gemini API with a simple prompt."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    
    if not api_key:
        print("X ERROR: No API key found!")
        print("Please set GOOGLE_API_KEY or GOOGLE_GEMINI_API_KEY in .env file")
        return False
    
    print("OK API key found: " + api_key[:10] + "...")
    
    try:
        client = genai.Client(api_key=api_key)
        print("OK Client created successfully")
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say hello and confirm you are working."
        )
        
        print("OK Response received: " + response.text[:100] + "...")
        return True
        
    except Exception as e:
        error_str = str(e)
        print("X Error: " + error_str)
        
        if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
            print("\n!! QUOTA EXHAUSTED - This is a Google API limitation, not our code issue")
            print("The solution is to use the immediate fallback to Groq API")
        elif "API_KEY" in error_str or "authentication" in error_str.lower():
            print("\nX Invalid API key - Please check your .env file")
        elif "model not found" in error_str.lower():
            print("\nX Model not available - Try gemini-1.5-flash instead")
        
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Gemini API Connection")
    print("=" * 60)
    print()
    
    success = test_gemini_api()
    
    print()
    print("=" * 60)
    if success:
        print("OK Gemini API is working!")
    else:
        print("!! Gemini API has issues (likely quota)")
    print("=" * 60)
