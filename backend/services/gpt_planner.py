from google.generativeai import configure, GenerativeModel
import os

configure(api_key=os.getenv("GEMINI_API_KEY"))
model = GenerativeModel("gemini-1.5-flash")

def generate_with_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text.strip()

