import os
from io import BytesIO
from cloudflare import Cloudflare
from PIL import Image
import gradio as gr
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path(__file__).resolve().parent.parent / '.env'

ACCOUNT_ID = "71b0dc84e2b478d2f6993300deb55adc"
API_TOKEN = "02mVybqSMCIhD9QHvUdjZXisxlDsDu1QDupHzPTM"

def inpaint_image(image, mask, prompt, negative_prompt, strength, guidance, nums_step ):
    print("running inpaint...")
    client = Cloudflare(api_token=API_TOKEN)
    try:
        data = client.workers.ai.with_raw_response.run(
            model_name="@cf/runwayml/stable-diffusion-v1-5-inpainting",
            account_id=ACCOUNT_ID,
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=image,
            mask=mask,
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
