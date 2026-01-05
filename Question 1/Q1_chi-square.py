# Auteur : Rémy Wilson
# Programme : Création d'un test chi-carré avec résidus.
# Date: 30 Décembre 2025

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("_CLEANDATA_.csv")
observed = pd.crosstab(df["originreportzone"], df["modeprimary"])
chi2, p, dof, expected = chi2_contingency(observed)
residuals = (observed - expected) / np.sqrt(expected)

plt.figure(figsize=(15, 8))
ax = sns.heatmap(residuals, annot=True, fmt=".1f", cmap="coolwarm", center=0, annot_kws={'fontsize':14, 'fontweight':'bold'})
cbar = ax.collections[0].colorbar
cbar.set_label('Résidus Standarisés', fontsize=16, fontweight='bold')

plt.title("Résidus standardisés du chi-carré : Secteur x Mode", fontsize=20, fontweight='bold', pad=15)
plt.xlabel("Mode", fontsize=16, fontweight='bold')
plt.ylabel("Secteur d'origine", fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()

contingency = pd.crosstab(df["originreportzone"], df["modeprimary"])

chi2, p, dof, expected = chi2_contingency(contingency)

n = contingency.values.sum()
r, k = contingency.shape
cramers_v = np.sqrt(chi2 / (n * (min(r-1, k-1))))

print(cramers_v)