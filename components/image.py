import os
from io import BytesIO
import json
import base64
import cloudflare
from PIL import Image
import gradio as gr
import asyncio
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path(__file__).resolve().parent.parent / '.env'

# set cloudflare api
API_TOKEN = os.getenv('CF_API_TOKEN')
# set account id and model name
ACCOUNT_ID = os.getenv('CF_ACCOUNT_ID')

async def generate_image(prompt, model):
    client = cloudflare.Cloudflare(api_token=API_TOKEN)
    try:
        data = client.workers.ai.with_raw_response.run(
            model_name=model,
            account_id=ACCOUNT_ID,
            prompt=prompt,
        )

        data = data.read()

        if model == "@cf/black-forest-labs/flux-1-schnell":
            # Extract the image data from the JSON
            json_data = json.loads(data)
            image_data = json_data["result"]["image"]

            # Decode the base64-encoded image data
            image_bytes = base64.b64decode(image_data)

            # Create a PIL Image object from the decoded bytes
            image = Image.open(BytesIO(image_bytes))
        else:
            image = Image.open(BytesIO(data))
        # random uuid filename
        imagename = os.path.join("outputs", f"{os.urandom(16).hex()}.webp")

        # save image in data folder
        image.save(imagename)

        return image

    except Exception as e:
        raise gr.Error(f'Errors, try again later. Reports：{str(e)}')
