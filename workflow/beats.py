import os, sys,json
import numpy as np
import torch
from beat_this.inference import File2Beats
from beat_this.utils import infer_beat_numbers

def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return File2Beats(checkpoint_path="final0", device=device, dbn=False)

def find_beats(f2b, audio):
    beats, downbeats = f2b(str(audio))
    numbers = infer_beat_numbers(beats, downbeats)

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

    regular_bars = float(np.mean(numbers[bar_ends] == beats_per_bar)) if len(bar_ends) else 0.0
    tempo_wobble = float(np.std(np.diff(beats)) / np.median(np.diff(beats))) if len(beats) > 2 else 1.0

    return {"beats": [float(t) for t in beats], "downbeats": [float(t) for t in downbeats],
            "beat_numbers": [int(n) for n in numbers], "bpm": float(bpm),
            "beats_per_bar": beats_per_bar, "pickup_beats": pickup,
            "regular_bars": regular_bars, "tempo_wobble": tempo_wobble}

if __name__ == "__main__":
    audio = sys.argv[1]
    out_json = os.path.splitext(os.path.basename(audio))[0] + '_beats.json'
    result = find_beats(load_model(), audio)

    print(f"{len(result['beats'])} beats, {len(result['downbeats'])} downbeats")
    print(f"tempo estimated at: {result['bpm']:.1f} bpm")
    print(f"{result['beats_per_bar']} beats per bar")
    print("first beats:", [f"{t:.2f}({n})" for t, n in zip(result["beats"][:8], result["beat_numbers"][:8])])
    print(f"grid trust: {result['regular_bars']:.0%} of bars regular, tempo wobble {result['tempo_wobble']:.2f}")

    # Save to JSON
    with open(out_json, "w") as f:
        json.dump(result, f, indent=2)
    print("wrote", out_json)

