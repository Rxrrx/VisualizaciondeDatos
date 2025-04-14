import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

# Desactivar advertencias de pandas
warnings.filterwarnings('ignore', category=FutureWarning)
pd.set_option('future.no_silent_downcasting', True)

# Función para cargar y procesar datos de SST
def cargar_procesar_sst(archivo, sheet_name):
    try:
        df_raw = pd.read_excel(archivo, sheet_name=sheet_name, header=None, engine='openpyxl')
        
        # Buscar encabezado
        header_idx = None
        for i, row in df_raw.iterrows():
            if isinstance(row[0], str) and 'year,month,day' in row[0]:
                header_idx = i
                break
        
        if header_idx is None:
            raise ValueError("No se encontró una fila con 'year,month,day' en el encabezado")
        
        header_row = df_raw.iloc[header_idx, 0]
        columns = header_row.split(',')
        
        # Procesar datos
        data_rows = df_raw.iloc[header_idx + 1 :, 0].dropna().tolist()
        data = []
        for row in data_rows:
            if isinstance(row, str):
                split_row = row.split(',')
                if len(split_row) >= len(columns):
                    data.append(split_row[:len(columns)])
        
        df_data = pd.DataFrame(data, columns=columns)
        df_data.columns = df_data.columns.str.lower().str.replace(' ', '_')
        
        # Convertir a formato numérico y crear fechas
        df_data['year'] = pd.to_numeric(df_data['year'], errors='coerce')
        df_data['month'] = pd.to_numeric(df_data['month'], errors='coerce')
        df_data['day'] = pd.to_numeric(df_data['day'], errors='coerce')
        df_data['date'] = pd.to_datetime(df_data[['year', 'month', 'day']], errors='coerce')
        df_data = df_data.set_index('date')
        
        # Asegurarse de que la columna de temperatura exista
        if 'mean_temperature_deg_c' in df_data.columns:
            df_data['mean_temperature_deg_c'] = pd.to_numeric(df_data['mean_temperature_deg_c'], errors='coerce')
        else:
            raise KeyError("No se encontró la columna 'mean_temperature_deg_c'")
        
        # Filtrar y promediar por año
        df_data = df_data.loc['2007':'2017']
        df_anual = df_data.resample('Y').mean(numeric_only=True)
        return df_anual['mean_temperature_deg_c']
    except Exception as e:
        print(f"Error procesando SST: {e}")
        raise

# Función para cargar y procesar datos de desembarque
def cargar_procesar_desembarque(archivo):
    try:
        df = pd.read_excel(archivo, header=None)
        row = df[df[0].str.contains("TOTAL PAIS", na=False)]
        if row.empty:
            raise ValueError("No se encontró la fila 'TOTAL PAIS'")
        
        # Extraer valores y convertir a millones de toneladas
        values = row.iloc[0, 1:12].values
        values = pd.Series(values).apply(lambda x: pd.to_numeric(x, errors='coerce')).fillna(0)
        values = values / 1000000  # Convertir a millones de toneladas
        values = values.clip(lower=0)
        years = pd.date_range(start='2007-12-31', end='2017-12-31', freq='Y')
        return pd.Series(values, index=years, name='Desembarque Total (millones ton)')
    except Exception as e:
        print(f"Error procesando desembarque: {e}")
        raise

# Cargar datos
try:
    sst_anual = cargar_procesar_sst("SST_ABSO_077.50W_072.50W_32.50S_27.xlsx", "SST_ABSO_077.50W_072.50W_32.50S")
    desembarque_anual = cargar_procesar_desembarque("2.series_2007_-_2017-1.xlsx")
except Exception as e:
    print("No se pudo cargar los datos:", e)
    exit(1)

# Alinear los años
years = sst_anual.index.intersection(desembarque_anual.index)
sst_anual = sst_anual.loc[years]
desembarque_anual = desembarque_anual.loc[years]

# Crear figura con dos ejes Y
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Añadir traza para la temperatura
fig.add_trace(
    go.Scatter(
        x=sst_anual.index.year,
        y=sst_anual,
        name="Temperatura Media (°C)",
        line=dict(color='royalblue', width=2),
        hovertemplate="Año: %{x}<br>Temperatura: %{y:.2f}°C<extra></extra>"
    ),
    secondary_y=False,
)

# Añadir traza para el desembarque
fig.add_trace(
    go.Scatter(
        x=desembarque_anual.index.year,
        y=desembarque_anual,
        name="Desembarque Total (millones ton)",
        line=dict(color='firebrick', width=2, dash='dash'),
        hovertemplate="Año: %{x}<br>Desembarque: %{y:.2f} millones ton<extra></extra>"
    ),
    secondary_y=True,
)

# Añadir sombreados para eventos de El Niño y La Niña
fig.add_vrect(x0=2009, x1=2010, fillcolor="orange", opacity=0.2, line_width=0,
              annotation_text="El Niño", annotation_position="top left")
fig.add_vrect(x0=2015, x1=2016, fillcolor="orange", opacity=0.2, line_width=0,
              annotation_text="El Niño", annotation_position="top left")
fig.add_vrect(x0=2007, x1=2008, fillcolor="lightblue", opacity=0.2, line_width=0,
              annotation_text="La Niña", annotation_position="top right")
fig.add_vrect(x0=2010, x1=2011, fillcolor="lightblue", opacity=0.2, line_width=0,
              annotation_text="La Niña", annotation_position="top right")

# Personalizar el diseño
fig.update_layout(
    title={
        'text': "Relación entre Temperatura Superficial del Mar y Desembarque Pesquero en Chile (2007-2017)<br><sub>Fuentes: ESA CCI (SST), SERNAPESCA (Desembarque)</sub>",
        'font': dict(size=18, family="Arial")
    },
    font=dict(size=12),
    height=600,
    width=1000,
    margin=dict(l=50, r=50, t=100, b=50),
    legend_title="Variables",
    template="plotly_white"
)

# Ajustar los ejes
fig.update_xaxes(title_text="Año")
fig.update_yaxes(title_text="Temperatura Media (°C)", secondary_y=False)
fig.update_yaxes(title_text="Desembarque Total (millones ton)", secondary_y=True, 
                 range=[0, desembarque_anual.max() + 1])

# Exportar el gráfico
try:
    fig.write_image("clima_capturas_lineas.png", engine="kaleido", scale=1)
    fig.write_image("clima_capturas_lineas.pdf", engine="kaleido")
    print("Proceso completado: Gráfico de líneas exportado")
except Exception as e:
    print("Error al exportar el gráfico:", e)