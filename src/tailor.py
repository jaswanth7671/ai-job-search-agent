import os
from typing import Dict

import google.generativeai as genai

BASE_RESUME = """Jaswanth Produturu — AI Engineer
Skills: Python, TensorFlow, PyTorch, MLflow, Docker, Kubernetes, SQL, AWS/GCP
Projects: LLM/RAG prototypes, prompt engineering, evaluation, basic MLOps workflows
"""

def tailor_application(job: Dict) -> Dict:
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()

    if not api_key:
        return {
            "resume_md": "⚠️ GOOGLE_API_KEY is not set. Add it in Hugging Face → Settings → Variables and secrets.",
            "cover_letter_md": "",
            "prompt": ""
        }

    genai.configure(api_key=api_key)

    prompt = f"""
You are generating job-specific application docs.

JOB:
Title: {job.get("title")}
Company: {job.get("company")}
Location: {job.get("location")}
Skills mentioned: {job.get("skills")}
Matched skills: {job.get("matched_skills")}
URL: {job.get("url")}

BASE RESUME:
{BASE_RESUME}

TASK:
1) Tailored RESUME in Markdown (1 page).
2) Tailored COVER LETTER in Markdown (250–350 words).
Do NOT invent employers/degrees/certs.

Return strictly:

## RESUME
...

## COVER_LETTER
...
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 1200
            }
        )
        text = resp.text or ""
    except Exception as e:
        return {
            "resume_md": f"⚠️ Gemini error: {str(e)}",
            "cover_letter_md": "",
            "prompt": prompt
        }

    resume_md, cover_md = "", ""
    if "## COVER_LETTER" in text:
        parts = text.split("## COVER_LETTER", 1)
        resume_md = parts[0].replace("## RESUME", "").strip()
        cover_md = parts[1].strip()
    else:
        resume_md = text.strip()

    return {"resume_md": resume_md, "cover_letter_md": cover_md, "prompt": prompt}
