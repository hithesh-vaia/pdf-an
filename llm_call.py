from openai import OpenAI
from pydantic import BaseModel
from app_secrets import API_KEY

import os
import json

# Resolve paths relative to the script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_PATH = os.path.join(SCRIPT_DIR, "report_mock.json")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "outputs.json")

print(f"Loading report from: {REPORT_PATH}", flush=True)
with open(REPORT_PATH, "r") as f:
    data = json.load(f)


from pydantic import BaseModel

class TopicIndex(BaseModel):
    key: str
    value: int  # start line / start index

class StructuredReport(BaseModel):
    groups: list[TopicIndex]


prompt = """
You are an expert at analyzing large JSON documents and creating navigation indexes.

You will be given a JSON report.

Your task is to identify the major semantic sections and create an ordered index.

Instructions:
1. Identify only high-level topics that represent meaningful sections of the report.
2. Do NOT create duplicate, overlapping, or overly granular topics.
3. Preserve the order in which topics first appear.
4. For each topic, return:
   - topic: A concise title (2-6 words).
   - start_line: The line number where the topic first begins in the input JSON.
5. Cover the entire document.
6. Return ONLY valid JSON matching the provided schema.
7. Do NOT include explanations, markdown, comments, or additional text.

Example:

Input:
{
  "company": {...},
  "governance": {...},
  "climate": {...},
  "risk_management": {...}
}

Output:
{
  "groups": [
    {
      "topic": "Company Overview",
      "start_line": 1
    },
    {
      "topic": "Governance",
      "start_line": 15
    },
    {
      "topic": "Climate Strategy",
      "start_line": 48
    },
    {
      "topic": "Risk Management",
      "start_line": 92
    }
  ]
}

Now analyze the provided JSON report and return the index.
max 10 groups
"""

client = OpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

print("Sending API request to Gemini...", flush=True)
completion = client.beta.chat.completions.parse(
    model="gemini-2.5-flash", 
      messages=[
    {"role": "system", "content": prompt},
    {"role": "user", "content": json.dumps(data)}
  ],
  response_format=StructuredReport

    
)

print("API request successful. Parsing response...", flush=True)
parsed = completion.choices[0].message.parsed
print(f"Saving output to: {OUTPUT_PATH}", flush=True)
with open(OUTPUT_PATH, "w") as f:
    json.dump(parsed.model_dump(), f, indent=2, ensure_ascii=False)
print("Saved successfully!", flush=True)