import sys, json
import numpy as np
import pretty_midi
import mido

GRIDS = {4: "16ths", 3: "8th-note triplets"}

def part_name(inst):
    return "Drums" if inst.is_drum else pretty_midi.program_to_instrument_name(inst.program)

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

# Test which grid fits better 16th or triplets
# Take note starts in second and interp and arange them
# Find average miss of all the notes 
def off_grid(pm, grid):
    starts = np.interp([n.start for inst in pm.instruments for n in inst.notes],
                       grid, np.arange(len(grid)))
    return {steps: np.mean(np.abs(starts * steps - np.round(starts * steps)) /
                                                            steps) for steps in GRIDS}
# Need to "snap" notes to their grid positions and clean them up
# inst = instrument part | grid = beat times in seconds | steps = steps per beat (16ths or triplets)
# kept = our cleaned notes | moved = counts notes that shift more than 50 ms (not good if a lot of them)
# dupes = same pitch at same start? keep longest note only
# keys let us put each pitch's notes in order on a time interval
# if same pitch and overlap cut first note to end where next one starts
def snap(inst, grid, steps):
    grid_index = np.arange(len(grid))
    snapped = {}

    length = dupes = trimmed = moved = 0
    for n in inst.notes:
        start, end = (int(s) for s in np.round(np.interp([n.start, n.end], grid,
                                                         grid_index) * steps))
        if abs(np.interp(start / steps, grid_index, grid) - n.start) > 0.05:
            moved += 1
        if end <= start:
            end = start + 1
            length += 1
        if (n.pitch, start) in snapped:
            dupes +=1
            if end <= snapped[(n.pitch, start)][0]:
                continue
        snapped[(n.pitch, start)] = (end, n.velocity)

    keys = sorted(snapped)
    kept = []

    for (pitch, start), nxt in zip(keys, keys[1:] + [None]):
        end, velocity = snapped[(pitch, start)]
        if nxt and nxt[0] == pitch and nxt[1] < end:
            end = nxt[1]
            trimmed +=1
        kept.append([start / steps, end / steps, pitch, velocity])
    return kept, (moved, length, dupes, trimmed)

def quantize(midi_path, beats_path, out_path):
    pm, beats_info = load(midi_path, beats_path)
    beats = np.array(beats_info["beats"])
    beats_per_bar = beats_info["beats_per_bar"]
    grid, add_before, add_after = build_grid(beats, beats_per_bar, beats_info["pickup_beats"], pm.get_end_time())
    off = off_grid(pm, grid)
    steps = min(off, key=off.get)
    cleaned = []

    for inst in pm.instruments:
        kept, (moved, length, dupes, trimmed) = snap(inst, grid, steps)
        cleaned.append((inst, kept))
        print(f" {part_name(inst):30s} {len(kept):4d} notes, {moved:3d} moved > 50ms, " 
              f"{length:3d} length, {dupes} duplicates, {trimmed} trimmed")
    return out_path

if __name__ == "__main__":
    stem = sys.argv[1].rsplit(".", 1)[0]
    try:
        quantize(stem + "_ymt3.mid", stem + "_beats.json", stem + "_quant.mid")
    except ValueError as exc:
        sys.exit(str(exc))
