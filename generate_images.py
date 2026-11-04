#!/usr/bin/env python3
"""
Character LoRA Image Generator
30 photorealistic images for LoRA training
"""

import requests
import json
import base64
import time
import os
from pathlib import Path

RUNPOD_API_KEY = ***"RUNPOD_API_KEY", "")
ENDPOINT_ID = ***"ENDPOINT_ID", "")

IMAGE_PROMPTS = [
    # Phase 1: Macro facial (1-6)
    {"id": "01", "desc": "Frontal macro", "prompt": "professional macro photography, frontal face, neutral expression, direct eye contact, nose bridge detail, natural skin pores, professional studio lighting, solid light grey background, photorealistic", "width": 1024, "height": 1024},
    {"id": "02", "desc": "Smiling macro", "prompt": "professional macro photography, frontal face, natural smile with slight teeth, eye crinkles, natural skin texture, professional studio lighting, solid light grey background, photorealistic", "width": 1024, "height": 1024},
    {"id": "03", "desc": "Left 3/4 macro", "prompt": "professional macro photography, three-quarter view, head rotated 45 degrees left, eyes toward camera, natural skin texture, professional studio lighting, solid light grey background, photorealistic", "width": 1024, "height": 1024},
    {"id": "04", "desc": "Right 3/4 macro", "prompt": "professional macro photography, three-quarter view, head rotated 45 degrees right, natural skin texture, professional studio lighting, solid light grey background, photorealistic", "width": 1024, "height": 1024},
    {"id": "05", "desc": "Left profile macro", "prompt": "professional macro photography, exact side profile 90 degrees, left side, neutral expression, natural skin texture, professional studio lighting, solid light grey background, photorealistic", "width": 1024, "height": 1024},
    {"id": "06", "desc": "Right profile macro", "prompt": "professional macro photography, exact side profile 90 degrees, right side, subtle smirk, natural skin texture, professional studio lighting, solid light grey background, photorealistic", "width": 1024, "height": 1024},

    # Phase 2: Headshots (7-16)
    {"id": "07", "desc": "Frontal neutral", "prompt": "professional headshot photography, straight-on, neutral expression, shoulders visible, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "08", "desc": "Genuine smile", "prompt": "professional headshot photography, broad genuine smile, natural eye crinkles, teeth slightly visible, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "09", "desc": "Confused expression", "prompt": "professional headshot photography, confused expression, slight frown, raised eyebrow, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "10", "desc": "Low angle", "prompt": "professional headshot photography, low camera angle below chin, head slightly tilted back, looking down at camera, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "11", "desc": "High angle", "prompt": "professional headshot photography, high camera angle above forehead, head slightly lowered, eyes looking upward, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "12", "desc": "Left 3/4", "prompt": "professional headshot photography, three-quarter view left, neutral expression, hair tucked behind ear, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "13", "desc": "Right 3/4 looking away", "prompt": "professional headshot photography, three-quarter view right, looking downward and away, contemplative, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "14", "desc": "Laughing", "prompt": "professional headshot photography, three-quarter view left, natural open-mouth laugh, joyful expression, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "15", "desc": "Left profile tilted up", "prompt": "professional headshot photography, left profile, head tilted slightly upward, elegant pose, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "16", "desc": "Right profile tilted down", "prompt": "professional headshot photography, right profile, head tilted slightly downward, hair visible, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},

    # Phase 3: Bust/Medium (17-24)
    {"id": "17", "desc": "Frontal bust", "prompt": "professional portrait photography, bust shot, shoulders square, neutral expression, white shirt, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "18", "desc": "Angled shoulders", "prompt": "professional portrait photography, bust shot, shoulders at 45 degrees, head facing camera, beige top, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "19", "desc": "Left 3/4 bust", "prompt": "professional portrait photography, three-quarter bust, relaxed posture, arms crossed, grey sweater, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "20", "desc": "Right 3/4 bust leaning", "prompt": "professional portrait photography, three-quarter bust, leaning slightly forward, black shirt, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "21", "desc": "High-angle bust", "prompt": "professional portrait photography, bust shot, camera 30 degrees above, hair parting visible, shoulders, muted blue blouse, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "22", "desc": "Low-angle bust", "prompt": "professional portrait photography, bust shot, camera below eye level, looking upward, white shirt, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "23", "desc": "Left profile bust", "prompt": "professional portrait photography, left profile bust, looking straight ahead, shoulder and upper-back posture, beige top, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "24", "desc": "Right profile bust looking back", "prompt": "professional portrait photography, right profile bust, looking back over shoulder toward camera, black shirt, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},

    # Phase 4: Full body (25-30)
    {"id": "25", "desc": "Waist-up frontal", "prompt": "professional full-body photography, waist-up, hands resting on hips, arms separated from torso, white shirt, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "26", "desc": "Waist-up 3/4", "prompt": "professional full-body photography, waist-up three-quarter, casual asymmetrical posture, grey sweater, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "27", "desc": "Back view", "prompt": "professional full-body photography, back view, head turned over right shoulder looking at camera, hair fully visible, black shirt, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "28", "desc": "Full body frontal", "prompt": "professional full-body photography, standing naturally, feet slightly apart, head to toe, white shirt and jeans, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "29", "desc": "Full body 3/4", "prompt": "professional full-body photography, three-quarter stance, one leg forward, weight shifted, beige top and pants, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216},
    {"id": "30", "desc": "Full body seated", "prompt": "professional full-body photography, seated on simple backless stool, relaxed posture, grey sweater and pants, professional studio lighting, solid light grey background, photorealistic", "width": 832, "height": 1216}
]

NEGATIVE_PROMPT = "blurry, distorted, artificial, smooth skin, cartoon, ugly, deformed, mutated, extra limbs, watermark, text, logo, signature, frame, border"

def generate_image(endpoint_id, prompt_data, api_key):
    """Generate a single image via RunPod API"""
    url = f"https://api.runpod.ai/v2/{endpoint_id}/runsync"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "input": {
            "prompt": prompt_data["prompt"],
            "negative_prompt": NEGATIVE_PROMPT,
            "width": prompt_data["width"],
            "height": prompt_data["height"],
            "num_inference_steps": 35,
            "guidance_scale": 5.0,
            "seed": -1
        }
    }

    response = requests.post(url, headers=headers, json=payload, timeout=300)
    response.raise_for_status()
    return response.json()

def save_image(image_b64, output_path):
    """Save base64 image to file"""
    img_data = base64.b64decode(image_b64)
    output_path.write_bytes(img_data)
    print(f"Saved: {output_path}")

def main():
    if not RUNPOD_API_KEY or not ENDPOINT_ID:
        print("Error: RUNPOD_API_KEY and ENDPOINT_ID must be set")
        return

    output_dir = Path("character_lora_dataset")
    output_dir.mkdir(exist_ok=True)

    print(f"Generating {len(IMAGE_PROMPTS)} images...")
    print(f"Endpoint: {ENDPOINT_ID}")

    results = []
    for prompt_data in IMAGE_PROMPTS:
        print(f"\n[{prompt_data['id']}] {prompt_data['desc']}")
        try:
            result = generate_image(ENDPOINT_ID, prompt_data, RUNPOD_API_KEY)

            if "output" in result and "images" in result["output"]:
                image_b64 = result["output"]["images"][0]
                output_path = output_dir / f"character_{prompt_data['id']}.png"
                save_image(image_b64, output_path)

                results.append({
                    "id": prompt_data["id"],
                    "status": "success",
                    "file": str(output_path)
                })
            else:
                error = result.get("error", "No image in response")
                print(f"  Error: {error}")
                results.append({
                    "id": prompt_data["id"],
                    "status": "failed",
                    "error": error
                })

        except Exception as e:
            print(f"  Error: {e}")
            results.append({
                "id": prompt_data["id"],
                "status": "failed",
                "error": str(e)
            })

        time.sleep(2)

    # Save report
    report_path = output_dir / "generation_report.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)

    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\nComplete: {success_count}/{len(IMAGE_PROMPTS)} images generated")
    print(f"Report saved: {report_path}")

if __name__ == "__main__":
    main()
