from openai import OpenAI
from .app_secrets import API_KEY
client = OpenAI(
  api_key=API_KEY,
  base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

models = client.models.list()
for model in models:
  print(model.id)
