FROM runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    aria2 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    runpod==1.7.7 \
    torch>=2.0.0 \
    diffusers==0.29.2 \
    transformers==4.41.2 \
    accelerate==0.30.1 \
    safetensors==0.4.2 \
    requests \
    huggingface-hub==0.23.5 \
    numpy \
    pillow

# Create model directories
RUN mkdir -p /workspace/models/checkpoints /workspace/models/loras

# Copy handler
COPY handler.py /workspace/handler.py

# Set working directory
WORKDIR /workspace

# Run the handler
CMD ["python", "/workspace/handler.py"]
