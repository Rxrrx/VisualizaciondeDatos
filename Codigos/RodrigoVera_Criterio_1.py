import pandas as pd
import plotly.graph_objects as go
import warnings

# Desactivar warnings de pandas
warnings.filterwarnings('ignore', category=FutureWarning)
pd.set_option('future.no_silent_downcasting', True)

# 1. Función de carga de datos (sin cambios)
def cargar_limpiar_datos(archivo, hoja, tipo_pesca):
    df = pd.read_excel(
        archivo, 
        sheet_name=hoja, 
        skiprows=4, 
        engine='openpyxl'
    ).dropna(how='all')
    
    df = df[~df.iloc[:, 0].str.contains("TOTAL", na=False)]
    df = df.replace(["-", " "], 0)
    
    cols_numericas = df.columns[1:-1] if "Tipo_Pesca" not in df.columns else df.columns[1:-2]
    df[cols_numericas] = df[cols_numericas].apply(pd.to_numeric, errors='coerce').fillna(0)
    
    df["Tipo_Pesca"] = tipo_pesca
    return df

# Carga de datos
df_artesanal = cargar_limpiar_datos(
    "desembarque_artesanal_por_region_2017-2.xlsx", 
    "des_art_region", 
    "Artesanal"
)
df_industrial = cargar_limpiar_datos(
    "desembarque_industrial_por_region_2017.xlsx", 
    "Des_ind_region", 
    "Industrial"
)

# 2. Procesamiento (sin cambios)
df_completo = pd.concat([df_artesanal, df_industrial], ignore_index=True)
regiones = [col for col in df_completo.columns[1:-2] if col != "Total"]

df_melted = df_completo.melt(
    id_vars=["ESPECIE", "Tipo_Pesca"],
    value_vars=regiones,
    var_name="Region",
    value_name="Toneladas"
)
df_filtrado = df_melted.nlargest(20, "Toneladas")

# 3. Construcción del gráfico (sin cambios)
categorias = {
    "region": {"color": "#a6cee3", "prefix": "Región "},
    "especie": {"color": "#b2df8a", "prefix": ""},
    "tipo_pesca": {"color": "#fb9a99", "prefix": ""}
}

nodos = (
    [f"Región {r}" for r in df_filtrado["Region"].unique()] +
    df_filtrado["ESPECIE"].unique().tolist() +
    df_filtrado["Tipo_Pesca"].unique().tolist()
)

colores_nodos = [
    categorias["region"]["color"] if n.startswith("Región ") else
    categorias["tipo_pesca"]["color"] if n in ["Artesanal", "Industrial"] else
    categorias["especie"]["color"] for n in nodos
]

indices = {nodo: i for i, nodo in enumerate(nodos)}
fuentes, destinos, valores = [], [], []
for _, row in df_filtrado.iterrows():
    fuentes.append(indices[f"Región {row['Region']}"])
    destinos.append(indices[row["ESPECIE"]])
    valores.append(row["Toneladas"])
    
    fuentes.append(indices[row["ESPECIE"]])
    destinos.append(indices[row["Tipo_Pesca"]])
    valores.append(row["Toneladas"])

fig = go.Figure(go.Sankey(
    arrangement="snap",
    node=dict(
        pad=30,
        thickness=15,
        line=dict(color="black", width=0.8),
        label=nodos,
        color=colores_nodos,
        hovertemplate="%{label}<br>Total: %{value:,} ton",
    ),
    link=dict(
        source=fuentes,
        target=destinos,
        value=valores,
        color="rgba(150, 150, 150, 0.3)",
        hovertemplate="%{source.label} → %{target.label}<br>%{value:,} ton",
    )
))

fig.update_layout(
    title={
        'text': "Flujo de Capturas Pesqueras en Chile (2017)<br><sub>Fuente: SERNAPESCA | Top 20 flujos</sub>",
        'font': dict(size=18, family="Arial")
    },
    font=dict(size=12),
    height=900,
    width=1200,
    margin=dict(l=80, r=80, t=100, b=80),
)

# 4. Exportación silenciosa
fig.write_image("sankey_pesca.png", engine="kaleido", scale=1)
fig.write_image("sankey_pesca.pdf", engine="kaleido")
print("Proceso completado: Gráfico exportado")