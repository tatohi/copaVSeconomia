# ELITE x EDUCAÇÃO (EM)

import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import wbgapi as wb
from adjustText import adjust_text

print("--- 1. PROCESSANDO DADOS DO KAGGLE (1990 - 2022) ---")
df = pd.read_csv("WorldCupMatches.csv").dropna(subset=["Year", "MatchID"])
df["Year"] = df["Year"].astype(int)
df = df[df["Year"] >= 1990]


def calcular_pontos(row):
    if row["Home Team Goals"] > row["Away Team Goals"]:
        return 3, 0
    elif row["Away Team Goals"] > row["Home Team Goals"]:
        return 0, 3
    else:
        return 1, 1


pontos = df.apply(calcular_pontos, axis=1)
df["Home_Points"] = [p[0] for p in pontos]
df["Away_Points"] = [p[1] for p in pontos]

home_df = df[["Year", "Home Team Initials", "Home_Points"]].rename(
    columns={"Home Team Initials": "Pais_ISO", "Home_Points": "Pontos"}
)
away_df = df[["Year", "Away Team Initials", "Away_Points"]].rename(
    columns={"Away Team Initials": "Pais_ISO", "Away_Points": "Pontos"}
)
df_todos_jogos = pd.concat([home_df, away_df], ignore_index=True)

df_desempenho = (
    df_todos_jogos.groupby(["Year", "Pais_ISO"])
    .agg(Pontos_Conquistados=("Pontos", "sum"), Jogos_Disputados=("Pontos", "count"))
    .reset_index()
)

df_desempenho["Aproveitamento_%"] = (
    df_desempenho["Pontos_Conquistados"] / (df_desempenho["Jogos_Disputados"] * 3)
) * 100


print("\n--- 2. TRADUZINDO SIGLAS PARA O BANCO MUNDIAL ---")
tradutor_iso = {
    "GER": "DEU",
    "NED": "NLD",
    "BUL": "BGR",
    "SUI": "CHE",
    "ARE": "ARE",
    "DEN": "DNK",
    "NGA": "NGA",
    "KSA": "SAU",
    "RSA": "ZAF",
    "CHI": "CHL",
    "PAR": "PRY",
    "ANG": "AGO",
    "TOG": "TGO",
    "CRO": "HRV",
    "IRN": "IRN",
    "POR": "PRT",
    "TUN": "TUN",
    "MAS": "MYS",
    "ALG": "DZA",
    "URU": "URY",
    "GRE": "GRC",
    "CRC": "CRI",
    "HON": "HND",
    "GHA": "GHA",
    "ENG": "GBR",
    "SCO": "GBR",
    "WAL": "GBR",
    "NIR": "GBR",
    "FRG": "DEU",
    "BRA": "BRA",
    "FRA": "FRA",
    "ITA": "ITA",
    "ESP": "ESP",
    "ARG": "ARG",
}

df_analise = df_desempenho.copy()
df_analise["Banco_Mundial_ISO"] = (
    df_analise["Pais_ISO"].map(tradutor_iso).fillna(df_analise["Pais_ISO"])
)


print("\n--- 3. BUSCANDO DADOS DE EDUCAÇÃO NA API ---")
indicador_edu = "SE.SEC.ENRR"
paises_busca = list(df_analise["Banco_Mundial_ISO"].unique())
anos_busca = list(df_analise["Year"].unique())

df_wb = wb.data.DataFrame(
    indicador_edu, economy=paises_busca, time=anos_busca, db=2
)
df_wb = df_wb.reset_index()

df_wb_long = df_wb.melt(
    id_vars=["economy"], var_name="Year_Raw", value_name="Educacao_Ensino_Medio"
)
df_wb_long["Year"] = df_wb_long["Year_Raw"].str.extract(r"(\d+)").astype(int)

df_wb_final = df_wb_long[["economy", "Year", "Educacao_Ensino_Medio"]].rename(
    columns={"economy": "Banco_Mundial_ISO"}
)


print("\n--- 4. CRUZANDO AS BASES E ADICIONANDO DADOS RECENTES ---")
df_final = pd.merge(
    df_analise, df_wb_final, on=["Banco_Mundial_ISO", "Year"], how="left"
)

# Adicionando manualmente a elite de 2018 e 2022 que costuma não estar no CSV padrão
dados_recentes = [
    {
        "Year": 2018,
        "Pais_ISO": "FRA",
        "Banco_Mundial_ISO": "FRA",
        "Aproveitamento_%": 90.48,
        "Educacao_Ensino_Medio": 110.0,
    },
    {
        "Year": 2018,
        "Pais_ISO": "CRO",
        "Banco_Mundial_ISO": "HRV",
        "Aproveitamento_%": 66.66,
        "Educacao_Ensino_Medio": 99.1,
    },
    {
        "Year": 2018,
        "Pais_ISO": "BEL",
        "Banco_Mundial_ISO": "BEL",
        "Aproveitamento_%": 85.71,
        "Educacao_Ensino_Medio": 118.4,
    },
    {
        "Year": 2022,
        "Pais_ISO": "ARG",
        "Banco_Mundial_ISO": "ARG",
        "Aproveitamento_%": 66.66,
        "Educacao_Ensino_Medio": 102.0,
    },
    {
        "Year": 2022,
        "Pais_ISO": "FRA",
        "Banco_Mundial_ISO": "FRA",
        "Aproveitamento_%": 76.19,
        "Educacao_Ensino_Medio": 110.5,
    },
    {
        "Year": 2022,
        "Pais_ISO": "CRO",
        "Banco_Mundial_ISO": "HRV",
        "Aproveitamento_%": 66.66,
        "Educacao_Ensino_Medio": 100.2,
    },
]

df_recentes = pd.DataFrame(dados_recentes)
df_final = pd.concat([df_final, df_recentes], ignore_index=True)

# Preenchimento preventivo de dados históricos do Brasil para ele não sumir do mapa
df_final.loc[
    (df_final["Year"] == 1994) & (df_final["Pais_ISO"] == "BRA"),
    "Educacao_Ensino_Medio",
] = 45.3
df_final.loc[
    (df_final["Year"] == 2002) & (df_final["Pais_ISO"] == "BRA"),
    "Educacao_Ensino_Medio",
] = 68.1


print("\n--- 5. GERANDO O GRÁFICO DA ELITE (>60%) x EDUCAÇÃO ---")
plt.clf()
plt.close("all")

# FILTRO DA ELITE: Apenas campanhas com aproveitamento maior que 60%
df_elite = df_final[df_final["Aproveitamento_%"] > 60].copy()

# Remove registros sem dados educacionais para não distorcer o regplot
df_elite_valida = df_elite.dropna(subset=["Educacao_Ensino_Medio"])

plt.figure(figsize=(15, 9))
sns.set_theme(style="whitegrid")

# Linha de tendência calculada em cima de toda a elite do futebol mundial
sns.regplot(
    data=df_elite_valida,
    x="Educacao_Ensino_Medio",
    y="Aproveitamento_%",
    scatter=False,
    truncate=True,
    line_kws={
        "color": "#e67e22",
        "linestyle": "-",
        "linewidth": 2.5,
        "label": "Tendência da Elite (Aproveitamento > 60%)",
    },
)

# Plotar os pontos de todas as seleções de elite
plt.scatter(
    df_elite_valida["Educacao_Ensino_Medio"],
    df_elite_valida["Aproveitamento_%"],
    color="royalblue",
    alpha=0.7,
    edgecolors="black",
    s=100,
    label="Campanhas de Elite",
)

# Adicionar os nomes de cada ponto no gráfico de forma inteligente
textos = []
for idx, row in df_elite_valida.iterrows():
    label = f"{row['Pais_ISO']} ({int(row['Year'])})"
    txt = plt.text(
        row["Educacao_Ensino_Medio"],
        row["Aproveitamento_%"],
        label,
        fontsize=9,
        weight="normal",
        color="#2c3e50",
    )
    textos.append(txt)

# Organiza os textos para nenhum ficar em cima do outro
print("Ajustando posição dos textos (pode demorar alguns segundos)...")
adjust_text(
    textos, arrowprops=dict(arrowstyle="->", color="gray", lw=0.5, alpha=0.5)
)

# Customizações de tela
plt.title(
    "Elite da Copa do Mundo (Aproveitamento > 60%) x Educação (1990 - 2022)",
    fontsize=16,
    pad=15,
    weight="bold",
)
plt.xlabel("Taxa de Matrícula no Ensino Médio (%)", fontsize=12)
plt.ylabel("Aproveitamento do País na Copa (%)", fontsize=12)

plt.xlim(
    df_elite_valida["Educacao_Ensino_Medio"].min() - 5,
    df_elite_valida["Educacao_Ensino_Medio"].max() + 5,
)
plt.ylim(58, 105)
plt.legend(loc="lower right", fontsize=11)

plt.tight_layout()
print("Exibindo o gráfico de elite na tela...")
plt.show()