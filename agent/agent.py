import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-pro")

def get_suggestion(insight):
    issue = insight.get("issue", "Unknown")
    value = insight.get("value", "N/A")

    prompt = f"""
    Ad Issue: {issue}
    Metric Value: {value}

    Suggest improvements.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Improve targeting or ad creative."