import os
import gradio as gr
import asyncio
from io import BytesIO
import base64
import numpy as np
from PIL import Image, ImageOps
from components import generate_text, generate_image, translator, inpaint_image, img2img_image
import flet as ft

FLUX_PROMPT ="flux_prompt.md"
SD_PROMPT = "sd_prompt.md"

prompt_new = ""

CSS = """
h1 {
    margin-top: 10px
}

footer {
    visibility: hidden;
}
"""

modelMap  = {
    "Qwen1.5-0.5B": "@cf/qwen/qwen1.5-0.5b-chat",
    "Mistral-7b": "@hf/thebloke/mistral-7b-instruct-v0.1-awq",
    "m2m100": "@cf/meta/m2m100-1.2b",
    "Qwen1.5-7B": "@cf/qwen/qwen1.5-7b-chat-awq",
    "Qwen1.5-14B": "@cf/qwen/qwen1.5-14b-chat-awq",
    "Llama3.1-8B": "@cf/meta/llama-3.1-8b-instruct-fast",
    "Flux.1-Schenell": "@cf/black-forest-labs/flux-1-schnell",
    "SDXL": "@cf/stabilityai/stable-diffusion-xl-base-1.0",
    "SDXL-lightning": "@cf/bytedance/stable-diffusion-xl-lightning"
}

# Image generation tab
with open(FLUX_PROMPT, 'r') as f:
    PRESET_PROMPT = f.read()

def update_prompt(model: str):
    global PRESET_PROMPT
    if model.startswith("SD"):
        with open(SD_PROMPT, 'r') as f:
            PRESET_PROMPT = f.read()
    else:
        with open(FLUX_PROMPT, 'r') as f:
            PRESET_PROMPT = f.read()
    return gr.update(value=PRESET_PROMPT)

# image generation
async def gen(imgModel: str, function: list):
    # if 1 in the function list
    if 1 in function:
        image_task = asyncio.create_task(generate_image(str(prompt_new), modelMap[imgModel]))
        output_image = await image_task
        yield output_image
    else:
        yield None

async def op_prompt(prompt: str, system_prompt: str, translateModel:str, chatModel: str, function: list):
    global prompt_new
    prompt = translator(prompt, modelMap[translateModel])
    print(function)
    if 0 in function:
        prompt_new = await asyncio.create_task(generate_text(prompt, system_prompt, modelMap[chatModel]))
        text_new = f"Prompts Translation🐴: {prompt}\n\nOptimized Prompts🦄: {prompt_new}"
    else:
        text_new = f"Prompts Translation🐴: {prompt}"
    yield text_new

def image_to_int_array(image, format="PNG"):
    """Current Workers AI REST API consumes an array of unsigned 8 bit integers"""
    # Convert to bytes
    buffer = BytesIO()
    image.save(buffer, format=format)

    # Convert to uint8 array and ensure values are between 0-255
    uint8_array = np.frombuffer(buffer.getvalue(), dtype=np.uint8)
    # Convert to regular Python list
    return uint8_array.tolist()

# Image inpainting Tab
def is_mask_empty(image) -> bool:
    gray_img = image.convert("L")
    pixels = list(gray_img.getdata())
    return all(pixel == 0 for pixel in pixels)

def inpaintGen(
        imgMask,
        inpaint_prompt: str,
        neg_prompt: str,
        strength: float,
        guidance: float,
        num_steps: int):

    source_path = imgMask["background"]
    mask_path = imgMask["layers"][0]
    mask = Image.open(mask_path)

    if not is_mask_empty(mask) and inpaint_prompt:
        print("Mask processing")
        img = Image.open(source_path)
        img = ImageOps.contain(img, (600, 600))
        img_array = image_to_int_array(img)
        alpha_channel = mask.split()[3]
        binary_mask = alpha_channel.point(lambda p: p > 0 and 255)
        mask_array = binary_mask
        mask_array = image_to_int_array(mask_array)

        ip_image = inpaint_image(img_array, mask_array, inpaint_prompt, neg_prompt, strength, guidance, num_steps)

        return ip_image
    else:
        print("Mask is empty")
        return None

# img2img

def img2img_Gen(
        image,
        prompt: str,
        neg_prompt: str,
        strength: float,
        guidance: float,
        num_steps: int):

    if image and prompt:
        print("Image processing")
        img = Image.open(image).convert('RGB')
        img = ImageOps.contain(img, (512, 512))

        img_array = image_to_int_array(img)

        image_out = img2img_image(img_array, prompt, neg_prompt, strength, guidance, num_steps)

        return image_out
    else:
        return None

# Gradio Interface

with gr.Blocks(theme="ocean", title="ImageX By snekkenull", css=CSS) as demo:
    gr.HTML("<h1><center>ImagenX</center></h1>")
    with gr.Tab("Image generation"):
        gr.HTML("""
        <p>
            <center>
                Based on Flux.1 model, it can generate the corresponding image according to your cue words. <br> By automatically optimizing the cue words, it helps you get better generation results.
            </center>
        </p>
        """)
        prompt = gr.Textbox(label='Prompts ✏️', placeholder="A car...")
        with gr.Row():
            sendBtn = gr.Button(value="Submit", variant='primary')
            clearBtn = gr.ClearButton([prompt], value="Clear")
        gen_text = gr.Textbox(label="Procession 🦖")
        gen_img = gr.Image(type="pil", label='Generate 🎨', height=600)
        with gr.Accordion("Advanced ⚙️", open=False):
            functions = gr.CheckboxGroup(choices=["Prompts Optimizer", "Image Generator"], value=["Prompts Optimizer", "Image Generator"], type = "index", label="Enable Features"),
            translateModel = gr.Dropdown(label="Prompts-To-Eng Model", value="Mistral-7b", choices=["m2m100", "Qwen1.5-0.5B", "Mistral-7b"])
            chatModel = gr.Dropdown(label="Prompts-Optimizer Model", value="Llama3.1-8B", choices=["Qwen1.5-7B", "Qwen1.5-14B", "Llama3.1-8B"])
            imgModel = gr.Dropdown(label="Image-Generator Model", value="Flux.1-Schenell", choices=["Flux.1-Schenell", "SDXL", "SDXL-lightning"])
            system_prompt = gr.Textbox(
                value = PRESET_PROMPT,
                label = "System Prompt",
                lines = 10,
            )

        imgModel.select(update_prompt, [imgModel], [system_prompt])

        gr.on(
            triggers = [
                prompt.submit,
                sendBtn.click,
            ],
            fn = op_prompt,
            inputs = [
                prompt,
                system_prompt,
                translateModel,
                chatModel,
                functions[0]
            ],
            outputs = [gen_text]
        ).then(gen, [imgModel, functions[0]], [gen_img])
    with gr.Tab("Inpainting"):
        gr.HTML("""
        <p>
            <center>
                The image generation model based on SDXL-Inpainting allows for localized redrawing of images based on your cue words and occlusions.
            </center>
        </p>
        """)
        with gr.Row():
            with gr.Column():
                imgMask = gr.ImageMask(type="filepath", label="Upload image", layers=False, height=800)
                inpaint_prompt = gr.Textbox(label='Prompts ✏️', placeholder="A cat...")
                with gr.Row():
                    Inpaint_sendBtn = gr.Button(value="Submit", variant='primary')
                    Inpaint_clearBtn = gr.ClearButton([imgMask, inpaint_prompt], value="Clear")
            image_out = gr.Image(type="pil", label="Output", height=960)
        with gr.Accordion("Advanced ⚙️", open=False):
            neg_prompt = gr.Textbox(label="Negative Prompt", value="")
            strength = gr.Slider(label="Strength", minimum=0, maximum=1, value=1, step=0.1)
            guidance = gr.Slider(label="Guidance", minimum=1, maximum=20, value=7.5, step=0.1)
            num_steps = gr.Slider(label="Steps", minimum=1, maximum=20, value=20, step=1)

        gr.on(
            triggers = [
                inpaint_prompt.submit,
                Inpaint_sendBtn.click,
            ],
            fn = inpaintGen,
            inputs = [
                imgMask,
                inpaint_prompt,
                neg_prompt,
                strength,
                guidance,
                num_steps
            ],
            outputs = [image_out]
        )
    with gr.Tab("IMG-TO-IMG"):
        gr.HTML("""
        <p>
            <center>
                The image generation model based on SDXL-Inpainting can generate graphs based on your cue words and images.
            </center>
        </p>
        """)
        with gr.Row():
            with gr.Column():
                imgUpload = gr.Image(type="filepath", label="Upload",  height=800)
                img2img_prompt = gr.Textbox(label='Prompts ✏️', placeholder="A cat...")
                with gr.Row():
                    img2img_sendBtn = gr.Button(value="Submit", variant='primary')
                    img2img_clearBtn = gr.ClearButton([imgUpload, img2img_prompt], value="Clear")
            img2img_out = gr.Image(type="pil", label="Output", height=960)
        with gr.Accordion("Advanced ⚙️", open=False):
            img2img_neg = gr.Textbox(label="Negative Prompt", value="")
            img2img_strength = gr.Slider(label="Strength", minimum=0, maximum=1, value=1, step=0.1)
            img2img_guidance = gr.Slider(label="Guidance", minimum=1, maximum=20, value=7.5, step=0.1)
            img2img_num_steps = gr.Slider(label="Steps", minimum=1, maximum=20, value=20, step=1)

        gr.on(
            triggers = [
                img2img_prompt.submit,
                img2img_sendBtn.click,
            ],
            fn = img2img_Gen,
            inputs = [
                imgUpload,
                img2img_prompt,
                img2img_neg,
                img2img_strength,
                img2img_guidance,
                img2img_num_steps
            ],
            outputs = [img2img_out]
        )

    gr.HTML("""
    <p><a href="https://github.dev/snekkenull/ImageX"> Snekkenull </a> OpenSource</p>
    """)

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)
