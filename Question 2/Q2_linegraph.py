# Auteur : Rémy Wilson
# Programme : Graphiques à ligne brisée pour la deuxième question
# Date: 31 Décembre 2025

import pandas as pd
import matplotlib.pyplot as plt

purpose_map = {
    'Travail': [10, 11, 12],
    'Études': [20, 30],
    'Achats': [40, 41],
    'Loisirs': [44, 45, 46],
    'Retour': [80],
    'Passagers': [51, 52],
    'Autre': [43, 777, 888]
}

mode_map = {
    'Auto': [1, 2],
    'Transport en commun': [3, 4, 5],
    'Modes actifs': [6, 7, 14, 15],
    'Autres': [8, 9, 10, 11, 13, 16, 18, 21, 22, 23, 24, 77]
}

time_periods = {
    'Matin pointe (6h-9h)': (600, 900),
    'Jour (9h-16h)': (900, 1600),
    'PM pointe (16h-19h)': (1600, 1900),
    'Soir (19h+)': (1900, 2800)
}

colors = {
    'Auto': '#E63946',
    'Transport en commun': '#457B9D',
    'Modes actifs': '#2A9D8F',
    'Autres': '#B8B8B8'
}

purpose_colors = {
    'Travail': '#003f5c',
    'Études': '#58508d',
    'Achats': '#bc5090',
    'Loisirs': '#ff6361',
    'Retour': '#ffa600',
    'Passagers': '#8A2BE2',
    'Autre': '#95a5a6'
}


def classify_purpose(code):
    for purpose, codes in purpose_map.items():
        if code in codes:
            return purpose
    return 'Autre'


def classify_mode(code):
    for mode, codes in mode_map.items():
        if code in codes:
            return mode
    return 'Autres'


def classify_time_period(time):
    for period, (start, end) in time_periods.items():
        if start <= time < end:
            return period
    return 'Autre'


def get_hour(time):
    if time >= 2400:
        return (time - 2400) // 100
    return time // 100


def prepare_data(df):
    df = df.copy()
    df['trip_purpose'] = df['trippurpose'].apply(classify_purpose)
    df['mode_category'] = df['modeprimary'].apply(classify_mode)
    df['time_period'] = df['departtime'].apply(classify_time_period)
    df['hour'] = df['departtime'].apply(get_hour)
    df = df[df['time_period'] != 'Autre']
    return df


def plot_profiles(df, figsize=(14, 7)):
    fig, ax = plt.subplots(figsize=figsize)

    main_purposes = ['Travail', 'Études', 'Achats', 'Loisirs', 'Retour', 'Passagers', 'Autre']

    for purpose in main_purposes:
        df_purpose = df[df['trip_purpose'] == purpose]
        hourly_counts = df_purpose.groupby('hour').size()

        ax.plot(hourly_counts.index, hourly_counts.values,
                linewidth=3, marker='o', markersize=6,
                label=purpose, color=purpose_colors[purpose], alpha=0.8)

    ax.set_xlabel('Heure de la journée', fontsize=16, fontweight='bold')
    ax.set_ylabel('Nombre de déplacements', fontsize=16, fontweight='bold')
    ax.set_title('Déplacements temporels par motif de déplacement',
                 fontsize=20, fontweight='bold', pad=15)
    ax.legend(title_fontsize=16, fontsize=14, loc='upper right', framealpha=0.9)
    ax.grid(alpha=0.3, linestyle='--')
    ax.set_xlim(4, 24)

    plt.tight_layout()
    plt.show()


def plot_hourly(df, figsize=(12, 5)):
    fig, ax = plt.subplots(figsize=figsize)
    hourly_counts = df.groupby('hour').size().reindex(range(0, 30), fill_value=0)

    ax.plot(hourly_counts.index, hourly_counts.values,
            linewidth=3, marker='o', markersize=6,
            color='#2F4F4F', label='Total')

    ax.set_xlabel('Heure de la journée', fontsize=16, fontweight='bold')
    ax.set_ylabel('Nombre de déplacements', fontsize=16, fontweight='bold')
    ax.set_title('Nombre total de déplacements par heure', fontsize=20, fontweight='bold', pad=15)
    ax.grid(alpha=0.3, linestyle='--')
    ax.set_xlim(5, 24)
    ax.set_xticks(list(range(5, 24)))

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    df = pd.read_csv('_CLEANDATA_.csv')

    df_prepared = prepare_data(df)
    plot_profiles(df_prepared)
    plot_hourly(df_prepared)