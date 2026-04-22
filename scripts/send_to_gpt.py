import os
from openai import OpenAI
key = os.getenv("OPENAI_API_SECRET_KEY")

client = OpenAI(api_key=key)

def message_gpt(message: str,model: str = "gpt-5-nano") -> str:
    response = client.responses.create(
        model=model,
        input=message
    )
    return response.output_text
