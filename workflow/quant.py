import sys, json
import numpy as np
import pretty_midi
import mido

def load(midi_path, beats_path):
    pm = pretty_midi.PrettyMIDI(str(midi_path))
    with open(beats_path) as f:
        beats_info = json.load(f)
    if sum(len(inst.notes) for inst in pm.instruments) == 0:
        raise ValueError(f"{midi_path} has no notes")
    if len(beats_info["beats"]) < 2:
        raise ValueError(f"{beats_path} needs at least two beats")
    return pm, beats_info

def build_grid(beats, beats_per_bar, pickup, song_end):
    # find gap between beats at the end and start of the song
    first_gap = beats[1] - beats[0]
    last_gap = beats[-1] - beats[-2]
    add_before = (beats_per_bar - pickup) % beats_per_bar # find out how many beats are missing to fill in first bar

    # need to make sure there isn't a long opening before first beat
    # if so add more beats before the first beat to fill in the gap
    while beats[0] - add_before * first_gap > 0.05:
        add_before += beats_per_bar
    before = beats[0] - first_gap * np.arange(add_before, 0, -1)

    # fill beats after the last beat until the end of the song, and make sure the last bar is complete
    after = []
    last = beats[-1]
    while last < song_end or (add_before + len(beats) + len(after) -1) % beats_per_bar:
        last += last_gap
        after.append(last)
    
    return np.concatenate([before, beats, after]), add_before, len(after)

def quantize(midi_path, beats_path, out_path):
    pm, beats_info = load(midi_path, beats_path)
    beats = np.array(beats_info["beats"])
    beats_per_bar = beats_info["beats_per_bar"]
    
    # print test statement will delete in future
    print(f"{len(pm.instruments)} parts, last note ends at {pm.get_end_time():.2f}s; "
          f"{len(beats)} beats from {beats[0]:.2f}s to {beats[-1]:.2f}s, {beats_per_bar} per bar, "
          f"{beats_info['pickup_beats']} pickup")

    grid, add_before, add_after = build_grid(beats, beats_per_bar, beats_info["pickup_beats"], pm.get_end_time())
    # print test statement will delete in future    
    print(f"grid: {(len(grid)- 1) // beats_per_bar} measures from {grid[0]:.2f}s to {grid[-1]:.2f}s, "
          f"{add_before} beats added before, {add_after} after")
          
    return out_path

if __name__ == "__main__":
    stem = sys.argv[1].rsplit(".", 1)[0]
    try:
        quantize(stem + "_ymt3.mid", stem + "_beats.json", stem + "_quant.mid")
    except ValueError as exc:
        sys.exit(str(exc))