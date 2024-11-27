import os
from cloudflare import Cloudflare
import gradio as gr
import asyncio
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path(__file__).resolve().parent.parent / '.env'

API_TOKEN = os.getenv('CF_API_TOKEN')
# set account id and model name
ACCOUNT_ID = os.getenv('CF_ACCOUNT_ID')

async def generate_text(prompt, system_prompt, model):
    client = Cloudflare(api_token=API_TOKEN)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
      ]
    try:
        result = client.workers.ai.run(
            account_id=ACCOUNT_ID,
            model_name=model,
            messages=messages,
        )

        print(f'response: {result["response"]}')

        return result["response"]

    except Exception as e:
        raise gr.Error(f'Errors, try again later. Reports：{str(e)}')