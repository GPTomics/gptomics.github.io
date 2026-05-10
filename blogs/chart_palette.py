'''Color palette for charts and figures across GPTomics blog posts.

Built to harmonize with the live site palette ('iris triadic'):
iris violet brand + warm red editorial + cyan spark + violet-undertoned ink
on lavender ivory. The site :root variables live in index.html /
blog.html / blogs/make_blog.py.

Site anchors (locked):
  --brand     #5d44a8  iris violet    biology / brand presence
  --editorial #c2483a  warm red       links, dates, pull-quote markers
  --spark     #00b7f3  electric cyan  decoration only (never text): blockquote bar, .hl highlight, hover shadows
  --ink       #16122e  violet-near-black  body text, headings
  --bg        #fbfafe  lavender ivory page background

Iris brand (ACCENT_IRIS) and warm red (TERRACOTTA / CHART_NET) do double
duty here — the same colors that mark a link or a date in body text also
mark categorical series on a chart, so figures rhyme with typography.
The cool secondary in chart roles is SLATE_TEAL (CHART_GROSS) and
SLATE_TEAL_LIGHT (CHART_OPEX) — broad analogous to brand-iris on the
cool side of the wheel (iris ~285 deg, slate-teal ~225 deg), so the cool
side of every chart stays in the same OKLCH neighborhood as the brand
and rhymes with the cyan spark above it.

Legacy constants ACCENT_GREEN (#2a7f62) and ACCENT_BLUE (#2c6aa6) are
retained but no longer used by any CHART_* role; they were the page
brand colors in earlier palettes (editorial single-warm and pre-2025
bilingual cool, respectively) and have been dropped site-wide.

Design rationale (research synthesis):

The chart palette extends from the cool brand-iris by mirroring it with
a custom warm arc spanning ~10-90 deg (warm red through ochre) — the
move FT, Stripe Press, and the NYT graphics desk use when their primary
brand sits on the cool side. Textbook split-complementary or triadic
expansions would cluster the warms or drop a clashing yellow-green,
neither of which fits the editorial register.

Two craft rules from Color Supply, Paletton, FT Origami, and Datawrapper
guidance carry the palette:

1. Equal-lightness across categorical colors. Every primary chart color
   sits in OKLCH L 0.45-0.60 so no single series visually dominates.
   Tints and shades are reserved for sequential ramps, never used as
   different categories in the same chart.
2. Editorial chroma band. Every primary chart color sits in OKLCH
   C 0.07-0.18 — the range FT, NYT, and Datawrapper Tones occupy. Below
   0.07 reads dusty on the lavender ivory; above 0.18 tips into Tableau
   defaults. (ACCENT_CYAN_BRIGHT is the one exception — it sits above
   the band and is reserved for highlight/annotation moments, never
   used as a standard categorical series.)

Sources: Evil Martians OKLCH guides; FT Origami o-colors palette;
ggthemes economist_pal; Datawrapper "colors for data vis style guides"
by Lisa Charlotte Muth; Paletton wiki; Color Supply harmony schemes;
Learn UI Design data-viz color guidance.
'''

INK = '#16122e'
MUTED = '#4d4666'
BG = '#fbfafe'
BG_ALT = '#ffffff'
BORDER = '#e4dff0'

ACCENT_IRIS = '#5d44a8'
IRIS_DARK = '#3e2c7d'
IRIS_LIGHT = '#9d8fcb'
IRIS_PALE = '#d4cce4'

ACCENT_CYAN_BRIGHT = '#00b7f3'

ACCENT_GREEN = '#2a7f62'
GREEN_DARK = '#1c5a45'
GREEN_LIGHT = '#7eb59c'
GREEN_PALE = '#cfe2d8'

ACCENT_BLUE = '#2c6aa6'
BLUE_DARK = '#1d4a78'
BLUE_LIGHT = '#7ea7ce'
BLUE_PALE = '#d3e0ed'

TERRACOTTA = '#c2483a'
TERRACOTTA_LIGHT = '#dc8676'
AMBER = '#a8842c'
AMBER_LIGHT = '#cfae6b'
CRIMSON = '#9c3a55'
PLUM = '#7a4775'
SLATE_TEAL = '#3a7588'
SLATE_TEAL_LIGHT = '#94b3bd'
OLIVE = '#7e8a3a'

CHART_REVENUE = INK
CHART_GRID = BORDER
CHART_AXIS = MUTED
CHART_GROSS = SLATE_TEAL
CHART_NET = TERRACOTTA
CHART_GROSS_BREAKEVEN = ACCENT_IRIS
CHART_NET_BREAKEVEN = CRIMSON
CHART_COGS = AMBER
CHART_OPEX = SLATE_TEAL_LIGHT
CHART_AI_TOKENS = TERRACOTTA
CHART_ZERO_LINE = MUTED

CATEGORICAL = [ACCENT_IRIS, SLATE_TEAL, TERRACOTTA, AMBER, CRIMSON, PLUM, SLATE_TEAL_LIGHT, OLIVE]

WEB_FONT_STACK = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"


def matplotlib_rc():
    '''Return rcParams that align matplotlib defaults with the site theme.'''
    return {
        'figure.facecolor': BG,
        'axes.facecolor': BG,
        'savefig.facecolor': BG,
        'savefig.transparent': False,
        'axes.edgecolor': MUTED,
        'axes.labelcolor': INK,
        'axes.titlecolor': INK,
        'xtick.color': MUTED,
        'ytick.color': MUTED,
        'text.color': INK,
        'grid.color': BORDER,
        'grid.linewidth': 0.6,
        'axes.linewidth': 0.7,
        'xtick.major.width': 0.7,
        'ytick.major.width': 0.7,
        'font.family': 'sans-serif',
        'font.sans-serif': ['Helvetica Neue', 'Helvetica', 'Arial', 'DejaVu Sans'],
        'font.size': 11.5,
        'axes.titlesize': 13,
        'axes.titleweight': 'semibold',
        'axes.labelsize': 11.5,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'legend.frameon': False,
        'legend.fontsize': 10.5,
        'svg.fonttype': 'none',
    }


def rewrite_svg_font(svg_path, stack=WEB_FONT_STACK):
    '''Replace matplotlib's emitted font-family with the full site web font stack.

    matplotlib emits a single resolved font name into the SVG (e.g. "Helvetica Neue").
    Browsers handle that fine, but to inherit the host page's exact system-ui look
    we substitute the full CSS stack so it cascades the same way as body text.
    '''
    import re
    text = svg_path.read_text() if hasattr(svg_path, 'read_text') else open(svg_path).read()
    text = re.sub(r"font-family:[^;\"]+", f'font-family:{stack}', text)
    text = re.sub(r'font-family="[^"]+"', f'font-family="{stack}"', text)
    if hasattr(svg_path, 'write_text'):
        svg_path.write_text(text)
    else:
        open(svg_path, 'w').write(text)
