import sys
import torch
import pretty_midi
from huggingface_hub import hf_hub_download
from yourmt3 import YMT3

print("cuda available:", torch.cuda.is_available())
ckpt = hf_hub_download("shethjenil/Audio2Midi_Models", "YMT3+.pt")
model = YMT3(ckpt, "YMT3+")
print("model loaded")

out_mid = sys.argv[1].rsplit(".", 1)[0] + "_ymt3.mid"
model.predict(sys.argv[1], 8, lambda i, total: print(f"  segment {i}/{total}", end="\r"), out_mid)
result = out_mid
print("\npredict returned:", type(result), result)

pm = pretty_midi.PrettyMIDI(str(result))
for inst in pm.instruments:
    name = "Drums" if inst.is_drum else pretty_midi.program_to_instrument_name(inst.program)
    print(f"{name:30s} {len(inst.notes):5d} notes")
