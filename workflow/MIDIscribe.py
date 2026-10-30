import sys
import torch
import pretty_midi
from huggingface_hub import hf_hub_download
from yourmt3 import YMT3


# load YourMT3+ 
def load_model():
    ckpt = hf_hub_download("shethjenil/Audio2Midi_Models", "YMT3+.pt")
    return YMT3(ckpt, "YMT3+", device="cuda" if torch.cuda.is_available() else "cpu")

# audio file -> MIDI file. 8 = segments per batch, progress gets (done, total)
def transcribe(model, audio, out_mid, progress=lambda i, total: None):
    model.predict(str(audio), 8, progress, str(out_mid))

if __name__ == "__main__":
    print("cuda available:", torch.cuda.is_available())
    model = load_model()
    print("model loaded")

    # song.wav -> song_ymt3.mid, next to the input
    out_mid = sys.argv[1].rsplit(".", 1)[0] + "_ymt3.mid"
    transcribe(model, sys.argv[1], out_mid, lambda i, total: print(f"  segment {i}/{total}", end="\r"))
    print("\nwrote", out_mid)

    # note count per part
    pm = pretty_midi.PrettyMIDI(str(out_mid))
    for inst in pm.instruments:
        name = "Drums" if inst.is_drum else pretty_midi.program_to_instrument_name(inst.program)
        print(f"{name:30s} {len(inst.notes):5d} notes")
