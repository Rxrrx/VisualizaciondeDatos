import pandas as pd
import plotly.express as px
import numpy as np


df = pd.read_csv("aquaculture-farmed-fish-production.csv")

df_total = df.groupby(['Entity', 'Code'], as_index=False)['Aquaculture production (metric tons)'].sum()

df_total['Producción acuícola (log)'] = np.log10(df_total['Aquaculture production (metric tons)'] + 1)

fig = px.choropleth(
    df_total,
    locations='Code',
    color='Producción acuícola (log)',
    hover_name='Entity',
    color_continuous_scale='Aggrnyl',
    title='Producción Acuícola Mundial (escala logarítmica)',
    labels={'Producción acuícola (log)': 'Producción acuícola (escala logarítmica)'}
)

fig.write_html("mapa_acuicultura.html")