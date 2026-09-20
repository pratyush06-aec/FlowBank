import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from groq import Groq
from dotenv import load_dotenv

load_dotenv("backend/.env")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
models = client.models.list()
for m in models.data:
    print(m.id)
