# Pipeline

Simple test of YourMT3+ transcribing. This was set up using WSL (Windows Subsystem for Linux).

## What you need

- Docker Desktop: https://www.docker.com/products/docker-desktop/
- WSL: https://learn.microsoft.com/en-us/windows/wsl/install

This will be a large image (10 GB). Highly recommend you do this on a PC and not a laptop.

Does not need an NVIDIA graphics card. It will auto switch to CPU (will take longer) if one is not detected.

## Docker Desktop setup

In Docker Desktop, go to Settings > Resources > WSL Integration, turn it on for Ubuntu (or whatever distro you chose), and click Apply & restart.

Docker Desktop must be running whenever you use it.

## To start

Make sure to start in WSL and inside the pipeline folder where MIDIscribe.py is.

1. Build the image. The period is very important, do not forget it. This will take a while.

```
docker build -t workflow .
```

2. Allow the script to be executed:

```
chmod +x run.sh
```

3. Add the song file of your choice to the pipeline folder and run:

```
./run.sh <file_name>.wav
```
