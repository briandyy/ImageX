import os
import cloudflare
import gradio as gr

API_TOKEN = os.getenv('CF_API_TOKEN')
# set account id and model name
ACCOUNT_ID = os.getenv('CF_ACCOUNT_ID')

translate_prompt = """
You are a professional translator, you can accurately translate any input content into natvie English. Your output should be only in English translation without other eplanation.
For example:
**Input** Coche de estilo ciberpunk.
**Output** A car in Cyber Punk style.
"""

def translator(prompt, translateModel):
    client = cloudflare.Cloudflare(api_token=API_TOKEN)
    if translateModel == "@cf/meta/m2m100-1.2b":
        try:
            result = client.workers.ai.run(
                account_id=ACCOUNT_ID,
                model_name=translateModel,
                text=prompt,
                target_lang='english'
            )

            print(f'response: {result["translated_text"]}')

            return result["translated_text"]

        except Exception as e:
            raise gr.Error(f'Errors, try again later. Reports：{str(e)}')
    else:
        messages = [
            {"role": "system", "content": translate_prompt},
            {"role": "user", "content": prompt}
        ]
        try:
            result = client.workers.ai.run(
            account_id=ACCOUNT_ID,
            model_name=translateModel,
            messages=messages,
            )

            print(f'response: {result["response"]}')

            return result["response"]

        except Exception as e:
            raise gr.Error(f'Errors, try again later. Reports：{str(e)}')