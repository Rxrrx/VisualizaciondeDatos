import pandas as pd
import os
import plotly.express as px
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Obtener la ruta absoluta del archivo
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_base = os.path.dirname(os.path.dirname(ruta_actual))  # Subir dos niveles
ruta_plantas = os.path.join(ruta_base, 'Fuentes de Datos', 'Datos_JuanGarcia', '2023_0502_plantas_por_lineas.xlsx')
ruta_variacion = os.path.join(ruta_base, 'Fuentes de Datos', 'Datos_JuanGarcia', '2023_0201_series_2013-2023_v20240617.xls')

# Leer el archivo de desembarque saltando las primeras 5 filas
df_industrial = pd.read_excel(ruta_plantas, skiprows=3)
df_variacion = pd.read_excel(ruta_variacion, skiprows=4)

# Crear diccionario de regiones
regiones = {
    1: 'Primera Región',
    2: 'Segunda Región',
    3: 'Tercera Región',
    4: 'Cuarta Región',
    5: 'Quinta Región',
    6: 'Sexta Región',
    7: 'Séptima Región',
    8: 'Octava Región',
    9: 'Novena Región',
    10: 'Décima Región',
    11: 'Undécima Región',
    12: 'Duodécima Región',
    13: 'Región Metropolitana',
    14: 'Decimocuarta Región',
    15: 'Decimoquinta Región',
    16: 'Decimosexta Región'
}

# Contar repeticiones y mapear a nombres de regiones
primera_columna = df_industrial.iloc[:, 0]
conteo = primera_columna.value_counts().reset_index()
conteo.columns = ['Número', 'Frecuencia']
conteo['Región'] = conteo['Número'].map(regiones)

# Crear el treemap con nombres de regiones
fig = px.treemap(conteo, 
                 values='Frecuencia',
                 path=['Región'],
                 title='Plantas por Región<br><sup>Fuente: SERNAPESCA (plantas por línea)</sup>')
fig.show()

# Encontrar las filas que comienzan con TOTAL, excluyendo TOTAL PAIS y GENERAL
indices_filas = []
nombres_indices = []

for idx, row in df_variacion.iterrows():
    valor = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
    if (valor.upper().startswith('TOTAL') and 
        'PAIS' not in valor.upper() and 
        'GENERAL' not in valor.upper()):
        nombres_indices.append(valor)
        # Convertir guiones a NaN y luego a números
        datos = pd.to_numeric(row.iloc[1:].replace('-', np.nan), errors='coerce')
        indices_filas.append(datos.values)

# Crear DataFrame con los datos transpuestos y tomar solo las primeras 5 filas
df_procesado = pd.DataFrame(indices_filas, index=nombres_indices)
df_procesado.columns = [str(year) for year in range(2013, 2013 + len(df_procesado.columns))]
df_5_filas = df_procesado.head()

# Preparar datos para plotly
df_plot = df_5_filas.reset_index()
df_plot = df_plot.melt(id_vars=['index'], var_name='Año', value_name='Valor')

# Crear gráfico de líneas interactivo con áreas
fig_lines = px.area(df_plot, 
                    x='Año', 
                    y='Valor', 
                    color='index',
                    title='Evolución de pesca y recolecion Totales por Año<br><sup>Fuente: SERNAPESCA (series)</sup>',
                    line_shape='spline')  # Para suavizar las líneas

fig_lines.update_layout(
    xaxis_title='Años',
    yaxis_title='Valores',
    legend_title='Categorías',
    showlegend=True
)

fig_lines.update_traces(
    opacity=0.6,  # Transparencia de las áreas
    line=dict(width=2)  # Grosor de las líneas
)

fig_lines.show()