# ImageX-CF-workers-AI-webUI

A Gradio webui for Cloudflare workers AI Text-to-Image.

Use Cloudflare text-generation model to optimze the prompt and text-to-image model to generate images.

## Preview

![alt text](<Screenshot.png>)

## Use

Clone the repo to your disk, change the .env.example to .env, and set the right values.Run the commands in directory:

<code>

python -m venv venv

source ./venv/bin/activate

python -m pip install -r requirements.txt

python app.py

</code>

## Demo

[ImageX-CF in HuggingFace](https://huggingface.co/spaces/vilarin/ImageX-CF)
