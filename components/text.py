import os
from cloudflare import Cloudflare
import gradio as gr
import asyncio
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path(__file__).resolve().parent.parent / '.env'

ACCOUNT_ID = "71b0dc84e2b478d2f6993300deb55adc"
API_TOKEN = "02mVybqSMCIhD9QHvUdjZXisxlDsDu1QDupHzPTM"

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
