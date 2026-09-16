"""Build the one-page helicopter control note with ReportLab.

Run with Python containing reportlab and pypdf. The final PDF is written beside
this source. Its layout follows the supplied Delta robot summary: US Letter,
two columns, Times typography, 10 pt body, centered author block.
"""
from pathlib import Path
import json

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import Paragraph, Spacer, Flowable
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "helicopter-entropy-optimal-control.pdf"
FONTS = Path("C:/Windows/Fonts")
for name, filename in [("TNR", "times.ttf"), ("TNR-Bold", "timesbd.ttf"),
                       ("TNR-Italic", "timesi.ttf"), ("TNR-BoldItalic", "timesbi.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(FONTS / filename)))
pdfmetrics.registerFontFamily("TNR", normal="TNR", bold="TNR-Bold",
                            italic="TNR-Italic", boldItalic="TNR-BoldItalic")
pdfmetrics.registerFont(TTFont("MathSymbols", str(FONTS / "seguisym.ttf")))

PAGE_W, PAGE_H = 612, 792
MARGIN, GUTTER = 49, 12
COL_W = (PAGE_W - 2 * MARGIN - GUTTER) / 2
TOP, BOTTOM = 635, 70
styles = {
    "body": ParagraphStyle("body", fontName="TNR", fontSize=10, leading=11.55,
        alignment=TA_JUSTIFY, firstLineIndent=10, spaceAfter=3),
    "abstract": ParagraphStyle("abstract", fontName="TNR-Bold", fontSize=9,
        leading=10.3, alignment=TA_JUSTIFY, firstLineIndent=10, spaceAfter=3),
    "keywords": ParagraphStyle("keywords", fontName="TNR-Bold", fontSize=9,
        leading=10.3, alignment=TA_JUSTIFY, firstLineIndent=10, spaceAfter=5),
    "heading": ParagraphStyle("heading", fontName="TNR", fontSize=10,
        leading=12, alignment=TA_CENTER, spaceBefore=6, spaceAfter=5),
    "equation": ParagraphStyle("equation", fontName="TNR", fontSize=10,
        leading=15, alignment=TA_CENTER),
    "reference": ParagraphStyle("reference", fontName="TNR", fontSize=8,
        leading=9.2, alignment=TA_LEFT, leftIndent=13, firstLineIndent=-13, spaceAfter=3),
}

def p(text, style="body"):
    text = text.replace('<sub>', '<sub rise="2" size="7">')
    text = text.replace('<super>', '<super rise="4" size="7">')
    text = text.replace('∈', '<font name="MathSymbols">∈</font>')
    return Paragraph(text, styles[style])

def h(number, title):
    return p(f"{number}. {title.upper()}", "heading")

class Equation(Flowable):
    def __init__(self, text, number):
        Flowable.__init__(self)
        self.par = p(text, "equation")
        self.number = number
        self.spaceBefore = 1
        self.spaceAfter = 5

    def wrap(self, width, avail_height):
        self.width = width
        _, self.height = self.par.wrap(width - 20, avail_height)
        return width, self.height

    def draw(self):
        self.par.drawOn(self.canv, 0, 0)
        self.canv.setFont("TNR", 10)
        self.canv.drawRightString(self.width, self.height / 2 - 3, f"({self.number})")

left = [
    p('<i>Abstract.</i> This note proposes entropy-generation-minimizing control '
      'for a conventional helicopter near hover. A nonlinear predictive controller '
      'seeks to reduce irreversible losses while completing a prescribed flight task. '
      'The method combines coupled rotorcraft dynamics, thermodynamic loss maps, '
      'and explicit operating constraints; it requires vehicle-specific identification '
      'and closed-loop validation.', "abstract"),
    p('<i>Index Terms:</i> Helicopter, entropy generation, exergy, nonlinear optimal control.', "keywords"),
    h("I", "Define the Mission and Dynamics"),
    p('Specify a fixed-duration hover-to-hover maneuver, payload, flight corridor, '
      'and endpoint tolerances. This prevents apparent savings obtained by doing '
      'less work. Assume a single main rotor, a tail rotor, and governed rotor speed.'),
    Equation('<i>dx/dt = f(x, u, w)</i>,<br/>'
             '<i>u</i> = [<i>θ</i><sub>0</sub>, <i>θ</i><sub>1c</sub>, '
             '<i>θ</i><sub>1s</sub>, <i>θ</i><sub>t</sub>]<super>T</super>.', 1),
    p('The inputs are main collective, two cyclic pitches, and tail collective. '
      'State <i>x</i> contains position, velocity, attitude, body rates, and relevant '
      'rotor flapping, inflow, actuator, and thermal states; <i>w</i> represents wind. '
      'Identify the coupled force and moment model around trim. Include governor '
      'dynamics when rotor-speed transients matter.'),
    h("II", "Account for Physical Entropy"),
    p('Choose a boundary covering the aircraft, propulsion, and specified wake '
      'relaxation. Define entropy generation rate <i>σ</i> in W/K. At fixed ambient '
      'temperature <i>T</i><sub>0</sub>, destroyed exergy equals '
      '<i>T</i><sub>0</sub> times generated entropy [1]. A component model gives'),
    Equation('<i>σ</i> = ∑<sub>j</sub> <i>P</i><sub>irr,j</sub>/<i>T</i><sub>j</sub>'
             ' + <i>σ</i><sub>other</sub> ≥ 0,<br/>'
             '<i>P</i><sub>ex,dest</sub> = <i>T</i><sub>0</sub><i>σ</i>.', 2),
    p('Here <i>P</i><sub>irr,j</sub> is locally dissipated power at absolute '
      'temperature <i>T</i><sub>j</sub>; <i>σ</i><sub>other</sub> includes heat-transfer, '
      'mixing, and chemical or electrochemical irreversibility as applicable. '
      'Fit these terms from component balances and measured loss maps without '
      'double counting.'),
    p('Rotor-induced power initially leaves as organized wake energy. Count it '
      'as entropy generation only when wake relaxation is included; otherwise '
      'retain it as outgoing exergy. Shaft power divided by ambient temperature '
      'is therefore not a general entropy model. Track stored mechanical and '
      'thermal energy so the horizon cannot hide losses.'),
]

right = [
    h("III", "Connect Rotor Loads to the Cost"),
    p('A near-hover power estimate for each rotor is [2]'),
    Equation('<i>P</i><sub>r</sub> ≈ <i>κ</i><sub>r</sub><i>F</i><sub>r</sub>'
             '<super>3/2</super>/(2<i>ρA</i><sub>r</sub>)<super>1/2</super>'
             ' + <i>P</i><sub>profile,r</sub>.', 3),
    p('<i>F</i><sub>r</sub> is thrust, <i>A</i><sub>r</sub> disk area, '
      '<i>ρ</i> air density, and <i>κ</i><sub>r</sub> the induced-power correction. '
      'Sum main- and tail-rotor requirements and drivetrain losses. Use calibrated '
      'inflow and drag maps for moving flight; the hover relation does not cover '
      'stall or vortex-ring descent. These power terms feed the entropy accounting '
      'in Section II.'),
    h("IV", "Solve a Constrained Flight Problem"),
    p('Discretize the dynamics over <i>N</i> steps of duration <i>Δt</i> and '
      'minimize total generated entropy:'),
    Equation('min<sub><i>U</i></sub> <i>J</i> = ∑<sub><i>k</i>=0</sub>'
             '<super><i>N</i>-1</super> <i>Δt σ(x</i><sub>k</sub>, <i>u</i><sub>k</sub>, '
             '<i>w</i><sub>k</sub>),<br/>'
             '<i>x</i><sub>k+1</sub> = <i>f</i><sub>Δt</sub>(<i>x</i><sub>k</sub>, '
             '<i>u</i><sub>k</sub>, <i>w</i><sub>k</sub>),<br/>'
             '<i>e</i><sub>k</sub> ∈ <i>E</i><sub>k</sub>, '
             '<i>x</i><sub>N</sub> ∈ <i>X</i><sub>f</sub>, '
             '(<i>x</i><sub>k</sub>, <i>u</i><sub>k</sub>, <i>Δu</i><sub>k</sub>) ∈ <i>C</i>.', 4),
    p('<i>U</i> is the input sequence, <i>x</i><sub>0</sub> the estimated state, '
      'and <i>w</i><sub>k</sub> the wind forecast. '
      '<i>E</i><sub>k</sub> bounds tracking error; <i>X</i><sub>f</sub> specifies '
      'terminal flight and mechanical/thermal states. <i>C</i> limits pitch commands '
      'and rates, rotor speed, shaft torque/power, temperatures, attitude, clearance, '
      'and the identified flight envelope. Choose a terminal set compatible with '
      'a stabilizing controller; entropy minimization alone does not ensure stability.'),
    h("V", "Implement and Validate"),
    p('First identify the model and solve offline by direct multiple shooting '
      'or collocation (e.g., CasADi [3]). Then estimate states, warm-start the '
      'optimization, apply its first input, and repeat as nonlinear model predictive '
      'control. Check feasibility and computation time; retain a stabilizing fallback.'),
    p('Compare the same maneuver with PID/LQR under wind, mass, and model errors. '
      'Report tracking error, integrated entropy or a declared power proxy, input '
      'energy, peak torque, and violations. Hover still requires positive power; '
      'no efficiency gain is established without these tests.'),
    p('REFERENCES', "heading"),
    p('[1] F. Philipp <i>et al.</i>, "Optimal control of port-Hamiltonian systems: '
      'energy, entropy, and exergy," 2024. '
      '<link href="https://arxiv.org/abs/2306.08914">arXiv:2306.08914</link>.', "reference"),
    p('[2] W. Johnson, <i>NDARC: NASA Design and Analysis of Rotorcraft</i>, '
      '<link href="https://rotorcraft.arc.nasa.gov/Publications/files/Johnson%20TP-2015-218751.pdf">'
      'NASA/TP-2015-218751</link>, 2015, ch. 11.', "reference"),
    p('[3] CasADi, "Optimal control with CasADi," documentation, sec. 8. '
      '<link href="https://web.casadi.org/docs/#optimal-control-with-casadi">'
      'web.casadi.org/docs</link>.', "reference"),
]

def measure(items):
    height = 0
    for item in items:
        _, hh = item.wrap(COL_W, PAGE_H)
        height += item.getSpaceBefore() + hh + item.getSpaceAfter()
    return height

def draw_column(c, items, x, top):
    y = top
    for item in items:
        y -= item.getSpaceBefore()
        _, hh = item.wrap(COL_W, PAGE_H)
        y -= hh
        item.drawOn(c, x, y)
        y -= item.getSpaceAfter()
    return y

if __name__ == "__main__":
    heights = [measure(left), measure(right)]
    print(json.dumps({"column_heights_pt": heights, "available_height_pt": TOP - BOTTOM}))
    if max(heights) > TOP - BOTTOM:
        raise RuntimeError("Content exceeds one-page layout; revise copy before rendering.")
    c = canvas.Canvas(str(OUTPUT), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle("Entropy-Minimizing Optimal Control of a Helicopter")
    c.setAuthor("Santiago Restrepo")
    c.setCreator("ReportLab; helicopter/build_pdf.py")
    c.setSubject("Proposed thermodynamic optimal-control method; one-page technical summary")
    c.setKeywords("helicopter, entropy generation, exergy, nonlinear MPC, optimal control")
    c.setFont("TNR", 22)
    c.drawCentredString(PAGE_W / 2, 721, "Entropy-Minimizing Control of a Helicopter")
    c.setFont("TNR", 11)
    c.drawCentredString(PAGE_W / 2, 690, "Santiago Restrepo")
    c.setFont("TNR", 10)
    c.drawCentredString(PAGE_W / 2, 677, "contact@waajacu.com     https://waajacu.com/")
    c.setFont("TNR-Italic", 10)
    c.drawCentredString(PAGE_W / 2, 660, "Proposed thermodynamic optimal-control method")
    bottoms = [draw_column(c, left, MARGIN, TOP),
               draw_column(c, right, MARGIN + COL_W + GUTTER, TOP)]
    c.showPage()
    c.save()
    reader = PdfReader(OUTPUT)
    assert len(reader.pages) == 1, "Expected a single page"
    txt = reader.pages[0].extract_text()
    for phrase in ["Define", "Entropy", "REFERENCES", "CasADi"]:
        assert phrase.lower() in txt.lower(), phrase
    assert "\ufffd" not in txt
    print(json.dumps({"output": str(OUTPUT), "pages": len(reader.pages),
                      "column_bottoms_pt": bottoms, "text_characters": len(txt),
                      "reference_links": len(reader.pages[0].get("/Annots", []))}))
