#!/usr/bin/env bash
GPU="--gpus all"
if ! command -v nvidia-smi > /dev/null; then GPU=""; echo "no NVIDIA GPU found, running on CPU"; fi
 
TTY=""
if [ $# -eq 0 ]; then
    echo "usage: ./run.sh <audio file>        run YourMT3+ and Beat_This on a file in this folder"
    echo "       ./run.sh <script.py> [args]  run a script in this folder"
    echo "       ./run.sh bash                open a shell in the environment"
    exit 1
elif [[ "$1" == *.py ]]; then
    CMD=(python "$@")
elif [ "$1" == "bash" ]; then
    CMD=(bash)
    TTY="-it"
else
    CMD=(bash -c 'set -e
        python MIDIscribe.py "$1"
	python beats.py "$1"' _ "$1")        
fi

# --- run in docker ---
# --rm: delete container when done
# --user: output files owned by you, not root
# HOME=/tmp: give tools a place to write cache
# mount this folder at /work, start there
# workflow = image name
docker run --rm $GPU $TTY \
    --user "$(id -u):$(id -g)" \
    -e HOME=/tmp \
    -v "$PWD":/work -w /work \
    workflow "${CMD[@]}"

