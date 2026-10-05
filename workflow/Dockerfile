#this docker will use python3.11-slim as the base
FROM python:3.11-slim

#installs required packages and the ffmpeg tools (for processing and converting audio/video files)
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*
 
#sets working directory
WORKDIR /work
#pip installs torch and pretty_midi libraries (for audio)
RUN pip install --no-cache-dir torch torchaudio \
    && pip install --no-cache-dir yourmt3 huggingface_hub torchcodec pretty_midi

#puts Hugging Face model files in different folder (prevents permission issues)
ENV HF_HOME=/models

#install hugging face models
RUN python -c "from huggingface_hub import hf_hub_download; hf_hub_download('shethjenil/Audio2Midi_Models', 'YMT3+.pt')" \
    && chmod -R a+rwX /models
ENV HF_HUB_OFFLINE=1
 
CMD ["bash"]

