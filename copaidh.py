# ELITE x PIB

import pandas as pd
import wbgapi as wb
import matplotlib.pyplot as plt
import seaborn as sns
# IMPORTANTE: Certifique-se de ter instalado via terminal: pip install adjustText
from adjustText import adjust_text

print("--- 1. PROCESSANDO DADOS DO KAGGLE ---")
df = pd.read_csv('WorldCupMatches.csv').dropna(subset=['Year', 'MatchID'])
df['Year'] = df['Year'].astype(int)
df = df[df['Year'] >= 1990]

def calcular_pontos(row):
    if row['Home Team Goals'] > row['Away Team Goals']:
        return 3, 0
    elif row['Away Team Goals'] > row['Home Team Goals']:
        return 0, 3
    else:
        return 1, 1

pontos = df.apply(calcular_pontos, axis=1)
df['Home_Points'] = [p[0] for p in pontos]
df['Away_Points'] = [p[1] for p in pontos]

home_df = df[['Year', 'Home Team Initials', 'Home_Points']].rename(
    columns={'Home Team Initials': 'Pais_ISO', 'Home_Points': 'Pontos'}
)
away_df = df[['Year', 'Away Team Initials', 'Away_Points']].rename(
    columns={'Away Team Initials': 'Pais_ISO', 'Away_Points': 'Pontos'}
)
df_todos_jogos = pd.concat([home_df, away_df], ignore_index=True)

df_desempenho = df_todos_jogos.groupby(['Year', 'Pais_ISO']).agg(
    Pontos_Conquistados=('Pontos', 'sum'),
    Jogos_Disputados=('Pontos', 'count')
).reset_index()

df_desempenho['Aproveitamento_%'] = (df_desempenho['Pontos_Conquistados'] / (df_desempenho['Jogos_Disputados'] * 3)) * 100


print("\n--- 2. TRADUZINDO SIGLAS PARA O BANCO MUNDIAL ---")
tradutor_iso = {
    'GER': 'DEU', 'NED': 'NLD', 'BUL': 'BGR', 'SUI': 'CHE', 'ARE': 'ARE',
    'DEN': 'DNK', 'NGA': 'NGA', 'KSA': 'SAU', 'RSA': 'ZAF', 'CHI': 'CHL',
    'PAR': 'PRY', 'ANG': 'AGO', 'TOG': 'TGO', 'CRO': 'HRV', 'IRN': 'IRN',
    'POR': 'PRT', 'TUN': 'TUN', 'MAS': 'MYS', 'ALG': 'DZA', 'URU': 'URY',
    'GRE': 'GRC', 'CRC': 'CRI', 'HON': 'HND', 'GHA': 'GHA', 'ENG': 'GBR',
    'SCO': 'GBR', 'WAL': 'GBR', 'NIR': 'GBR', 'FRG': 'DEU', 'BRA': 'BRA',
    'FRA': 'FRA', 'ITA': 'ITA', 'ESP': 'ESP', 'ARG': 'ARG'
}

df_analise = df_desempenho.copy()
df_analise['Banco_Mundial_ISO'] = df_analise['Pais_ISO'].map(tradutor_iso).fillna(df_analise['Pais_ISO'])


print("\n--- 3. BUSCANDO DADOS NO BANCO MUNDIAL (API) ---")
indicadores = {
    'NY.GDP.PCAP.CD': 'PIB_Per_Capita',
    'SE.SEC.ENRR': 'Educacao_Ensino_Medio'
}

paises_busca = list(df_analise['Banco_Mundial_ISO'].unique())
anos_busca = list(df_analise['Year'].unique())

df_wb = wb.data.DataFrame(indicadores.keys(), economy=paises_busca, time=anos_busca, db=2)
df_wb = df_wb.reset_index()

df_wb_long = df_wb.melt(id_vars=['economy', 'series'], var_name='Year_Raw', value_name='Valor')
df_wb_long['Year'] = df_wb_long['Year_Raw'].str.extract(r'(\d+)').astype(int)

df_wb_pivot = df_wb_long.pivot(index=['economy', 'Year'], columns='series', values='Valor').reset_index()
df_wb_pivot = df_wb_pivot.rename(columns=indicadores).rename(columns={'economy': 'Banco_Mundial_ISO'})


print("\n--- 4. CRUZANDO AS BASES DE DADOS ---")
df_final = pd.merge(
    df_analise,
    df_wb_pivot,
    on=['Banco_Mundial_ISO', 'Year'],
    how='inner'
)


print("\n--- 5. GERANDO O GRÁFICO DA ELITE DA COPA ---")
plt.clf()
plt.close('all')

# Filtrar apenas os países de alto desempenho (Aproveitamento > 60%)
df_elite = df_final[df_final['Aproveitamento_%'] > 60].copy()

# Remove nulos apenas do PIB para não bugar o gráfico
df_elite_valida = df_elite.dropna(subset=['PIB_Per_Capita'])

plt.figure(figsize=(14, 8))
sns.set_theme(style="whitegrid")

# CORREÇÃO CRUCIAL: Mudamos 'data=df_final' para 'data=df_elite_valida'
# Agora a linha será calculada baseada APENAS nos pontos que estão na tela!
sns.regplot(
    data=df_elite_valida, x='PIB_Per_Capita', y='Aproveitamento_%', 
    scatter=False, truncate=True,
    line_kws={'color':'red', 'linewidth': 2.5, 'label': 'Tendência da Elite (>60%)'}
)

# Plotar os pontos da elite
plt.scatter(
    df_elite_valida['PIB_Per_Capita'], df_elite_valida['Aproveitamento_%'], 
    color='royalblue', alpha=0.7, edgecolors='black', s=100, label='Campanhas de Elite (>60%)'
)

# Adicionar os nomes dos países e anos com o adjust_text
textos = []
for idx, row in df_elite_valida.iterrows():
    label = f"{row['Pais_ISO']} ({int(row['Year'])})"
    peso_fonte = 'bold' if row['Aproveitamento_%'] == 100 else 'normal'
    
    txt = plt.text(
        row['PIB_Per_Capita'], row['Aproveitamento_%'], label,
        fontsize=9,
        weight=peso_fonte,
        color="#2c3e50"
    )
    textos.append(txt)

print("Organizando rótulos e desenhando as setas...")
adjust_text(
    textos, 
    arrowprops=dict(arrowstyle="->", color="gray", lw=0.6, alpha=0.6)
)

# Customização dos eixos e títulos
plt.title('Elite da Copa do Mundo (1990 - Presente) x PIB Per Capita', fontsize=16, pad=15, weight='bold')
plt.xlabel('PIB Per Capita (USD Atual)', fontsize=12)
plt.ylabel('Aproveitamento do País na Copa (%)', fontsize=12)

# Ajuste perfeito dos limites para enquadrar as bolinhas e a nova linha
plt.xlim(df_elite_valida['PIB_Per_Capita'].min() - 2000, df_elite_valida['PIB_Per_Capita'].max() + 5000)
plt.ylim(58, 105) 

plt.legend(loc='lower right', fontsize=11)

plt.tight_layout()
print("Exibindo o gráfico com a linha de tendência corrigida!")
plt.show()