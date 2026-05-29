import google.generativeai as genai
import os
from dotenv import load_dotenv
from schemas.audit_schemas import RubricBootstrapSchema
from gemini.prompts import RUBRIC_BOOTSTRAP_PROMPT
from gemini.client import GeminiClient

load_dotenv()
client = GeminiClient()

print("Using audit model:", client.audit_model)

try:
    prompt = f"{RUBRIC_BOOTSTRAP_PROMPT}\n\nQuery: When was ISRO founded?"
    result = client.generate_structured(prompt, RubricBootstrapSchema)
    print("Parsed result:", result)
except Exception as e:
    print("Error:", e)
