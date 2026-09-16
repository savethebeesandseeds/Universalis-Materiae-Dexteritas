"""Build the one-page humanoid locomotion note. Requires reportlab and pypdf.

US Letter, two columns, Times 10 pt body; matches the Delta and helicopter notes.
Run this file with Python; the final PDF is written beside this source.
"""
from pathlib import Path
import json

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import Paragraph, Flowable
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "humanoid-underactuated-deep-learning.pdf"
FONT_DIR = Path("C:/Windows/Fonts")
for name, filename in [("TNR", "times.ttf"), ("TNR-Bold", "timesbd.ttf"),
                       ("TNR-Italic", "timesi.ttf"), ("TNR-BoldItalic", "timesbi.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename)))
pdfmetrics.registerFontFamily("TNR", normal="TNR", bold="TNR-Bold",
                            italic="TNR-Italic", boldItalic="TNR-BoldItalic")
pdfmetrics.registerFont(TTFont("MathSymbols", str(FONT_DIR / "seguisym.ttf")))

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
    for symbol in '∈∥':
        text = text.replace(symbol, f'<font name="MathSymbols">{symbol}</font>')
    return Paragraph(text, styles[style])

def h(number, title):
    return p(f"{number}. {title.upper()}", "heading")

class Equation(Flowable):
    def __init__(self, text, number):
        Flowable.__init__(self)
        self.par = p(text, "equation")
        self.number = number
        self.spaceBefore, self.spaceAfter = 1, 5

    def wrap(self, width, available_height):
        self.width = width
        _, self.height = self.par.wrap(width - 20, available_height)
        return width, self.height

    def draw(self):
        self.par.drawOn(self.canv, 0, 0)
        self.canv.setFont("TNR", 10)
        self.canv.drawRightString(self.width, self.height / 2 - 3, f"({self.number})")

left = [
    p('<i>Abstract.</i> This brief proposes deep reinforcement learning for '
      'underactuated humanoid walking. A neural policy learns foot placement, '
      'load transfer, and whole-body coordination through interaction with '
      'simulated contact dynamics. Joint feedback executes the learned commands. '
      'The workflow combines physical modeling, policy training, and validation '
      'before hardware deployment; no robot-specific performance is assumed.', "abstract"),
    p('<i>Index Terms:</i> Humanoid, bipedal locomotion, underactuation, deep reinforcement learning.', "keywords"),
    h("I", "Model the Floating Base and Contact"),
    p('Assume a free-standing humanoid with <i>n</i> actuated joints. Let '
      '<i>q</i> denote configuration and <i>v</i> generalized velocity. Between '
      'impacts, the floating-base dynamics are [1]'),
    Equation('<i>M(q) dv/dt + h(q, v) = Bτ + J</i><sub>c</sub>'
             '<super>T</super><i>λ</i>,<br/>'
             '<i>dq/dt = N(q)v</i>.', 1),
    p('<i>M</i> is inertia, <i>h</i> includes gravity and velocity terms, '
      '<i>B</i> maps joint torques <i>τ</i>, and <i>J</i><sub>c</sub><super>T</super> maps contact '
      'forces <i>λ</i>; <i>N</i> handles orientation kinematics. The base has six '
      'unactuated directions. Foot contact changes the available control authority: '
      'fixed flat-foot support can be fully actuated in reduced coordinates.'),
    p('Model unilateral, nonpenetrating contact, friction limits, and impact '
      'velocity resets. Foot forces come from the coupled contact dynamics. '
      'The policy influences base momentum through joint motion and ground '
      'reaction forces; it must learn when to shift weight and place the next foot.'),
    h("II", "Connect a Neural Policy to the Motors"),
    p('Use command <i>c</i> = (forward speed, lateral speed, yaw rate) and '
      'history <i>H</i> of IMU angular velocity, projected gravity, joint '
      'positions/velocities, and previous actions. A causal Transformer encodes '
      'this history to address partial observability [2].'),
    Equation('<i>a</i><sub>t</sub> ~ <i>π</i><sub>θ</sub>( · | <i>H</i><sub>t</sub>, '
             '<i>c</i><sub>t</sub>),<br/>'
             '<i>q</i><sub>des</sub> = <i>q</i><sub>nom</sub> + <i>D</i> tanh(<i>a</i><sub>t</sub>),<br/>'
             '<i>τ</i> = sat[<i>K</i><sub>p</sub>(<i>q</i><sub>des</sub> - '
             '<i>q</i><sub>a</sub>) - <i>K</i><sub>d</sub><i>v</i><sub>a</sub>].', 2),
    p('<i>θ</i> denotes policy parameters; <i>D</i> scales offsets about '
      '<i>q</i><sub>nom</sub>, and sat applies motor torque limits. Joint states '
      '<i>q</i><sub>a</sub>, <i>v</i><sub>a</sub> drive faster proportional-derivative '
      '(PD) loops. Match gains, action rates, and delays to the hardware.'),
    p('An asymmetric training critic can use simulator ground truth. '
      'The actor must use only deployment observations; privileged terrain '
      'or velocity signals must not leak into its inputs.'),
]

right = [
    h("III", "Train for Commanded Locomotion"),
    p('Train an actor and value critic with proximal policy optimization '
      '(PPO) [3] in parallel physics simulations. Collect rollouts, estimate '
      'advantages, update the actor with PPO\'s clipped objective, and fit '
      'the critic to return targets. Optimize the expected discounted return:'),
    Equation('max<sub><i>θ</i></sub> <i>J(θ)</i> = '
             'E<sub><i>π</i><sub>θ</sub></sub>'
             '[∑<sub><i>t</i>=0</sub><super><i>T</i>-1</super> '
             '<i>γ</i><super>t</super><i>r</i><sub>t</sub>].', 3),
    p('<i>T</i> is the task horizon and <i>γ</i> the discount factor; bootstrap '
      'values at nonterminal rollout truncations. '
      'Reward velocity/yaw tracking and upright locomotion; penalize falls, '
      'slip, collisions, effort, and abrupt action changes. Normalize terms '
      'before tuning weights. Test for shortcuts such as shuffling or hopping '
      'when the task calls for walking.'),
    h("IV", "Bridge Simulation and Hardware"),
    p('Identify link inertia, joint friction, motor response, and latency. '
      'Randomize mass, center of mass, ground friction, actuator strength, '
      'sensor noise, and delays over plausible ranges. Add pushes and a '
      'curriculum from standing and slow steps to turns and uneven terrain. '
      'Such simulation-trained policies have transferred to real humanoids [2]; '
      'transfer must be verified for the target robot.'),
    p('Freeze network weights and observation normalization for deployment. '
      'Use the policy mean with the same action transformation and filtering. '
      'Enforce actuator and command limits, monitor joint state and temperature, '
      'and provide an independent timeout/fall supervisor.'),
    h("V", "Measure What Generalizes"),
    p('Evaluate multiple training seeds on held-out terrains, payloads, '
      'disturbances, and latency. Compare with a model-based walking baseline '
      'using fall rate, command-tracking error, slip, energy per distance, '
      'torque saturation, and inference time. Progress from simulation to '
      'restrained hardware trials and supervised walking. Report tested '
      'conditions and failures; a successful rollout is not a stability proof.'),
    p('REFERENCES', "heading"),
    p('[1] R. Tedrake, <i>Underactuated Robotics</i>, "Planning and Control '
      'through Contact," MIT notes. '
      '<link href="https://underactuated.mit.edu/contact.html">'
      'underactuated.mit.edu/contact.html</link>.', "reference"),
    p('[2] I. Radosavovic <i>et al.</i>, "Real-world humanoid locomotion with '
      'reinforcement learning," <i>Science Robotics</i>, 9, eadi9579, 2024. '
      '<link href="https://doi.org/10.1126/scirobotics.adi9579">'
      'doi:10.1126/scirobotics.adi9579</link>.', "reference"),
    p('[3] J. Schulman <i>et al.</i>, "Proximal Policy Optimization '
      'Algorithms," 2017. <link href="https://arxiv.org/abs/1707.06347">'
      'arXiv:1707.06347</link>.', "reference"),
]

def measure(items):
    total = 0
    for item in items:
        _, height = item.wrap(COL_W, PAGE_H)
        total += item.getSpaceBefore() + height + item.getSpaceAfter()
    return total

def draw_column(c, items, x, top):
    y = top
    for item in items:
        y -= item.getSpaceBefore()
        _, height = item.wrap(COL_W, PAGE_H)
        y -= height
        item.drawOn(c, x, y)
        y -= item.getSpaceAfter()
    return y

def check_glyphs():
    missing = []
    for item in left + right:
        for frag in (item.par.frags if isinstance(item, Equation) else item.frags):
            face = pdfmetrics.getFont(frag.fontName).face
            for char in getattr(frag, 'text', ''):
                if char.strip() and hasattr(face, 'charToGlyph') and ord(char) not in face.charToGlyph:
                    missing.append((frag.fontName, hex(ord(char))))
    assert not missing, missing

if __name__ == '__main__':
    check_glyphs()
    heights = [measure(left), measure(right)]
    print(json.dumps({'column_heights_pt': heights, 'available_height_pt': TOP - BOTTOM}))
    if max(heights) > TOP - BOTTOM:
        raise RuntimeError('Content exceeds one-page layout; revise the copy.')
    c = canvas.Canvas(str(OUTPUT), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle('Underactuated Humanoid Locomotion')
    c.setAuthor('Santiago Restrepo')
    c.setCreator('ReportLab; humanoid/build_pdf.py')
    c.setSubject('Deep reinforcement learning method for humanoid bipedal walking')
    c.setKeywords('humanoid, bipedal locomotion, underactuation, deep learning, PPO, sim-to-real')
    c.setFont('TNR', 22)
    c.drawCentredString(PAGE_W / 2, 721, 'Underactuated Humanoid Locomotion')
    c.setFont('TNR', 11)
    c.drawCentredString(PAGE_W / 2, 680, 'Santiago Restrepo')
    c.setFont('TNR', 10)
    c.drawCentredString(PAGE_W / 2, 667, 'contact@waajacu.com     https://waajacu.com/')
    c.setFont('TNR-Italic', 10)
    c.drawCentredString(PAGE_W / 2, 650, 'Learning-based control method for bipedal walking')
    bottoms = [draw_column(c, left, MARGIN, TOP),
               draw_column(c, right, MARGIN + COL_W + GUTTER, TOP)]
    c.showPage()
    c.save()
    reader = PdfReader(OUTPUT)
    assert len(reader.pages) == 1
    text = reader.pages[0].extract_text()
    for phrase in ['Floating Base', 'Neural Policy', 'PPO', 'REFERENCES']:
        assert phrase.lower() in text.lower(), phrase
    assert '\ufffd' not in text
    print(json.dumps({'output': str(OUTPUT), 'pages': len(reader.pages),
                      'column_bottoms_pt': bottoms, 'text_characters': len(text),
                      'reference_links': len(reader.pages[0].get('/Annots', []))}))
