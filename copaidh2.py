# CAMPEÕES x PIB

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import wbgapi as wb
from adjustText import adjust_text

print("--- 1. PROCESSANDO TODO O HISTÓRICO DO KAGGLE (DESDE 1930) ---")
df = pd.read_csv("WorldCupMatches.csv").dropna(subset=["Year", "MatchID"])
df["Year"] = df["Year"].astype(int)


# Função para calcular os pontos por partida
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

# Separando jogo dentro e fora de casa
home_df = df[["Year", "Home Team Initials", "Home_Points"]].rename(
    columns={"Home Team Initials": "Pais_ISO", "Home_Points": "Pontos"}
)
away_df = df[["Year", "Away Team Initials", "Away_Points"]].rename(
    columns={"Away Team Initials": "Pais_ISO", "Away_Points": "Pontos"}
)
df_todos_jogos = pd.concat([home_df, away_df], ignore_index=True)

# Agrupando desempenho por ano e país
df_desempenho = (
    df_todos_jogos.groupby(["Year", "Pais_ISO"])
    .agg(Pontos_Conquistados=("Pontos", "sum"), Jogos_Disputados=("Pontos", "count"))
    .reset_index()
)

# Cálculo do aproveitamento percentual
df_desempenho["Aproveitamento_%"] = (
    df_desempenho["Pontos_Conquistados"] / (df_desempenho["Jogos_Disputados"] * 3)
) * 100


print("\n--- 2. TRADUZINDO SIGLAS PARA O BANCO MUNDIAL ---")
tradutor_iso = {
    "GER": "DEU",
    "FRG": "DEU",
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
    "BRA": "BRA",
    "FRA": "FRA",
    "ITA": "ITA",
    "ESP": "ESP",
    "ARG": "ARG",
    "URS": "RUS",
    "TCH": "CZE",
    "YUG": "SRB",
}

df_analise = df_desempenho.copy()
df_analise["Banco_Mundial_ISO"] = (
    df_analise["Pais_ISO"].map(tradutor_iso).fillna(df_analise["Pais_ISO"])
)


print("\n--- 3. BUSCANDO DADOS NO BANCO MUNDIAL (API) ---")
indicador_pib = "NY.GDP.PCAP.CD"

paises_busca = list(df_analise["Banco_Mundial_ISO"].unique())
# Filtramos para buscar apenas dados de 1960 em diante na API
anos_busca = [y for y in list(df_analise["Year"].unique()) if y >= 1960]

df_wb = wb.data.DataFrame(
    indicador_pib, economy=paises_busca, time=anos_busca, db=2
)
df_wb = df_wb.reset_index()

df_wb_long = df_wb.melt(
    id_vars=["economy"], var_name="Year_Raw", value_name="PIB_Per_Capita"
)
df_wb_long["Year"] = df_wb_long["Year_Raw"].str.extract(r"(\d+)").astype(int)
df_wb_final = df_wb_long[["economy", "Year", "PIB_Per_Capita"]].rename(
    columns={"economy": "Banco_Mundial_ISO"}
)


print(
    "\n--- 4. CRUZANDO AS BASES E ADICIONANDO COPAS RECENTES (2018 e 2022) ---"
)
df_final = pd.merge(
    df_analise, df_wb_final, on=["Banco_Mundial_ISO", "Year"], how="left"
)

# Adicionamos manualmente os dois últimos campeões do mundo (França 2018 e Argentina 2022)
dados_recentes = [
    {
        "Year": 2018,
        "Pais_ISO": "FRA",
        "Banco_Mundial_ISO": "FRA",
        "Pontos_Conquistados": 19,
        "Jogos_Disputados": 7,
        "Aproveitamento_%": 90.48,
        "PIB_Per_Capita": 41570.0,
    },
    {
        "Year": 2022,
        "Pais_ISO": "ARG",
        "Banco_Mundial_ISO": "ARG",
        "Pontos_Conquistados": 14,
        "Jogos_Disputados": 7,
        "Aproveitamento_%": 66.66,
        "PIB_Per_Capita": 13650.0,
    },
]

df_recentes = pd.DataFrame(dados_recentes)
df_final = pd.concat([df_final, df_recentes], ignore_index=True)


print("\n--- 5. GERANDO O GRÁFICO EXCLUSIVO DOS CAMPEÕES (1960-2022) ---")
plt.clf()
plt.close("all")

# Lista com os campeões para filtragem exata
campeoes_historicos = {
    1930: "URU",
    1934: "ITA",
    1938: "ITA",
    1950: "URU",
    1954: "FRG",
    1958: "BRA",
    1962: "BRA",
    1966: "ENG",
    1970: "BRA",
    1974: "FRG",
    1978: "ARG",
    1982: "ITA",
    1986: "ARG",
    1990: "FRG",
    1994: "BRA",
    1998: "FRA",
    2002: "BRA",
    2006: "ITA",
    2010: "ESP",
    2014: "GER",
    2018: "FRA",
    2022: "ARG",
}

# Filtra o DataFrame para conter APENAS quem ergueu a taça
df_final["Eh_Campeao"] = df_final.apply(
    lambda row: campeoes_historicos.get(row["Year"]) == row["Pais_ISO"], axis=1
)
df_campeoes = df_final[df_final["Eh_Campeao"] == True].copy()

# Remove registros anteriores a 1960 que não possuem dados de PIB na API
df_campeoes_valido = df_campeoes.dropna(subset=["PIB_Per_Capita"])

plt.figure(figsize=(14, 8))
sns.set_theme(style="whitegrid")

# Linha de tendência calculada estritamente sobre os campeões válidos
sns.regplot(
    data=df_campeoes_valido,
    x="PIB_Per_Capita",
    y="Aproveitamento_%",
    scatter=False,
    truncate=True,
    line_kws={
        "color": "#e74c3c",
        "linestyle": "-",
        "linewidth": 2.5,
        "label": "Tendência dos Campeões",
    },
)

# Plotar os pontos clássicos dourados dos campeões
plt.scatter(
    df_campeoes_valido["PIB_Per_Capita"],
    df_campeoes_valido["Aproveitamento_%"],
    color="#f1c40f",
    alpha=0.9,
    edgecolors="black",
    s=150,
    label="Campeão Mundial",
)

# Geração de rótulos dinâmicos com setas conectoras
textos = []
for idx, row in df_campeoes_valido.iterrows():
    exibir_nome = "GER" if row["Pais_ISO"] == "FRG" else row["Pais_ISO"]
    label = f"{exibir_nome} ({int(row['Year'])})"

    txt = plt.text(
        row["PIB_Per_Capita"],
        row["Aproveitamento_%"],
        label,
        fontsize=9,
        weight="bold",
        color="#2c3e50",
    )
    textos.append(txt)

print("Ajustando os rótulos dos campeões e criando as setas...")
adjust_text(
    textos, arrowprops=dict(arrowstyle="->", color="black", lw=0.6, alpha=0.5)
)

# Customizações finais de layout e margens estritas
plt.title(
    "Histórico dos Campeões do Mundo x PIB Per Capita (1960 - 2022)",
    fontsize=16,
    pad=15,
    weight="bold",
)
plt.xlabel("PIB Per Capita no Ano do Título (USD Atual)", fontsize=12)
plt.ylabel("Aproveitamento de Pontos do Campeão (%)", fontsize=12)

plt.xlim(
    df_campeoes_valido["PIB_Per_Capita"].min() - 2000,
    df_campeoes_valido["PIB_Per_Capita"].max() + 5000,
)
plt.ylim(65, 105)
plt.legend(loc="lower right", fontsize=11)

plt.tight_layout()
print("Pronto! Exibindo o gráfico corrigido dos campeões...")
plt.show()