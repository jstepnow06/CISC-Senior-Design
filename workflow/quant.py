import sys, json
import numpy as np
import pretty_midi
import mido

GRIDS = {4: "16ths", 3: "8th-note triplets"}
TPB = 480
SQUASH = 1
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
    if np.any(np.diff(beats_info["beats"]) <= 0):
        raise ValueError(f"{beats_path} has beats out of order or doubled")
    return pm, beats_info

def build_grid(beats, beats_per_bar, pickup, song_end):
    # find gap between beats at the end and start of the song
    gap = np.median(np.diff(beats))
    add_before = (beats_per_bar - pickup) % beats_per_bar # find out how many beats are missing to fill in first bar

    # need to make sure there isn't a long opening before first beat
    # if so add more beats before the first beat to fill in the gap
    while beats[0] - add_before * gap > 0.05:
        add_before += beats_per_bar
    before = beats[0] - gap * np.arange(add_before, 0, -1)

    # fill beats after the last beat until the end of the song, and make sure the last bar is complete
    after = []
    last = beats[-1]
    while last < song_end or (add_before + len(beats) + len(after) -1) % beats_per_bar:
        last += gap
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
def tick(pos):
    return round(pos * TPB)

# Maps the tempo of the song that way it is dynamic
# grid is input as we need beat times
# loop over every pair of grid beats a, b. first pair: a after 0s -> a = 0
# squash any beat before 0 seconds so it doesn't get counted.
def tempo_events(grid):
    events = []
    for i in range(len(grid) - 1):
        a, b = grid[i], grid[i + 1]
        if i == 0 and a > 0:
            a = 0
        tempo = min(max(round((b-a) * 1e6), 1), 16777215)
        if b <= 0:
            events.append((tick(i), SQUASH))
        elif a < 0:
            events.append((tick(i), SQUASH))
            events.append((tick(i - a / (b-a)), tempo))
        else:
            events.append((tick(i), tempo))
    return events

# Iterating through each parts (instruments) 
# take the tempo events we created and append them as the tempo at that time
# We also want time signature which is usually 4/4 (will have to add more)
# create an array called msgs to store tuples of the start and end of a note, its pitch and velocity.
def write_midi(out_path, events, grid_len, beats_per_bar, cleaned):
    out = mido.MidiFile(ticks_per_beat=TPB)

    tempo_track = mido.MidiTrack()
    tempo_track.append(mido.MetaMessage("time_signature", numerator = beats_per_bar, 
                                        denominator = 4, time = 0))
    now = 0
    for t, tempo in events:
        tempo_track.append(mido.MetaMessage("set_tempo", tempo = tempo, time = t - now))
        now = t
    tempo_track.append(mido.MetaMessage("end_of_track", time = tick(grid_len - 1) - now))
    out.tracks.append(tempo_track)

    channels = iter(c for c in range(16) if c != 9)
    for inst, notes in cleaned:
        if not notes:
            continue
        ch = 9 if inst.is_drum else next(channels, 0)
        track = mido.MidiTrack()
        track.append(mido.MetaMessage("track_name", name = part_name(inst),
                                      time = 0))
        if not inst.is_drum:
            track.append(mido.Message("program_change", channel=ch,
                                      program = inst.program, time = 0))
        msgs = []
        for start, end, pitch, velocity in notes:
            msgs.append((tick(start), 1 , pitch, velocity))
            msgs.append((tick(end), 0, pitch, 0))
        msgs.sort()
        now = 0
        for t, on, pitch, velocity in msgs:
            kind = "note_on" if on else "note_off"
            track.append(mido.Message(kind, channel = ch, note = pitch,
                                      velocity = velocity, time = t- now))
            now = t
        track.append(mido.MetaMessage("end_of_track", time = 0))
        out.tracks.append(track)
    out.save(out_path)

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
    write_midi(str(out_path), tempo_events(grid), len(grid), beats_per_bar, cleaned)
    print("wrote", out_path)

    return out_path

if __name__ == "__main__":
    stem = sys.argv[1].rsplit(".", 1)[0]
    try:
        quantize(stem + "_ymt3.mid", stem + "_beats.json", stem + "_quant.mid")
    except ValueError as exc:
        sys.exit(str(exc))
