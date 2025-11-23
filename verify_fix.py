import sys
import os

# Add src to path
sys.path.append(os.getcwd())

from src.agent import ensure_gemini

try:
    print("Initializing model...")
    model = ensure_gemini()
    print(f"Model initialized: {model.model_name}")
    
    print("Generating content...")
    response = model.generate_content("Hello, are you working?")
    print(f"Response received: {response.text[:50]}...")
    print("SUCCESS")
except Exception as e:
    print(f"FAILURE: {e}")
