# Auteur : Rémy Wilson
# Programme : 2 heatmap pour tendances temporelles par motif et mode.
# Date: 31 Décembre 2025

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

zone_map = {
    'Centre-ville': [1, 50, 100, 240, 600, 800],
    'Banlieue intérieure': [120, 140, 180, 200, 260, 625, 650, 700, 820],
    'Banlieue extérieure': [300, 400, 425, 500, 350, 360, 450, 560, 750, 840, 845]
}

df = pd.read_csv("_CLEANDATA_.csv")

cdf = df.copy()
cdf['departtime'] = pd.to_numeric(cdf['departtime'], errors='coerce')

hh_vals = (cdf['departtime'] // 100)
mm_vals = cdf['departtime'] - hh_vals * 100
valid_time = cdf['departtime'].between(0, 2959) & hh_vals.between(0, 29) & mm_vals.between(0, 59)
cdf.loc[~valid_time, 'departtime'] = np.nan

hh_vals = (cdf['departtime'] // 100)
mm_vals = cdf['departtime'] - hh_vals * 100
cdf['dep_hour'] = hh_vals

zone_rev = {}
for zname, zlist in zone_map.items():
    for z in zlist:
        zone_rev[int(z)] = zname

def map_zone(series):
    ser_num = pd.to_numeric(series, errors='coerce')
    return ser_num.map(zone_rev).fillna('Autre / hors liste')

cdf['origin_zone_group'] = map_zone(cdf['originreportzone'])
cdf['dest_zone_group'] = map_zone(cdf['destreportzone'])

purpose_map = {
    'Travail': [10, 11, 12],
    'Études': [20, 30],
    'Achats': [40, 41],
    'Loisirs': [44, 45, 46],
    'Retour': [80],
    'Passagers': [51, 52],
    'Autre': [43, 777, 888]
}

purpose_rev = {}
for name, codes in purpose_map.items():
    for code in codes:
        purpose_rev[code] = name

mode_categories = {
    'Auto': [1, 2],
    'Transport en commun': [3, 4, 5],
    'Modes actifs': [6, 7, 14, 15],
    'Autres': [8, 9, 10, 11, 13, 16, 18, 21, 22, 23, 24, 77]
}

mode_rev = {}
for name, codes in mode_categories.items():
    for code in codes:
        mode_rev[code] = name

cdf['purpose_group'] = pd.to_numeric(cdf['trippurpose'], errors='coerce').map(purpose_rev).fillna('Autre')
cdf['mode_group'] = pd.to_numeric(cdf['modeprimary'], errors='coerce').map(mode_rev).fillna('Autres')

if 'time_period' not in cdf.columns:
    time_periods = {
        'Matin pointe': (600, 900),
        'Jour': (900, 1600),
        'PM pointe': (1600, 1900),
        'Soir': (1900, 2800)
    }
    cdf['time_period'] = pd.NA
    for name, (start_hhmm, end_hhmm) in time_periods.items():
        mask = cdf['departtime'].between(start_hhmm, end_hhmm - 1)
        cdf.loc[mask, 'time_period'] = name

piv_purpose = (cdf.dropna(subset=['dep_hour'])
               .groupby(['purpose_group', 'dep_hour']).size()
               .reset_index(name='trips'))
piv_purpose['purpose_total'] = piv_purpose.groupby('purpose_group')['trips'].transform('sum')
piv_purpose['share_within_purpose'] = piv_purpose['trips'] / piv_purpose['purpose_total']
heat_purpose = piv_purpose.pivot(index='purpose_group', columns='dep_hour', values='share_within_purpose').fillna(0)

plt.figure(figsize=(12,4))
sns.heatmap(heat_purpose, cmap='viridis')
plt.title('Horaire des départs par motif', fontsize=20, fontweight='bold', pad=15)
plt.xlabel('Heure', fontsize=16, fontweight='bold')
plt.ylabel('Motif de déplacement', fontsize=16, fontweight='bold')
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.tight_layout()
plt.show()

piv_mode = (cdf.dropna(subset=['dep_hour'])
            .groupby(['mode_group', 'dep_hour']).size()
            .reset_index(name='trips'))
piv_mode['mode_total'] = piv_mode.groupby('mode_group')['trips'].transform('sum')
piv_mode['share_within_mode'] = piv_mode['trips'] / piv_mode['mode_total']
heat_mode = piv_mode.pivot(index='mode_group', columns='dep_hour', values='share_within_mode').fillna(0)

plt.figure(figsize=(12,3))
sns.heatmap(heat_mode, cmap='magma')
plt.title('Horaire des départs par mode', fontsize=20, fontweight='bold', pad=15)
plt.xlabel('Heure', fontsize=16, fontweight='bold')
plt.ylabel('Mode de transport', fontsize=16, fontweight='bold')
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.tight_layout()
plt.show()