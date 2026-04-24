import os
from openai import OpenAI

key = os.getenv("OPENAI_API_SECRET_KEY")
client = OpenAI(api_key=key)


def message_gpt(message: str, model: str = "gpt-5-nano") -> str:
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": message}]
    )
    return response.choices[0].message.content
