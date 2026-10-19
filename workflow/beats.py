import os, sys ,json
import numpy as np 
import torch
from beat_this.inference import File2Beats
from beat_this.utils import infer_beat_numbers

audio = sys.argv[1]
out_json = os.path.splitext(os.path.basename(audio))[0] + "_beats.json"
device = "cuda" if torch.cuda.is_available() else "cpu"

# Loading beat model
# Get times of beats and downbeats
# Number each beat in its bar
f2b = File2Beats(checkpoint_path="final0", device=device, dbn =False)
beats, downbeats = f2b(audio)
numbers = infer_beat_numbers(beats,downbeats)

# --- tempo + bars ---
# bpm: typical gap between beats -> beats per minute
# bar_ends: last beat of each bar (beat right before each "1")
# beats_per_bar: most common last-beat number (4 = 4/4). none = 4
# pickup: beats before first "1"
# this will have to be looked at more. Math is not perfect but its relatively close.
bpm = 60 / np.median(np.diff(beats)) if len(beats) > 1 else 0.0
bar_ends = np.where(numbers ==1)[0][1:] - 1
beats_per_bar = int(np.bincount(numbers[bar_ends]).argmax()) if len(bar_ends) else 4
pickup = int (np.argmax(numbers == 1 )) if 1 in numbers else 0

#Show output to console
print(f"{len(beats)} beats, {len(downbeats)} downbeats")
print(f"tempo estimated at: {bpm:.1f} bpm")
print(f"{beats_per_bar} beats per bar")
print("first beats:", [f"{t:.2f}({n})" for t, n in zip(beats[:8], numbers[:8])])

# Save to JSON 
json.dump({"beats": [float(t) for t in beats], "downbeats": [float(t) for t in downbeats],
           "beat_numbers": [int(n) for n in numbers], "bpm": float(bpm),
           "beats_per_bar": beats_per_bar, "pickup_beats": pickup}, open(out_json, "w"), indent=2)
print("wrote", out_json)

