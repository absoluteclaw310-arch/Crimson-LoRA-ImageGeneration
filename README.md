# Crimson LoRA Image Generation

RunPod serverless endpoint for generating photorealistic character images using SDXL + LoRA.

## Features

- 30-image generation pipeline optimized for LoRA training
- Multiple camera angles: macro, headshot, bust, full body
- Identity preservation through LoRA weights
- Professional studio lighting and backgrounds
- Automated generation with quality control

## Models

- **Checkpoint**: Juggernaut XL v9 (photorealistic)
- **LoRA**: Custom character LoRA (Crimson)
- **Resolution**: 832x1216 (portrait) and 1024x1024 (macro)

## Usage

### Environment Variables

```bash
export RUNPOD_API_KEY="your_api_key"
export ENDPOINT_ID="your_endpoint_id"
```

### Generate Images

```bash
python generate_images.py
```

Images are saved to `character_lora_dataset/` directory.

### Deploy to RunPod

1. Build Docker image:
```bash
docker build -t crimson-lora .
```

2. Push to registry and deploy as serverless endpoint.

## Image Schedule

**Phase 1: Macro Facial (01-06)**
- Frontal, smiling, 3/4 views, profiles

**Phase 2: Headshots (07-16)**
- Neutral, smiling, confused, low/high angles, profiles

**Phase 3: Bust/Medium (17-24)**
- Frontal, angled, crossed arms, leaning

**Phase 4: Full Body (25-30)**
- Waist-up, back view, standing, seated

## Output

```
character_lora_dataset/
├── character_01.png
├── character_02.png
├── ...
├── character_30.png
└── generation_report.json
```

## License

CreativeML Open RAIL-M (for Juggernaut XL)
