import runpod
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image
import base64
import io
import os
import requests
import json

# Configuration from environment
MODEL_URL = os.environ.get("MODEL_URL", "")
LORA_URL = os.environ.get("LORA_URL", "")
CHECKPOINT_DIR = "/workspace/models/checkpoints"
LORA_DIR = "/workspace/models/loras"

def download_file(url, dest):
    """Download file with progress"""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest):
        print(f"File already exists: {dest}")
        return dest
    
    print(f"Downloading {url} to {dest}...")
    response = requests.get(url, stream=True, timeout=300)
    response.raise_for_status()
    
    with open(dest, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"Downloaded: {dest} ({os.path.getsize(dest)} bytes)")
    return dest

# Global pipeline
pipeline = None

def load_pipeline():
    """Load SDXL + LoRA pipeline"""
    global pipeline
    if pipeline is not None:
        return pipeline
    
    print("Loading SDXL pipeline...")
    
    # Download checkpoint
    checkpoint_path = os.path.join(CHECKPOINT_DIR, "model.safetensors")
    download_file(MODEL_URL, checkpoint_path)
    
    # Load pipeline
    pipe = StableDiffusionXLPipeline.from_single_file(
        checkpoint_path,
        torch_dtype=torch.float16,
        use_safetensors=True
    )
    pipe = pipe.to("cuda")
    
    # Load LoRA if provided
    if LORA_URL:
        lora_path = os.path.join(LORA_DIR, "character.safetensors")
        download_file(LORA_URL, lora_path)
        print(f"Loading LoRA: {lora_path}")
        pipe.load_lora_weights(lora_path)
        print("LoRA loaded successfully")
    
    print("Pipeline ready!")
    return pipe

def handler(job):
    """RunPod serverless handler"""
    global pipeline
    
    print(f"Job received: {job}")
    
    # Load pipeline on first request
    if pipeline is None:
        pipeline = load_pipeline()
    
    # Parse input
    job_input = job.get("input", {})
    
    prompt = job_input.get("prompt", "")
    negative_prompt = job_input.get("negative_prompt", "")
    width = job_input.get("width", 1024)
    height = job_input.get("height", 1024)
    num_inference_steps = job_input.get("num_inference_steps", 25)
    guidance_scale = job_input.get("guidance_scale", 7.5)
    seed = job_input.get("seed", -1)
    num_images = job_input.get("num_images", 1)
    
    if not prompt:
        return {"error": "No prompt provided"}
    
    # Generate
    generator = None
    if seed != -1:
        generator = torch.Generator("cuda").manual_seed(seed)
    
    print(f"Generating {num_images} image(s): {width}x{height}, steps={num_inference_steps}")
    
    result = pipeline(
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        generator=generator,
        num_images_per_prompt=num_images
    )
    
    # Encode images
    images_base64 = []
    for image in result.images:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        images_base64.append(img_str)
    
    print(f"Generated {len(images_base64)} image(s)")
    
    return {
        "mode": "image",
        "images": images_base64,
        "seed": seed if seed != -1 else None,
        "width": width,
        "height": height,
        "lora_loaded": LORA_URL != ""
    }

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
