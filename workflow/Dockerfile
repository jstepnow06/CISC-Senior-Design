FROM python:3.11-slim
 
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*
 
WORKDIR /work
RUN pip install --no-cache-dir torch torchaudio \
    && pip install --no-cache-dir yourmt3 huggingface_hub torchcodec pretty_midi
 
ENV HF_HOME=/models
RUN python -c "from huggingface_hub import hf_hub_download; hf_hub_download('shethjenil/Audio2Midi_Models', 'YMT3+.pt')" \
    && chmod -R a+rwX /models
ENV HF_HUB_OFFLINE=1
 
CMD ["bash"]

