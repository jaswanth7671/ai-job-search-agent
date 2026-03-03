import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def tailor_resume(job):

    prompt = f"""
Tailor this AI Engineer resume for the job:

Title: {job.title}
Company: {job.company}
Location: {job.location}
Skills: {job.skills}

Return a short tailored resume paragraph.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )

    return response.choices[0].message.content
