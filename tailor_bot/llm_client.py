import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables. Please check your .env file.")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )

    def generate_tailored_content(self, prompt):
        """
        Sends the prompt to the LLM and returns the response.
        """
        try:
            response = self.client.chat.completions.create(
                model="openai/gpt-5-mini", # Using GPT-5 Mini via OpenRouter
                extra_headers={
                    "HTTP-Referer": "https://github.com/resume-tailor-bot",
                    "X-Title": "Resume Tailor Bot",
                },
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates LaTeX code for resumes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return None
