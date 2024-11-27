import os
from io import BytesIO
import cloudflare
from PIL import Image
import gradio as gr
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path(__file__).resolve().parent.parent / '.env'

API_TOKEN = os.getenv('CF_API_TOKEN')
# set account id and model name
ACCOUNT_ID = os.getenv('CF_ACCOUNT_ID')

def img2img_image(image, prompt, negative_prompt, strength, guidance, nums_step):
    print("running img2img...")
    client = cloudflare.Cloudflare(api_token=API_TOKEN)
    try:
        data = client.workers.ai.with_raw_response.run(
            model_name="@cf/runwayml/stable-diffusion-v1-5-img2img",
            account_id=ACCOUNT_ID,
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=image,
            strength=strength,
            guidance=guidance,
            num_steps=nums_step,
        )
        
        data = data.read()

        image = Image.open(BytesIO(data))
        # random uuid filename
        imagename = os.path.join("outputs", f"{os.urandom(16).hex()}.webp")

        # save image in data folder
        image.save(imagename)

        return image

    except Exception as e:
        raise gr.Error(f'发生错误，请稍后重试。故障报告：{str(e)}')