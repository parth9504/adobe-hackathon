# Use lightweight Python image compatible with AMD64 CPUs
FROM --platform=linux/amd64 python:3.9-slim

# Create working directory inside the container
WORKDIR /app

# Copy all local files into container's working dir
COPY . .

# Install required Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Preload the transformer model for offline use
RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-MiniLM-L3-v2')"

# Default command to run when the container starts
CMD ["python", "round1a.py"]
