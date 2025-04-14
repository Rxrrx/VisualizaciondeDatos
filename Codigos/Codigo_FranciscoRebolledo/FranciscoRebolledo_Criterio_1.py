import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

#------------------------------------------------Cargar archivo Excel--------------------------------------------

base_dir = os.path.dirname(__file__)
file_path = os.path.join(base_dir, "..", "..", "Fuentes de Datos", "Datos_FranciscoRebolledo", "2023_0303_desembarque_total_por_mes_v20240610.xlsx")
df = pd.read_excel(file_path, sheet_name="des_total_mes_2023", skiprows=4)

#---------------------------------------------------Limpiar datos------------------------------------------------

df = df.rename(columns={df.columns[0]: "Especie"})
df = df[df["Especie"].notna()]
df = df[~df["Especie"].str.upper().str.contains("TOTAL")]
if 'Total' in df.columns:
    df = df.drop(columns=['Total'])
df = df.replace("-", 0)
df.iloc[:, 1:] = df.iloc[:, 1:].apply(pd.to_numeric, errors="coerce").fillna(0)

#--------------------------------------------Transformar a formato largo-----------------------------------------

df_long = df.melt(id_vars="Especie", var_name="Mes", value_name="Toneladas")

#------------------------------Seleccionar las 10 especies más desembarcadas en el año---------------------------

top_species = df_long.groupby("Especie")["Toneladas"].sum().nlargest(10).index
df_top = df_long[df_long["Especie"].isin(top_species)]

#-----------------------------------------Crear tabla pivote para gráfico----------------------------------------

pivot_df = df_top.pivot_table(index="Mes", columns="Especie", values="Toneladas", aggfunc="sum", fill_value=0)

#-------------------------------------------Asegurar orden cronológico-------------------------------------------

meses_orden = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
               "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
pivot_df = pivot_df.reindex(meses_orden)

#-------------------------------------------Gráfico de barras apiladas-------------------------------------------

fig, ax = plt.subplots(figsize=(16, 9))
pivot_df.plot(kind="bar", stacked=True, colormap="tab20", ax=ax)

ax.set_title("Top 10 especies desembarcadas por mes (2023)", fontsize=16)
ax.set_xlabel("Mes", fontsize=12)
ax.set_ylabel("Toneladas", fontsize=12)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
ax.legend(title="Especie", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.grid(True)
plt.show()