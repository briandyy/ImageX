# ImageX 
**Cloudflare-Workers-AI-Image Generator-WebUI**

A Gradio webui for Cloudflare workers AI Text-to-Image, Image Inpainting, Image-To-Image generations.

Use Cloudflare text-generation model to translate prompts, and auto optimzing the prompts and text-to-image model to generate images.

## Preview

![image-gen](<image1.png>)

![inpainting](<image2.png>)

![image-to-image](<image3.png>)

## Use

Clone the repo to your disk, change the .env.example to .env, and set the right values.Run the commands in terminal on the directory:

```
python -m venv venv

source ./venv/bin/activate

python -m pip install -r requirements.txt

python app.py
```

## Demo For Text-to-Image Lite Version

(This lite demo is missing Inpainting and IMG-to-IMG, API settings required.)

[ImageX-CF in HuggingFace](https://huggingface.co/spaces/vilarin/ImageX-CF)
