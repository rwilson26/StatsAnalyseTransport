# Auteur : Rémy Wilson
# Programme : Nuage à points avec régression et matrice de corrélation complexe
# Date: 3 Janvier 2025

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from math import radians, sin, cos, sqrt, atan2
from scipy.stats import pearsonr

df = pd.read_csv('_CLEANDATA_.csv')

zone_coords = {
    1: (45.4215, -75.6972), 50: (45.4050, -75.6800), 100: (45.4350, -75.6500),
    120: (45.3900, -75.6700), 140: (45.3850, -75.6600), 180: (45.3650, -75.6700),
    200: (45.3700, -75.7200), 240: (45.3800, -75.7400), 260: (45.3500, -75.7600),
    300: (45.4700, -75.5200), 350: (45.5200, -75.5500), 360: (45.3200, -75.5800),
    400: (45.3500, -75.5500), 425: (45.3000, -75.7000), 450: (45.2500, -75.7500),
    500: (45.3500, -75.9000), 560: (45.4000, -75.9500), 600: (45.4300, -75.7100),
    625: (45.4500, -75.7500), 650: (45.4800, -75.7300), 700: (45.4000, -75.8500),
    750: (45.5500, -75.9000), 800: (45.4650, -75.7200), 820: (45.4800, -75.6800),
    840: (45.5500, -75.6000), 845: (45.6000, -75.5500)
}

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance

centre_ville_coords = zone_coords[1]

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

zone_col = 'originreportzone'
mode_col = 'modeprimary'

df_clean = df.dropna(subset=[zone_col, mode_col])

def get_sector_category(zone_id):
    for categorie, zones in sector_classification.items():
        if zone_id in zones:
            return categorie
    return None

def get_mode_category(mode_id):
    for categorie, modes in mode_categories.items():
        if mode_id in modes:
            return categorie
    return None

df_clean['Categorie_Secteur'] = df_clean[zone_col].apply(get_sector_category)
df_clean['Categorie_Mode'] = df_clean[mode_col].apply(get_mode_category)

zone_data = []

for zone_id, zone_name in zones_dict.items():
    df_zone = df_clean[df_clean[zone_col] == zone_id]
    total_deplacements = len(df_zone)
    
    if total_deplacements > 0:
        part_auto = len(df_zone[df_zone['Categorie_Mode'] == 'Auto']) / total_deplacements * 100
        part_tc = len(df_zone[df_zone['Categorie_Mode'] == 'Transport en commun']) / total_deplacements * 100
        part_actifs = len(df_zone[df_zone['Categorie_Mode'] == 'Modes actifs']) / total_deplacements * 100
        
        zone_lat, zone_lon = zone_coords[zone_id]
        distance_km = calculate_distance(centre_ville_coords[0], centre_ville_coords[1], 
                                        zone_lat, zone_lon)
        
        secteur = get_sector_category(zone_id)
        
        zone_data.append({
            'Zone_ID': zone_id,
            'Zone_Nom': zone_name,
            'Secteur': secteur,
            'Distance_km': distance_km,
            'Part_Auto': part_auto,
            'Part_TC': part_tc,
            'Part_Actifs': part_actifs,
            'Total_Deplacements': total_deplacements
        })

analysis_df = pd.DataFrame(zone_data)

# Module-level configuration (replaces CorrelationMatrix class variables)
num_vars = ["Distance_km", "Part_Auto", "Part_TC", "Part_Actifs"]
secteur_colors = {
    "Centre-ville": "#E63946", 
    "Banlieue intérieure": "#457B9D",
    "Banlieue extérieure": "#2A9D8F"
}

var_labels = {
    "Distance_km": "Distance au centre-ville (km)",
    "Part_Auto": "Part automobile (%)",
    "Part_TC": "Part transport en commun (%)",
    "Part_Actifs": "Part modes actifs (%)"
}


def corr_by_secteur(x, y, **kws):
    ax = plt.gca()
    df_temp = kws.get("data", analysis_df)

    ypos = 0.85
    for secteur, color in secteur_colors.items():
        sub = df_temp[df_temp["Secteur"] == secteur]
        if len(sub) > 2:
            r, p = pearsonr(sub[x.name].dropna(), sub[y.name].dropna())
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            ax.text(0.5, ypos, f"{secteur}: r = {r:.3f}{sig}",
                    transform=ax.transAxes,
                    ha="center", va="center", fontsize=11, color=color,
                    fontweight="bold")
        ypos -= 0.18

    r_global, p_global = pearsonr(df_temp[x.name].dropna(), df_temp[y.name].dropna())
    sig_global = "***" if p_global < 0.001 else "**" if p_global < 0.01 else "*" if p_global < 0.05 else ""
    ax.text(0.5, ypos, f"Corrélation globale: r = {r_global:.3f}{sig_global}",
            transform=ax.transAxes,
            ha="center", va="center", fontsize=12, color="black",
            bbox=dict(facecolor="lightgrey", edgecolor="black", boxstyle="round,pad=0.3", alpha=0.9))


def scatter_with_regression(x, y, **kws):
    ax = plt.gca()
    color = kws.get("color")

    ax.scatter(x, y, color=color, alpha=0.6, s=100, edgecolor='black', linewidth=1)

    if len(x) > 2:
        mask = ~(np.isnan(x) | np.isnan(y))
        if mask.sum() > 2:
            X = x[mask].values.reshape(-1, 1)
            Y = y[mask].values
            model = np.polyfit(X.flatten(), Y, 1)
            x_range = np.linspace(X.min(), X.max(), 100)
            y_pred = np.polyval(model, x_range)

            try:
                darker_color = sns.set_hls_values(color, l=.3)
            except Exception:
                darker_color = color

            ax.plot(x_range, y_pred, color=darker_color, linewidth=2.5, zorder=3, alpha=0.9)


def plot_correlation_matrix():
    g = sns.PairGrid(analysis_df, vars=num_vars, hue="Secteur", palette=secteur_colors, corner=False, diag_sharey=False, height=3)

    g.map_lower(scatter_with_regression)
    g.map_upper(corr_by_secteur)
    g.map_diag(sns.histplot, kde=True, alpha=0.7, edgecolor='black')

    for i in range(len(num_vars)):
        for j in range(len(num_vars)):
            ax = g.axes[i, j]
            if ax is not None:
                y_var = num_vars[i]
                x_var = num_vars[j]

                if j == 0:
                    ax.set_ylabel(var_labels.get(y_var, y_var), fontsize=11, fontweight="bold", rotation=85)
                    ax.yaxis.set_label_coords(-0.12, 0.5)
                else:
                    ax.set_ylabel("")

                if i == len(num_vars)-1:
                    ax.set_xlabel(var_labels.get(x_var, x_var), fontsize=11, fontweight="bold")
                    ax.xaxis.set_label_coords(0.5, -0.20)
                else:
                    ax.set_xlabel("")

    g.fig.subplots_adjust(top=0.85)
    g.fig.suptitle("Analyse de corrélation des variables de transport", fontsize=20, fontweight="bold", y=0.95)

    g.fig.text(0.25, 0.89, "Secteurs:", fontsize=16, fontweight="bold")
    xpos_start = 0.38
    spacing = 0.15
    for i, (secteur, color) in enumerate(secteur_colors.items()):
        g.fig.text(xpos_start + i * spacing, 0.89, secteur, color=color, fontsize=14, fontweight="bold")

    plt.show()
    return g

def scatterplot():
    
    x = analysis_df['Distance_km'].values
    y = analysis_df['Part_Auto'].values
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    r_squared = r_value ** 2
    
    plt.figure(figsize=(10, 7))
    
    for secteur, color in secteur_colors.items():
        df_secteur = analysis_df[analysis_df['Secteur'] == secteur]
        plt.scatter(df_secteur['Distance_km'], df_secteur['Part_Auto'], 
                   color=color, s=150, alpha=0.7, 
                   edgecolor='black', linewidth=1.5, label=secteur)
    
    x_range = np.array([x.min()-1, x.max()+1])
    y_pred = intercept + slope * x_range
    plt.plot(x_range, y_pred, color="black", linewidth=3, 
            label=f'y = {slope:.3f}x + {intercept:.3f}')
    
    stats_text = f'$r$ = {r_value:.3f}\n$R^2$ = {r_squared:.3f}'
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes,
            fontsize=14, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    plt.xlabel('Distance au centre-ville (km)', fontsize=16, fontweight='bold')
    plt.ylabel('Part automobile (%)', fontsize=16, fontweight='bold')
    plt.title('Relation distance-part automobile', 
             fontsize=20, fontweight='bold', pad=20)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=11)
    plt.tight_layout()

    plt.show()
    
if __name__ == "__main__":
    scatterplot()
    plot_correlation_matrix()