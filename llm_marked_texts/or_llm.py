import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_llm_response(system_prompt, orig_text, op_text, max_tokens=300):

    client = OpenAI(
        api_key=os.getenv('OPENROUTER_APIKEY'),
        base_url="https://openrouter.ai/api/v1"
    )

    user_prompt = f"Исходный текст: {orig_text} Текст опровержение: {op_text}"

    response = client.chat.completions.create(
        model="meta-llama/llama-3.3-70b-instruct:free",
        
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.6,
        max_tokens=max_tokens
    )

    result = response.choices[0].message.content
    return result