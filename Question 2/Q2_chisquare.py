# Auteur : Rémy Wilson
# Programme : Heatmap des résidus et test chi-carré.
# Date: 31 Décembre 2025

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl

df = pd.read_csv("_CLEANDATA_.csv")

COL_PURPOSE = "trippurpose"
COL_MODE = "modeprimary"

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

def map_category(val, mapping):
    for k, codes in mapping.items():
        if val in codes:
            return k
    return np.nan

df["purpose_cat"] = df[COL_PURPOSE].apply(lambda x: map_category(x, purpose_map))
df["mode_cat"] = df[COL_MODE].apply(lambda x: map_category(x, mode_map))
df = df.dropna(subset=["purpose_cat", "mode_cat"])

time_periods = {
    'Matin pointe': (600, 900),
    'Jour': (900, 1600),
    'PM pointe': (1600, 1900),
    'Soir': (1900, 2800)
}

def map_time(t):
    for k, (a, b) in time_periods.items():
        if a <= t < b:
            return k
    return np.nan

df["time_cat"] = df["departtime"].apply(map_time)
df = df.dropna(subset=["time_cat"])

periods = list(time_periods.keys())
resid_dict = {}
stats = {}
max_abs = 0.0

for period in periods:
    sub = df[df["time_cat"] == period]
    observed = pd.crosstab(sub["purpose_cat"], sub["mode_cat"])

    if observed.shape[0] < 2 or observed.shape[1] < 2:
        resid_dict[period] = None
        continue

    chi2, p, dof, expected = chi2_contingency(observed)
    residuals = (observed - expected) / np.sqrt(expected)

    resid_dict[period] = residuals
    stats[period] = (chi2, p, dof, observed.sum().sum())
    max_abs = max(max_abs, residuals.abs().values.max())

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
axes = axes.flatten()

for ax, period in zip(axes, periods):
    residuals = resid_dict.get(period)

    sns.heatmap(
        residuals,
        annot=True,
        fmt=".1f",
        cmap="coolwarm",
        center=0,
        vmin=-max_abs,
        vmax=max_abs,
        annot_kws={"fontsize": 14, "fontweight": "bold"},
        ax=ax,
        cbar=False
    )

    ax.set_title(period, fontsize=16, fontweight='bold')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.tick_params(axis='x', labelrotation=30)
    ax.tick_params(axis='y', labelrotation=0)
    ax.tick_params(axis='both', labelsize=10)

norm = mpl.colors.Normalize(vmin=-max_abs, vmax=max_abs)
sm = mpl.cm.ScalarMappable(cmap="coolwarm", norm=norm)
sm.set_array([])

fig.subplots_adjust(
    left=0.16,   # wider plots, still enough room for Y label
    right=0.86,
    top=0.90,
    bottom=0.12,
    wspace=0.40,
    hspace=0.35
)

cbar_ax = fig.add_axes([0.88, 0.15, 0.02, 0.7])
cbar = fig.colorbar(sm, cax=cbar_ax)
cbar.set_label("Résidus standardisés", fontsize=13, fontweight='bold')

fig.suptitle("Résidus standardisés : Motif × Mode par période",
             fontsize=20, fontweight='bold')

fig.text(0.5, 0.05, 'Mode', ha='center',
         fontsize=14, fontweight='bold')

fig.text(0.085, 0.5, 'Motif de déplacement',
         va='center', rotation='vertical',
         fontsize=14, fontweight='bold')

plt.show()