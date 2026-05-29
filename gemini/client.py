import google.generativeai as genai
from pydantic import BaseModel
from config import GEMINI_API_KEY, AUDIT_MODEL, GENERATION_MODEL, GROUNDING_MODEL

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class GeminiClient:
    def __init__(self):
        self.audit_model = AUDIT_MODEL
        self.generation_model = GENERATION_MODEL
        self.grounding_model = GROUNDING_MODEL

    def generate(self, system_instruction: str, prompt: str, temperature: float = 0.4) -> str:
        model = genai.GenerativeModel(
            model_name=self.generation_model,
            system_instruction=system_instruction,
            generation_config=genai.GenerationConfig(temperature=temperature)
        )
        response = model.generate_content(prompt)
        return response.text

    def generate_structured(self, prompt: str, response_schema: type[BaseModel], system_instruction: str = "", temperature: float = 0.0) -> BaseModel | None:
        kwargs = {
            "model_name": self.audit_model,
            "generation_config": genai.GenerationConfig(
                temperature=temperature,
                response_mime_type="application/json",
                response_schema=response_schema,
            )
        }
        if system_instruction:
            kwargs["system_instruction"] = system_instruction
            
        model = genai.GenerativeModel(**kwargs)
        try:
            response = model.generate_content(prompt)
            return response_schema.model_validate_json(response.text)
        except Exception as e:
            print(f"Error generating structured output: {e}")
            return None

    def run_grounding(self, claims_prompt: str) -> dict:
        model = genai.GenerativeModel(
            model_name=self.grounding_model,
            tools=[{"google_search": {}}]
        )
        response = model.generate_content(claims_prompt)

        text_content = "".join(
            part.text for part in response.candidates[0].content.parts
            if hasattr(part, "text")
        )

        grounding_meta = None
        if hasattr(response.candidates[0], "grounding_metadata"):
            # store it as a dict or raw object
            grounding_meta = response.candidates[0].grounding_metadata

        return {
            "text_content": text_content,
            "grounding_metadata": grounding_meta
        }
