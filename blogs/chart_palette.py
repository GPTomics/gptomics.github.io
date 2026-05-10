'''Color palette for charts and figures across GPTomics blog posts.

Built to harmonize with the live site palette ('editorial single-warm'):
brand forest-green + editorial terracotta + ink type on ivory. The site
:root variables live in index.html / blog.html / blogs/make_blog.py.

Site anchors (locked):
  --brand     #2a7f62  forest green   biology / brand presence
  --editorial #b35a3f  terracotta     links, dates, pull-quote markers
  --ink       #0f231a  near-black     body text, headings, logo gradient terminus
  --bg        #fcfff9  ivory          page background

Brand green (ACCENT_GREEN) and terracotta (TERRACOTTA / CHART_NET) do
double duty here — the same colors that mark a link or a date in body
text also mark categorical series on a chart, so figures rhyme with
typography. The cool secondary in chart roles is SLATE_TEAL (CHART_GROSS)
and SLATE_TEAL_LIGHT (CHART_OPEX) — analogous to brand-green so the cool
side of every chart stays in the same OKLCH neighborhood as the brand.
ACCENT_BLUE (#2c6aa6) is retained as a constant but no longer used by
any CHART_* role; it was the page brand color before the move to
editorial single-warm and was dropped site-wide.

Design rationale (research synthesis):

The chart palette extends from the cool brand-green by mirroring it with
a custom warm arc spanning ~10-90 deg (crimson through ochre) — the move
FT, Stripe Press, and the NYT graphics desk use when their primary brand
sits on the cool side. Textbook split-complementary or triadic expansions
would cluster the warms or drop a clashing purple, neither of which fits
the editorial register.

Two craft rules from Color Supply, Paletton, FT Origami, and Datawrapper
guidance carry the palette:

1. Equal-lightness across categorical colors. Every primary chart color
   sits in OKLCH L 0.49-0.60 so no single series visually dominates.
   Tints and shades are reserved for sequential ramps, never used as
   different categories in the same chart.
2. Editorial chroma band. Every color sits in OKLCH C 0.07-0.14 — the
   range FT, NYT, and Datawrapper Tones occupy. Below 0.07 reads dusty
   on the warm ivory background; above 0.14 tips into Tableau defaults.

Sources: Evil Martians OKLCH guides; FT Origami o-colors palette;
ggthemes economist_pal; Datawrapper "colors for data vis style guides"
by Lisa Charlotte Muth; Paletton wiki; Color Supply harmony schemes;
Learn UI Design data-viz color guidance.
'''

INK = '#0f231a'
MUTED = '#3c5a4c'
BG = '#fcfff9'
BG_ALT = '#ffffff'
BORDER = '#dfe9e3'

ACCENT_GREEN = '#2a7f62'
GREEN_DARK = '#1c5a45'
GREEN_LIGHT = '#7eb59c'
GREEN_PALE = '#cfe2d8'

ACCENT_BLUE = '#2c6aa6'
BLUE_DARK = '#1d4a78'
BLUE_LIGHT = '#7ea7ce'
BLUE_PALE = '#d3e0ed'

TERRACOTTA = '#b35a3f'
TERRACOTTA_LIGHT = '#d49278'
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
CHART_GROSS_BREAKEVEN = ACCENT_GREEN
CHART_NET_BREAKEVEN = CRIMSON
CHART_COGS = AMBER
CHART_OPEX = SLATE_TEAL_LIGHT
CHART_AI_TOKENS = TERRACOTTA
CHART_ZERO_LINE = MUTED

CATEGORICAL = [ACCENT_GREEN, ACCENT_BLUE, TERRACOTTA, AMBER, CRIMSON, PLUM, SLATE_TEAL, OLIVE]

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
