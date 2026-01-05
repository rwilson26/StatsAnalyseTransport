# Auteur : Rémy Wilson
# Programme : Création d'un csv avec tableaux de contingence
# Date: 31 Décembre 2025

import pandas as pd
import numpy as np

sector_map = {
    'Centre-ville': [1, 50, 100, 240, 600, 800],
    'Banlieue intérieure': [120, 140, 180, 200, 260, 625, 650, 700, 820],
    'Banlieue extérieure': [300, 400, 425, 500, 350, 360, 450, 560, 750, 840, 845]
}

mode_map = {
    'Auto': [1, 2],
    'Transport en commun': [3, 4, 5],
    'Modes actifs': [6, 7, 14, 15],
    'Autres': [8, 9, 10, 11, 13, 16, 18, 21, 22, 23, 24, 77]
}

def classify_sector(code):
    for sector, codes in sector_map.items():
        if code in codes:
            return sector
    return 'Autre'

def classify_mode(code):
    for mode, codes in mode_map.items():
        if code in codes:
            return mode
    return 'Autres'


def create_comprehensive_table(df):
    df = df.copy()
    df['origin_sector'] = df['originreportzone'].apply(classify_sector)
    df['mode_category'] = df['modeprimary'].apply(classify_mode)
    df = df[df['origin_sector'] != 'Autre']

    freq_table = pd.crosstab(
        df['origin_sector'],
        df['mode_category'],
        margins=True,
        margins_name='TOTAL'
    )

    pct_by_sector = pd.crosstab(
        df['origin_sector'],
        df['mode_category'],
        normalize='index'
    ) * 100

    pct_by_mode = pd.crosstab(
        df['origin_sector'],
        df['mode_category'],
        normalize='columns'
    ) * 100

    pct_total = pd.crosstab(
        df['origin_sector'],
        df['mode_category'],
        normalize='all'
    ) * 100

    df['mode_sustainable'] = df['mode_category'].apply(
        lambda x: 'Durable (TC+Actif)' if x in ['Transport en commun', 'Modes actifs'] else 'Auto/Autres'
    )

    sustainable_table = pd.crosstab(
        df['origin_sector'],
        df['mode_sustainable'],
        normalize='index'
    ) * 100

    dominant_mode = pct_by_sector.idxmax(axis=1)

    ratio_auto_sustainable = []
    for sector in pct_by_sector.index:
        auto = pct_by_sector.loc[sector, 'Auto']
        tc = pct_by_sector.loc[sector, 'Transport en commun']
        actif = pct_by_sector.loc[sector, 'Modes actifs']
        ratio = auto / (tc + actif) if (tc + actif) > 0 else np.inf
        ratio_auto_sustainable.append(ratio)

    diversity_index = []
    for sector in pct_by_sector.index:
        probs = pct_by_sector.loc[sector].values / 100
        probs = probs[probs > 0]
        diversity = -np.sum(probs * np.log(probs))
        diversity_index.append(diversity)

    summary_stats = pd.DataFrame({
        'Déplacements (n)': freq_table.drop('TOTAL', errors='ignore').sum(axis=1),
        'Mode dominant': dominant_mode,
        'Part dominante (%)': pct_by_sector.max(axis=1).round(1),
        'TC + Actifs (%)': (pct_by_sector['Transport en commun'] + pct_by_sector['Modes actifs']).round(1),
        'Ratio Auto/(TC+Actifs)': [f'{r:.2f}' for r in ratio_auto_sustainable],
        'Diversité modale': [f'{d:.3f}' for d in diversity_index]
    })

    return {
        'frequencies': freq_table,
        'pct_by_sector': pct_by_sector,
        'pct_by_mode': pct_by_mode,
        'pct_total': pct_total,
        'sustainable': sustainable_table,
        'summary': summary_stats
    }


def export_to_csv(tables, filename='analyse_contingence_q1.xlsx'):
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        tables['frequencies'].to_excel(writer, sheet_name='Fréquences')
        tables['pct_by_sector'].to_excel(writer, sheet_name='Pct par secteur')
        tables['pct_by_mode'].to_excel(writer, sheet_name='Pct par mode')
        tables['sustainable'].to_excel(writer, sheet_name='Modes durables')
        tables['summary'].to_excel(writer, sheet_name='Statistiques')
    
if __name__ == '__main__':
    df = pd.read_csv('_CLEANDATA_.csv')
    tables = create_comprehensive_table(df)
    export_to_csv(tables)