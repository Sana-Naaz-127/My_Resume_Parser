import fitz
import os
import json
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def pdf_to_text(pdf_file):
    document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in document:
        text += page.get_text()
    return text

def parse_resume(text):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment")

    client = Groq(api_key=api_key)
    text = text[:5000]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""
Extract structured data from this resume.

Return ONLY valid JSON. No explanation, no markdown, no code fences.

Schema:
{{
  "name": "",
  "email": "",
  "phone": "",
  "skills": [],
  "education": [{{"degree": "", "institution": "", "year": ""}}],
  "experience": [{{"title": "", "company": "", "duration": ""}}],
  "summary": ""
}}

Resume Text:
{text}
"""
        }],
        max_tokens=1500
    )

    content = response.choices[0].message.content.strip()

    # Strip markdown code fences if model ignores instructions
    content = re.sub(r"^```(?:json)?\s*", "", content)
    content = re.sub(r"\s*```$", "", content)
    content = content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to extract JSON object if there's extra text around it
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"error": "Invalid JSON from model", "raw": content}