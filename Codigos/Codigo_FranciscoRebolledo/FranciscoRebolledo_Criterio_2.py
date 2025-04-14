import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

#------------------------------------------------Cargar archivo Excel--------------------------------------------

base_dir = os.path.dirname(__file__)
file_path = os.path.join(base_dir, "..", "..", "Fuentes de Datos", "Datos_FranciscoRebolledo", "2023_0302_desembarque_total_por_region_20240610.xlsx")
df = pd.read_excel(file_path, sheet_name="des_total_region_2023", skiprows=4)

#---------------------------------------------------Limpiar datos------------------------------------------------

df = df.rename(columns={df.columns[0]: "Especie"})
df = df[df["Especie"].notna()]
df = df[~df["Especie"].str.upper().str.contains("TOTAL")]
if 'Total' in df.columns:
    df = df.drop(columns=['Total'])

df = df.replace("-", 0)
df.iloc[:, 1:] = df.iloc[:, 1:].apply(pd.to_numeric, errors="coerce").fillna(0)

#--------------------------------------------Transformar a formato largo-----------------------------------------

df_long = df.melt(id_vars="Especie", var_name="Región", value_name="Toneladas")

#---------------------------------Seleccionar 10 especies con más toneladas totales------------------------------

top_species = df_long.groupby("Especie")["Toneladas"].sum().nlargest(10).index
df_top = df_long[df_long["Especie"].isin(top_species)]

#-----------------------------------------Crear tabla pivote para gráfico----------------------------------------

heatmap_data = df_top.pivot_table(index="Especie", columns="Región", values="Toneladas", aggfunc="sum", fill_value=0)
heatmap_data = heatmap_data.loc[heatmap_data.sum(axis=1).sort_values(ascending=False).index]

#---------------------------------------------------Heatmap------------------------------------------------------

plt.figure(figsize=(16, 9))
sns.heatmap(heatmap_data, cmap="YlGnBu", annot=True, fmt=".0f", linewidths=0.5, linecolor='gray')

plt.title("Desembarque de Top 10 especies por región (2023)", fontsize=16)
plt.xlabel("Región", fontsize=12)
plt.ylabel("Especie", fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()