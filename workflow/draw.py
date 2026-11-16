import sys, io 
from pathlib import Path
import mido
from music21 import converter, key as m21key
import verovio
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas

# Take tempo values and make them usable for music21 
# Walk each track and get rid of their set_tempo msg 
# Carry takes those gaps from the cut set_tempo msg and adds them to kept msg
# There is issues with music21 and many tempo changes so we pick one median tempo
def prep_midi(midi_path, out_path):
    mid = mido.MidiFile(str(midi_path))
    tempos = sorted(m.tempo for t in mid.tracks for m in t if m.type == "set_tempo" and m.tempo > 1000)
    median = tempos[len(tempos) // 2] if tempos else 500000 # 120 bpm

    keep = []
    for track in mid.tracks:
        if any(getattr(m, "channel", None) == 9 for m in track):
            continue
        carry = 0
        new = []
        for m in track:
            if m.type == "set_tempo":
                    carry += m.time 
                    continue
            new.append(m.copy(time = m.time + carry))
            carry = 0
        track[:] = new
        keep.append(track)

    mid.tracks = keep
    mid.tracks[0].insert(1, mido.MetaMessage("set_tempo", tempo = median, time = 0))
    mid.save(str(out_path))
    return out_path

# QuantizePost snaps the note times and quarterLengthDivision allows for 16ths
# and triplets. We use analyze(key) to see how often each pitch shows up
# For loop is to get the first measure, insert its key at an offset of 0.
def to_musicxml(midi_path, out_path):
    score = converter.parse(str(midi_path), quantizePost = True, quarterLengthDivisors=(4,3))
    k = score.analyze("key")

    print(f"key: {k}")
    for part in score.parts:
        first = part.getElementsByClass("Measure").first()
        if first is not None:
            first.insert(0, m21key.KeySignature(k.sharps))
    score.write("musicxml", fp = str(out_path))

    return out_path

# Setting the pdf page output dimensions
# we use the renderToSVG on the page to make it an svg string 
# This allows for svg2rlg to wrap it as a reportlab drawing.
# We then draw the pdf with renderPDF.draw
def to_pdf(xml_path, out_path):
    tk = verovio.toolkit()
    tk.setInputFrom("musicxml")
    tk.setOptions({"pageWidth": 2100, "pageHeight": 2970, "scale": 35,
                   "adjustPageHeight": False, "breaks": "auto", "header": "none", "footer": "none"})
    if not tk.loadFile(str(xml_path)):
                    raise ValueError(f"could not read {xml_path}, problem with dependency verovio")

    pages = tk.getPageCount()
    pdf = None
    for p in range(1, pages + 1):
        svg = tk.renderToSVG(p)
        drawing = svg2rlg(io.StringIO(svg))
        if pdf is None:
            pdf = canvas.Canvas(str(out_path), pagesize = (drawing.width, drawing.height))
        renderPDF.draw(drawing, pdf, 0, 0)
        pdf.showPage()
    pdf.save()

    return out_path, pages


def make_sheet(quant_path):
    stem = str(quant_path).replace("_quant.mid", "")
    mid = prep_midi(quant_path, stem + "_sheet.mid")
    xml = to_musicxml(mid, stem + "_sheet.musicxml")
    pdf, pages = to_pdf(xml, stem + "_sheet.pdf")
    print(f"wrote {pdf}, {pages} pages")

    return pdf
if __name__ == "__main__":

    stem = sys.argv[1].rsplit(".", 1)[0]
    try:
        make_sheet(stem + "_quant.mid")
    except ValueError as exc:
        sys.exit(str(exc))

