# Auteur : Rémy Wilson
# Programme : Graphique Sankey qui montre le flux de temps - Motif - mode
# Date: 31 Décembre 2025

import pandas as pd
import plotly.graph_objects as go

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
    'Auto': '#ff6361',
    'Transport en commun': '#003f5c',
    'Modes actifs': '#58508d',
    'Autres': '#ffa600'
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


def classify_time(time):
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
    df['time_period'] = df['departtime'].apply(classify_time)
    df['hour'] = df['departtime'].apply(get_hour)
    df = df[df['time_period'] != 'Autre']
    return df


def plot_sankey(df, max_flows=50, node_label_size=18):
    df_sample = df.sample(min(len(df), 5000), random_state=42)
    flow_counts = df_sample.groupby(['time_period', 'trip_purpose', 'mode_category']).size().reset_index(name='count')
    flow_counts = flow_counts.nlargest(max_flows, 'count')

    time_nodes = list(flow_counts['time_period'].unique())
    purpose_nodes = list(flow_counts['trip_purpose'].unique())
    mode_nodes = list(flow_counts['mode_category'].unique())

    all_nodes = time_nodes + purpose_nodes + mode_nodes
    node_dict = {node: idx for idx, node in enumerate(all_nodes)}

    source = []
    target = []
    value = []
    link_color_sources = []

    def hex_to_rgba(hex_color, alpha=0.25):
        hex_color = str(hex_color).lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        except Exception:
            r, g, b = (150, 150, 150)
        return f'rgba({r},{g},{b},{alpha})'

    tp_links = (flow_counts.groupby(['time_period', 'trip_purpose'])['count']
                .sum().reset_index())
    for _, row in tp_links.iterrows():
        src = node_dict[row['time_period']]
        tgt = node_dict[row['trip_purpose']]
        source.append(src)
        target.append(tgt)
        value.append(row['count'])
        link_color_sources.append(hex_to_rgba('#90D5FF', alpha=0.25))

    pm_links = (flow_counts.groupby(['trip_purpose', 'mode_category'])['count']
                .sum().reset_index())
    for _, row in pm_links.iterrows():
        src = node_dict[row['trip_purpose']]
        tgt = node_dict[row['mode_category']]
        source.append(src)
        target.append(tgt)
        value.append(row['count'])
        hexcol = purpose_colors.get(row['trip_purpose'], '#95a5a6')
        link_color_sources.append(hex_to_rgba(hexcol, alpha=0.25))

    node_colors = []
    for node in all_nodes:
        if node in time_periods:
            node_colors.append('#90D5FF')
        elif node in purpose_colors:
            node_colors.append(purpose_colors[node])
        elif node in colors:
            node_colors.append(colors[node])
        else:
            node_colors.append('#95a5a6')

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color=node_colors
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_color_sources
        )
    )])

    fig.update_layout(
        font=dict(size=node_label_size, family='"Arial Black", Arial, sans-serif'),
        height=700, width=1200
    )

    fig.show()


if __name__ == '__main__':
    df = pd.read_csv('_CLEANDATA_.csv')
    
    df_prepared = prepare_data(df)
    plot_sankey(df_prepared)