'''Render the two cost-economics SVG figures from the blog's underlying model.

Recreates the math from blogs/cost_economics_modeling.ipynb (which lives next to
the source markdown in ~/Documents/essays/cost economics) using the cached
chart_palette so the figures harmonize with the live site theme.
'''

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chart_palette as p

OUT_DIR = Path(__file__).resolve().parent.parent / 'blog' / 'assets' / 'how_ai_changes_software_pnl'

TOTAL_USERS = 1_000_000
N_USERS = np.linspace(1, TOTAL_USERS, 1000)
REVENUE_PER_USER = 120

SAAS_FIXED_BASE = 25_000_000
SAAS_FIXED_STEP_PCT = 0.10
SAAS_OPEX_RATE = 0
SAAS_C_FLOOR = 24
SAAS_ALPHA = 176
SAAS_BASELINE_COGS = SAAS_C_FLOOR * 100 + SAAS_ALPHA * np.sqrt(100)

AI_FIXED_BASE = SAAS_FIXED_BASE / 10
AI_TOKEN_COST = 75


def saas_series(n_users):
    var_cost = SAAS_C_FLOOR + SAAS_ALPHA / np.sqrt(n_users)
    revenue = REVENUE_PER_USER * n_users
    cogs = SAAS_BASELINE_COGS + var_cost * n_users
    opex = SAAS_OPEX_RATE * revenue
    fixed = SAAS_FIXED_BASE * (1 + SAAS_FIXED_STEP_PCT * np.floor(np.log2(np.maximum(n_users, 1))))
    total = cogs + opex + fixed
    profit = revenue - total
    gross = (revenue - cogs) / revenue
    net = profit / revenue
    breakeven_net = n_users[np.argmax(profit > 0)]
    breakeven_gross = np.ceil(((SAAS_ALPHA + np.sqrt(SAAS_ALPHA**2 + 4 * (REVENUE_PER_USER - SAAS_C_FLOOR) * SAAS_BASELINE_COGS)) / (2 * (REVENUE_PER_USER - SAAS_C_FLOOR)))**2)
    return revenue, cogs, opex + fixed, gross, net, breakeven_gross, breakeven_net


def ai_series(n_users):
    revenue = REVENUE_PER_USER * n_users
    infra = SAAS_BASELINE_COGS + (SAAS_C_FLOOR + SAAS_ALPHA / np.sqrt(n_users)) * n_users
    tokens = AI_TOKEN_COST * n_users
    cogs = infra + tokens
    fixed = AI_FIXED_BASE * (1 + SAAS_FIXED_STEP_PCT * np.floor(np.log2(np.maximum(n_users, 1))))
    total = cogs + fixed
    profit = revenue - total
    gross = (revenue - cogs) / revenue
    net = profit / revenue
    breakeven_net = n_users[np.argmax(profit > 0)]
    breakeven_gross = np.ceil(((SAAS_ALPHA + np.sqrt(SAAS_ALPHA**2 + 4 * (REVENUE_PER_USER - SAAS_C_FLOOR - AI_TOKEN_COST) * SAAS_BASELINE_COGS)) / (2 * (REVENUE_PER_USER - SAAS_C_FLOOR - AI_TOKEN_COST)))**2)
    return revenue, infra, tokens, fixed, gross, net, breakeven_gross, breakeven_net


def style_axis(ax):
    ax.grid(alpha=0.55, linewidth=0.6, color=p.BORDER)
    ax.tick_params(colors=p.MUTED, length=3)
    for spine in ('left', 'bottom'):
        ax.spines[spine].set_color(p.MUTED)


def place_legend(ax, ncol):
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.18), ncol=ncol, frameon=False, handlelength=1.8, columnspacing=1.6, handletextpad=0.6)


def save_figure(fig, out):
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.30)
    fig.savefig(out, format='svg', bbox_inches='tight', facecolor=p.BG)
    plt.close(fig)
    p.rewrite_svg_font(out)
    print(f'wrote {out}')


def render_saas():
    revenue, cogs, build_opex, gross, net, be_g, be_n = saas_series(N_USERS)

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))

    axes[0].stackplot(N_USERS, cogs, build_opex, labels=['COGS', 'Build & opex'], colors=[p.CHART_COGS, p.BLUE_LIGHT], alpha=0.9, edgecolor=p.BG, linewidth=0.4)
    axes[0].plot(N_USERS, revenue, color=p.CHART_REVENUE, linewidth=2.0, label='Revenue')
    axes[0].axvline(be_g, color=p.CHART_GROSS_BREAKEVEN, linestyle=':', linewidth=1.4, label=f'Gross Break-even: {be_g:.0f} users')
    axes[0].axvline(be_n, color=p.CHART_NET_BREAKEVEN, linestyle=':', linewidth=1.4, label=f'Net Break-even: {be_n / 1e3:.0f}K users')
    axes[0].set_xlabel('Users [Million]')
    axes[0].set_ylabel('Revenue [Hundred-Million $]')
    axes[0].set_title('Revenue & Costs')
    place_legend(axes[0], ncol=3)
    style_axis(axes[0])

    axes[1].plot(N_USERS, gross * 100, color=p.CHART_GROSS, linewidth=2.0, label='Gross margin')
    axes[1].plot(N_USERS, net * 100, color=p.CHART_NET, linewidth=2.0, label='Net margin')
    axes[1].axhline(0, color=p.CHART_ZERO_LINE, linestyle='--', linewidth=0.7)
    axes[1].axvline(be_g, color=p.CHART_GROSS_BREAKEVEN, linestyle=':', linewidth=1.4, label=f'Gross Break-even: {be_g:.0f} users')
    axes[1].axvline(be_n, color=p.CHART_NET_BREAKEVEN, linestyle=':', linewidth=1.4, label=f'Net Break-even: {be_n / 1e3:.0f}K users')
    axes[1].set_xlabel('Users [Million]')
    axes[1].set_ylabel('Margin [%]')
    axes[1].set_title('Gross & Net Margin')
    axes[1].set_ylim(-100, 100)
    place_legend(axes[1], ncol=2)
    style_axis(axes[1])

    save_figure(fig, OUT_DIR / 'figure_1.svg')


def render_ai():
    revenue, infra, tokens, fixed, gross, net, be_g, be_n = ai_series(N_USERS)

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))

    axes[0].stackplot(N_USERS, infra, tokens, fixed, labels=['Infra COGS', 'AI tokens', 'Build & opex'], colors=[p.CHART_COGS, p.CHART_AI_TOKENS, p.BLUE_LIGHT], alpha=0.9, edgecolor=p.BG, linewidth=0.4)
    axes[0].plot(N_USERS, revenue, color=p.CHART_REVENUE, linewidth=2.0, label='Revenue')
    axes[0].axvline(be_g, color=p.CHART_GROSS_BREAKEVEN, linestyle=':', linewidth=1.4, label=f'Gross Break-even: {be_g:.0f} users')
    axes[0].axvline(be_n, color=p.CHART_NET_BREAKEVEN, linestyle=':', linewidth=1.4, label=f'Net Break-even: {be_n / 1e3:.0f}K users')
    axes[0].set_xlabel('Users [Million]')
    axes[0].set_ylabel('Revenue [Hundred-Million $]')
    axes[0].set_title('Revenue & Costs')
    place_legend(axes[0], ncol=3)
    style_axis(axes[0])

    axes[1].plot(N_USERS, gross * 100, color=p.CHART_GROSS, linewidth=2.0, label='Gross margin')
    axes[1].plot(N_USERS, net * 100, color=p.CHART_NET, linewidth=2.0, label='Net margin')
    axes[1].axhline(0, color=p.CHART_ZERO_LINE, linestyle='--', linewidth=0.7)
    axes[1].axvline(be_g, color=p.CHART_GROSS_BREAKEVEN, linestyle=':', linewidth=1.4, label=f'Gross Break-even: {be_g:.0f} users')
    axes[1].axvline(be_n, color=p.CHART_NET_BREAKEVEN, linestyle=':', linewidth=1.4, label=f'Net Break-even: {be_n / 1e3:.0f}K users')
    axes[1].set_xlabel('Users [Million]')
    axes[1].set_ylabel('Margin [%]')
    axes[1].set_title('Gross & Net Margin')
    axes[1].set_ylim(-100, 100)
    place_legend(axes[1], ncol=2)
    style_axis(axes[1])

    save_figure(fig, OUT_DIR / 'figure_2.svg')


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(p.matplotlib_rc())
    render_saas()
    render_ai()


if __name__ == '__main__':
    main()
