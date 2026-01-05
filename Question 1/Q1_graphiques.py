# Auteur : Rémy Wilson
# Programme : Graphiques pour la première question de recherche
# Date: 29 Décembre 2025

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

zones_dict = {
    1: 'Ottawa Centre', 50: 'Ottawa Inner Area', 100: 'Ottawa East',
    120: 'Beacon Hill', 140: 'Alta Vista', 180: 'Hunt Club',
    200: 'Merivale', 240: 'Ottawa West', 260: 'Bayshore/Cedarview',
    300: 'Orleans', 350: 'Rural East', 360: 'Rural Southeast',
    400: 'South Gloucester/Letrim', 425: 'South Nepean', 450: 'Rural Southwest',
    500: 'Kanata/Stittsville', 560: 'Rural West', 600: 'Île de Hull',
    625: 'Hull Périphérie', 650: 'Plateau', 700: 'Aylmer',
    750: 'Rural Northwest', 800: 'Gatineau Centre', 820: 'Gatineau Est',
    840: 'Rural Northeast', 845: 'Masson-Angers'
}

sector_classification = {
    'Centre-ville': [1, 50, 100, 240, 600, 800],
    'Banlieue intérieure': [120, 140, 180, 200, 260, 625, 650, 700, 820],
    'Banlieue extérieure': [300, 400, 425, 500, 350, 360, 450, 560, 750, 840, 845]
}

mode_categories = {
    'Auto': [1, 2],
    'Transport en commun': [3, 4, 5],
    'Modes actifs': [6, 7, 14, 15],
    'Autres': [8, 9, 10, 11, 13, 16, 18, 21, 22, 23, 24, 77]
}


def classify_sector(zone):
    for sector, zones in sector_classification.items():
        if zone in zones:
            return sector
    return 'Autre'


def classify_mode(mode):
    for category, modes in mode_categories.items():
        if mode in modes:
            return category
    return 'Autres'


def apply_classification(df, origin_col='originreportzone', mode_col='modeprimary', drop_autre=True):
    df = df.copy()
    df['origin_sector'] = df[origin_col].apply(classify_sector)
    df['mode_category'] = df[mode_col].apply(classify_mode)
    if drop_autre:
        df = df[df['origin_sector'] != 'Autre']
    return df


def prepare_crosstab(df, origin_col='origin_sector', mode_col='mode_category',
                     sector_order=None, mode_order=None, normalize=True):
    sector_order = sector_order or ['Centre-ville', 'Banlieue intérieure', 'Banlieue extérieure']
    mode_order = mode_order or ['Auto', 'Transport en commun', 'Modes actifs', 'Autres']

    crosstab = pd.crosstab(df[origin_col], df[mode_col], normalize='index' if normalize else None)
    if normalize:
        crosstab = crosstab * 100

    crosstab = crosstab.reindex([s for s in sector_order if s in crosstab.index])
    present_modes = [m for m in mode_order if m in crosstab.columns]
    crosstab = crosstab[present_modes]
    return crosstab


def plot_from_crosstab(crosstab_df, title=None, colors=None, figsize=(12, 7)):
    colors = colors or {
        'Auto': '#ff6361',
        'Transport en commun': '#003f5c',
        'Modes actifs': '#58508d',
        'Autres': '#ffa600'
    }

    fig, ax = plt.subplots(figsize=figsize)

    crosstab_df.plot(
        kind='bar',
        stacked=True,
        ax=ax,
        color=[colors.get(col, '#95a5a6') for col in crosstab_df.columns],
        width=0.6, fontsize=16
    )

    ax.set_xlabel('Secteur de résidence', fontsize=16, fontweight='bold')
    ax.set_ylabel('Pourcentage des déplacements (%)', fontsize=16, fontweight='bold')
    ax.set_title(title or 'Distribution modale par secteur de résidence',
                 fontsize=20, fontweight='bold', pad=15)

    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

    ax.legend(
        title='Mode de transport',
        title_fontsize=16,
        fontsize=14,
        loc='upper left',
        bbox_to_anchor=(1.02, 1),
        frameon=True
    )
    ax.yaxis.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    ax.set_ylim(0, 100)

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    df = pd.read_csv('_CLEANDATA_.csv')

    df_classified = apply_classification(df)
    crosstab = prepare_crosstab(df_classified)
    plot_from_crosstab(crosstab)